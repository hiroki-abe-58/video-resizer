# Video Compressor - Cross-Platform Audio/Video Quality Mode Selection

[日本語](README_ja.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [ไทย](README_th.md)

A cross-platform video compression CLI tool for Windows, macOS, and Linux. Compress videos to a target file size with selectable quality modes (audio priority, video priority, or balanced).

## Features

- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Precise Size Control**: Specify target size in MB (decimal support)
- **Quality Mode Selection**: Choose between audio priority, video priority, or balanced mode
  - Audio Priority (192kbps): Music, lectures, ASMR
  - Video Priority (128kbps): Anime, movies, gameplay
  - Balanced (160kbps): General videos
- **Real-time Progress Display**: Shows progress bar and estimated time remaining
- **2-Pass Encoding**: Achieves high-quality compression
- **Batch Processing**: Process entire directories at once
- **Dry Run Mode**: Preview compression results without actual encoding
- **Processing History Log**: Automatically saved to `~/.video-compressor/history.log`
- **Format Conversion**: Supports MP4, MOV, AVI, MKV, WebM, FLV
- **Comprehensive Error Handling**: Clear error messages for common issues

## Requirements

### Operating Systems
- **Windows**: Windows 10 or later
- **macOS**: macOS 10.14 or later
- **Linux**: Ubuntu 18.04+, Debian 10+, Fedora 30+, Arch Linux

### Software
- Python 3.8 or later
- ffmpeg

## Installation

### 1. Install ffmpeg

#### Windows

**Option 1: Chocolatey (Recommended)**
```bash
choco install ffmpeg
```

**Option 2: Scoop**
```bash
scoop install ffmpeg
```

**Option 3: Manual Installation**
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract to C:\ffmpeg
3. Add C:\ffmpeg\bin to system PATH

#### macOS

```bash
brew install ffmpeg
```

#### Linux

**Ubuntu/Debian**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Fedora**
```bash
sudo dnf install ffmpeg
```

**Arch Linux**
```bash
sudo pacman -S ffmpeg
```

### 2. Download Script

```bash
# Clone from GitHub
git clone https://github.com/hiroki-abe-58/video-compressor.git
cd video-compressor

# Or download directly
curl -O https://raw.githubusercontent.com/hiroki-abe-58/video-compressor/main/compress_video.py
```

### 3. Grant Execute Permission (macOS/Linux only)

```bash
chmod +x compress_video.py
```

## Usage

### Basic Usage

**Windows**
```bash
python compress_video.py
# or
py compress_video.py
```

**macOS/Linux**
```bash
python3 compress_video.py
# or
./compress_video.py
```

### Command Line Options

```bash
# Normal mode
python compress_video.py

# Dry run mode (preview without encoding)
python compress_video.py --dry-run

# Show version and platform
python compress_video.py --version

# Show help
python compress_video.py --help
```

### Execution Flow

#### Phase 1: Input File Path
```
Enter the path to the video file or directory and press Enter:
> /path/to/video.mp4
```

**Windows Example**: `C:\Users\username\Videos\video.mp4`
**macOS/Linux Example**: `/home/username/Videos/video.mp4`

**Tip**: Drag and drop from Explorer (Windows) or Finder (macOS) works too

#### Phase 2: Target Size Input
```
File name: video.mp4
Current file size: 150.50 MB
Video duration: 00:05:30

To what size (MB) should this video be compressed? Enter a number (decimals allowed):
> 50
```

#### Phase 2.5: Quality Mode Selection
```
[Phase 2.5] Quality Mode Selection
Which mode do you want to use for compression?

  1. Audio Priority (Audio 192kbps)
     For music, lectures, ASMR where audio quality is important

  2. Video Priority (Audio 128kbps)
     For anime, movies, gameplay where video quality is important

  3. Balanced (Audio 160kbps)
     For general videos. Balanced audio and video quality

Select a number (default: 1):
```

#### Phase 3: Format Conversion (Optional)
```
Do you want to convert the file extension? (y/press Enter):
```

#### Phase 4: Compression
Progress bar with estimated time remaining is displayed.

#### Phase 5: Complete
```
Compression complete! The compressed video file has been saved.
============================================================
Quality Mode: Video Priority
File name: video--compressed--50.0MB--2025-11-03-15-30-45.mp4
Target size: 50.00 MB
Actual size: 49.85 MB
Difference: 0.15 MB
Compression ratio: 66.9%
Processing time: 00:10:21
============================================================
```

## Quality Modes

### Comparison for 50MB Target (5-minute 1080p video)

| Mode | Video Bitrate | Audio Bitrate | Best For |
|------|---------------|---------------|----------|
| Audio Priority | 1145 kbps | 192 kbps | Music videos, concerts, lectures, ASMR |
| Balanced | 1241 kbps | 160 kbps | Vlogs, tutorials, general content |
| Video Priority | 1337 kbps | 128 kbps | Anime, movies, gameplay, action videos |

**Video Priority mode allocates 17% more bitrate to video compared to Audio Priority!**

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- File paths use backslashes (C:\Users\...)
- Drag and drop from Explorer supported

### macOS
- Use Terminal
- File paths use forward slashes (/Users/...)
- Drag and drop from Finder supported

### Linux
- Use any terminal emulator
- File paths use forward slashes (/home/...)
- Full Unicode support in most modern terminals

## Processing History

All operations are automatically logged to:
- **Windows**: `C:\Users\username\.video-compressor\history.log`
- **macOS**: `/Users/username/.video-compressor/history.log`
- **Linux**: `/home/username/.video-compressor/history.log`

### View Logs

**Windows (PowerShell)**
```powershell
Get-Content ~\.video-compressor\history.log -Tail 20
```

**Windows (Command Prompt)**
```cmd
type %USERPROFILE%\.video-compressor\history.log
```

**macOS/Linux**
```bash
tail -n 20 ~/.video-compressor/history.log
```

## Dry Run Mode

Preview compression results without actual encoding:

```bash
python compress_video.py --dry-run
```

## Batch Processing

Process all video files in a directory:

```bash
python compress_video.py

# Enter directory path
> /path/to/videos/
```

## Output File Format

```
[original_filename]--compressed--[target_size]MB--[yyyy-mm-dd-hh-mm-ss].[extension]
```

## Error Handling

This tool detects and clearly displays the following errors:

- ffmpeg not installed
- File does not exist
- Unsupported file format
- Target size larger than current size
- Target size too small
- Invalid input values
- Encoding errors

## Technical Details

### Compression Algorithm

1. **Get video duration** (using ffprobe)
2. **Select quality mode** (audio/video/balanced)
3. **Calculate required video bitrate from target size**
4. **High-quality compression with 2-pass encoding**

### Supported File Formats

**Input**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.m4v`, `.mpeg`, `.mpg`

**Output**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`

## Troubleshooting

### ffmpeg not found

**Windows**
```bash
# Verify ffmpeg is in PATH
where ffmpeg

# If not found, reinstall or add to PATH
```

**macOS**
```bash
brew install ffmpeg
```

**Linux**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
```

### Compression takes too long
- 2-pass encoding is time-consuming
- Long videos may take tens of minutes
- Progress can be monitored via progress bar

### Permission errors (macOS/Linux)
```bash
chmod +x compress_video.py
```

### Python command not found

**Windows**: Try `py` instead of `python`
**macOS/Linux**: Try `python3` instead of `python`

## Version History

### v1.5.0
- Added Windows and Linux support
- Platform-specific ffmpeg installation instructions
- Cross-platform path handling

### v1.4.0
- Added quality mode selection (audio/video/balanced)
- Enhanced logging with mode information

### v1.3.0
- Added processing history logging
- Log rotation support (10MB, 5 generations)

### v1.2.0
- Added dry run mode
- Quality level estimation

### v1.1.0
- Added batch processing
- Directory input support

### v1.0.0
- Initial release (macOS only)
- Basic compression with audio priority

## License

MIT License

## Author

[hiroki-abe-58](https://github.com/hiroki-abe-58)

## Acknowledgments

Reference: https://note.com/genelab_999/n/n5db5c3a80793
