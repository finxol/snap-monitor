#!/usr/bin/env python3
"""Eurostar Snap availability check (single pass, for GitHub Actions)."""

import os
import time

import requests

ORIGIN = "7015400"          # London
DESTINATION = "8727100"     # Paris
ADULTS = 1
DATES = [
    "2026-08-21",
]

NO_TICKETS_MARKER = "no Snap tickets are available"
GAP_BETWEEN_DATES = 2.0
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def search_url(date_str):
    return (
        "https://snap.eurostar.com/uk-en/search"
        f"?adult={ADULTS}&origin={ORIGIN}&destination={DESTINATION}"
        f"&outbound={date_str}"
    )


def is_available(date_str):
    try:
        resp = requests.get(
            search_url(date_str),
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-GB,en"},
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [warn] request failed for {date_str}: {e}")
        return None
    text = resp.text
    if "Train results" not in text and "Snap" not in text:
        print(f"  [warn] unexpected page for {date_str}, treating as unknown")
        return None
    return NO_TICKETS_MARKER not in text


def notify(date_str):
    url = search_url(date_str)
    message = (
        f"Eurostar Snap: tickets may be AVAILABLE for {date_str} "
        f"(London to Paris, {ADULTS} adults).\nBook now: {url}"
    )
    print("ALERT:", message)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
                timeout=15,
            )
        except requests.RequestException as e:
            print(f"  [warn] Telegram send failed: {e}")
    else:
        print("  [warn] Telegram not configured, alert printed only")


def main():
    unknown = 0
    for date_str in DATES:
        state = is_available(date_str)
        if state is True:
            notify(date_str)
        elif state is False:
            print(f"  {date_str}: no tickets")
        else:
            print(f"  {date_str}: unknown")
            unknown += 1
        time.sleep(GAP_BETWEEN_DATES)

    # If every date came back "unknown", the check is degraded (Eurostar may be
    # blocking us or changed its page). Exit non-zero so the workflow marks the
    # run as failed and fires the Telegram failure alert.
    if unknown == len(DATES):
        raise SystemExit("ERROR: all dates returned 'unknown' — check is degraded")


if __name__ == "__main__":
    main()
