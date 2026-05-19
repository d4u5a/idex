# 🎬 Auto Music Video Pro

**State-of-the-Art Automatic Music Video Generator**

Fully automated pipeline that syncs video clips to the rhythm and lyrical context of your music tracks.

## ✨ Features

- **🎵 Beat Detection**: Precision beat tracking using Librosa (or FFmpeg fallback)
- **🏷️ Tag Extraction**: Reads MP3 ID3 tags for title, artist, genre, and mood
- **🧠 Semantic Matching**: Intelligently matches video clips to song themes based on filenames
- **✂️ Beat-Sync Cutting**: Cuts video exactly on detected beats
- **🎨 Creative Transitions**: 
  - Glitch effects on downbeats
  - Smooth Zoom transitions
  - Wipe effects
  - Standard cuts
- **📦 Batch Processing**: Process entire music folders automatically

## 🚀 Quick Start

### 1. Add Your Files
```
./music/     → Place your MP3, WAV, or FLAC files here
./clips/     → Place your MP4, MOV, AVI clips here
```

**Tip:** Name your clips descriptively for better matching!
- `party_crowd_dance.mp4` → Matches energetic songs
- `nature_beach_sunset.mp4` → Matches calm/chill songs  
- `city_neon_night.mp4` → Matches urban/trap vibes

### 2. Run the Generator

**Option A: Quick Start Script**
```bash
./run_auto_mv_pro.sh
```

**Option B: Direct Command**
```bash
python3 auto_music_video_pro.py -m ./music -c ./clips -o ./output
```

### 3. Get Your Video
Generated videos appear in `./output/` with the format: `{songname}_MV.mp4`

## 📋 How It Works

1. **Analysis Phase**
   - Scans music folder for audio files
   - Extracts ID3 tags (title, artist, genre) or uses filename
   - Detects mood from keywords (party, sad, trap, etc.)
   - Analyzes video clip filenames for semantic tags

2. **Beat Detection**
   - Uses Librosa for high-precision BPM and beat timestamps
   - Identifies downbeats (every 4th beat) for special effects

3. **Smart Matching**
   - Scores each video clip against song keywords
   - Prioritizes clips with matching themes (e.g., "party" song → "crowd" clips)
   - Rotates top-scoring clips to avoid repetition

4. **Rendering**
   - Builds complex FFmpeg filter graphs
   - Trims clips to exact beat durations
   - Applies transitions (glitch, zoom, wipe) on downbeats
   - Overlays original audio track

## 🔧 Requirements

- **Python 3.8+**
- **FFmpeg** (must be installed system-wide)
- **Python Packages**: librosa, numpy, soundfile, mutagen

Install dependencies:
```bash
pip install librosa numpy soundfile mutagen
```

## 📁 Directory Structure

```
/workspace/
├── auto_music_video_pro.py    # Main script
├── run_auto_mv_pro.sh         # Quick start wrapper
├── music/                     # Input: Audio files
├── clips/                     # Input: Video clips
├── output/                    # Output: Generated videos
├── temp/                      # Temporary processing files
└── logs/                      # Processing logs
```

## 🎯 Mood Detection Examples

The script automatically detects song mood from tags/filename:

| Keywords Detected | Mood Assigned | Best Matching Clips |
|------------------|---------------|---------------------|
| party, dance, happy, summer | `energetic_party` | crowd, dance, people |
| sad, blue, rain, night | `sad_cinematic` | nature, sky, ocean |
| trap, bass, dark, street | `aggressive_trap` | city, neon, urban |

## ⚙️ Advanced Usage

Custom input/output folders:
```bash
python3 auto_music_video_pro.py \
  -m /path/to/music \
  -c /path/to/clips \
  -o /path/to/output
```

## 🐛 Troubleshooting

**"No music files found"**
- Ensure files are in `.mp3`, `.wav`, or `.flac` format
- Check that files are directly in the `./music/` folder

**"FFmpeg NOT found"**
- Install FFmpeg: `sudo apt install ffmpeg` (Linux) or download from ffmpeg.org

**"Librosa not found"**
- Install: `pip install librosa numpy soundfile`

**Render fails with complex filters**
- Update to latest FFmpeg version
- Script will attempt fallback rendering automatically

## 📄 License

MIT License - Free for personal and commercial use.

---

**Enjoy creating professional music videos automatically! 🎉**
