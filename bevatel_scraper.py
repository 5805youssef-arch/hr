"""
Bevatel Chat Scraper — Production v1.0
=======================================
Scrapes ALL chat messages from Bevatel API within a date range
using forced reverse pagination (cursor-based).

Date Range: 2026-01-03 → 2026-04-02
Strategy:
  1. Index all conversations from the API (with caching)
  2. Filter conversations that overlap with the target date range
  3. For each conversation, fetch messages using reverse pagination
     (the `before` cursor param fetches older messages)
  4. Stop fetching when messages fall before START_DATE
  5. Save results to CSV incrementally
"""

import requests
import pandas as pd
import os
import sys
import time
import json
import logging
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────

ACCOUNT_ID = 305
API_TOKEN = "GECwNWow2Vix9KAvk1tWRQKK"
BASE_URL = "https://chat.bevatel.com/api/v1/accounts"

# Date range (inclusive)
START_DATE = datetime(2026, 1, 3, 0, 0, 0)
END_DATE = datetime(2026, 4, 2, 23, 59, 59)

# Output files
OUTPUT_CSV = "bevatel_chats_2026_Q1.csv"
INDEX_CACHE_FILE = "chats_index_cache.json"
PROGRESS_FILE = "scrape_progress.json"

# Rate limiting / delays
DELAY_BETWEEN_PAGES = 1.0      # seconds between conversation list pages
DELAY_BETWEEN_CHATS = 1.5      # seconds between each conversation scrape
DELAY_BETWEEN_MSG_PAGES = 0.3  # seconds between message pagination calls
DELAY_ON_RATE_LIMIT = 30       # seconds to wait on 429
MAX_RETRIES = 4                # max retries per request

# ─────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("bevatel")

# ─────────────────────────────────────────────────────────────────
# HTTP SESSION
# ─────────────────────────────────────────────────────────────────

session = requests.Session()
session.headers.update({"api_access_token": API_TOKEN})


# ─────────────────────────────────────────────────────────────────
# UTILITY: ROBUST REQUEST WITH RETRY + EXPONENTIAL BACKOFF
# ─────────────────────────────────────────────────────────────────

