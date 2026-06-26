# YouTube History CLI

CLI tool to fetch your **complete** YouTube watch history.

## Features

✅ **Complete history** - Videos + Shorts (including music) \
✅ **Automatic cookie extraction** from browser \
✅ **Automatic pagination** - Fetches entire history \
✅ **Search** by term (title or channel) \
✅ **JSON export** with videos and shorts separated \
✅ **Minimal dependencies** - Only `browser-cookie3` + `requests`

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/SamuelGadiel/yt_history.git
cd yt_history
python -m venv venv
source venv/bin/activate  # Mac/Linux (Windows: venv\Scripts\activate)
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add YOUTUBE_API_KEY (see section below)

# 3. Extract cookies from browser
python yt_history.py extract-cookies

# 4. Use it!
python yt_history.py list
python yt_history.py search "music"
python yt_history.py export --limit 0
```

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
# ou
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
4. Copy the key value (starts with `AIza...`)

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

### Cookie Extraction (initial setup)

Extract cookies from your browser (one-time setup):

```bash
python yt_history.py extract-cookies
```

**What it does:**

1. Detects installed browsers (Chrome, Firefox, Safari, Edge, Brave)
2. Extracts YouTube cookies automatically
3. Creates `browser_auth.json` file in project directory
4. Tests authentication by fetching history

**Output:**

```
============================================================
AUTOMATIC COOKIE EXTRACTION
============================================================

🔍 Detecting browsers...
   ✓ Firefox
   ✗ Chrome
   ✗ Safari

✓ Using Firefox

============================================================
📡 Extracting cookies from Firefox...
   ✓ 15 cookies extracted
   ✓ Critical cookies: SAPISID, HSID, SSID, SID

💾 Saving cookies...
   ✓ Saved: /path/to/yt_history/browser_auth.json

🧪 Testing authentication...
   ✓ Success! 189 items in history

   📹 First: Video Title Here

============================================================
✅ SUCCESS!

Use with:
  python yt_history.py list
============================================================
```

### Two authentication modes

| Mode                  | Command                                    | When to use                                          |
| --------------------- | ------------------------------------------ | ---------------------------------------------------- |
| **Saved cookies**     | `python yt_history.py list`                | Normal use (cookies last 3-5 days)                   |
| **Live cookies** (🔴) | `python yt_history.py list --live-cookies` | When cookies expired or to always have fresh cookies |

**Saved cookies** (default):

- Extract once, use until expiration (3-5 days)
- Faster (doesn't extract on every command)
- Ideal for daily use

**Live cookies**:

- Extracts fresh cookies from browser on every command
- Requires browser running locally
- Useful when `browser_auth.json` expired

---

## Usage

### List history

```bash
# Last 50 items (default, using saved cookies)
python yt_history.py list

# Last 200 items
python yt_history.py list --limit 200

# All history
python yt_history.py list --limit 0

# Filter only videos
python yt_history.py list --type videos

# Filter only shorts
python yt_history.py list --type shorts

# Using live cookies (extracts from browser on-the-fly)
python yt_history.py list --live-cookies

# Live mode with limit
python yt_history.py list --limit 500 --live-cookies

# Verbose mode (shows progress and debug)
python yt_history.py list --verbose
python yt_history.py list -v --live-cookies
```

**Output:**

```
✅ 5 items found (2 shorts, 3 videos)

📱 SHORTS
────────────────────────────────────────────────────────────────────────────────

1. 📱 Quick Python Tutorial in 60 Seconds
   🕐 Today
   🔗 https://www.youtube.com/watch?v=dQw4w9WgXcQ

🎬 VIDEOS
────────────────────────────────────────────────────────────────────────────────

2. 🎬 Complete Guide to Docker Containers
   📺 Tech Channel
   🕐 Today
   🔗 https://www.youtube.com/watch?v=abc123def45

3. 🎬 Building REST APIs with FastAPI
   📺 Programming Tutorials
   🕐 Today
   🔗 https://www.youtube.com/watch?v=xyz789ghi01
```

**Verbose mode:**

Add `--verbose` to see detailed progress and cookie extraction logs:

```bash
python yt_history.py list --verbose --live-cookies
```

Output shows:

- Cookie extraction progress
- Loading progress with item count
- Debug logs from HTTP requests

### Search history

```bash
# Search in last 50 items (default, saved cookies)
python yt_history.py search "cooking"

# Search in last 500 items
python yt_history.py search "cooking" --limit 500

