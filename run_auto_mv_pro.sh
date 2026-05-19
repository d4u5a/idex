#!/bin/bash
# Quick Start for Auto Music Video Pro

echo "🎬 =========================================="
echo "   Auto Music Video Pro - Quick Start"
echo "========================================== 🎬"

# Check if music and clips folders exist and have files
MUSIC_COUNT=$(find ./music -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.flac" \) 2>/dev/null | wc -l)
CLIPS_COUNT=$(find ./clips -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.avi" \) 2>/dev/null | wc -l)

echo ""
echo "📂 Status:"
echo "   Music files: $MUSIC_COUNT"
echo "   Video clips: $CLIPS_COUNT"
echo ""

if [ "$MUSIC_COUNT" -eq 0 ]; then
    echo "⚠️  No music files found in ./music/"
    echo "   Please add MP3, WAV, or FLAC files to the music folder."
    exit 1
fi

if [ "$CLIPS_COUNT" -eq 0 ]; then
    echo "⚠️  No video clips found in ./clips/"
    echo "   Please add MP4, MOV, or AVI files to the clips folder."
    exit 1
fi

echo "🚀 Starting automatic music video generation..."
echo ""

python3 auto_music_video_pro.py -m ./music -c ./clips -o ./output

echo ""
echo "✅ Done! Generated videos are in ./output/"