def api_get(url, params=None):
    """
    GET request with retry logic and exponential backoff.
    Returns parsed JSON on success, None on permanent failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, params=params, timeout=30)

            if r.status_code == 200:
                return r.json()

            if r.status_code == 429:
                wait = DELAY_ON_RATE_LIMIT * attempt
                log.warning(f"Rate limited (429). Waiting {wait}s... (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                continue

            # Other errors
            log.error(f"HTTP {r.status_code} for {url} params={params}")
            if r.status_code >= 500:
                # Server error — retry
                time.sleep(2 ** attempt)
                continue
            # Client error (4xx except 429) — don't retry
            return None

        except requests.exceptions.ConnectionError as e:
            log.warning(f"Connection error (attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(2 ** attempt)
        except requests.exceptions.Timeout:
            log.warning(f"Timeout (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(2 ** attempt)
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            time.sleep(2 ** attempt)

    log.error(f"All {MAX_RETRIES} retries exhausted for {url}")
    return None


# ─────────────────────────────────────────────────────────────────
# UTILITY: TIMESTAMP PARSING
# ─────────────────────────────────────────────────────────────────

def parse_timestamp(ts):
    """Convert a Unix timestamp (seconds) to datetime. Returns None on failure."""
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(int(ts))
    except (ValueError, TypeError, OSError):
        return None


def format_dt(dt):
    """Format datetime to string."""
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ─────────────────────────────────────────────────────────────────
# MODULE 1: INDEX ALL CONVERSATIONS (with disk cache)
# ─────────────────────────────────────────────────────────────────

def load_index_cache():
    """Load cached conversation index from disk if available."""
    if os.path.exists(INDEX_CACHE_FILE):
        try:
            with open(INDEX_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                log.info(f"Loaded {len(data):,} conversations from cache ({INDEX_CACHE_FILE})")
                return data
        except Exception as e:
            log.warning(f"Cache file corrupted ({e}), rebuilding...")
            os.remove(INDEX_CACHE_FILE)
    return None


def save_index_cache(chats):
    """Save conversation index to disk for resume."""
    with open(INDEX_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False)
    log.info(f"Saved index cache: {len(chats):,} conversations")


def fetch_all_conversations():
    """
    Fetch all conversation metadata from the API.
    Uses disk cache to avoid re-fetching on restart.

    Strategy: fetch each status separately (open/resolved/pending) instead of
    status=all, which can cause 500 errors on large datasets due to server-side
    query timeouts. Partial progress is saved after every page so a crash at
    page N resumes from page N rather than restarting from page 1.

    Returns list of conversation dicts sorted oldest-first.
    """
    cached = load_index_cache()
    if cached:
        return cached

    log.info("=" * 60)
    log.info("PHASE 1: Indexing all conversations from server...")
    log.info("=" * 60)

    # Fetch each status type separately to avoid server-side timeouts
    # that occur with status=all on large accounts (causes HTTP 500)
    STATUSES = ["open", "resolved", "pending"]
    seen_ids = set()
    all_chats = []

    # Partial progress file so we can resume within Phase 1 after a crash
    PARTIAL_FILE = INDEX_CACHE_FILE + ".partial"
    start_from = {}  # {status: next_page_to_fetch}

    if os.path.exists(PARTIAL_FILE):
        try:
            with open(PARTIAL_FILE, "r", encoding="utf-8") as f:
                partial = json.load(f)
            all_chats = partial.get("chats", [])
            start_from = partial.get("start_from", {})
            seen_ids = {str(c.get("id")) for c in all_chats}
            log.info(f"Resuming Phase 1 from partial save ({len(all_chats):,} already indexed)")
        except Exception:
            pass

    def save_partial():
        with open(PARTIAL_FILE, "w", encoding="utf-8") as f:
            json.dump({"chats": all_chats, "start_from": start_from}, f, ensure_ascii=False)

    for status in STATUSES:
        page = start_from.get(status, 1)
        log.info(f"  Fetching status='{status}' starting at page {page}...")
        consecutive_500s = 0

        while True:
            params = {"status": status, "per_page": 50, "page": page}
            data = api_get(f"{BASE_URL}/{ACCOUNT_ID}/conversations", params)

            if data is None:
                consecutive_500s += 1
                if consecutive_500s >= 3:
                    log.error(f"  3 consecutive failures on status={status} page={page}, moving on.")
                    break
                log.warning(f"  Page {page} failed, retrying after extra wait...")
                time.sleep(10)
                continue

            consecutive_500s = 0
            payload = data.get("data", {}).get("payload", [])

            if not payload:
                log.info(f"  status='{status}' complete at page {page - 1}.")
                break

            # Deduplicate across statuses (a conv can appear in multiple)
            added = 0
            for chat in payload:
                cid = str(chat.get("id"))
                if cid not in seen_ids:
                    seen_ids.add(cid)
                    all_chats.append(chat)
                    added += 1

            log.info(f"  status='{status}' page {page} | +{added} new | total: {len(all_chats):,}")

            # Save partial progress after every page
            start_from[status] = page + 1
            save_partial()

            page += 1
            time.sleep(DELAY_BETWEEN_PAGES)

    # Clean up partial file now that we're done
    if os.path.exists(PARTIAL_FILE):
        os.remove(PARTIAL_FILE)

    if not all_chats:
        log.error("No conversations found. Check API token / account ID.")
        return []

    # Sort oldest first
    all_chats.sort(key=lambda x: x.get("created_at") or 0)
    save_index_cache(all_chats)
    log.info(f"Indexed {len(all_chats):,} unique conversations total.")
    return all_chats


# ─────────────────────────────────────────────────────────────────
# MODULE 2: FILTER CONVERSATIONS BY DATE RANGE
# ─────────────────────────────────────────────────────────────────

def filter_conversations_by_date(chats):
    """
    Keep only conversations that COULD contain messages in our date range.
    A conversation is relevant if:
      - Its created_at is before END_DATE (it existed during our window)
      - Its last_activity_at (or updated) is after START_DATE (it was active)
    We keep a generous filter here; exact message filtering happens in Phase 3.
    """
    start_ts = int(START_DATE.timestamp())
    end_ts = int(END_DATE.timestamp())

    filtered = []
    for chat in chats:
        created = chat.get("created_at") or 0
        # last_activity_at might be a timestamp or might not exist
        last_activity = chat.get("last_activity_at") or chat.get("timestamp") or created

        # Conversation was created before our end date AND
        # had activity after our start date
        if created <= end_ts and last_activity >= start_ts:
            filtered.append(chat)

    log.info(f"Date filter: {len(filtered):,} / {len(chats):,} conversations overlap with "
             f"{START_DATE.date()} → {END_DATE.date()}")
    return filtered


# ─────────────────────────────────────────────────────────────────
# MODULE 3: FETCH MESSAGES WITH REVERSE PAGINATION
# ─────────────────────────────────────────────────────────────────

def fetch_messages_for_conversation(conv_id):
    """
    Fetch ALL messages for a conversation using reverse pagination.

    Strategy:
      - First call: no `before` param → gets the most recent messages
      - Each subsequent call: `before=<lowest_msg_id>` → gets older messages
      - Stop when:
          a) API returns empty payload (no more messages)
          b) All messages in a batch are older than START_DATE
      - Filter: only keep messages within [START_DATE, END_DATE]

    Returns list of cleaned message dicts.
    """
    url = f"{BASE_URL}/{ACCOUNT_ID}/conversations/{conv_id}/messages"
    messages = []
    seen_ids = set()
    cursor = None  # the `before` cursor (lowest message ID from previous batch)
    page_num = 0

    while True:
        page_num += 1
        params = {}
        if cursor is not None:
            params["before"] = cursor

        data = api_get(url, params)

        if data is None:
            log.warning(f"  Conv {conv_id}: API error at message page {page_num}, stopping.")
            break

        payload = data.get("payload", [])
        if not payload:
            break  # No more messages

        # Track if ALL messages in this batch are before START_DATE
        all_before_start = True
        batch_added = 0

        for msg in payload:
            msg_id = msg.get("id")
            if msg_id is None or msg_id in seen_ids:
                continue
            seen_ids.add(msg_id)

            msg_dt = parse_timestamp(msg.get("created_at"))

            if msg_dt is not None:
                # Check if this message is within our date range
                if START_DATE <= msg_dt <= END_DATE:
                    all_before_start = False
                    messages.append(extract_message_fields(msg, conv_id, msg_dt))
                    batch_added += 1
                elif msg_dt > END_DATE:
                    # Message is AFTER our range — skip but keep paginating backwards
                    all_before_start = False
                elif msg_dt < START_DATE:
                    # Message is BEFORE our range — this one doesn't reset the flag
                    pass
            else:
                # Can't parse timestamp — include it to be safe
                all_before_start = False
                messages.append(extract_message_fields(msg, conv_id, None))
                batch_added += 1

        # If every message in this batch is older than START_DATE, stop
        if all_before_start:
            break

        # Move cursor to the oldest message ID in this batch for next iteration
        batch_ids = [m.get("id") for m in payload if m.get("id") is not None]
        if not batch_ids:
            break

        new_cursor = min(batch_ids)
        if cursor is not None and new_cursor >= cursor:
            # Safety: avoid infinite loop if cursor isn't advancing
            log.warning(f"  Conv {conv_id}: cursor not advancing ({cursor} → {new_cursor}), stopping.")
            break
        cursor = new_cursor

        time.sleep(DELAY_BETWEEN_MSG_PAGES)

    return messages


def extract_message_fields(msg, conv_id, msg_dt):
    """Extract the fields we care about from a raw message dict."""
    # Determine sender
    sender_info = msg.get("sender", {}) or {}
    sender_name = sender_info.get("name", "")
    sender_type = msg.get("message_type")  # 0=incoming, 1=outgoing, 2=activity

    if sender_type == 0:
        sender_label = f"Customer: {sender_name}" if sender_name else "Customer"
    elif sender_type == 1:
        sender_label = f"Agent: {sender_name}" if sender_name else "Agent"
    elif sender_type == 2:
        sender_label = "System"
    else:
        sender_label = sender_name or "Unknown"

    # Message content
    content = msg.get("content") or ""
    # Some messages have content_attributes with more info
    if not content:
        attrs = msg.get("content_attributes", {}) or {}
        if attrs.get("deleted"):
            content = "[deleted]"

    return {
        "conversation_id": conv_id,
        "message_id": msg.get("id"),
        "timestamp": format_dt(msg_dt),
        "sender": sender_label,
        "sender_name": sender_name,
        "message_type": sender_type,
        "content": content,
        "private": msg.get("private", False),
    }


# ─────────────────────────────────────────────────────────────────
# MODULE 4: PROGRESS TRACKING (resume after crash)
# ─────────────────────────────────────────────────────────────────

def load_progress():
    """Load set of already-scraped conversation IDs."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
            return set(str(x) for x in data)
        except Exception:
            return set()
    return set()


