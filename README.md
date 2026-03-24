# Unauthorized USB Detector

This project monitors USB device insertions on your **Linux** system and takes a photo with your webcam, sending an email alert if an unauthorized USB device is detected.

## Features
- Detects all USB insertions (including at startup)
- Takes a photo with the webcam when a USB is inserted
- Sends an email alert with the photo attached
- Whitelist support for trusted USB serial numbers
- Works as a background watcher script (no need for udev rules)

## Requirements
- Python 3.x
- OpenCV (`cv2`)
- A working webcam
- Internet connection for email sending
- Gmail account with App Password (for SMTP)

## Setup
1. Clone this repository or copy the files to your system.
2. Install dependencies:
   ```bash
   pip install opencv-python
   ```
3. Edit `usb_guard.py` and set your trusted USB serial, email, and app password.
4. Run the watcher:
   ```bash
   python3 usb_watcher.py
   ```


## Configuration
- Edit `SECURE_SERIAL`, `SENDER_MAIL`, `APP_PASSWORD`, and `RECIPIENT_MAIL` in `usb_guard.py`.
- The script will create logs and save photos in your home directory.

### How to Get a 16-character Gmail App Password

To use Gmail for sending emails from this script, you need to generate a 16-character App Password. This is required because Google does not allow direct login with your main password for less secure apps.

1. Go to your Google Account settings: https://myaccount.google.com/
2. Enable 2-Step Verification if you haven't already (under Security > Signing in to Google).
3. After enabling 2-Step Verification, go to the App Passwords page: https://myaccount.google.com/apppasswords
4. Select 'Mail' as the app and 'Other' (or your device) as the device, then click 'Generate'.
5. Google will show you a 16-character password. Copy this and use it as `APP_PASSWORD` in `usb_guard.py`.

> **Note:** Never share your App Password. You can revoke it anytime from your Google Account settings.

### How to Find Your Authenticated USB Serial Number

1. Plug in your trusted USB device.
2. Open a terminal and run:
   ```bash
   lsblk -S -o NAME,SERIAL,MODEL,TRAN,VENDOR
   ```
   or
   ```bash
   udevadm info --query=all --name=/dev/sdX | grep ID_SERIAL_SHORT
   ```
   (Replace `/dev/sdX` with your USB device, e.g., `/dev/sdb`)
3. Find the serial number for your device in the output.
4. Copy the serial number and paste it as the value of `SECURE_SERIAL` in `usb_guard.py`.

## License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---
**Security Note:**
- This tool is for educational and personal security use. Do not use it for malicious purposes.
