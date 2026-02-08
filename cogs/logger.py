import datetime as dt
import json
import os
from typing import Optional, Set

import discord
from discord import app_commands
from discord.ext import commands

from db import (
    get_guild_settings,
    get_last_join_ts,
    get_last_out_ts,
    set_active,
    set_inactive,
    set_last_join_ts,
    set_last_out_ts,
)

ALLOWLIST_PATH = os.getenv("MIKU_ALLOWLIST", "allowlist.json")
REPO_URL = os.getenv("MIKU_REPO_URL", "https://github.com/yourname/MikuLogger")


def owner_only():
    async def predicate(ctx: commands.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)

    return commands.check(predicate)


def app_owner_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        bot = interaction.client
        if isinstance(bot, commands.Bot):
            return await bot.is_owner(interaction.user)
        return False

    return app_commands.check(predicate)


class JoinLeaveLogger(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._allowlist_cache: Optional[Set[int]] = None
        self._allowlist_mtime: Optional[float] = None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.guild is None:
            return
        if not self._is_allowed(member.guild.id):
            return

        now = int(dt.datetime.now(tz=dt.timezone.utc).timestamp())
        last_out_ts = get_last_out_ts(member.guild.id, member.id)
        set_last_join_ts(member.guild.id, member.id, now)

        channel = self._get_active_log_channel(member.guild)
        if channel is None:
            return

        description = (
            f"Miku waves hello! {member.mention} joined the server / ミクが手を振っています。参加しました。\n"
            f"Last leave / 最終退出: {self._format_short_ts(last_out_ts)}"
        )

        embed = discord.Embed(
            title="Member Joined / 参加",
            description=description,
            color=discord.Color.blue(),
            timestamp=dt.datetime.now(tz=dt.timezone.utc),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="User / ユーザー", value=f"{member} (ID: {member.id})", inline=False
        )
        embed.add_field(
            name="Guild / サーバー", value=f"{member.guild} (ID: {member.guild.id})", inline=False
        )

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        if member.guild is None:
            return
        if not self._is_allowed(member.guild.id):
            return

        now = int(dt.datetime.now(tz=dt.timezone.utc).timestamp())
        last_join_ts = get_last_join_ts(member.guild.id, member.id)
        set_last_out_ts(member.guild.id, member.id, now)

        channel = self._get_active_log_channel(member.guild)
        if channel is None:
            return

        description = (
            f"Miku says bye! {member} left the server / ミクが見送ります。退出しました。\n"
            f"Last join / 最終参加: {self._format_short_ts(last_join_ts)}"
        )

        embed = discord.Embed(
            title="Member Left / 退出",
            description=description,
            color=discord.Color.red(),
            timestamp=dt.datetime.now(tz=dt.timezone.utc),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="User / ユーザー", value=f"{member} (ID: {member.id})", inline=False
        )
        embed.add_field(
            name="Guild / サーバー", value=f"{member.guild} (ID: {member.guild.id})", inline=False
        )

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.hybrid_command(name="activelogger")
    @commands.guild_only()
    @owner_only()
    @app_owner_only()
    @app_commands.guild_only()
    async def activelogger(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """Activate logging in this guild and set the log channel."""
        if not await self._ensure_allowed(ctx):
            return
        set_active(ctx.guild.id, channel.id)
        await ctx.send(
            f"Miku is online! Logging enabled at {channel.mention} / ミク起動! ログを有効化しました。"
        )

    @commands.hybrid_command(name="inactive")
    @commands.guild_only()
    @owner_only()
    @app_owner_only()
    @app_commands.guild_only()
    async def inactive(self, ctx: commands.Context) -> None:
        """Deactivate logging in this guild."""
        if not await self._ensure_allowed(ctx):
            return
        if not await self._ensure_active(ctx):
            return
        set_inactive(ctx.guild.id)
        await ctx.send(
            "Miku is taking a nap. Logging disabled / ミクおやすみ。ログを無効化しました。"
        )

    @commands.hybrid_command(name="showlog")
    @commands.guild_only()
    @owner_only()
    @app_owner_only()
    @app_commands.guild_only()
    async def showlog(self, ctx: commands.Context) -> None:
        """Show current log channel and status for this guild."""
        if not await self._ensure_allowed(ctx):
            return
        if not await self._ensure_active(ctx):
            return
        channel, active = get_guild_settings(ctx.guild.id)
        if channel is None:
            await ctx.send(
                "Miku can't find the log channel yet / ログチャンネル未設定です。"
            )
            return
        status = "enabled" if active else "disabled"
        status = f"{status} / {'有効' if active else '無効'}"
        channel_obj = ctx.guild.get_channel(channel)
        channel_text = channel_obj.mention if channel_obj else f"ID {channel}"
        await ctx.send(f"Log channel: {channel_text}. Status: {status}.")

    @commands.hybrid_command(name="lastjoin")
    @commands.guild_only()
    @owner_only()
    @app_owner_only()
    @app_commands.guild_only()
    async def lastjoin(
        self, ctx: commands.Context, member: Optional[discord.Member] = None
    ) -> None:
        """Show the last join time for a member."""
        if not await self._ensure_allowed(ctx):
            return
        if not await self._ensure_active(ctx):
            return
        member = member or ctx.author
        ts = get_last_join_ts(ctx.guild.id, member.id)
        await ctx.send(
            f"Last join / 最終参加 of {member.mention}: {self._format_short_ts(ts)}"
        )

    @commands.hybrid_command(name="lastout")
    @commands.guild_only()
    @owner_only()
    @app_owner_only()
    @app_commands.guild_only()
    async def lastout(
        self, ctx: commands.Context, member: Optional[discord.Member] = None
    ) -> None:
        """Show the last leave time for a member."""
        if not await self._ensure_allowed(ctx):
            return
        if not await self._ensure_active(ctx):
            return
        member = member or ctx.author
        ts = get_last_out_ts(ctx.guild.id, member.id)
        await ctx.send(
            f"Last leave / 最終退出 of {member.mention}: {self._format_short_ts(ts)}"
        )

    def _get_active_log_channel(
        self, guild: discord.Guild
    ) -> Optional[discord.TextChannel]:
        if not self._is_allowed(guild.id):
            return None
        channel_id, active = get_guild_settings(guild.id)
        if not active or channel_id is None:
            return None
        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            return None
        return channel

    async def _ensure_allowed(self, ctx: commands.Context) -> bool:
        if ctx.guild is None:
            return False
        if not self._is_allowed(ctx.guild.id):
            await ctx.send(
                f"Miku can't run here yet. See: {REPO_URL} / このサーバーでは利用できません。"
            )
            return False
        return True

    async def _ensure_active(self, ctx: commands.Context) -> bool:
        if ctx.guild is None:
            return False
        _, active = get_guild_settings(ctx.guild.id)
        if not active:
            await ctx.send(
                "Miku is not active here yet. Use /activelogger #channel. "
                "/ まだ有効ではありません。/activelogger #channel で有効化してください。"
            )
            return False
        return True

    def _is_allowed(self, guild_id: int) -> bool:
        allowlist = self._load_allowlist()
        return guild_id in allowlist

    def _load_allowlist(self) -> Set[int]:
        try:
            stat = os.stat(ALLOWLIST_PATH)
        except FileNotFoundError:
            self._allowlist_cache = set()
            self._allowlist_mtime = None
            return self._allowlist_cache

        if (
            self._allowlist_cache is not None
            and self._allowlist_mtime == stat.st_mtime
        ):
            return self._allowlist_cache

        try:
            with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._allowlist_cache = set()
            self._allowlist_mtime = stat.st_mtime
            return self._allowlist_cache

        ids = data.get("guild_ids", []) if isinstance(data, dict) else data
        allowlist: Set[int] = set()
        for item in ids if isinstance(ids, list) else []:
            try:
                allowlist.add(int(item))
            except (TypeError, ValueError):
                continue

        self._allowlist_cache = allowlist
        self._allowlist_mtime = stat.st_mtime
        return allowlist

    @staticmethod
    def _format_short_ts(ts: Optional[int]) -> str:
        if ts is None:
            return "no data / データなし"
        ts_dt = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc)
        return ts_dt.strftime("%d/%m/%Y %H:%M:%S UTC")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(JoinLeaveLogger(bot))
