import os
import subprocess
from pathlib import Path

def build_ffmpeg_command(video_path, sub_path, output_path, settings, font_path=None):
    cmd = [
        'ffmpeg', '-i', str(video_path),
        '-vf', f"ass={sub_path}",
        '-c:v', settings['codec'], '-crf', str(settings['crf']),
        '-r', str(settings['fps']),
        '-b:a', settings['audio_bitrate'],
        '-y', str(output_path)
    ]
    # Additional style settings can be appended via ass modifications
    return cmd


def encode_with_progress(cmd, progress_callback=None):
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stderr:
        if 'time=' in line:
            # parse progress and call callback
            if progress_callback:
                progress_callback(line)
    process.wait()
    return process.returncode


---
