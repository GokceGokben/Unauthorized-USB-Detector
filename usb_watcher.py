import time
import subprocess
import sys
import os


# Trusted USB serial number
SECURE_SERIAL = ""
# To keep track of last detected USB serials
last_serials = set()

# Full path to usb_guard.py
USB_GUARD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usb_guard.py")

# Get USB serial numbers
def get_usb_serials():
    serials = set()
    try:
        output = subprocess.check_output([
            "lsblk", "-S", "-o", "SERIAL,MODEL,TRAN,VENDOR"
        ], text=True)
        for line in output.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 1:
                serial = parts[0]
                # jump over PCI-like serials and empty ones
                if serial and not serial.startswith("0000:") and serial != "":
                    serials.add(serial)
    except Exception:
        pass
    # Also check via sysfs
    try:
        for d in os.listdir("/sys/bus/usb/devices/"):
            serial_path = f"/sys/bus/usb/devices/{d}/serial"
            if os.path.isfile(serial_path):
                with open(serial_path) as f:
                    serial = f.read().strip()
                    # jump over PCI-like serials and empty ones
                    if serial and not serial.startswith("0000:") and serial != "":
                        serials.add(serial)
    except Exception:
        pass
    return serials

def main():
    global last_serials
    print("USB watcher started. Press Ctrl+C to exit.")
    #Check for already connected USBs on startup
    last_serials = get_usb_serials()
    # A dictionary to track the connection and disconnection times of each USB
    usb_seen = {s: True for s in last_serials}
    for s in last_serials:
        if s != SECURE_SERIAL:
            print(f"Unauthorized USB detected on startup: {s}")
            subprocess.Popen([sys.executable, USB_GUARD_PATH, s])
    while True:
        serials = get_usb_serials()
        # Find removed USBs
        removed = set(usb_seen.keys()) - serials
        for s in removed:
            usb_seen.pop(s, None)
        # Find newly added USBs
        new = serials - set(usb_seen.keys())
        for s in new:
            if s != SECURE_SERIAL:
                print(f"Unauthorized USB detected: {s}")
                subprocess.Popen([sys.executable, USB_GUARD_PATH, s])
            usb_seen[s] = True
        last_serials = serials
        time.sleep(2)

if __name__ == "__main__":
    main()