# Search in all history
python yt_history.py search "cooking" --limit 0

# Search only in videos
python yt_history.py search "music" --type videos

# Search only in shorts
python yt_history.py search "tutorial" --type shorts --limit 0

# Search with live cookies
python yt_history.py search "cooking" --limit 0 --live-cookies
```

**What it does:**

- Searches in your history (default: last 50 items)
- Filters by title **or** channel name
- Case-insensitive
- Shows videos and shorts separated

**Output:**

```
✅ 2 result(s) found

🎬 VIDEOS
────────────────────────────────────────────────────────────────────────────────

1. 🎬 Easy Pasta Recipe Tutorial
   📺 Cooking Channel
   🕐 Yesterday
   🔗 https://www.youtube.com/watch?v=abc123def45

2. 🎬 10 Best Cooking Tips for Beginners
   📺 Chef's Kitchen
   🕐 Jun 15
   🔗 https://www.youtube.com/watch?v=xyz789abc12

================================================================================
```

### Export history

```bash
# Export last 50 items (default, saved cookies)
python yt_history.py export

# Export last 1000 items
python yt_history.py export --limit 1000

# Export all history
python yt_history.py export --limit 0

# Export only videos
python yt_history.py export --type videos --limit 0

# Export only shorts
python yt_history.py export --type shorts --limit 0

# Export with live cookies (always fresh)
python yt_history.py export --limit 0 --live-cookies

# Custom output file
python yt_history.py export --output my_history.json --limit 0

# Verbose mode
python yt_history.py export --verbose --limit 0
```

**Exported JSON structure:**

```json
{
  "total_items": 50,
  "statistics": {
    "short": 1,
    "video": 49
  },
  "videos": [
    {
      "video_id": "abc123def45",
      "title": "Complete Guide to Docker Containers",
      "channel_name": "Tech Channel",
      "channel_id": "UCXuqSBlHAE6Xw-yeJA0Tunw",
      "thumbnail_url": "https://i.ytimg.com/vi/abc123def45/hqdefault.jpg",
      "duration": "15:30",
      "view_count": "1.2M views",
      "watched_time": "Today",
      "type": "video",
      "url": "https://www.youtube.com/watch?v=abc123def45"
    }
  ],
  "shorts": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Quick Python Tutorial in 60 Seconds",
      "channel_name": null,
      "channel_id": null,
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/frame0.jpg",
      "duration": null,
      "view_count": "500K views",
      "watched_time": "Today",
      "type": "short",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ]
}
```

**Command output:**

```
✅ Exported: /path/to/yt_history/youtube_history.json
   Total: 50 items
   Statistics:
     - video: 49
     - short: 1
```

### Extract cookies (setup)

```bash
# Initial setup or when cookies expire
python yt_history.py extract-cookies

# Save to custom file
python yt_history.py extract-cookies --output custom_auth.json
```

**When to use:**

- Initial setup (first time)
- When "No items found" error appears (cookies expired)
- To switch browsers

### Help & Verbose Mode

```bash
# Show all available commands
python yt_history.py --help

# Help for specific command
python yt_history.py list --help
python yt_history.py search --help
python yt_history.py export --help

# Enable verbose output (shows progress and debug)
python yt_history.py list --verbose
python yt_history.py list --verbose --live-cookies

# Short form
python yt_history.py list -v
```

---

## Use Cases (Real-world examples)

### 1. Complete history backup

```bash
# Export everything (may take a few minutes)
python yt_history.py export --limit 0 --output backup_$(date +%Y%m%d).json --verbose

# Result: backup_20260626.json with your entire history
```

### 2. Analyze videos watched from a channel

```bash
# Search all videos from "Linus Tech Tips"
python yt_history.py search "Linus Tech Tips" --limit 0 --type videos

# Export only videos from this channel
python yt_history.py search "Linus Tech Tips" --limit 0 --type videos > ltt_videos.txt
```

### 3. List last 100 shorts

```bash
# List last 100 shorts from history (not necessarily from today)
python yt_history.py list --type shorts --limit 100
```

### 4. Integration with other Python scripts

```python
# Import as library
from src import HistoryFetcher, YouTubeClient, load_cookies_from_file

# Load cookies
cookies = load_cookies_from_file('browser_auth.json')

# Create client
client = YouTubeClient(cookies)

# Fetch history
fetcher = HistoryFetcher(client)
grouped = fetcher.fetch_all_grouped(limit=100)

