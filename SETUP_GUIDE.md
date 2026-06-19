# 🎬 IDEX — Auto Music Video Pro (NEXT LEVEL)

**Professional-grade automatic music video generation with hardware-safe processing, semantic clip matching, and beat-synchronized editing.**

---

## 🚀 Quick Start (60 seconds)

### Windows
```powershell
Right-Click install.ps1 → "Mit PowerShell ausführen"
# OR
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### Linux/Mac
```bash
python3 -m venv .venv
source .venv/bin/activate  # or: . .venv/Scripts/activate (Windows Git Bash)
pip install -r requirements.txt
python src/cli.py -m ./music -c ./clips -o ./output
```

---

## 📁 Setup

1. **Add your files:**
   ```
   ./music/     ← MP3, WAV, FLAC files
   ./clips/     ← MP4, MOV, AVI video clips
   ```

2. **Run the engine:**
   ```bash
   # Simple mode
   python src/cli.py

   # Custom paths
   python src/cli.py -m D:\my_music -c D:\my_clips -o D:\output

   # Batch processing
   python src/cli.py --batch

   # Start API server
   python src/cli.py --api --port 5000
   ```

---

## 🎯 Core Features

### 🧠 Audio Analysis Engine
- **Beat Detection**: Librosa-based BPM & downbeat tracking
- **Section ID**: Intelligent verse/chorus/bridge recognition
- **Energy Mapping**: Dynamic intensity profiling per section
- **Harmonic Analysis**: Chromagram + spectral centroid tracking

### 🎨 Semantic Clip Matching
- **9D Vector Space**: Genre, mood, shot scale, motion, intensity
- **O(1) Cache Loading**: Pre-computed `weedit_db.json` metadata
- **Cosine Similarity**: Intelligent clip-to-section matching
- **Rotation Strategy**: Prevents clip repetition via cooldown

### 🛡️ Hardware Safety
- **ResourceGuard**: Concurrent FFmpeg limiter (thread-safe)
- **RAM Monitoring**: Free memory thresholds (default: 1GB)
- **GPU VRAM Tracking**: NVIDIA NVML support with fallback
- **Graceful Degradation**: Auto-scales workers to available CPU cores

### 🎬 Intelligent Editing
- **Energy-Based Transitions**: 
  - High energy (>0.7) → Glitch/Zoom effects
  - Medium energy (0.4-0.7) → Fade transitions
  - Low energy (<0.4) → Hard cuts
- **FFmpeg Filtering**: Complex filter graphs with safety bounds
- **Atomic Rendering**: Safe subprocess management with timeouts

---

## 📊 Architecture

```
src/
├── cli.py                    # CLI entry point
├── core/
│   ├── engine.py            # Main orchestrator (AudioAnalyzer + timeline builder)
│   ├── clip_pool.py         # 9D semantic clip selection
│   └── claw_guard.py        # Resource & concurrency safeguard
└── api/
    └── server.py            # Flask REST API

db/
└── weedit_db.json          # Pre-computed clip metadata cache

config/
└── .env                      # Configuration (FFmpeg paths, workers, etc)

music/                        # Input: Audio files
clips/                        # Input: Video clips
output/                       # Output: Generated videos
```

---

## 🔧 Configuration

Edit `config/.env`:

```env
# FFmpeg
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe

# Video Quality
DEFAULT_QUALITY=23          # CRF (lower = better, 0-51)
DEFAULT_CODEC=libx264
DEFAULT_PRESET=fast         # ultrafast, superfast, veryfast, faster, fast, medium, slow...
DEFAULT_FPS=30

# Processing
MAX_WORKERS=4               # Concurrent FFmpeg processes
TEMP_DIR=./output/temp
DATABASE_PATH=./db/idex.db

# Resource Guards
MIN_FREE_RAM_MB=1024        # Minimum free system RAM
MIN_FREE_VRAM_MB=512        # Minimum free GPU VRAM
MONITOR_GPU=true            # Enable GPU monitoring

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/idex.log
```

---

## 🎮 Command Line Interface

```bash
# Help
python src/cli.py --help

# Process music folder
python src/cli.py -m ./music -c ./clips -o ./output

# Verbose logging
python src/cli.py -v

# Batch mode (process all)
python src/cli.py --batch

# Start API server
python src/cli.py --api --host 127.0.0.1 --port 5000

# Custom configuration
python src/cli.py \
  -m D:\my_music \
  -c D:\my_clips \
  -o D:\videos \
  --batch -v
```

---

## 🌐 REST API

### Start Server
```bash
python src/cli.py --api --port 5000
```

### Health Check
```bash
curl http://127.0.0.1:5000/api/health
```

### Scan Files
```bash
curl -X POST http://127.0.0.1:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "music_dir": "./music",
    "clips_dir": "./clips"
  }'
```

### Generate Video
```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "music_file": "song.mp3",
    "output_name": "output.mp4"
  }'
```

---

## 🐳 Docker Deployment

### Build & Run
```bash
docker-compose up -d
```

### Access
- API: `http://localhost:5000`
- Volume mounts:
  - `./music` → `/app/music`
  - `./clips` → `/app/clips`
  - `./output` → `/app/output`
  - `./db` → `/app/db`

---

## 📦 Database Schema

