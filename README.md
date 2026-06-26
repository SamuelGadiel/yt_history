# YouTube History CLI

CLI tool to fetch your **complete** YouTube watch history (videos, music, shorts).

## Features

✅ **Complete history** - Videos + Shorts + Music \
✅ **Automatic cookie extraction** from browser \
✅ **Automatic pagination** - Fetches entire history \
✅ **Search** by term \
✅ **Export** to JSON \
✅ **Zero external dependencies** - Custom HTTP client

---

## Installation

### 1. Requirements

- Python 3.11+
- Chrome, Firefox, Safari, Edge, or Brave installed
- Logged into YouTube in your browser

### 2. Setup

```bash
# Clone repository
git clone https://github.com/SamuelGadiel/yt_history.git
cd yt_history

# Create virtual environment
python -m venv venv

# Activate venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### 3. Get YouTube API Key

The API key is YouTube's public web client key. To obtain it:

1. Open any video on [youtube.com](https://youtube.com) (make sure you're logged in)
2. Right-click on the page → **View Page Source** (or press `Ctrl+U` / `Cmd+Option+U`)
3. Search for: `INNERTUBE_API_KEY`
4. Copy the key value

**Edit `.env`** and paste the key:

```bash
YOUTUBE_API_KEY=your_api_key_here
```

> **Note:** This key identifies the client type, not individual users. User authentication is handled via browser cookies.

### 4. Configure Locale (Optional)

By default, timestamps appear in **English** ("Today", "Yesterday").

To change the language, edit `.env`:

```bash
YOUTUBE_LANGUAGE=pt-BR
YOUTUBE_REGION=BR
```

**Format:**

- `YOUTUBE_LANGUAGE`: [BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag) (e.g., `en-US`, `pt-BR`, `es-ES`)
- `YOUTUBE_REGION`: [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code (e.g., `US`, `BR`, `ES`)

**Effect:**

- Changes timestamp language only
- Leaving empty defaults to English
- Does not affect video data or history content

**Examples:**

| Language        | YOUTUBE_LANGUAGE | YOUTUBE_REGION | Timestamp     |
| --------------- | ---------------- | -------------- | ------------- |
| English (US)    | `en-US`          | `US`           | "Today"       |
| Portuguese (BR) | `pt-BR`          | `BR`           | "Hoje"        |
| Spanish (Spain) | `es-ES`          | `ES`           | "Hoy"         |
| German          | `de-DE`          | `DE`           | "Heute"       |
| French          | `fr-FR`          | `FR`           | "Aujourd'hui" |

> **Note:** Leave both fields empty in `.env` to use the default (English).

---

## Authentication

Extract cookies from your browser (one-time setup):

```bash
python yt_history.py extract-cookies
```

**What it does:**

1. Detects installed browsers (Chrome, Firefox, etc.)
2. Extracts YouTube cookies automatically
3. Creates `browser_auth.json`
4. Tests authentication

**Output:**

```
✅ SUCCESS!
   189 items in history

Use with:
  python yt_history.py list
```

---

## Usage

### List history

```bash
# Last 50 items (default, using saved cookies)
python yt_history.py list

# Last 200 items
python yt_history.py list --limit 200

# Using live cookies (extracted from browser on-the-fly)
python yt_history.py list --live-cookies

# Live mode with limit
python yt_history.py list --limit 500 --live-cookies
```

**Output:**

```
✅ 5 items found (2 shorts, 3 videos)

📱 SHORTS
────────────────────────────────────────────────────────────────────────────────

1. 📱 Video title here
   🕐 Today
   🔗 https://www.youtube.com/watch?v=abc123

🎬 VIDEOS
────────────────────────────────────────────────────────────────────────────────

2. 🎬 Another video
   📺 Channel Name
   🕐 Today
   🔗 https://www.youtube.com/watch?v=def456
```

> **Verbose mode:** Add `--verbose` to see detailed progress and cookie extraction logs:
>
> ```bash
> python yt_history.py list --verbose --live-cookies
> ```

### Search history

```bash
# Search in last 50 items (default, saved cookies)
python yt_history.py search "cooking"

# Search in last 500 items
python yt_history.py search "cooking" --limit 500

# Search in all history
python yt_history.py search "cooking" --limit 0

