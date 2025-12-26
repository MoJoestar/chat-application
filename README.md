# chat-application
# 💬 Multi-Client Chat Application

A local network chat application supporting both wired and wireless connectivity without requiring internet access. Built with Python using socket programming, multithreading, and tkinter GUI.

## 🎯 Project Overview

This is a complete chat application that allows multiple users on the same local network to communicate through private and group messages. All messages are encrypted and stored in a database for persistence.

### Key Features
- ✅ Server-client architecture with multithreading
- ✅ Private messaging (one-to-one)
- ✅ Group messaging (broadcast to all)
- ✅ Message persistence (SQLite database)
- ✅ Graphical User Interface (tkinter)
- ✅ Connection management & graceful disconnection
- ✅ Message encryption for security
- ✅ Wired connectivity (Ethernet/LAN)
- ✅ Wireless connectivity (Wi-Fi LAN)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Real-time online users list
- ✅ Chat history on reconnection

## 📋 Requirements

### Software
- Python 3.8 or higher
- pip (Python package manager)

### Python Packages
```bash
pip install -r requirements.txt
```

Required package:
- `cryptography` - For message encryption

## 🚀 Quick Start Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/chat-application.git
cd chat-application
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start the Server
```bash
python -m server.server
```

You should see:
```
============================================================
Chat Server Started Successfully!
============================================================
Server Address: 0.0.0.0:5555
Waiting for connections...
```

### Step 4: Start Client(s)
Open a new terminal/command prompt and run:
```bash
python -m client.gui
```

