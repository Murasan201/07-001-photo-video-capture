# Photo/Video Capture Application

Simple Python scripts for capturing photos and recording videos using Raspberry Pi camera modules. These lightweight scripts are designed for educational purposes and easy understanding.

## Features

- **Photo Capture**: Quick photo capture with Picamera2
- **Video Recording**: 10-second video recording with H.264 encoding and MP4 conversion
- **Preview Support**: Automatic preview display when available (desktop environment)
- **Headless Operation**: Works without display for SSH/remote usage
- **Error Handling**: Robust error handling with informative messages

## System Requirements

### Hardware
- Raspberry Pi 5 (recommended) or Raspberry Pi 4
- Raspberry Pi Camera Module v2, v3, or HQ Camera
- microSD card with Raspberry Pi OS
- 5V power adapter

### Software
- Raspberry Pi OS (latest recommended)
- Python 3.9 or higher
- Picamera2 library
- FFmpeg (for video conversion)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Murasan201/07-001-photo-video-capture.git
cd 07-001-photo-video-capture
```

### 2. Install Dependencies

Update system and install required packages:
```bash
sudo apt update
sudo apt install -y python3-picamera2 ffmpeg
```

### 3. Enable Camera Interface
```bash
sudo raspi-config
# Navigate to Interface Options > Camera > Enable
# Reboot after enabling
sudo reboot
```

## Usage

### Photo Capture Script (`photo_capture.py`)

Captures a single photo and saves it as JPEG:

```bash
# Basic usage - captures a photo
python3 photo_capture.py

# Output: photo_[timestamp].jpg (e.g., photo_20251016_143052.jpg)
```

**Features:**
- Resolution: 1920x1080 (Full HD)
- Format: JPEG
- Auto-timestamped filename
- Automatic camera resource cleanup

### Video Recording Script (`video_capture.py`)

Records a 10-second video and saves it as MP4:

```bash
# Basic usage - records 10 seconds of video
python3 video_capture.py

# Output: test_video.mp4
```

**Features:**
- Resolution: 1920x1080 (Full HD)
- Duration: 10 seconds
- Format: H.264 encoded, converted to MP4
- Bitrate: 10 Mbps
- Preview: Automatic when display is available
- Headless: Works without display via SSH

### Running in Different Environments

#### Desktop Environment (with display)
```bash
# Preview will be shown automatically
python3 photo_capture.py
python3 video_capture.py
```

#### SSH/Remote Access (headless)
```bash
# Works without display - no preview
python3 photo_capture.py
python3 video_capture.py
```

#### Force display environment
```bash
# If display exists but not detected
export DISPLAY=:0
python3 video_capture.py
```

## File Structure

```
07-001-photo-video-capture/
├── photo_capture.py      # Photo capture script
├── video_capture.py      # Video recording script
├── README.md            # This documentation
├── requirements.txt     # Python dependencies
├── LICENSE             # MIT License
├── CLAUDE.md           # Project rules (Japanese)
└── 07-001_写真動画キャプチャアプリ_要件定義書.md  # Requirements (Japanese)
```

## Output Files

- **Photos**: `photo_YYYYMMDD_HHMMSS.jpg`
- **Videos**: `test_video.mp4` (fixed name for simplicity)

## Safety and Security Considerations

⚠️ **Important Safety Guidelines**

### Camera Privacy
- Always be aware of what you are recording
- Respect privacy laws and regulations in your area
- Inform subjects when recording
- Store recordings securely

### Hardware Safety
- Ensure proper power supply to prevent corruption
- Handle camera modules with care
- Keep the camera lens clean
- Avoid extreme temperatures or humidity

### Data Security
- Regularly backup important recordings
- Use appropriate file permissions
- Monitor storage capacity
- Delete unnecessary files

## Troubleshooting

### Common Issues and Solutions

#### Camera Not Detected
```
Error: Camera not detected
```
**Solutions:**
1. Check camera cable connection
2. Enable camera interface: `sudo raspi-config`
3. Restart: `sudo reboot`
4. Check with: `libcamera-hello`

#### Permission Denied
```
Error: Permission denied
```
**Solutions:**
1. Add user to video group: `sudo usermod -a -G video $USER`
2. Log out and log back in
3. Check camera isn't in use by another process

#### Qt Display Error (SSH)
```
qt.qpa.xcb: could not connect to display
```
**Solution:**
This is normal when running via SSH. The script automatically detects this and runs without preview.

#### FFmpeg Not Found
```
Error: ffmpeg command not found
```
**Solution:**
Install FFmpeg: `sudo apt install -y ffmpeg`

#### Storage Space Issues
```
Error: No space left on device
```
**Solutions:**
1. Check space: `df -h`
2. Clean old files: `rm *.jpg *.mp4 *.h264`
3. Use external storage

### Performance Tips

- Ensure sufficient storage before recording
- Use a fast microSD card (Class 10 or higher)
- Close unnecessary applications
- Keep system cool during extended use

## Technical Details

### Photo Capture (`photo_capture.py`)
- Uses Picamera2 library
- Captures at main stream resolution
- JPEG format with automatic quality

### Video Recording (`video_capture.py`)
- H.264 hardware encoding via Picamera2
- 10 Mbps bitrate for good quality
- FFmpeg conversion to MP4 container
- Automatic cleanup of temporary H.264 file

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

This project is designed as an educational tool for learning Raspberry Pi camera programming. Contributions and improvements are welcome!

## Additional Documentation

- [Requirements Document](./07-001_写真動画キャプチャアプリ_要件定義書.md) (Japanese)
- [Project Rules](./CLAUDE.md) (Japanese)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages carefully
3. Ensure all dependencies are installed
4. Verify hardware connections

---

**Document ID:** 07-001  
**Last Updated:** 2025-10-16  
**Target Audience:** Programming beginners, Raspberry Pi learners, Camera module users