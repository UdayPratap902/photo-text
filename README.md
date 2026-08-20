
## ✨ Features
- **Supports Both Photos and Videos**: Works with `.jpg`, `.jpeg`, `.png`, `.webp` images and `.mp4`, `.mov`, `.mkv`, `.avi` videos.

## ⚙️ Prerequisites

Before running the script, make sure you have the following installed on your system:

### 1. Install Python Packages
Open your terminal or command prompt and run:
```bash
pip install pillow opencv-python numpy
```

### 2. Install FFmpeg
The script uses FFmpeg to preserve the original audio in videos.
- **Windows:** Open PowerShell or Command Prompt as Administrator and run: `winget install Gyan.FFmpeg`
- **macOS:** Open Terminal and run: `brew install ffmpeg`
- **Linux:** Open Terminal and run: `sudo apt install ffmpeg`

> **Note for Windows Users:** After installing FFmpeg, you might need to restart your terminal or PC for the `ffmpeg` command to be recognized.

---

## 🚀 How to Use

### 📝 1. Set Your Timestamp, Gaps & Text
Open `script.py` in your favorite editor and customize the configuration variables at the top:

- **`BASE_START_TIMESTAMP`**: The starting timestamp for the **first** file in your batch. 
  - Format: `"17 Aug 2026 13:02:31"` or `"12:32:08"`
- **`MIN_GAP_SECONDS`** & **`MAX_GAP_SECONDS`**: The random time gap range (in seconds) added between consecutive files in the batch (default: `60` to `180` seconds).
- **`STATIC_TEXT_LINES`**: Your static metadata (like GPS, Speed, or Location). If you want the text to appear in multiple lines on the image/video, write them as multiple strings in the list.

**Example:**
```python
BASE_START_TIMESTAMP = "24 Aug 2026 14:30:00"

MIN_GAP_SECONDS = 60   # Minimum gap (e.g. 1 minute)
MAX_GAP_SECONDS = 180  # Maximum gap (e.g. 3 minutes)

STATIC_TEXT_LINES = [
    "📍 New York City",
    "Altitude: 87.8msnm",
    "Shot on iPhone"
]
```

### 📁 2. Add Media
Place all the photos and videos you want to process inside the `input` folder. 

### ▶️ 3. Run the Script
Open your terminal or command prompt and run the command:
```bash
python script.py
```

### 🎉 4. Boom!
Check the `output` folder! All your processed media with perfectly aligned timestamps (incremented per file), custom text, and original audio will be waiting for you.