1. Enter your username
2. Enter server address (use `localhost` if on same machine, or server's IP address)
3. Enter port (default: `5555`)
4. Click "Connect"

### Step 5: Start Chatting! 🎉
- Use the **Group Chat** button to send messages to everyone
- Click on a username in the sidebar for **private chat**
- Press `Ctrl+Enter` to send messages quickly

## 📁 Project Structure
```
chat-application/
├── server/                 # Server-side code
│   ├── server.py          # Main server (Person 1)
│   ├── client_handler.py  # Client management (Person 1)
│   └── database.py        # Database operations (Person 2)
├── client/                 # Client-side code
│   ├── client.py          # Client networking (Person 3)
│   ├── message_handler.py # Message processing (Person 3)
│   └── gui.py             # User interface (Person 4)
├── shared/                 # Shared utilities
│   ├── protocol.py        # Message protocol (Person 5)
│   ├── encryption.py      # Security features (Person 5)
│   └── utils.py           # Helper functions (Person 5)
├── database/              # Database files (auto-generated)
├── logs/                  # Log files (auto-generated)
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 👥 Team Members & Responsibilities

| Person | Role | Files | Responsibilities |
|--------|------|-------|------------------|
| **Person 1** | Server Core & Connection Management | `server.py`, `client_handler.py` | TCP server, multithreading, client connections, message routing |
| **Person 2** | Database & Message Persistence | `database.py` | SQLite database, save/retrieve messages, user management |
| **Person 3** | Client Networking & Message Handling | `client.py`, `message_handler.py` | Socket connection, send/receive messages, message processing |
| **Person 4** | GUI Development | `gui.py` | Tkinter interface, user experience, visual design |
| **Person 5** | Protocol & Security | `protocol.py`, `encryption.py`, `utils.py` | Message format, encryption, constants, utilities |

## 🔧 Configuration

### Server Configuration
Edit `shared/utils.py` to change server settings:
```python
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 5555       # Port number
MAX_CLIENTS = 100        # Maximum concurrent clients
```

### Network Setup

#### 🔌 Wired Connection (Ethernet)
1. Connect all PCs using Ethernet cables or through a LAN switch/router
2. Set static IP addresses on the same subnet (e.g., 192.168.1.x)
3. Start server on one PC
4. Clients connect using server's IP address

**Example:**
- Server PC: 192.168.1.10
- Client 1: 192.168.1.11
- Client 2: 192.168.1.12

Clients enter `192.168.1.10` as server address.

#### 📡 Wireless Connection (Wi-Fi)
1. Connect all devices to the same Wi-Fi network
2. Find server's IP address:
   - **Windows:** `ipconfig` in Command Prompt
   - **Linux/Mac:** `ifconfig` or `ip addr` in Terminal
3. Clients connect using server's IP address

**No internet required!** The application works entirely on the local network.

## 🧪 Testing

### Test Individual Modules

**Test Database:**
```bash
python server/database.py
```

**Test Protocol:**
```bash
python shared/protocol.py
```

**Test Encryption:**
```bash
python shared/encryption.py
```

**Test Client:**
```bash
python client/client.py
```

### Run Unit Tests (Optional)
```bash
pytest tests/
```

## 📖 How to Use

### For Users

1. **Connect to Server**
   - Enter username (3-20 characters, alphanumeric)
   - Enter server address and port
   - Click Connect

2. **Send Group Messages**
   - Click "Group Chat" button
   - Type message and press Ctrl+Enter or click Send

3. **Send Private Messages**
   - Click on a username in the sidebar
   - Type message and send

4. **View Online Users**
   - Online users appear in the left sidebar
   - Click "Refresh" to update the list

5. **Disconnect**
   - Close the window or click X
   - Confirm disconnection

### For Administrators

**Start Server:**
```bash
python -m server.server
```

**Stop Server:**
- Press `Ctrl+C` in the terminal
- Server will gracefully disconnect all clients

**View Logs:**
- Check `logs/` folder for detailed logs
- Logs include connections, messages, errors

**Database Location:**
- `database/chat.db`
- Use any SQLite browser to view contents

## 🔒 Security Features

- **Message Encryption:** All messages encrypted using Fernet (AES-128)
- **No Plain Text:** Messages never transmitted in plain text
- **Secure Storage:** Messages stored securely in SQLite database
- **Username Validation:** Prevents malicious usernames
- **Input Sanitization:** All inputs validated before processing

## 🐛 Troubleshooting

### Connection Issues

**Problem:** Cannot connect to server
- ✅ Ensure server is running
- ✅ Check firewall settings (allow Python/port 5555)
- ✅ Verify all devices on same network
- ✅ Confirm correct IP address and port

**Problem:** "Username already taken"
- ✅ Choose a different username
- ✅ Wait if someone just disconnected

### Database Issues

**Problem:** Database errors
- ✅ Database auto-creates on first run
- ✅ Check `database/` folder exists
- ✅ Ensure write permissions

### GUI Issues

**Problem:** GUI doesn't appear
- ✅ Ensure tkinter is installed (comes with Python)
- ✅ On Linux: `sudo apt-get install python3-tk`

## 📊 Features Checklist

- [x] Server-client architecture
- [x] Multithreading support
- [x] Private messaging
- [x] Group messaging
- [x] Message persistence (database)
- [x] Graphical user interface
- [x] Connection management
- [x] Wired connectivity (LAN)
- [x] Wireless connectivity (Wi-Fi)
- [x] Message encryption
- [x] Online users list
- [x] Chat history
- [x] Cross-platform compatibility
- [x] Error handling
- [x] Logging system

## 🎓 Educational Purpose

This project is developed as part of a **Computer Networks course** to demonstrate:
- Socket programming concepts
- Client-server architecture
- Network protocols
- Multithreading
- Database integration
- GUI development
- Security basics

## 📞 Support & Contributing

### Found a Bug?
1. Check if it's already reported in Issues
2. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)

### Want to Contribute?
1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit (`git commit -m 'Add some AmazingFeature'`)
5. Push to branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 📝 License

This project is for educational purposes as part of a Computer Networks course.

## 🙏 Acknowledgments

- **Course:** Computer Networks
- **Institution:** [Your University/Institution]
- **Team Size:** 5 members
- **Development Period:** [Your timeframe]

## 📧 Contact

For questions or support, please contact the team members or create an issue in the repository.

---

**Made with ❤️ for Computer Networks Project**

---

## Quick Commands Reference
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python -m server.server

# Start client GUI
python -m client.gui

# Run tests
pytest tests/

# View logs
cat logs/chat_app_*.log
```

---

**Note:** This application is designed for local network use only and does not require internet connectivity.
