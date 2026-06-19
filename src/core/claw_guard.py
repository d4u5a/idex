#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claw_guard.py — Concurrency, GPU VRAM & System Memory Safeguard.
Protects host systems from physical RAM exhaustion and thread starvation.
"""

from __future__ import annotations

import os
import sys
import shutil
import subprocess
import threading
import time
from typing import Any, List, Dict, Optional

# Soft imports for system monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False


class ResourceGuard:
    """
    Limits concurrent FFmpeg/OpenCV subprocesses and monitors multi-vendor GPU VRAM
    and motherboard RAM to prevent thread starvation and out-of-memory crashes.
    """
    
    def __init__(
        self, 
        max_ffmpeg_processes: int = 4, 
        min_free_ram_mb: int = 1024,
        min_free_vram_mb: int = 512,
        monitor_vram: bool = True
    ):
        cpu_cores = os.cpu_count() or 4
        # Limit workers gracefully based on core availability
        self.max_workers = min(max_ffmpeg_processes, max(1, cpu_cores - 1))
        self.min_free_ram = min_free_ram_mb * 1024 * 1024
        self.min_free_vram = min_free_vram_mb * 1024 * 1024
        self.monitor_vram = monitor_vram
        
        self.semaphore = threading.BoundedSemaphore(self.max_workers)
        self._active_processes: set = set()
        self._lock = threading.Lock()
        
        # Initialize GPU metrics monitoring via NVML
        self._nvml_initialized = False
        if self.monitor_vram and HAS_NVML:
            try:
                pynvml.nvmlInit()
                self._nvml_initialized = True
                logger_msg = "GPU monitoring initialized."
            except Exception:
                logger_msg = "NVIDIA NVML not available or GPU drivers skipped."
        else:
            logger_msg = "GPU checking disabled."

        print(f"🛡️ [CLAW-GUARD] Resource pool initialized: Cap={self.max_workers} threads, RAM-Floor={min_free_ram_mb}MB")
        if self._nvml_initialized:
            print(f"🎮 [CLAW-GUARD] VRAM Guard active: VRAM-Floor={min_free_vram_mb}MB")

    def get_system_free_ram(self) -> int:
        """Returns free physical memory on host system in bytes."""
        if HAS_PSUTIL:
            return psutil.virtual_memory().available
        
        # Windows command-line fallback without psutil
        try:
            cmd = "wmic OS get FreePhysicalMemory /Value"
            res = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=True, timeout=5)
            for line in res.stdout.split("\n"):
                if "FreePhysicalMemory" in line:
                    kb = int(line.split("=")[1].strip())
                    return kb * 1024
        except Exception:
            pass
        return 2048 * 1024 * 1024  # Neutral 2GB fallback

    def get_gpu_free_vram(self) -> int:
        """Returns free VRAM on primary GPU in bytes."""
        if self._nvml_initialized and HAS_NVML:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                return info.free
            except Exception:
                pass
        return 1024 * 1024 * 1024  # Neutral 1GB fallback

    def check_safety_thresholds(self) -> bool:
        """Validates physical and virtual thresholds before dispatching threads."""
        free_ram = self.get_system_free_ram()
        if free_ram < self.min_free_ram:
            free_mb = round(free_ram / (1024 * 1024))
            min_mb = self.min_free_ram // (1024 * 1024)
            print(f"⚠️ [CLAW-GUARD] Low System RAM! Current: {free_mb}MB, Threshold: {min_mb}MB")
            return False

        if self._nvml_initialized:
            free_vram = self.get_gpu_free_vram()
            if free_vram < self.min_free_vram:
                vram_mb = round(free_vram / (1024 * 1024))
                min_vram_mb = self.min_free_vram // (1024 * 1024)
                print(f"⚠️ [CLAW-GUARD] Low VRAM! Current: {vram_mb}MB, Threshold: {min_vram_mb}MB")
                return False

        return True

    def block_until_safe(self, interval_seconds: float = 2.0, max_wait: int = 300) -> bool:
        """Halts pipeline until memory pressures clear. Returns False if timeout."""
        elapsed = 0
        while not self.check_safety_thresholds():
            if elapsed >= max_wait:
                print(f"❌ [CLAW-GUARD] Timeout waiting for resources (>{max_wait}s)")
                return False
            time.sleep(interval_seconds)
            elapsed += interval_seconds
        return True

    def run_safe_subprocess(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Runs a subprocess bound securely inside the concurrent execution semaphore."""
        if not self.block_until_safe():
            raise RuntimeError("System resources unavailable - timeout waiting for memory")
        
        with self.semaphore:
            try:
                if "stdout" not in kwargs:
                    kwargs["stdout"] = subprocess.PIPE
                if "stderr" not in kwargs:
                    kwargs["stderr"] = subprocess.PIPE
                if "text" not in kwargs:
                    kwargs["text"] = True

                proc = subprocess.Popen(command, **kwargs)
                
                with self._lock:
                    self._active_processes.add(proc)

                try:
                    stdout, stderr = proc.communicate(timeout=3600)  # 1 hour timeout
                    returncode = proc.poll() or 0
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                    raise RuntimeError(f"Process timeout: {' '.join(command)}")
                
                with self._lock:
                    self._active_processes.discard(proc)

                if returncode != 0:
                    raise RuntimeError(f"Child process failed (Code {returncode}): {stderr}")

                return subprocess.CompletedProcess(command, returncode, stdout, stderr)
            except Exception as e:
                raise RuntimeError(f"ClawGuard subprocess error: {e}")

    def terminate_all(self) -> None:
        """Terminate all active spawned child subprocesses."""
        with self._lock:
            for p in self._active_processes.copy():
                try:
                    p.kill()
                    print(f"💀 Terminated child process: PID {p.pid}")
                except Exception:
                    pass
            self._active_processes.clear()

    def get_status(self) -> Dict[str, Any]:
        """Returns current resource status."""
        return {
            "max_workers": self.max_workers,
            "active_processes": len(self._active_processes),
            "free_ram_mb": round(self.get_system_free_ram() / (1024 * 1024)),
            "free_vram_mb": round(self.get_gpu_free_vram() / (1024 * 1024)) if self._nvml_initialized else None,
            "ram_threshold_mb": self.min_free_ram // (1024 * 1024),
            "vram_threshold_mb": self.min_free_vram // (1024 * 1024) if self._nvml_initialized else None,
        }

    def __del__(self) -> None:
        """Shutdown NVML cleanly when garbage collected."""
        if self._nvml_initialized and HAS_NVML:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
