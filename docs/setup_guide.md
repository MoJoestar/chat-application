# 🔧 Complete Setup Guide

This guide will walk you through setting up the Multi-Client Chat Application from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Network Configuration](#network-configuration)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Operating System:** Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** Version 3.8 or higher
- **RAM:** Minimum 2GB
- **Storage:** 100MB free space
- **Network:** Ethernet port or Wi-Fi capability

### Software Requirements
- Python 3.8+
- pip (Python package manager)
- Git (for cloning repository)

### Check Your Python Version
```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

**Important:** On Windows, make sure to check "Add Python to PATH" during installation!

---

## Installation

### Step 1: Clone the Repository
```bash
# Using HTTPS
git clone https://github.com/your-username/chat-application.git

# OR using SSH
git clone git@github.com:your-username/chat-application.git

# Navigate to project directory
cd chat-application
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `cryptography` - For message encryption

### Step 4: Verify Installation
```bash
python -c "import cryptography; print('All dependencies installed!')"
```

If no errors appear, you're ready to go! ✅

---

## Network Configuration

### Scenario 1: Testing on Single Computer (Localhost)

**Use Case:** Testing the application on one machine

**Configuration:**
- Server Address: `localhost` or `127.0.0.1`
- Port: `5555`

**Steps:**
1. Start server in one terminal
2. Start multiple clients in separate terminals
3. All communication happens locally

**No network setup needed!** ✨

---

### Scenario 2: Wired Network (Ethernet/LAN)

**Use Case:** Office, lab, or home network with Ethernet cables

#### Setup Steps:

**1. Connect Hardware**
- Connect all PCs using Ethernet cables to a switch/router
- OR connect two PCs directly with an Ethernet cable (crossover/auto-MDI)

**2. Configure Network Settings**

**Windows:**
```
1. Open Control Panel → Network and Internet → Network Connections
2. Right-click Ethernet adapter → Properties
3. Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties
4. Choose "Use the following IP address"
5. Configure:
   - Server PC: IP: 192.168.1.10, Subnet: 255.255.255.0
   - Client PC 1: IP: 192.168.1.11, Subnet: 255.255.255.0
   - Client PC 2: IP: 192.168.1.12, Subnet: 255.255.255.0
6. Click OK
```

**macOS:**
```
1. System Preferences → Network
2. Select Ethernet → Configure IPv4 → Manually
3. Set IP address (e.g., 192.168.1.10)
4. Set Subnet Mask: 255.255.255.0
5. Apply
```

**Linux:**
```bash
# Edit network configuration
sudo nano /etc/network/interfaces

# Add:
auto eth0
iface eth0 inet static
address 192.168.1.10
netmask 255.255.255.0

# Restart networking
sudo systemctl restart networking
```

**3. Find Server IP Address**

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" under Ethernet adapter
```

**macOS/Linux:**
```bash
ifconfig
# or
ip addr show
# Look for inet address
```

**4. Test Connection**
```bash
# From client PC, ping server
ping 192.168.1.10
```

If you get replies, the network is working! ✅

---

### Scenario 3: Wireless Network (Wi-Fi)

**Use Case:** Devices connected to same Wi-Fi router/hotspot

#### Setup Steps:

**1. Connect All Devices to Same Wi-Fi**
- Connect to same Wi-Fi network
- Ensure network allows peer-to-peer communication (some public networks block this)

**2. Find Server IP Address**

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" under Wireless LAN adapter
```

**macOS:**
```bash
ifconfig en0 | grep inet
```

**Linux:**
```bash
ip addr show wlan0
```

Example output: `192.168.0.105`

**3. Configure Firewall**

**Windows:**
```
1. Windows Defender Firewall → Advanced Settings
2. Inbound Rules → New Rule
3. Port → TCP → 5555
4. Allow the connection
5. Apply to all profiles
6. Name: "Chat Application"
```

**macOS:**
```bash
# Allow Python through firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/bin/python3
```

**Linux (UFW):**
```bash
sudo ufw allow 5555/tcp
sudo ufw reload
```

**4. Test Connection**
```bash
ping [server-ip-address]
```

---

### Scenario 4: Creating a Wi-Fi Hotspot

**Use Case:** No router available, create your own network

**Windows 10/11:**
```
1. Settings → Network & Internet → Mobile hotspot
2. Turn on "Share my Internet connection"
3. Set network name and password
4. Note the IP address shown (usually 192.168.137.1)
```

**macOS:**
```
1. System Preferences → Sharing
2. Enable "Internet Sharing"
3. Share from: Ethernet, To: Wi-Fi
4. Wi-Fi Options: Set network name and password
```

**Linux:**
```bash
# Using nmcli
nmcli dev wifi hotspot ssid ChatNetwork password 12345678
```

---

## Running the Application

### Starting the Server

**1. Navigate to Project Directory**
```bash
cd chat-application
```

**2. Activate Virtual Environment** (if using)
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Start Server**
```bash
python -m server.server
```

**Expected Output:**
```
============================================================
Chat Server Started Successfully!
============================================================
Server Address: 0.0.0.0:5555
Waiting for connections...
Press Ctrl+C to stop the server
```

**Server is now running!** ✅

---

### Starting the Client

**Option 1: GUI Client (Recommended)**

**1. Open New Terminal/Command Prompt**

**2. Navigate to Project Directory**
```bash
cd chat-application
```

**3. Activate Virtual Environment** (if using)
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**4. Start Client**
```bash
python -m client.gui
```

**5. Login**
- Enter username (3-20 characters)
- Enter server address:
  - `localhost` (same computer)
  - `192.168.x.x` (network IP)
- Enter port: `5555`
- Click "Connect"

**You're now connected!** ✅

---

### Running Multiple Clients

**Method 1: Multiple Terminals**
1. Open 3-4 terminal windows
2. Run `python -m client.gui` in each
3. Use different usernames

**Method 2: Different Computers**
1. Install application on each computer
2. All connect to same server IP
3. Each uses unique username

---

## Testing

### Test Checklist

#### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] Client connects to server
- [ ] Username validation works
- [ ] Can send group messages
- [ ] Can receive group messages
- [ ] Can send private messages
- [ ] Can receive private messages
- [ ] Online users list updates
- [ ] Chat history loads on connect

#### ✅ Network Connectivity
- [ ] Works on localhost
- [ ] Works on wired LAN
- [ ] Works on Wi-Fi
- [ ] Multiple clients can connect
- [ ] Messages delivered in real-time

#### ✅ Error Handling
- [ ] Duplicate username rejected
- [ ] Invalid username rejected
- [ ] Server offline message shown
- [ ] Disconnection handled gracefully
- [ ] Network interruption detected

#### ✅ Database
- [ ] Messages saved to database
- [ ] History retrieved on reconnect
- [ ] Database file created automatically
- [ ] No data loss on disconnect

### Performance Testing

**Load Test:**
```bash
# Start server
python -m server.server

# Start 10 clients (in separate terminals)
for i in {1..10}; do
    python -m client.gui &
done
```

**Expected Results:**
- All clients connect successfully
- No lag in message delivery
- Server handles load without crashes

---

## Troubleshooting

### Issue: "Module not found" Error

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
pip list
```

---

### Issue: "Port already in use"

**Cause:** Another application using port 5555

**Solution 1: Change Port**
Edit `shared/utils.py`:
```python
SERVER_PORT = 5556  # Use different port
```

**Solution 2: Kill Process**

**Windows:**
```bash
netstat -ano | findstr :5555
taskkill /PID [process_id] /F
```

**macOS/Linux:**
```bash
lsof -i :5555
kill -9 [process_id]
```

---

### Issue: "Connection refused"

**Possible Causes:**
1. Server not running
2. Wrong IP address
3. Firewall blocking
4. Different networks

**Solutions:**
1. Start server first
2. Verify IP with `ipconfig`/`ifconfig`
3. Check firewall settings
4. Ensure same network

---

### Issue: tkinter not found (Linux)

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

### Issue: Permission denied on Linux

**Solution:**
```bash
# Give execution permissions
chmod +x server/server.py
chmod +x client/gui.py
```

---

### Issue: Database locked

**Solution:**
```bash
# Stop all applications
# Delete database file
rm database/chat.db

# Restart server (database will recreate)
```

---

## Advanced Configuration

### Change Server Port

Edit `shared/utils.py`:
```python
SERVER_PORT = 8080  # Your custom port
```

### Increase Max Clients

Edit `shared/utils.py`:
```python
MAX_CLIENTS = 200  # More clients
```

### Change Database Location

Edit `shared/utils.py`:
```python
DB_PATH = '/path/to/custom/location/chat.db'
```

### Enable Debug Logging

Edit `shared/utils.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    # ... rest of config
)
```

---

## Next Steps

After successful setup:
1. Read [User Manual](user_manual.md) for usage instructions
2. Read [API Documentation](api_documentation.md) for technical details
3. Explore the codebase to understand implementation
4. Customize and extend features

---

## Getting Help

### Still Having Issues?

1. **Check Logs:** Look in `logs/` folder for error details
2. **GitHub Issues:** Search existing issues or create new one
3. **Documentation:** Review other docs in `docs/` folder
4. **Team Members:** Contact team members for support

---

## Summary

You should now have:
- ✅ Python environment set up
- ✅ Dependencies installed
- ✅ Network configured
- ✅ Application running
- ✅ Clients connected

**Happy Chatting! 💬**
