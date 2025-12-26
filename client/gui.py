"""
PERSON 4: Graphical User Interface (GUI)

This file creates the user-friendly interface using tkinter.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.client import ChatClient
from client.message_handler import MessageHandler
from shared.protocol import MessageType
from shared.utils import log_info, log_error


class ChatGUI:
    """
    Main GUI class for the chat application.
    """
    
    def __init__(self):
        """
        Initialize the GUI.
        """
        self.client = ChatClient()
        self.message_handler = MessageHandler()
        
        # Set callback for incoming messages
        self.client.set_message_callback(self.handle_incoming_message)
        
        self.root = None
        self.connected = False
        self.current_chat_mode = "group"  # "group" or "private"
        self.selected_user = None
        
        log_info("GUI initialized")
    
    def start(self):
        """
        Start the GUI application.
        """
        self.show_login_window()
    
    # ==================== LOGIN WINDOW ====================
    
    def show_login_window(self):
        """
        Display the login window.
        """
        self.root = tk.Tk()
        self.root.title("Chat Application - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window(self.root, 400, 300)
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Multi-Client Chat Application",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root,
            text="Computer Networks Project",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        subtitle_label.pack()
        
        # Username frame
        username_frame = tk.Frame(self.root)
        username_frame.pack(pady=20)
        
        tk.Label(username_frame, text="Username:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12), width=20)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        self.username_entry.focus()
        
        # Server settings frame
        server_frame = tk.Frame(self.root)
        server_frame.pack(pady=10)
        
        tk.Label(server_frame, text="Server:", font=("Arial", 10)).grid(row=0, column=0, padx=5, sticky=tk.E)
        
        self.server_entry = tk.Entry(server_frame, font=("Arial", 10), width=15)
        self.server_entry.insert(0, "localhost")
        self.server_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(server_frame, text="Port:", font=("Arial", 10)).grid(row=0, column=2, padx=5, sticky=tk.E)
        
        self.port_entry = tk.Entry(server_frame, font=("Arial", 10), width=8)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        # Connect button
        self.connect_button = tk.Button(
            self.root,
            text="Connect",
            command=self.connect_to_server,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.connect_button.pack(pady=20)
        
        # Status label
        self.login_status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 10),
            fg="#e74c3c"
        )
        self.login_status_label.pack()
        
        # Bind Enter key to connect
        self.username_entry.bind('<Return>', lambda e: self.connect_to_server())
        self.server_entry.bind('<Return>', lambda e: self.connect_to_server())
        self.port_entry.bind('<Return>', lambda e: self.connect_to_server())
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def connect_to_server(self):
        """
        Handle connect button click.
        """
        username = self.username_entry.get().strip()
        server = self.server_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not username:
            self.login_status_label.config(text="Please enter a username")
            return
        
        if not server:
            server = "localhost"
        
        try:
            port = int(port)
        except ValueError:
            self.login_status_label.config(text="Invalid port number")
            return
        
        # Disable button while connecting
        self.connect_button.config(state=tk.DISABLED, text="Connecting...")
        self.login_status_label.config(text="Connecting to server...", fg="#3498db")
        self.root.update()
        
        # Attempt connection
        success, message = self.client.connect(username, server, port)
        
        if success:
            self.connected = True
            self.login_status_label.config(text="Connected!", fg="#27ae60")
            self.root.after(500, self.show_chat_window)
        else:
            self.connect_button.config(state=tk.NORMAL, text="Connect")
            self.login_status_label.config(text=f"Error: {message}", fg="#e74c3c")
    
    # ==================== CHAT WINDOW ====================
    
    def show_chat_window(self):
        """
        Display the main chat window.
        """
        self.root.destroy()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"Chat - {self.client.get_username()}")
        self.root.geometry("900x600")
        
        # Center window
        self.center_window(self.root, 900, 600)
        
        # Create main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar (users list)
        self.create_sidebar(main_container)
        
        # Right side (chat area)
        self.create_chat_area(main_container)
        
        # Status bar at bottom
        self.create_status_bar()
        
        # Request initial data
        self.client.request_online_users()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def create_sidebar(self, parent):
        """
        Create the sidebar with online users list.
        """
        sidebar = tk.Frame(parent, bg="#34495e", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            sidebar,
            text="Online Users",
            font=("Arial", 14, "bold"),
            bg="#34495e",
            fg="white"
        )
        title_label.pack(pady=10)
        
        # Group chat button
        self.group_chat_button = tk.Button(
            sidebar,
            text="📢 Group Chat",
            command=self.switch_to_group_chat,
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.group_chat_button.pack(fill=tk.X, padx=10, pady=5)
        
        # Users list label
        tk.Label(
            sidebar,
            text="Private Chat:",
            font=("Arial", 10),
            bg="#34495e",
            fg="#bdc3c7"
        ).pack(pady=(10, 5))
        
        # Users listbox with scrollbar
        users_frame = tk.Frame(sidebar, bg="#34495e")
        users_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(users_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.users_listbox = tk.Listbox(
            users_frame,
            font=("Arial", 11),
            bg="#2c3e50",
            fg="white",
            selectbackground="#3498db",
            yscrollcommand=scrollbar.set,
            cursor="hand2"
        )
        self.users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.users_listbox.yview)
        
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # Refresh button
        refresh_button = tk.Button(
            sidebar,
            text="🔄 Refresh",
            command=self.refresh_users,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            cursor="hand2"
        )
        refresh_button.pack(fill=tk.X, padx=10, pady=10)
    
    def create_chat_area(self, parent):
        """
        Create the main chat area.
        """
        chat_container = tk.Frame(parent)
        chat_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(chat_container, bg="#3498db", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        self.chat_title_label = tk.Label(
            header,
            text="Group Chat",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        )
        self.chat_title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Chat display area
        chat_frame = tk.Frame(chat_container)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=("Consolas", 11),
            bg="#ecf0f1",
            fg="#2c3e50",
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        self.chat_display.tag_config("notification", foreground="#7f8c8d", font=("Arial", 10, "italic"))
        self.chat_display.tag_config("error", foreground="#e74c3c", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("private", foreground="#9b59b6", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("own_message", foreground="#27ae60", font=("Consolas", 11))
        
        # Message input area
        input_frame = tk.Frame(chat_container, bg="#bdc3c7")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.message_entry = scrolledtext.ScrolledText(
            input_frame,
            font=("Arial", 11),
            height=3,
            wrap=tk.WORD
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.message_entry.focus()
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send\n(Ctrl+Enter)",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            width=12
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Ctrl+Enter to send
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
    
    def create_status_bar(self):
        """
        Create status bar at bottom.
        """
        status_bar = tk.Frame(self.root, bg="#34495e", height=25)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            status_bar,
            text="● Connected",
            font=("Arial", 9),
            bg="#34495e",
            fg="#27ae60"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.user_count_label = tk.Label(
            status_bar,
            text="Users: 0",
            font=("Arial", 9),
            bg="#34495e",
            fg="white"
        )
        self.user_count_label.pack(side=tk.RIGHT, padx=10)
    
    # ==================== MESSAGE HANDLING ====================
    
    def send_message(self):
        """
        Send a message to the server.
        """
        message_text = self.message_entry.get("1.0", tk.END).strip()
        
        if not message_text:
            return
        
        # Validate message
        is_valid, error = self.message_handler.validate_outgoing_message(message_text)
        if not is_valid:
            messagebox.showerror("Invalid Message", error)
            return
        
        # Send message
        if self.current_chat_mode == "group":
            success, msg = self.client.send_message(message_text, is_group=True)
        else:
            if not self.selected_user:
                messagebox.showwarning("No Recipient", "Please select a user for private chat")
                return
            success, msg = self.client.send_message(message_text, receiver=self.selected_user, is_group=False)
        
        if success:
            # Display sent message
            formatted = self.message_handler.format_sent_message(
                message_text,
                receiver=self.selected_user if self.current_chat_mode == "private" else None
            )
            self.display_message(formatted, tag="own_message")
            
            # Clear input
            self.message_entry.delete("1.0", tk.END)
        else:
            messagebox.showerror("Send Error", msg)
    
    def handle_incoming_message(self, message_dict):
        """
        Handle incoming message from server (callback).
        """
        try:
            # Process message
            processed = self.message_handler.process_incoming_message(message_dict)
            
            msg_type = message_dict.get('type')
            
            if msg_type == MessageType.GROUP:
                # Group message
                self.display_message(processed['display_text'])
            
            elif msg_type == MessageType.PRIVATE:
                # Private message
                self.display_message(processed['display_text'], tag="private")
            
            elif msg_type == MessageType.USER_JOINED or msg_type == MessageType.USER_LEFT:
                # User notification
                self.display_message(processed['display_text'], tag="notification")
                self.client.request_online_users()
            
            elif msg_type == MessageType.USERS_LIST:
                # Update users list
                users = processed.get('users', [])
                self.update_users_list(users)
            
            elif msg_type == MessageType.HISTORY:
                # Chat history
                messages = processed.get('messages', [])
                self.display_history(messages)
            
            elif msg_type == MessageType.STATUS:
                # Status message
                self.display_message(processed['display_text'], tag="notification")
            
            elif msg_type == MessageType.ERROR:
                # Error message
                self.display_message(processed['display_text'], tag="error")
            
            elif msg_type == MessageType.AUTH_SUCCESS:
                # Auth success
                self.display_message(processed['display_text'], tag="notification")
            
            elif msg_type == MessageType.DISCONNECT:
                # Server disconnect
                self.display_message(processed['display_text'], tag="error")
                self.connected = False
                self.update_status("Disconnected", "#e74c3c")
            
            else:
                # Unknown type
                if processed.get('notification'):
                    self.display_message(processed['display_text'], tag="notification")
        
        except Exception as e:
            log_error(f"Error handling incoming message: {e}")
    
    def display_message(self, message_text, tag=None):
        """
        Display a message in the chat area.
        """
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message_text + "\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_history(self, messages):
        """
        Display chat history.
        """
        if not messages:
            return
        
        self.display_message("=" * 50, tag="notification")
        self.display_message("Chat History", tag="notification")
        self.display_message("=" * 50, tag="notification")
        
        formatted_messages = self.message_handler.parse_history(messages)
        for msg in formatted_messages:
            self.display_message(msg)
        
        self.display_message("=" * 50, tag="notification")
    
    # ==================== USER LIST MANAGEMENT ====================
    
    def update_users_list(self, users):
        """
        Update the online users list.
        """
        # Remove current user from list
        current_user = self.client.get_username()
        users = [u for u in users if u != current_user]
        
        # Update listbox
        self.users_listbox.delete(0, tk.END)
        for user in sorted(users):
            self.users_listbox.insert(tk.END, f"💬 {user}")
        
        # Update count
        self.user_count_label.config(text=f"Users: {len(users) + 1}")  # +1 for self
    
    def refresh_users(self):
        """
        Refresh online users list.
        """
        self.client.request_online_users()
        self.display_message("Refreshing users list...", tag="notification")
    
    def on_user_select(self, event):
        """
        Handle user selection for private chat.
        """
        selection = self.users_listbox.curselection()
        if selection:
            index = selection[0]
            user_text = self.users_listbox.get(index)
            # Remove emoji
            self.selected_user = user_text.replace("💬 ", "")
            self.switch_to_private_chat(self.selected_user)
    
    def switch_to_group_chat(self):
        """
        Switch to group chat mode.
        """
        self.current_chat_mode = "group"
        self.selected_user = None
        self.chat_title_label.config(text="Group Chat")
        self.group_chat_button.config(relief=tk.SUNKEN, bg="#27ae60")
        self.display_message("\n*** Switched to Group Chat ***\n", tag="notification")
    
    def switch_to_private_chat(self, username):
        """
        Switch to private chat mode with specific user.
        """
        self.current_chat_mode = "private"
        self.selected_user = username
        self.chat_title_label.config(text=f"Private Chat with {username}")
        self.group_chat_button.config(relief=tk.RAISED, bg="#3498db")
        self.display_message(f"\n*** Private Chat with {username} ***\n", tag="notification")
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def update_status(self, status_text, color):
        """
        Update status bar.
        """
        self.status_label.config(text=f"● {status_text}", fg=color)
    
    def center_window(self, window, width, height):
        """
        Center window on screen.
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        """
        Handle window close event.
        """
        if self.connected:
            if messagebox.askokcancel("Quit", "Do you want to disconnect and quit?"):
                self.client.disconnect()
                self.root.destroy()
        else:
            self.root.destroy()


# ==================== MAIN ====================

def main():
    """
    Main function to start the GUI.
    """
    app = ChatGUI()
    app.start()


if __name__ == "__main__":
    main()
