import os
import sys
import datetime
import time
import socket
import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURATION ---

# Example: '1234567890ABCDEF' (use your trusted USB serial number)
SECURE_SERIAL = "YOUR_USB_SERIAL_HERE"
# Example: 'yourusername' (output of 'whoami')
USER_NAME = "YOUR_USERNAME_HERE"
# Example: 'youraddress@gmail.com'
SENDER_MAIL = "YOUR_EMAIL_HERE"
# Example: 'abcd efgh ijkl mnop' (16-char app password from Google)
APP_PASSWORD = "YOUR_APP_PASSWORD_HERE"
# Example: 'recipient@gmail.com'
RECIPIENT_MAIL = "RECIPIENT_EMAIL_HERE"


# Example: 'write your username'
BASE_PATH = "/home/youruser/usb_guard"
# Example: 'write your username'
PHOTO_PATH = "/home/youruser/Pictures"

# Directory check
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

if not os.path.exists(PHOTO_PATH):
    os.makedirs(PHOTO_PATH)

def write_event(message):
    with open(f"{BASE_PATH}/activity.log", "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def send_mail(photo_path, device_id):
    msg = MIMEMultipart()
    msg['From'] = SENDER_MAIL
    msg['To'] = RECIPIENT_MAIL
    #realistic security alert 
    msg['Subject'] = f"[Security Alert] Unauthorized Physical Access: {device_id}"
    
    body = f"""
    System Security Alert
    -----------------------
    Detection Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Case:  Unauthorized USB device connected to the system.
    Device Serial Number: {device_id}
    
    In accordance with security protocol, a photograph of the attacker was taken and is attached.    
    Please check the system security  
    """
    msg.attach(MIMEText(body, 'plain'))

    with open(photo_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= evidence_photo.jpg")
        msg.attach(part)

    last_error = None
    for attempt in range(1, 6):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=20)
            server.starttls()
            server.login(SENDER_MAIL, APP_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except (socket.gaierror, TimeoutError, smtplib.SMTPException, OSError) as e:
            last_error = e
            with open(f"{BASE_PATH}/error.log", "a") as f:
                f.write(f"Error (attempt) {attempt}/5): {str(e)}\n")
            if attempt < 5:
                time.sleep(2)

    with open(f"{BASE_PATH}/error.log", "a") as f:
        f.write(f"Error (permanent): {str(last_error)}\n")
    return False

def take_photo():
    cam = cv2.VideoCapture(0)
    # short waiting time to warm up the camera
    for _ in range(5): cam.read() 
    ret, frame = cam.read()
    if ret:
        file_path = f"{PHOTO_PATH}/evidence_{datetime.datetime.now().strftime('%H%M%S')}.jpg"
        cv2.imwrite(file_path, frame)
        cam.release()
        return file_path
    cam.release()
    return None

# Main trigger
inserted_device = os.environ.get('ID_SERIAL_SHORT') or (sys.argv[1] if len(sys.argv) > 1 else None)

if not inserted_device:
    # Do not do anything, exit.
    sys.exit(0)

write_event(f"USB event is detected: serial={inserted_device}")
photo = take_photo()
if inserted_device != SECURE_SERIAL:
    write_event(f"USB device detected: {inserted_device}")
else:
    write_event(f"Secure device connected: {inserted_device}")
if photo:
    write_event(f"Photo is taken: {photo}")
    if send_mail(photo, inserted_device):
        write_event("E-mail sent successfully")
    else:
        write_event("Failed to send e-mail")
else:
    write_event("Photo is not taken")