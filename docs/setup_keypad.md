# Keypad Setup and Testing

1. Pair keypad with `bluetoothctl`:
   - `scan on`, `pair`, `connect`, `trust`
2. Run `sudo evtest` to find the correct `/dev/input/eventX`.
3. Press `+`, `-`, `0` to confirm keycodes.
4. Update `main_tkinter_fps.py` or `main_opencv_fps.py`:
   ```python
   threading.Thread(target=keypad_listener, args=("/dev/input/eventX",), daemon=True).start()

# Steps to stablize the connection

1. Mark the device as trusted. Ensures Pi will always try to reconnect automatically. In `bluetoothctl`: `trust <MAC address>`

2. Auto-reconnect with systemd service. In `/etc/systemd/system/keypad.service`
----------------------
[Unit]
Description=Bluetooth Keypad Auto Connect
After=bluetooth.target

[Service]
ExecStart=/usr/bin/bluetoothctl connect <MAC address>
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
-----------------------
Enable it to force a reconnect attempt if the link drops: `sudo systemctl enable keypad.service

3. Reduce aggressive power management. Disable Bluetooth power saving by editing /etc/bluetooth/main.conf: 
Ini------------------------
[Policy]
AutoEnable=true
Code------------------------
btcoex_enable=0



