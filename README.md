# Snap monitor

A small GitHub Actions job that checks [Eurostar Snap](https://snap.eurostar.com)
ticket availability for London → Paris and sends a Telegram alert when tickets
may be available.

## How it works

- [`snap_check.py`](snap_check.py) does a single pass over a list of dates,
  fetching the Eurostar Snap search page for each one (2 adults, London → Paris).
- If the "no Snap tickets are available" marker is **absent** from a date's page,
  it treats that date as possibly available and sends a Telegram message with a
  direct booking link.
- [`.github/workflows/snap.yml`](.github/workflows/snap.yml) runs the script on a
  schedule and can also be triggered manually from the Actions tab.

## Schedule

The workflow is scheduled with `cron: "*/5 * * * *"`. Note that **GitHub Actions
cron has a 5-minute minimum** and scheduled runs are best-effort — they are often
**delayed** under load. In practice this checks roughly every ~5 minutes (and
sometimes less often), not on a guaranteed cadence.

## Configuration

Edit the constants at the top of `snap_check.py` to change the route, number of
adults, or the list of dates.

Telegram credentials are read from environment variables and are **never** stored
in the repo. They are set as GitHub Actions repository secrets:

- `TELEGRAM_BOT_TOKEN` — your bot token from [@BotFather](https://t.me/BotFather)
- `TELEGRAM_CHAT_ID` — the chat id to send alerts to

```sh
gh secret set TELEGRAM_BOT_TOKEN
gh secret set TELEGRAM_CHAT_ID
```

If the secrets are not configured, the script still runs and prints alerts to the
Actions log instead of sending them.

## Running locally

```sh
pip install requests
export TELEGRAM_BOT_TOKEN=...   # optional
export TELEGRAM_CHAT_ID=...     # optional
python snap_check.py
```
