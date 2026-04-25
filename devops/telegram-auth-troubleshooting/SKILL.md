---
name: telegram-auth-troubleshooting
description: Diagnose and fix cases where the Hermes Telegram bot silently ignores messages from group members (auth allowlist issues).
---

# Telegram Bot: Bot Not Responding in Groups

Diagnose and fix cases where the Hermes Telegram bot silently ignores messages from group members.

## Symptoms

- Bot works in DM but ignores messages in groups
- Bot only responds when explicitly mentioned (`@botname`)
- Logs show `Unauthorized user` warnings
- Privacy mode is already disabled (checked in BotFather)

## Diagnosis Steps

### 1. Check logs for authorization rejections

```bash
grep "Unauthorized user" ~/.hermes/logs/errors.log | tail -20
```

If you see lines like:
```
WARNING gateway.run: Unauthorized user: 8093676393 (Tom Tong) on telegram
```
→ This confirms the authorization allowlist is blocking users.

### 2. Verify privacy mode is disabled (BotFather)

In Telegram, message @BotFather:
1. `/mybots` → select your bot
2. **Bot Settings** → **Bot Privacy** → ensure **Disable** is ON

### 3. Check the allowlist in `~/.hermes/.env`

```bash
grep TELEGRAM_ALLOWED_USERS ~/.hermes/.env
```

If it lists only your username (e.g., `TELEGRAM_ALLOWED_USERS=arm2arm`), other users will be blocked.

## Fix

Edit `~/.hermes/.env` — add the Telegram user ID(s) to the allowlist:

```
# Before:
TELEGRAM_ALLOWED_USERS=arm2arm

# After (add comma-separated IDs):
TELEGRAM_ALLOWED_USERS=arm2arm,8093676393
```

Find a user's Telegram ID by sending them to a bot that reports IDs (like @userinfobot on Telegram).

### Allow all users (less secure, simpler)

Set in `.env`:
```
TELEGRAM_ALLOW_ALL_USERS=true
```

## Restart Gateway

```bash
hermes gateway restart
```

## Key Files

- **`~/.hermes/.env`** — `TELEGRAM_ALLOWED_USERS` env var (comma-separated Telegram user IDs or usernames)
- **`~/.hermes/.env`** — `TELEGRAM_ALLOW_ALL_USERS` (true = no restrictions)
- **`~/.hermes/.env`** — `TELEGRAM_HOME_CHANNEL` (default delivery chat)

## Gotchas

- `.env` changes require a gateway restart — they are not hot-reloaded
- Usernames in the allowlist work (e.g., `arm2arm`) but user IDs are more reliable
- Privacy mode disabled in BotFather is required for the bot to see group messages at all — without it, the bot only sees `/start`, `/help`, mentions, and replies
- If `TELEGRAM_ALLOWED_USERS` is set, it takes precedence over `TELEGRAM_ALLOW_ALL_USERS`
- The bot silently drops unauthorized messages in groups (no error sent to the user) — always check logs first