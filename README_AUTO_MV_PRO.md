# 🎬 Auto Music Video Pro

**AI-Powered Music Video Generator** - Inspired by CutClaw  
Fully automatic local generation with beat-sync, lyric matching, and creative transitions.

## ✨ Features

- **🎵 Beat Detection**: Automatic BPM analysis and beat mapping
- **📝 Lyric & Tag Extraction**: Reads ID3 tags (Title, Artist, Genre, Lyrics) from MP3s
- **🎯 Semantic Matching**: Matches video clips to song mood/keywords automatically
- **✂️ Beat-Sync Cuts**: Cuts video exactly on detected beats
- **🌈 Creative Transitions**: Fade, Wipe, Glitch effects between clips
- **📁 Batch Processing**: Process entire music libraries automatically

## 📂 Directory Structure

```
/workspace/
├── music/          # ← Place your MP3/WAV/FLAC files here
├── clips/          # ← Place your MP4/MOV/AVI clips here
├── output/         # ← Generated music videos appear here
├── auto_mv_pro.py  # Main script
└── run_auto_mv_pro.sh  # Quick start script
```

## 🚀 Quick Start

### 1. Add Your Media
- Copy music files to `./music/` (e.g., `rapper_hit_song.mp3`)
- Copy video clips to `./clips/` (e.g., `party_crowd_night.mp4`, `car_drive_sunset.mp4`)

> 💡 **Tip**: Name your clips descriptively! The AI uses filenames for semantic matching.
> - Good: `beach_waves_sunset.mp4`, `city_traffic_night.mp4`
> - Bad: `video001.mp4`, `clip_final.mp4`

### 2. Run the Generator

```bash
cd /workspace
./run_auto_mv_pro.sh
```

Or manually:
```bash
python3 auto_mv_pro.py -m ./music -c ./clips -o ./output
```

### 3. Get Your Video
Check `./output/` for your generated music video: `Artist_Title_MV.mp4`

## 🔧 How It Works

1. **Scans Music**: Extracts metadata (tags, lyrics, genre) and detects beats
2. **Indexes Clips**: Parses filenames for keywords (e.g., "party", "night", "car")
3. **Smart Matching**: 
   - Matches song genre/mood → clip keywords
   - Aligns clip changes with beat timestamps
4. **Renders Video**: Uses FFmpeg to cut, transition, and sync everything

## 📋 Requirements

- **Python 3.8+**
- **FFmpeg** (pre-installed on most systems)
- **Python packages**: `mutagen`, `numpy` (auto-installed)

Optional for advanced beat detection:
```bash
pip install librosa
```

## 🎨 Example Workflow

**Input:**
- Music: `travis_scott_sicko_mode.mp3` (Tags: Hip-Hop, Rap | Lyrics: "...sun is down...")
- Clips: 
  - `night_city_lights.mp4`
  - `party_crowd_dance.mp4`
  - `car_speed_tunnel.mp4`

**Output:**
- `travis_scott_sicko_mode_MV.mp4` with:
  - Cuts on every snare hit
  - Night/city clips during "sun is down" lyrics
  - Fast cuts during high-energy beats
  - Smooth fade/wipe transitions

## 🐛 Troubleshooting

**No music files found?**
- Ensure files are in `./music/` with extensions .mp3, .wav, .flac

**No clips found?**
- Add video files to `./clips/` (.mp4, .mov, .avi)

**FFmpeg errors?**
- Install FFmpeg: `sudo apt install ffmpeg` (Linux) or download from ffmpeg.org

## 📄 License

MIT License - Free for personal and commercial use.

---
Made with ❤️ for creators | Inspired by CutClaw research