### `weedit_db.json`
Pre-computed clip metadata for O(1) loading:

```json
{
  "path": "D:\\clips\\urban_street.mp4",
  "duration": 6.04,
  "motion_score": 50.0,
  "shot_scale": "medium",
  "camera_movement": "static",
  "brightness": 75.3,
  "dominant_colors": [[216, 173, 153], [94, 89, 120], ...],
  "vector": [0.56, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 1.0]
}
```

**Vector Dimensions (9D):**
- [0] Hip-Hop affinity (0.0-1.0)
- [1-4] Genre flags (Pop, Electronic, Rock, Soul)
- [5-7] Mood flags (Happy, Intense, Calm)
- [8] Motion intensity (0.0-1.0)

---

## ⚙️ Requirements

### System
- **Python 3.8+**
- **FFmpeg** (system-wide installation)
- **~2GB disk space** (dependencies + temp files)
- **1GB+ free RAM** (configurable)

### Python Dependencies
```
numpy>=1.24.0
scipy>=1.10.0
librosa>=0.10.0
mutagen>=1.46.0
scikit-learn>=1.3.0
tqdm>=4.65.0
flask>=2.3.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
```

### Optional (GPU Acceleration)
```
tensorflow>=2.13.0
torch>=2.0.0
pynvml>=12.0.0   # NVIDIA GPU monitoring
psutil>=5.9.0    # System RAM monitoring
```

---

## 🐛 Troubleshooting

### "Python not found"
**Windows:**
- Download from https://python.org
- ✅ Check "Add Python to PATH"
- Restart computer

**Linux/Mac:**
```bash
which python3  # Should show path
python3 --version  # Should be 3.8+
```

### "FFmpeg not found"
**Windows:**
```powershell
winget install Gyan.FFmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### "No music/clips files found"
- Check folder paths (absolute recommended)
- Verify files are directly in folder (not subfolders)
- Supported audio: `.mp3`, `.wav`, `.flac`, `.m4a`
- Supported video: `.mp4`, `.mov`, `.avi`, `.mkv`

### "Out of memory" errors
Edit `config/.env`:
```env
MIN_FREE_RAM_MB=2048      # Increase threshold
MAX_WORKERS=2             # Reduce concurrent processes
```

### "Low VRAM" warnings
```env
MIN_FREE_VRAM_MB=1024     # Increase GPU threshold
MONITOR_GPU=false         # Disable GPU checking
```

---

## 🎯 Workflow

```
1. User adds MP3s to ./music/
2. User adds video clips to ./clips/
3. System scans & pre-analyzes files
4. Engine processes each track:
   - Beat detection → sections identified
   - Semantic matching → best clips selected
   - Timeline built → transitions assigned
   - FFmpeg renders → final video
5. Videos saved to ./output/
```

---

## 📈 Performance Tips

### Speed Up Rendering
```env
DEFAULT_PRESET=ultrafast  # Fastest (worse quality)
DEFAULT_FPS=24            # Lower FPS = smaller files
MAX_WORKERS=8             # More parallel workers
```

### Better Quality
```env
DEFAULT_PRESET=slow       # Slower (better quality)
DEFAULT_QUALITY=18        # Higher quality (lower CRF)
DEFAULT_FPS=60            # Higher FPS
```

### GPU Acceleration
```bash
# Install GPU support
pip install tensorflow torch pynvml psutil

# Edit engine.py to use GPU codecs:
# -c:v hevc_nvenc  (NVIDIA)
# -c:v h264_nvenc  (NVIDIA)
```

---

## 🎨 Output Format

Generated videos:
- **Name**: `{Artist}_{Title}_MV.mp4`
- **Codec**: H.264 (libx264)
- **Audio**: AAC 192kbps
- **FPS**: 30fps (configurable)
- **Resolution**: Source clip resolution

Example:
```
Juice WRLD_Robbery_MV.mp4
```

---

## 📝 Advanced Usage

### Batch Process with Custom Settings
```bash
python src/cli.py \
  -m ./music \
  -c ./clips \
  -o ./output \
  --batch \
  -v
```

### Monitor Resources
```python
from src.core.claw_guard import ResourceGuard

guard = ResourceGuard()
status = guard.get_status()
print(f"RAM: {status['free_ram_mb']}MB")
print(f"VRAM: {status['free_vram_mb']}MB")
print(f"Workers: {status['max_workers']}")
```

### Programmatic Usage
```python
from src.core.engine import AutoMusicVideoEngine

engine = AutoMusicVideoEngine(
    music_dir="./music",
    clips_dir="./clips",
    output_dir="./output",
    verbose=True
)
engine.run()
```

---

## 🔐 License

MIT License — Free for personal and commercial use.

---

## 📞 Support

- **Issues**: https://github.com/d4u5a/idex/issues
- **Discussions**: https://github.com/d4u5a/idex/discussions
- **Documentation**: See `README_PRO.md` for advanced topics

---

## 🎉 You're Ready!

```bash
# 1. Install
powershell -ExecutionPolicy Bypass -File .\install.ps1

# 2. Add files
# ./music/ → Your MP3s
# ./clips/ → Your video clips

# 3. Run
python src/cli.py --batch

# 4. Watch magic happen!
# Check ./output/ for your videos
```

**Enjoy creating professional music videos automatically!** 🚀