def save_progress(done_ids):
    """Save the set of completed conversation IDs."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(done_ids), f)


# ─────────────────────────────────────────────────────────────────
# MODULE 5: CSV OUTPUT
# ─────────────────────────────────────────────────────────────────

CSV_COLUMNS = [
    "conversation_id",
    "message_id",
    "timestamp",
    "sender",
    "sender_name",
    "message_type",
    "content",
    "private",
]


def append_to_csv(messages):
    """Append a batch of messages to the output CSV."""
    if not messages:
        return
    df = pd.DataFrame(messages, columns=CSV_COLUMNS)
    file_exists = os.path.exists(OUTPUT_CSV)
    df.to_csv(
        OUTPUT_CSV,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8-sig",
    )


# ─────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("Bevatel Chat Scraper — Starting")
    log.info(f"Date range: {START_DATE.date()} → {END_DATE.date()}")
    log.info("=" * 60)

    # Phase 1: Index all conversations (cached)
    all_chats = fetch_all_conversations()
    if not all_chats:
        log.error("No conversations to process. Exiting.")
        return

    # Phase 2: Filter by date range
    relevant_chats = filter_conversations_by_date(all_chats)
    if not relevant_chats:
        log.warning("No conversations found in the target date range.")
        return

    # Phase 3: Fetch messages with reverse pagination
    done_ids = load_progress()
    total = len(relevant_chats)
    total_messages = 0
    skipped = 0

    log.info("=" * 60)
    log.info(f"PHASE 3: Fetching messages from {total:,} conversations")
    log.info(f"Already completed: {len(done_ids):,}")
    log.info("=" * 60)

    start_time = time.time()

    for i, chat in enumerate(relevant_chats, 1):
        conv_id = str(chat.get("id"))

        if conv_id in done_ids:
            skipped += 1
            continue

        chat_dt = parse_timestamp(chat.get("created_at"))
        log.info(f"[{i}/{total}] Conv {conv_id} (created {format_dt(chat_dt)}) ... ")

        messages = fetch_messages_for_conversation(conv_id)

        if messages:
            append_to_csv(messages)
            total_messages += len(messages)

        # Mark as done
        done_ids.add(conv_id)
        save_progress(done_ids)

        log.info(f"  → {len(messages)} messages extracted (total so far: {total_messages:,})")

        # ETA calculation
        processed = i - skipped
        if processed > 0:
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = total - i
            if rate > 0:
                eta_seconds = remaining / rate
                eta_min = eta_seconds / 60
                log.info(f"  → ETA: ~{eta_min:.0f} min remaining")

        time.sleep(DELAY_BETWEEN_CHATS)

    # Final summary
    log.info("=" * 60)
    log.info("DONE!")
    log.info(f"Conversations processed: {total - skipped:,}")
    log.info(f"Conversations skipped (already done): {skipped:,}")
    log.info(f"Total messages extracted: {total_messages:,}")
    log.info(f"Output file: {OUTPUT_CSV}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