# Search with live cookies
python yt_history.py search "cooking" --limit 0 --live-cookies
```

**What it does:**

- Searches in your history (default: last 50 items)
- Filters by title or channel name
- Case-insensitive

**Output:**

```
✅ 1 result(s) found

🎬 VIDEOS
────────────────────────────────────────────────────────────────────────────────

1. 🎬 Easy Pasta Recipe Tutorial
   📺 Cooking Channel
   🕐 Yesterday
   🔗 https://www.youtube.com/watch?v=abc123
```

### Export history

```bash
# Export last 50 items (default, saved cookies)
python yt_history.py export

# Export last 1000 items
python yt_history.py export --limit 1000

# Export all history
python yt_history.py export --limit 0

# Export with live cookies (always fresh)
python yt_history.py export --limit 0 --live-cookies

# Custom output file
python yt_history.py export --output my_history.json --limit 0
```

**JSON format:**

```json
{
  "total_items": 50,
  "statistics": {
    "short": 1,
    "video": 49
  },
  "items": [
    {
      "video_id": "abc123def456",
      "title": "Sample Video Title",
      "channel_name": "Example Channel",
      "channel_id": "UCD0u5Ubc8YQEXNuFsdqTAjQ",
      "thumbnail_url": "https://i.ytimg.com/vi/abc123def456/frame0.jpg",
      "duration": "01:00",
      "view_count": "220K views",
      "watched_time": "Today",
      "type": "short",
      "url": "https://www.youtube.com/watch?v=abc123def456"
    }
  ]
}
```

### Extract cookies (setup)

```bash
# First-time setup or when cookies expire
python yt_history.py extract-cookies

# Save to custom file
python yt_history.py extract-cookies --output custom_auth.json
```

### Help & Verbose Mode

```bash
# Show all available commands
python yt_history.py --help

# Enable verbose output (shows progress and debug info)
python yt_history.py list --verbose
python yt_history.py list --verbose --live-cookies