# Process data
for video in grouped.videos:
    print(f"{video.title} - {video.channel_name}")

for short in grouped.shorts:
    print(f"[SHORT] {short.title}")
```

### 5. Progress monitoring

```bash
# See how many items were loaded in real-time
python yt_history.py export --limit 0 --verbose

# Output:
#    Fetching... 50 items
#    Fetching... 100 items
#    Fetching... 500 items
#    ...
```

---

## Architecture

### Project structure

The project is organized into modules with clear responsibilities:

**Core modules (src/):**

- `__init__.py` - Public module interface (main exports)
- `exceptions.py` - Custom exception hierarchy
- `config.py` - Configuration management (.env)
- `auth.py` - Authentication and cookie handling
- `models.py` - Data models (HistoryGroup)
- `history_filter.py` - Filtering and grouping utilities
- `progress.py` - Progress reporting
- `youtube_client.py` - HTTP client for YouTube API
- `history_parser.py` - Response parser (videos/shorts)
- `history_fetcher.py` - Pagination and fetching

**Root files:**

- `yt_history.py` - Main CLI application (commands: list, export, search, extract-cookies)
- `.env` - Configuration (API key, locale)
- `.env.example` - Configuration template
- `requirements.txt` - Python dependencies
- `browser_auth.json` - Saved cookies (auto-generated)

### How it works

1. **YouTube API** - Uses YouTube's internal endpoints (`/youtubei/v1/browse`)
2. **Cookie authentication** - Extracts cookies from browser automatically via `browser-cookie3`
3. **SAPISID authentication** - Uses same authentication method as browser (SAPISIDHASH)
4. **Complete history** - Fetches videos and shorts (music videos are included as type "video")
5. **Automatic pagination** - Iterates through all continuation tokens
6. **Type-safe** - Fully typed with dataclasses and type hints
7. **Modular** - Clean separation of responsibilities (config, auth, parsing, filtering)

### Execution flow

```
1. Load configuration (.env)
   ↓
2. Load cookies (browser_auth.json or --live-cookies)
   ↓
3. Create YouTubeClient (SAPISID authentication)
   ↓
4. HistoryFetcher.fetch_all_grouped()
   ├─ Fetch first page (browseId: FEhistory)
   ├─ Parse response (HistoryParser)
   ├─ Extract continuation token
   ├─ Fetch next page (continuation)
   └─ Repeat until no more pages
   ↓
5. Filter by type (videos/shorts/all)
   ↓
6. Display or export results
```

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

## Field Reference

Extracted fields for each video/short:

| Field           | Description                       | Example                                            | Nullable |
| --------------- | --------------------------------- | -------------------------------------------------- | -------- |
| `video_id`      | YouTube video ID (11 chars)       | `bda1GHblwis`                                      | No       |
| `title`         | Video/short title                 | `Working 10 Hours in a Random Asian Tech Mall`     | No       |
| `channel_name`  | Channel name                      | `Linus Tech Tips`                                  | Yes      |
| `channel_id`    | Channel ID                        | `UCXuqSBlHAE6Xw-yeJA0Tunw`                         | Yes      |
| `thumbnail_url` | Thumbnail URL                     | `https://i.ytimg.com/vi/bda1GHblwis/hqdefault.jpg` | Yes      |
| `duration`      | Video duration                    | `10:45`, `01:30:00`                                | Yes      |
| `view_count`    | View count text                   | `16K views`, `1.2M views`                          | Yes      |
| `watched_time`  | When watched (locale-dependent)   | `Today`, `Yesterday`, `Jun 15`, `Hoje`             | Yes      |
| `type`          | Item type                         | `video`, `short`                                   | No       |
| `url`           | Full YouTube URL (auto-generated) | `https://www.youtube.com/watch?v=bda1GHblwis`      | No       |

**Notes:**

- **Shorts** usually have `channel_name`, `channel_id`, and `duration` as `null`
- **Thumbnail format**:
  - Videos: `hqdefault.jpg`, `hqdefault_custom_1.jpg`
  - Shorts: `frame0.jpg`, `hq2.jpg`
- **watched_time** format depends on `YOUTUBE_LANGUAGE` in `.env`

---

## Troubleshooting

### "No items found"

**Cause:** Cookies expired (last 3-5 days)

**Solution:**

```bash
python yt_history.py extract-cookies
```

Or use `--live-cookies` to extract fresh ones:

```bash
python yt_history.py list --live-cookies
```

---

### "Chrome 127+ blocked cookies"

