"""
PERSON 3: Message Handler

This file processes and formats messages on the client side.
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.protocol import Protocol, MessageType
from shared.utils import log_info, log_error, validate_message


class MessageHandler:
    """
    Handles message processing and formatting for the client.
    """
    
    def __init__(self):
        """
        Initialize message handler.
        """
        log_info("Message handler initialized")
    
    def process_incoming_message(self, message_dict):
        """
        Process a message received from the server.
        
        Args:
            message_dict (dict): Parsed message dictionary
        
        Returns:
            dict: Processed message with display format
        """
        try:
            msg_type = message_dict.get('type')
            
            processed = {
                'type': msg_type,
                'original': message_dict,
                'display_text': '',
                'notification': False
            }
            
            if msg_type == MessageType.GROUP:
                # Group message
                sender = message_dict.get('sender', 'Unknown')
                content = message_dict.get('content', '')
                timestamp = message_dict.get('timestamp', '')
                
                processed['display_text'] = self.format_group_message(sender, content, timestamp)
                processed['sender'] = sender
                processed['content'] = content
                processed['timestamp'] = timestamp
            
            elif msg_type == MessageType.PRIVATE:
                # Private message
                sender = message_dict.get('sender', 'Unknown')
                content = message_dict.get('content', '')
                timestamp = message_dict.get('timestamp', '')
                
                processed['display_text'] = self.format_private_message(sender, content, timestamp)
                processed['sender'] = sender
                processed['content'] = content
                processed['timestamp'] = timestamp
                processed['is_private'] = True
            
            elif msg_type == MessageType.USER_JOINED:
                # User joined notification
                content = message_dict.get('content', '')
                processed['display_text'] = f"*** {content} ***"
                processed['notification'] = True
            
            elif msg_type == MessageType.USER_LEFT:
                # User left notification
                content = message_dict.get('content', '')
                processed['display_text'] = f"*** {content} ***"
                processed['notification'] = True
            
            elif msg_type == MessageType.USERS_LIST:
                # Online users list
                data = message_dict.get('data', {})
                users = data.get('users', [])
                processed['users'] = users
                processed['display_text'] = f"Online users: {', '.join(users)}"
            
            elif msg_type == MessageType.HISTORY:
                # Chat history
                data = message_dict.get('data', {})
                messages = data.get('messages', [])
                processed['messages'] = messages
                processed['display_text'] = f"--- Chat History ({len(messages)} messages) ---"
            
            elif msg_type == MessageType.STATUS:
                # Status message
                content = message_dict.get('content', '')
                processed['display_text'] = f"[STATUS] {content}"
                processed['notification'] = True
            
            elif msg_type == MessageType.ERROR:
                # Error message
                content = message_dict.get('content', '')
                processed['display_text'] = f"[ERROR] {content}"
                processed['notification'] = True
                processed['is_error'] = True
            
            elif msg_type == MessageType.AUTH_SUCCESS:
                # Authentication successful
                content = message_dict.get('content', '')
                processed['display_text'] = f"✓ {content}"
                processed['notification'] = True
            
            elif msg_type == MessageType.AUTH_FAILED:
                # Authentication failed
                content = message_dict.get('content', '')
                processed['display_text'] = f"✗ Authentication failed: {content}"
                processed['notification'] = True
                processed['is_error'] = True
            
            elif msg_type == MessageType.DISCONNECT:
                # Server disconnect
                content = message_dict.get('content', 'Server disconnected')
                processed['display_text'] = f"*** {content} ***"
                processed['notification'] = True
            
            else:
                # Unknown message type
                processed['display_text'] = f"[Unknown message type: {msg_type}]"
            
            return processed
            
        except Exception as e:
            log_error(f"Error processing incoming message: {e}")
            return {
                'type': 'error',
                'display_text': '[Error processing message]',
                'notification': True,
                'is_error': True
            }
    
    def format_group_message(self, sender, content, timestamp):
        """
        Format a group message for display.
        
        Args:
            sender (str): Message sender
            content (str): Message content
            timestamp (str): Message timestamp
        
        Returns:
            str: Formatted message
        """
        time_str = self.extract_time_from_timestamp(timestamp)
        return f"[{time_str}] {sender}: {content}"
    
    def format_private_message(self, sender, content, timestamp):
        """
        Format a private message for display.
        
        Args:
            sender (str): Message sender
            content (str): Message content
            timestamp (str): Message timestamp
        
        Returns:
            str: Formatted message
        """
        time_str = self.extract_time_from_timestamp(timestamp)
        return f"[{time_str}] {sender} (private): {content}"
    
    def format_sent_message(self, content, receiver=None, timestamp=None):
        """
        Format a message that was sent by the current user.
        
        Args:
            content (str): Message content
            receiver (str): Receiver username (for private)
            timestamp (str): Message timestamp
        
        Returns:
            str: Formatted message
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        time_str = self.extract_time_from_timestamp(timestamp)
        
        if receiver:
            return f"[{time_str}] You -> {receiver}: {content}"
        else:
            return f"[{time_str}] You: {content}"
    
    def extract_time_from_timestamp(self, timestamp):
        """
        Extract time (HH:MM:SS) from full timestamp.
        
        Args:
            timestamp (str): Full timestamp string
        
        Returns:
            str: Time only
        """
        try:
            if not timestamp:
                return datetime.now().strftime("%H:%M:%S")
            
            # Try to parse timestamp
            if ' ' in timestamp:
                # Format: "YYYY-MM-DD HH:MM:SS"
                time_part = timestamp.split(' ')[1]
                return time_part
            else:
                # Assume it's already just time
                return timestamp
        except:
            return datetime.now().strftime("%H:%M:%S")
    
    def validate_outgoing_message(self, message_text):
        """
        Validate message before sending.
        
        Args:
            message_text (str): Message to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        return validate_message(message_text)
    
    def parse_history(self, messages):
        """
        Parse chat history messages for display.
        
        Args:
            messages (list): List of message dictionaries
        
        Returns:
            list: List of formatted message strings
        """
        formatted_messages = []
        
        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            formatted = self.format_group_message(sender, content, timestamp)
            formatted_messages.append(formatted)
        
        return formatted_messages
    
    def create_notification_text(self, notification_type, data):
        """
        Create a notification message.
        
        Args:
            notification_type (str): Type of notification
            data: Notification data
        
        Returns:
            str: Formatted notification
        """
        notifications = {
            'connected': f"*** Connected to server ***",
            'disconnected': f"*** Disconnected from server ***",
            'connection_lost': f"*** Connection lost. Trying to reconnect... ***",
            'reconnected': f"*** Reconnected to server ***",
            'user_joined': f"*** {data} joined the chat ***",
            'user_left': f"*** {data} left the chat ***",
        }
        
        return notifications.get(notification_type, f"*** {notification_type} ***")
    
    def extract_mentions(self, message_text):
        """
        Extract @mentions from message text (optional feature).
        
        Args:
            message_text (str): Message text
        
        Returns:
            list: List of mentioned usernames
        """
        import re
        
        # Find all @username patterns
        mentions = re.findall(r'@(\w+)', message_text)
        return mentions
    
    def highlight_mentions(self, message_text, current_username):
        """
        Highlight mentions in message text (optional feature).
        
        Args:
            message_text (str): Message text
            current_username (str): Current user's username
        
        Returns:
            tuple: (highlighted_text, is_mentioned)
        """
        mentions = self.extract_mentions(message_text)
        is_mentioned = current_username in mentions
        
        # You can add special formatting here in the GUI
        return message_text, is_mentioned
    
    def format_message_for_history(self, message_dict):
        """
        Format message dictionary for storage/display in history.
        
        Args:
            message_dict (dict): Message dictionary
        
        Returns:
            dict: Formatted message for history
        """
        return {
            'sender': message_dict.get('sender', 'Unknown'),
            'content': message_dict.get('content', ''),
            'timestamp': message_dict.get('timestamp', ''),
            'type': message_dict.get('type', 'unknown'),
            'receiver': message_dict.get('receiver', None)
        }


# ==================== TEST CODE ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Message Handler")
    print("=" * 60)
    
    handler = MessageHandler()
    
    # Test group message
    print("\n1. Testing group message formatting...")
    group_msg = Protocol.create_group_message("Alice", "Hello everyone!")
    processed = handler.process_incoming_message(group_msg)
    print(f"Display: {processed['display_text']}")
    
    # Test private message
    print("\n2. Testing private message formatting...")
    private_msg = Protocol.create_private_message("Bob", "Alice", "Hi there!")
    processed = handler.process_incoming_message(private_msg)
    print(f"Display: {processed['display_text']}")
    
    # Test validation
    print("\n3. Testing message validation...")
    valid, error = handler.validate_outgoing_message("Hello!")
    print(f"Valid: {valid}, Error: {error}")
    
    valid, error = handler.validate_outgoing_message("")
    print(f"Empty message valid: {valid}, Error: {error}")
    
    # Test mentions
    print("\n4. Testing mention extraction...")
    text = "Hey @Alice and @Bob, check this out!"
    mentions = handler.extract_mentions(text)
    print(f"Mentions found: {mentions}")
    
    # Test history parsing
    print("\n5. Testing history parsing...")
    history_data = [
        {'sender': 'Alice', 'content': 'Hello', 'timestamp': '2024-12-26 10:00:00'},
        {'sender': 'Bob', 'content': 'Hi Alice!', 'timestamp': '2024-12-26 10:01:00'}
    ]
    formatted_history = handler.parse_history(history_data)
    for msg in formatted_history:
        print(f"  {msg}")
    
    print("\n" + "=" * 60)
    print("Message Handler test complete!")
    print("=" * 60)
