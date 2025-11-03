# Video Compressor - Audio/Video Quality Mode Selection

[日本語](README_ja.md) | [中文](README_zh.md) | [한국어](README_ko.md)

A video compression CLI tool for macOS. Compress videos to a target file size with selectable quality modes (audio priority, video priority, or balanced).

## Features

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

- macOS
- Python 3.8 or later
- ffmpeg

## Installation

### 1. Install ffmpeg

```bash
brew install ffmpeg
```

### 2. Download Script

```bash
# Clone from GitHub
git clone https://github.com/hiroki-abe-58/video-compressor.git
cd video-compressor

# Or download directly
curl -O https://raw.githubusercontent.com/hiroki-abe-58/video-compressor/main/compress_video.py
chmod +x compress_video.py
```

### 3. Grant Execute Permission

```bash
chmod +x compress_video.py
```

## Usage

### Basic Usage

```bash
python3 compress_video.py
```

Or:

```bash
./compress_video.py
```

### Command Line Options

```bash
# Normal mode
./compress_video.py

# Dry run mode (preview without encoding)
./compress_video.py --dry-run

# Show version
./compress_video.py --version

# Show help
./compress_video.py --help
```

### Execution Flow

#### Phase 1: Input File Path
```
Enter the path to the video file or directory and press Enter:
> /path/to/video.mp4
```

**Tip**: Drag and drop from Finder works too

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
> y

Available formats:
  1. MP4 (H.264)
  2. MOV (QuickTime)
  3. AVI
  4. MKV (Matroska)
  5. WebM
  6. FLV (Flash Video)

Select a number: 1
```

#### Phase 4: Compression
```
[1/2] Pass 1: Analyzing bitrate...
Pass 1: [████████████████████░░░░░░░░░░░░░░░░░░░░]  48.5% | Time remaining: 00:02:15

[2/2] Pass 2: Final encoding...
Pass 2: [████████████████████████████████████████] 100.0% | Time remaining: 00:00:00
```

#### Phase 5: Complete
```
Compression complete! The compressed video file has been saved.
============================================================
Quality Mode: Video Priority
File name: video--compressed--50.0MB--2025-11-03-15-30-45.mp4
Save location: /path/to/video--compressed--50.0MB--2025-11-03-15-30-45.mp4
Target size: 50.00 MB
Actual size: 49.85 MB
Difference: 0.15 MB
Compression ratio: 66.9%
Processing time: 00:10:21
============================================================

Processing history saved to ~/.video-compressor/history.log

Compress another video? (y/n):
```

## Quality Modes

### Comparison for 50MB Target (5-minute 1080p video)

| Mode | Video Bitrate | Audio Bitrate | Best For |
|------|---------------|---------------|----------|
| Audio Priority | 1145 kbps | 192 kbps | Music videos, concerts, lectures, ASMR |
| Balanced | 1241 kbps | 160 kbps | Vlogs, tutorials, general content |
| Video Priority | 1337 kbps | 128 kbps | Anime, movies, gameplay, action videos |

**Video Priority mode allocates 17% more bitrate to video compared to Audio Priority!**

### When to Use Each Mode

**Audio Priority**
- Music performances and concerts
- Lectures and presentations
- ASMR content
- Podcasts with video
- Any content where audio fidelity is critical

**Video Priority**
- Anime and animation
- Movies and films
- Gaming footage and walkthroughs
- Action videos with complex motion
- Visual effects demonstrations

**Balanced**
- Vlogs and personal videos
- Tutorials and how-tos
- Interviews
- General purpose videos
- When both audio and video matter equally

## Dry Run Mode

Preview compression results without actual encoding:

```bash
./compress_video.py --dry-run
```

**Output Example**:
```
Dry Run Results
============================================================
Input file: video.mp4
Current size: 150.50 MB
Target size: 50.00 MB
Compression ratio: 66.8%
Video duration: 00:05:30