**Cause:** Chrome 127+ blocks external cookie access

**Solution:** Use Firefox (detected automatically)

```bash
# extract-cookies detects and prioritizes Firefox automatically
python yt_history.py extract-cookies
```

Or use `--live-cookies` with Firefox open:

```bash
python yt_history.py list --live-cookies
```

---

### "ModuleNotFoundError: No module named 'requests'"

**Cause:** Dependencies not installed

**Solution:**

```bash
pip install -r requirements.txt
```

Make sure you're in the virtual environment:

```bash
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows
```

---

### "YOUTUBE_API_KEY not configured"

**Cause:** `.env` file missing or API key not set

**Solution:**

```bash
cp .env.example .env
# Edit .env and add your API key (see Installation section)
```

Validate if key starts with `AIza`:

```bash
grep YOUTUBE_API_KEY .env
# Should show: YOUTUBE_API_KEY=AIzaSy...
```

---

### "AuthenticationError: SAPISID cookie not found"

**Cause:** Extracted cookies don't contain SAPISID (not logged into YouTube)

**Solution:**

1. Open your browser (Chrome, Firefox, etc.)
2. Go to [youtube.com](https://youtube.com)
3. Log in to your Google account
4. Extract cookies again:

```bash
python yt_history.py extract-cookies
```

---

### "Failed to extract cookies from all available browsers"

**Cause:** No browser detected or all failed

**Solution:**

1. Make sure you have a supported browser installed:
   - Firefox (recommended)
   - Chrome
   - Safari (macOS)
   - Edge (Windows)
   - Brave

2. Verify you're logged into YouTube in the browser

3. On macOS, allow Keychain access when prompted

4. Try verbose mode to see details:

```bash
python yt_history.py extract-cookies --verbose
```

---

### Live cookies too slow

**Cause:** `--live-cookies` extracts cookies from browser on every command (slower)

**Solution:** Use saved cookies (default):

```bash
# Extract once
python yt_history.py extract-cookies

# Use saved cookies (fast)
python yt_history.py list
python yt_history.py export --limit 0
```

Saved cookies last 3-5 days.

---

### JSON export too large

**Cause:** Entire history can have thousands of items

**Solution:** Use `--limit` to export only part:

```bash
# Last 1000 items
python yt_history.py export --limit 1000

# Only videos (reduces size)
python yt_history.py export --type videos --limit 0
```

---

## Security

### Are cookies safe?

⚠️ **Cookies contain your complete Google session.**

**Important:**

- Cookies have full access to your Google account
- **DO NOT share** `browser_auth.json` with third parties
- **DO NOT commit** `browser_auth.json` to git (already in `.gitignore`)
- This project **does not send** cookies to external servers
- All data stays **locally** on your computer
- This project **does not log** anything to the internet

**Recommendations:**

- Keep `browser_auth.json` private
- Don't expose the file in public repositories
- Cookies expire in 3-5 days when saved to file
- Use `--live-cookies` if you prefer not to save cookies

**What this project does:**

- ✅ Reads cookies from local browser
- ✅ Uses cookies to authenticate with YouTube API
- ✅ Saves cookies to `browser_auth.json` (local only)
- ✅ Uses HTTPS for all requests

**What this project does NOT do:**

- ❌ Send cookies to external servers
- ❌ Log user data
- ❌ Modify YouTube history
- ❌ Access data beyond video history

---

## Performance

**Approximate times** (varies with internet speed):

| History      | Estimated time | Items/second |
| ------------ | -------------- | ------------ |
| 50 items     | ~1-2 seconds   | 25-50        |
| 500 items    | ~10-15 seconds | 30-50        |
| 5000 items   | ~2-3 minutes   | 30-40        |
| 50000+ items | ~20-30 minutes | 25-40        |

**Optimization:**

- Use `--limit` to fetch only what's needed
- `--live-cookies` is slower than saved cookies
- Verbose mode (`--verbose`) adds ~10% overhead

---

## Contributing

Project created for personal use, but PRs are welcome!

### How to contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Guidelines

- Maintain type hints in all Python code
- Add tests for new features
- Update README if adding commands/flags
- Follow PEP 8 (use `black` for formatting)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Inspiration

This project was inspired by:

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - SAPISID authentication reference
- [YouTube.js](https://github.com/LuanRT/YouTube.js) - Endpoint structure
- [browser-cookie3](https://github.com/borisbabic/browser_cookie3) - Cookie extraction from browser
