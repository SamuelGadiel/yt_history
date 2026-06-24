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
python extract_cookies.py
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
# Last 50 items (default)
python yt_history.py list

# Last 200 items
python yt_history.py list --limit 200
```

**Output:**

```
🔍 Fetching YouTube history...
   Loading... 50 items

✅ 5 items found

1. 📱 Video title here
   🕐 Today
   🔗 https://www.youtube.com/watch?v=abc123

2. 🎬 Another video
   📺 Channel Name
   🕐 Today
   🔗 https://www.youtube.com/watch?v=def456
```

### Search history

```bash
# Search in last 50 items (default)
python yt_history.py search "cooking"

# Search in last 500 items
python yt_history.py search "cooking" --limit 500

# Search in all history
python yt_history.py search "cooking" --limit 0
```

**What it does:**

- Searches in your history (default: last 50 items)
- Filters by title or channel name
- Case-insensitive

**Output:**

```
🔎 Searching 'cooking' in history...
   Analyzing... 50 items

✅ 1 result(s) found

1. 🎬 Easy Pasta Recipe Tutorial
   📺 Cooking Channel
   🕐 Yesterday
   🔗 https://www.youtube.com/watch?v=abc123
```

### Export history

```bash
# Export last 50 items (default)
python yt_history.py export

# Export last 1000 items
python yt_history.py export --limit 1000

# Export all history
python yt_history.py export --limit 0

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

### Refresh cookies

```bash
# When cookies expire
python yt_history.py refresh-cookies
```

### Help

```bash
# Show all available commands
python yt_history.py --help
```

---

## Architecture

```
yt-setup/
├── src/
│   ├── youtube_client.py      # HTTP client for YouTube API
│   ├── history_parser.py      # Video/short parser
│   └── history_fetcher.py     # Automatic pagination
│
├── .env                       # Configuration (API key)
├── .env.example               # Configuration template
├── requirements.txt           # Python dependencies
├── extract_cookies.py         # Cookie extraction
├── yt_history.py              # Main CLI
└── browser_auth.json          # Saved cookies (generated)
```

### How it works

1. **YouTube API** - Uses YouTube's internal endpoints
2. **Cookie authentication** - Extracts cookies from browser automatically
3. **Complete history** - Fetches videos, shorts, and music
4. **Automatic pagination** - Iterates through all continuation tokens

### Why not OAuth?

OAuth **doesn't work** with YouTube's history endpoints.

I tested:

- OAuth + browse endpoint → HTTP 400
- Browser cookies → Works perfectly

---

## Troubleshooting

### "No items found"

**Cause:** Cookies expired

**Solution:**

```bash
python yt_history.py refresh-cookies
```

### "Chrome 127+ blocked cookies"

**Cause:** Recent Chrome versions block external cookie access

**Solution:** Use Firefox

```bash
# extract_cookies.py automatically detects
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