# Short form
python yt_history.py list -v
```

**Verbose mode shows:**

- Cookie extraction progress
- Loading progress with item count
- Debug logs from HTTP requests

---

## Architecture

```
yt-setup/
├── src/
│   ├── __init__.py            # Public module interface
│   ├── constants.py           # Enums, constants, UI messages
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── config.py              # Configuration management (.env)
│   ├── auth.py                # Authentication and cookie handling
│   ├── models.py              # Data models (HistoryGroup)
│   ├── history_filter.py      # Filtering and grouping utilities
│   ├── progress.py            # Progress reporting
│   ├── youtube_client.py      # HTTP client for YouTube API
│   ├── history_parser.py      # Response parser (videos/shorts)
│   └── history_fetcher.py     # Pagination and fetching
│
├── .env                       # Configuration (API key, locale)
├── .env.example               # Configuration template
├── requirements.txt           # Python dependencies
├── yt_history.py              # Main CLI application
└── browser_auth.json          # Saved cookies (generated)
```

### How it works

1. **YouTube API** - Uses YouTube's internal endpoints
2. **Cookie authentication** - Extracts cookies from browser automatically
3. **Complete history** - Fetches videos, shorts, and music
4. **Automatic pagination** - Iterates through all continuation tokens
5. **Type-safe** - Fully typed with dataclasses and enums
6. **Modular** - Clean separation of responsibilities (config, auth, parsing, filtering)

### Why Browser Cookies Instead of OAuth?

**OAuth authentication is broken for YouTube history access** and has been since August 2024.

#### Technical Investigation

We extensively tested OAuth with multiple approaches:

- **YouTube History API** (`browseId: FEhistory`) → HTTP 400
- **YouTube Music History** (`browseId: FEmusic_history`) → HTTP 400
- **Different clients** (WEB, WEB_REMIX, ANDROID, TV) → All failed

#### Why OAuth Doesn't Work

Google intentionally broke OAuth for YouTube/YouTube Music authenticated endpoints in 2024-2025:

- **ytmusicapi**: OAuth returns HTTP 400 for all authenticated endpoints since August 2025 ([issue #813](https://github.com/sigma67/ytmusicapi/issues/813))
- **YouTube.js**: OAuth only works with TV client, [documented as "no longer recommended"](https://ytjs.dev/guide/authentication)
- **Official stance**: "Due to recent changes by Google, OAuth2 sign-in only works when using the TV client. This method is no longer recommended - please use cookies instead."

Attempted workarounds (all failed):

- Switch to `IOS_MUSIC` client ([PR #815](https://github.com/sigma67/ytmusicapi/pull/815)) - incompatible response format
- Custom OAuth clients - rejected server-side with "invalid argument"

#### Cookie-Based Authentication

Browser cookies are currently **the only working method** for accessing YouTube history.

**How it works:**

- Extracts authentication cookies from your browser (Chrome, Firefox, Safari, etc.)
- Uses Google's SAPISIDHASH authentication (same as browser)
- Cookies contain session tokens: `SAPISID`, `SIDCC`, `PSIDTS`, etc.

**Limitation - Cookie Expiration:**

Google intentionally expires cookies used outside the browser:

- **In browser**: Cookies last weeks/months
- **Saved to file**: Cookies expire in 3-5 days ([yt-dlp issue #13964](https://github.com/yt-dlp/yt-dlp/issues/13964))
- **Reason**: Bot detection - Google detects "anomalous usage patterns"

Timeline:

- **2024**: Cookies lasted ~1 month when saved to file
- **2026**: Cookies expire in 3-5 days (anti-bot detection strengthened)

**Two modes available:**

1. **Saved cookies** (default): Extract once, use until expiration (3-5 days)

   ```bash
   python yt_history.py extract-cookies
   python yt_history.py list
   ```

2. **Live extraction** (`--live-cookies`): Extract fresh cookies on every command
   ```bash
   python yt_history.py list --live-cookies
   ```

Live extraction requires browser running locally but provides always-fresh cookies.

#### References

- ytmusicapi OAuth broken: https://github.com/sigma67/ytmusicapi/issues/813
- YouTube.js auth guide: https://ytjs.dev/guide/authentication
- yt-dlp cookie expiration: https://github.com/yt-dlp/yt-dlp/issues/13964
- Cookie-based auth explanation: https://stackoverflow.com/a/32065323/5726546

---

## Troubleshooting

### "No items found"

**Cause:** Cookies expired

**Solution:**

```bash
python yt_history.py extract-cookies
```

### "Chrome 127+ blocked cookies"

**Cause:** Recent Chrome versions block external cookie access

**Solution:** Use Firefox

```bash
# extract-cookies automatically detects
# and prioritizes Firefox if available
```

### "ModuleNotFoundError"

**Cause:** Dependencies not installed

**Solution:**

```bash
pip install -r requirements.txt
```

### "YOUTUBE_API_KEY not configured"

**Cause:** `.env` file missing or API key not set

**Solution:**

```bash
cp .env.example .env
# Edit .env and add your API key (see Installation section)
```

---

## Extracted Data

For each video/short:

| Field           | Description                 | Example                                     |
| --------------- | --------------------------- | ------------------------------------------- |
| `video_id`      | Video ID                    | `abc123def456`                              |
| `title`         | Title                       | `Sample Video Title`                        |
| `channel_name`  | Channel name                | `Example Channel`                           |
| `channel_id`    | Channel ID (when available) | `UC1234567890abcdef`                        |
| `thumbnail_url` | Thumbnail URL               | `https://i.ytimg.com/vi/abc123/maxres.jpg`  |
| `watched_time`  | When watched                | `Today`, `Yesterday`, `Jun 9`               |
| `type`          | Type                        | `video`, `short`                            |
| `url`           | Full URL                    | `https://www.youtube.com/watch?v=abc123...` |

---

## Security

### Are cookies safe?

⚠️ **Cookies contain your complete Google session.**

This is just for local use, DO NOT share cookies with third parties. \
All data presented is immediately discarded. \
This project does not keep any of your data. \
This project does not log anything to the internet.

---

## Contributing

Project created for personal use, but PRs are welcome!

### How to contribute

1. Fork
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Inspiration

This project was inspired by:

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - SAPISID authentication reference
- [YouTube.js](https://github.com/LuanRT/YouTube.js) - Endpoint structure
- [browser-cookie3](https://github.com/borisbabic/browser_cookie3) - Cookie extraction
