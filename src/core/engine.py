#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDEX Auto Music Video Engine — NEXT LEVEL
Hardware-safe, semantically-intelligent music video generation with beat-sync precision.
"""

import os
import sys
import glob
import random
import subprocess
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from tqdm import tqdm
from dataclasses import dataclass

# Import core modules
from .claw_guard import ResourceGuard
from .clip_pool import ClipPool

try:
    import librosa
    from mutagen.id3 import ID3
    from mutagen.mp3 import MP3
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    print("⚠️ Warning: librosa/mutagen not found. Install with: pip install librosa mutagen")


@dataclass
class AudioSection:
    """Represents a section of music (verse, chorus, bridge, etc)"""
    name: str
    start_time: float
    end_time: float
    duration: float
    bpm: float
    energy: float  # 0.0 (low) to 1.0 (high)
    beat_times: List[float]
    semantic_vector: np.ndarray


@dataclass
class EditPoint:
    """Represents a single cut/transition in the final video"""
    start_time: float
    end_time: float
    clip_path: Path
    clip_offset: float
    duration: float
    transition: str  # "cut", "fade", "glitch", "zoom"
    intensity: float  # 0.0-1.0


class AudioAnalyzer:
    """Analyzes audio and detects beat structure, energy levels, and semantics."""
    
    def __init__(self):
        if not HAS_AUDIO:
            raise RuntimeError("librosa and mutagen required. Install: pip install librosa mutagen")
    
    def analyze_track(self, path: Path) -> Dict:
        """Deep audio analysis with beat detection and section identification."""
        y, sr = librosa.load(str(path), sr=22050, mono=True)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Beat detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, y=y, sr=sr)
        bpm = float(np.atleast_1d(tempo)[0])
        beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
        
        # Harmonic/Percussive decomposition
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        percussive_energy = np.abs(librosa.stft(y_percussive))
        
        # Chromagram for harmonic analysis
        chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
        
        # RMS energy over time for dynamics
        rms = librosa.feature.rms(y=y)[0]
        rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
        
        # Spectral centroid for timbre
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Read ID3 tags for metadata
        metadata = self._read_metadata(path)
        
        return {
            "path": str(path),
            "duration": duration,
            "bpm": bpm,
            "beat_times": beat_times,
            "rms": rms.tolist(),
            "rms_times": rms_times.tolist(),
            "spectral_centroid": spec_cent.tolist(),
            "chromagram": chromagram.tolist(),
            "metadata": metadata,
        }
    
    def _read_metadata(self, path: Path) -> Dict:
        """Extract ID3 tags."""
        meta = {
            "title": path.stem,
            "artist": "Unknown",
            "genre": "Hip-Hop",
            "bpm_tag": None,
        }
        
        if path.suffix.lower() == ".mp3" and HAS_AUDIO:
            try:
                tags = ID3(str(path))
                if "TIT2" in tags:
                    meta["title"] = str(tags["TIT2"])
                if "TPE1" in tags:
                    meta["artist"] = str(tags["TPE1"])
                if "TCON" in tags:
                    meta["genre"] = str(tags["TCON"])
                if "TBPM" in tags:
                    meta["bpm_tag"] = int(str(tags["TBPM"]))
            except Exception:
                pass
        
        return meta
    
    def identify_sections(self, analysis: Dict) -> List[AudioSection]:
        """Intelligently identify song sections (intro, verse, chorus, bridge, outro)."""
        beat_times = analysis["beat_times"]
        bpm = analysis["bpm"]
        rms = np.array(analysis["rms"])
        rms_times = np.array(analysis["rms_times"])
        duration = analysis["duration"]
        
        # Normalize RMS for energy detection
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-8)
        
        # Detect major changes in energy (section boundaries)
        energy_delta = np.abs(np.diff(rms_norm, prepend=rms_norm[0]))
        threshold = np.percentile(energy_delta, 85)
        section_indices = np.where(energy_delta > threshold)[0]
        
        # Map to time
        section_times = rms_times[section_indices]
        section_times = np.concatenate([[0], section_times, [duration]])
        section_times = np.unique(section_times)
        
        # Classify sections by energy pattern
        section_names = ["intro", "verse", "pre-chorus", "chorus", "bridge", "verse", "chorus", "outro"]
        sections = []
        
        for i in range(len(section_times) - 1):
            start = section_times[i]
            end = section_times[i + 1]
            
            # Get energy level in this section
            mask = (rms_times >= start) & (rms_times < end)
            avg_energy = float(np.mean(rms_norm[mask])) if mask.any() else 0.5
            
            # Get beats in section
            section_beats = [b for b in beat_times if start <= b < end]
            
            name = section_names[min(i, len(section_names) - 1)]
            
            sections.append(AudioSection(
                name=name,
                start_time=float(start),
                end_time=float(end),
                duration=float(end - start),
                bpm=bpm,
                energy=avg_energy,
                beat_times=section_beats,
                semantic_vector=np.array([avg_energy, len(section_beats) / max(1, end - start)] + [0] * 7, dtype=np.float32),
            ))
        
        return sections


class AutoMusicVideoEngine:
    """Main pipeline orchestrator with hardware safety and intelligent editing."""
    
    def __init__(self, music_dir: str, clips_dir: str, output_dir: str, verbose: bool = False):
        self.music_dir = Path(music_dir)
        self.clips_dir = Path(clips_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        # Initialize safety and resource management
        self.guard = ResourceGuard(
            max_ffmpeg_processes=4,
            min_free_ram_mb=1024,
            min_free_vram_mb=512,
            monitor_vram=True
        )
        
        # Initialize clip pool
        try:
            self.pool = ClipPool(str(clips_dir))
        except Exception as e:
            print(f"⚠️ ClipPool initialization warning: {e}")
            self.pool = None
        
        # Initialize audio analyzer
        try:
            self.analyzer = AudioAnalyzer()
        except Exception as e:
            print(f"⚠️ AudioAnalyzer not available: {e}")
            self.analyzer = None
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "temp").mkdir(parents=True, exist_ok=True)
        
        self.tracks = []
        self.clips = []
    
    def log(self, msg: str):
        """Conditional verbose logging."""
        if self.verbose:
            print(f"[DEBUG] {msg}")
    
    def scan_music(self):
        """Scan and analyze music files."""
        print(f"\n🎵 Scanning music: {self.music_dir}")
        
        if not self.music_dir.exists():
            print(f"❌ Music folder not found: {self.music_dir}")
            return
        
        extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a']
        files = []
        for ext in extensions:
            files.extend(self.music_dir.glob(ext))
        
        if not files:
            print("❌ No music files found!")
            return
        
        for file in tqdm(files, desc="Loading & analyzing music"):
            try:
                if not self.analyzer:
                    print(f"⚠️ Cannot analyze {file.name} - AudioAnalyzer not available")
                    continue
                
                analysis = self.analyzer.analyze_track(file)
                sections = self.analyzer.identify_sections(analysis)
                
                meta = analysis["metadata"]
                print(f"   ✓ {meta['title']} by {meta['artist']} ({analysis['duration']:.1f}s @ {analysis['bpm']:.0f} BPM)")
                self.log(f"   Identified {len(sections)} sections")
                
                self.tracks.append({
                    "path": file,
                    "analysis": analysis,
                    "sections": sections,
                    "metadata": meta,
                })
            except Exception as e:
                print(f"   ✗ Error analyzing {file.name}: {e}")
    
    def scan_clips(self):
        """Scan clips via ClipPool."""
        print(f"\n🎬 Scanning clips: {self.clips_dir}")
        
        if not self.pool:
            print("❌ ClipPool not initialized")
            return
        
        self.clips = self.pool.clips
        print(f"📦 Loaded {len(self.clips)} clips from pool")
    
    def build_timeline(self, track_data: Dict) -> List[EditPoint]:
        """Build intelligent timeline with semantic matching."""
        print(f"\n🎬 Building timeline for: {track_data['metadata']['title']}")
        
        sections = track_data["sections"]
        timeline = []
        
        for sec_idx, section in enumerate(sections):
            print(f"   [{section.name.upper()}] {section.start_time:.1f}s - {section.end_time:.1f}s (Energy: {section.energy:.2f})")
            
            if not self.pool or not self.clips:
                continue
            
            # Select best clip semantically matching this section
            try:
                best_clip = self.pool.select_best_clip(
                    min_duration=section.duration,
                    query_vector=section.semantic_vector,
                    avoid_reuse=True,
                    cooldown=3
                )
                
                # Determine transition type based on energy
                if section.energy > 0.7:
                    transition = "glitch" if random.random() > 0.5 else "zoom"
                elif section.energy > 0.4:
                    transition = "fade"
                else:
                    transition = "cut"
                
                edit = EditPoint(
                    start_time=section.start_time,
                    end_time=section.end_time,
                    clip_path=best_clip.path,
                    clip_offset=0.0,
                    duration=section.duration,
                    transition=transition,
                    intensity=section.energy,
                )
                timeline.append(edit)
                self.log(f"   Selected: {best_clip.path.name} ({transition})")
            except Exception as e:
                print(f"   ⚠️ Could not select clip: {e}")
        
        return timeline
    
    def render_video(self, output_path: Path, timeline: List[EditPoint], audio_path: Path):
        """Render final video with hardware-safe FFmpeg."""
        print(f"\n🎬 Rendering: {output_path.name}")
        
        if not timeline:
            print("❌ Empty timeline - no clips to render")
            return False
        
        # Build FFmpeg filter complex
        inputs = ["-i", str(audio_path)]
        filter_parts = []
        
        for idx, edit in enumerate(timeline):
            inputs.extend(["-i", str(edit.clip_path)])
            
            # Trim clip to duration
            label = f"v{idx}"
            trim_filter = f"[{idx+1}:v]trim=0:{edit.duration},setpts=PTS-STARTPTS[{label}]"
            filter_parts.append(trim_filter)
        
        # Concatenate all clips
        concat_inputs = "".join([f"[v{i}]" for i in range(len(timeline))])
        concat_filter = f"{concat_inputs}concat=n={len(timeline)}:v=1:a=0[outv]"
        filter_parts.append(concat_filter)
        
        complex_filter = ";".join(filter_parts)
        
        # FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", complex_filter,
            "-map", "[outv]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path)
        ]
        
        try:
            result = self.guard.run_safe_subprocess(cmd)
            print(f"✅ SUCCESS: {output_path.name}")
            return True
        except Exception as e:
            print(f"❌ Render failed: {e}")
            return False
    
    def run(self):
        """Execute the full pipeline."""
        print("\n" + "═" * 60)
        print("  IDEX — Auto Music Video Pro (NEXT LEVEL)")
        print("═" * 60)
        
        # Show resource status
        status = self.guard.get_status()
        print(f"\n🛡️ Resources: {status['free_ram_mb']}MB RAM / {status['free_vram_mb']}MB VRAM")
        
        self.scan_music()
        self.scan_clips()
        
        if not self.tracks or not self.clips:
            print("\n❌ Cannot proceed. Missing media files.")
            return
        
        print(f"\n✓ Ready: {len(self.tracks)} tracks × {len(self.clips)} clips")
        
        # Process each track
        for track_data in self.tracks:
            try:
                sections = track_data["sections"]
                timeline = self.build_timeline(track_data)
                
                if timeline:
                    output_name = f"{track_data['metadata']['artist']}_{track_data['metadata']['title']}_MV.mp4"
                    output_path = self.output_dir / output_name
                    self.render_video(output_path, timeline, track_data["path"])
                else:
                    print(f"⚠️ Skipping {track_data['metadata']['title']} - no valid timeline")
            
            except Exception as e:
                print(f"❌ Error processing track: {e}")
        
        print(f"\n🎉 Done! Check {self.output_dir}")
        print(f"📊 Final status: {self.guard.get_status()}")


if __name__ == "__main__":
    engine = AutoMusicVideoEngine("./music", "./clips", "./output", verbose=True)
    engine.run()
