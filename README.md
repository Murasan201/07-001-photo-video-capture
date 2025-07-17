# Photo/Video Capture Application

A Python application for capturing photos and recording videos using Raspberry Pi camera modules or USB cameras. This application supports both Picamera2 and OpenCV backends for maximum compatibility.

## Features

- **Dual Camera Support**: Compatible with both Raspberry Pi camera modules and USB webcams
- **Multiple Formats**: Support for JPEG/PNG photos and MP4 videos
- **Flexible Resolution**: Configurable width and height for both photos and videos
- **Command Line Interface**: Easy-to-use CLI with comprehensive options
- **Automatic Timestamping**: Files are automatically named with timestamps
- **Error Handling**: Robust error handling with informative messages
- **Resource Management**: Proper camera resource cleanup

## System Requirements

### Hardware
- Raspberry Pi 5 (recommended)
- Raspberry Pi Camera Module v2 or compatible USB webcam
- microSD card with Raspberry Pi OS
- 5V power adapter

### Software
- Raspberry Pi OS (latest recommended)
- Python 3.9 or higher

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Murasan201/07-001-photo-video-capture.git
cd 07-001-photo-video-capture
```

### 2. Install Dependencies

For Raspberry Pi camera module (Picamera2):
```bash
sudo apt update
sudo apt install python3-picamera2
```

For USB cameras (OpenCV):
```bash
pip3 install opencv-python
```

### 3. Enable Camera Interface (for Pi Camera)
```bash
sudo raspi-config
# Navigate to Interface Options > Camera > Enable
```

## Usage

### Basic Commands

#### Photo Capture
```bash
# Capture a photo with default settings (1920x1080, JPEG)
python3 photo_video_capture.py photo

# Capture with custom resolution and format
python3 photo_video_capture.py photo --width 2560 --height 1440 --format png

# Specify output directory
python3 photo_video_capture.py photo --output ./my_photos
```

#### Video Recording
```bash
# Record video with default settings (1280x720, 30fps, 10 seconds)
python3 photo_video_capture.py video

# Record with custom settings
python3 photo_video_capture.py video --width 1920 --height 1080 --fps 24 --duration 30

# Specify output directory
python3 photo_video_capture.py video --output ./my_videos --duration 5
```

#### Force OpenCV Usage
```bash
# Use OpenCV instead of Picamera2 (useful for USB cameras)
python3 photo_video_capture.py photo --use-opencv
python3 photo_video_capture.py video --use-opencv
```

### Command Line Options

#### Common Options
- `--output DIR`: Specify output directory (default: current directory)
- `--use-opencv`: Force OpenCV usage instead of Picamera2

#### Photo Options
- `--width WIDTH`: Image width in pixels (default: 1920)
- `--height HEIGHT`: Image height in pixels (default: 1080)
- `--format FORMAT`: File format - jpg or png (default: jpg)

#### Video Options
- `--width WIDTH`: Video width in pixels (default: 1280)
- `--height HEIGHT`: Video height in pixels (default: 720)
- `--fps FPS`: Frame rate (default: 30)
- `--duration SECONDS`: Recording duration in seconds (default: 10)

### File Naming Convention

Files are automatically named with timestamps:
- Photos: `photo_YYYYMMDD_HHMMSS.{format}`
- Videos: `video_YYYYMMDD_HHMMSS.mp4`

Example: `photo_20250717_143052.jpg`

## Safety and Security Considerations

⚠️ **Important Safety Guidelines**

### Camera Privacy
- Always be aware of what you are recording
- Respect privacy laws and regulations in your area
- Inform subjects when recording in public spaces
- Store recordings securely and delete unnecessary files

### Hardware Safety
- Ensure proper power supply to prevent data corruption
- Handle camera modules with care to avoid damage
- Keep the camera lens clean and protected
- Avoid exposing the camera to extreme temperatures or humidity

### Data Security
- Regularly backup important recordings
- Use appropriate file permissions to protect sensitive content
- Consider encryption for sensitive recordings
- Be mindful of storage capacity limitations

### System Security
- Keep your Raspberry Pi OS updated
- Use strong passwords for system access
- Limit network access if not required
- Monitor system resources during recording

## Troubleshooting

### Common Issues

#### Camera Not Detected
```
Error: Camera not detected
```
**Solutions:**
1. Check camera connection to Raspberry Pi
2. Enable camera interface: `sudo raspi-config`
3. Restart the system: `sudo reboot`
4. Try using `--use-opencv` flag for USB cameras

#### Permission Denied
```
Error: Permission denied when accessing camera
```
**Solutions:**
1. Add user to video group: `sudo usermod -a -G video $USER`
2. Check camera isn't being used by another process
3. Restart and try again

#### Library Import Errors
```
Error: No available camera libraries
```
**Solutions:**
1. Install Picamera2: `sudo apt install python3-picamera2`
2. Install OpenCV: `pip3 install opencv-python`
3. Check Python version compatibility (3.9+)

#### Storage Space Issues
```
Error: No space left on device
```
**Solutions:**
1. Check available space: `df -h`
2. Clean up old recordings: `rm old_videos/*.mp4`
3. Change output directory to external storage

#### Recording Quality Issues
**For poor video quality:**
1. Increase resolution: `--width 1920 --height 1080`
2. Adjust frame rate: `--fps 24`
3. Ensure adequate lighting
4. Clean camera lens

**For large file sizes:**
1. Reduce resolution: `--width 640 --height 480`
2. Lower frame rate: `--fps 15`
3. Shorten recording duration: `--duration 5`

### Getting Help

If you encounter issues not covered here:

1. Check the application logs for detailed error messages
2. Verify your hardware setup matches the requirements
3. Test with minimal settings first
4. Consult the Raspberry Pi camera documentation

### Performance Tips

- Use lower resolutions for longer recordings
- Ensure sufficient storage space before recording
- Close unnecessary applications during video recording
- Use a fast microSD card (Class 10 or higher)
- Keep the system cool during extended recording sessions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

This project is designed as an educational tool for learning Raspberry Pi camera programming. Contributions are welcome!

## Documentation

- [Requirements Document](./07-001_写真動画キャプチャアプリ_要件定義書.md) (Japanese)
- [Project Rules](./CLAUDE.md) (Japanese)

---

**Document ID:** 07-001  
**Last Updated:** 2025-07-17  
**Target Audience:** Programming beginners, Raspberry Pi learners, Image/Video processing beginners