[Quality Mode]
  Video Priority: Prioritize video quality, minimize audio

[Encoding Settings]
  Video bitrate: 1337 kbps
  Audio bitrate: 128 kbps (AAC)
  Codec: H.264 (libx264)

[Estimated Quality]
  High quality (minor degradation)

[Output File]
  File name: video--compressed--50.0MB--2025-11-03-15-30-45.mp4
  Save location: /path/to/video--compressed--50.0MB--2025-11-03-15-30-45.mp4
============================================================

To actually compress, run without the --dry-run option.
```

## Batch Processing

Process all video files in a directory:

```bash
./compress_video.py

# Enter directory path
> /Users/username/Videos/batch-compress/

# 5 video files found:
#   1. video1.mp4 (150.50 MB)
#   2. video2.mov (200.30 MB)
#   ...

# Select settings method:
#   1. Batch settings (apply same settings to all files)
#   2. Individual settings (configure each file separately)
```

## Processing History

All operations are automatically logged to `~/.video-compressor/history.log`

### View Logs

```bash
# View all logs
cat ~/.video-compressor/history.log

# View recent logs
tail -n 20 ~/.video-compressor/history.log

# Follow logs in real-time
tail -f ~/.video-compressor/history.log

# Search for errors
grep ERROR ~/.video-compressor/history.log
```

### Log Format

```
YYYY-MM-DD HH:MM:SS - LEVEL - Message

Example:
2025-11-03 15:30:45 - INFO - Video compression tool v1.4.0 started
2025-11-03 15:30:50 - INFO - Quality mode selected: Video Priority
2025-11-03 15:31:02 - INFO - Compression started: video.mp4, Mode: Video Priority, Current size: 150.50MB, Target size: 50.00MB, Video bitrate: 1337kbps, Audio bitrate: 128kbps
2025-11-03 15:41:23 - INFO - Compression completed: video.mp4 -> video--compressed--50.0MB--2025-11-03-15-31-02.mp4, Mode: Video Priority, Current size: 150.50MB, Target size: 50.00MB, Actual size: 49.85MB, Difference: 0.15MB, Compression ratio: 66.9%, Processing time: 00:10:21
```

## Output File Format

```
[original_filename]--compressed--[target_size]MB--[yyyy-mm-dd-hh-mm-ss].[extension]
```

Example:
```
my_video--compressed--50.0MB--2025-11-03-15-30-45.mp4
```

## Error Handling

This tool detects and clearly displays the following errors:

- ffmpeg not installed
- File does not exist
- Unsupported file format
- Target size larger than current size
- Target size too small (audio alone exceeds capacity)
- Invalid input values (non-numeric)
- Encoding errors

## Technical Details

### Compression Algorithm

1. **Get video duration** (using ffprobe)
2. **Select quality mode** (audio/video/balanced)
3. **Calculate required video bitrate from target size**
   ```
   Video bitrate = (target size - audio size) / video duration * 0.95
   ```
4. **High-quality compression with 2-pass encoding**
   - Pass 1: Analyze bitrate distribution
   - Pass 2: Optimized encoding

### Supported File Formats

**Input**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.m4v`, `.mpeg`, `.mpg`

**Output**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`

## Troubleshooting

### ffmpeg not found
```bash
brew install ffmpeg
```

### Compression takes too long
- 2-pass encoding is time-consuming (pass 1 + pass 2)
- Long videos may take tens of minutes
- Progress can be monitored via progress bar

### Target size deviation
- Deviation of ±5% is normal
- For more accuracy, set target size slightly smaller

### Encoding fails
- Check disk space
- Verify video file is not corrupted
- Try a different extension

## Version History

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
- Initial release
- Basic compression with audio priority

## License

MIT License

## Author

[hiroki-abe-58](https://github.com/hiroki-abe-58)

## Acknowledgments

Reference: https://note.com/genelab_999/n/n5db5c3a80793
