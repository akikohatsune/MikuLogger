# MikuLogger

English | [日本語](README.md)

A demo logger that records Discord join/leave events. Logging is enabled **only** after running **/activelogger** in a server.\
**Miku playful mode** is enabled, so messages use a cute, light tone (EN/JA).

## Features
- Real-time join/leave logs (embeds)
- Stores last join/last leave timestamps (UTC)
- Per-guild log channel settings
- Allowlist-based demo access control
- Hybrid commands (slash + prefix)

## Requirements
- Python 3.10+ recommended
- `discord.py>=2.3`

## Setup
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Set the bot token
   ```bash
   export DISCORD_TOKEN="YOUR_TOKEN"
   ```
3. Add your guild ID to the allowlist
   ```json
   {
     "guild_ids": [123456789012345678]
   }
   ```
4. Run
   ```bash
   python main.py
   ```

## Intents
Enable the following in the Discord Developer Portal:
- Server Members Intent
- Message Content Intent (for prefix commands)

## Commands
- `/activelogger #channel` or `!activelogger #channel`
  - Enable logging and set the channel
- `/inactive` or `!inactive`
  - Disable logging
- `/showlog` or `!showlog`
  - Show current settings (only when active)
- `/lastjoin [member]` or `!lastjoin [member]`
  - Show last join time (only when active)
- `/lastout [member]` or `!lastout [member]`
  - Show last leave time (only when active)

## Notes
- Time format: `dd/mm/yyyy HH:MM:SS UTC`
- If a guild is not in the allowlist, commands are blocked.
- If the allowlist file is missing, all commands are blocked.

## Environment Variables
- `DISCORD_TOKEN`: bot token
- `MIKU_DB`: SQLite DB path (default `miku.db`)
- `MIKU_ALLOWLIST`: allowlist JSON path (default `allowlist.json`)
- `MIKU_REPO_URL`: URL shown when demo is not enabled
