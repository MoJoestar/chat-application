"""
PERSON 2: Database & Message Persistence

This file handles all database operations for storing and retrieving messages.
"""

import sqlite3
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import DB_PATH, log_info, log_error


class Database:
    """
    Handles all database operations for the chat application.
    """
    
    def __init__(self, db_path=DB_PATH):
        """
        Initialize database connection.
        """
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        self.connection = None
        self.create_tables()
        log_info(f"Database initialized at {db_path}")
    
    def connect(self):
        """
        Create database connection.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            return conn
        except Exception as e:
            log_error(f"Error connecting to database: {e}")
            return None
    
    def create_tables(self):
        """
        Create necessary database tables if they don't exist.
        """
        try:
            conn = self.connect()
            if conn is None:
                log_error("Cannot create tables: no database connection")
                return
            
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_username TEXT NOT NULL,
                    receiver_username TEXT,
                    message_text TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_group_message BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            log_info("Database tables created successfully")
            
        except Exception as e:
            log_error(f"Error creating tables: {e}")
    
    def save_message(self, sender, receiver, message_text, is_group=False):
        """
        Save a message to the database.
        
        Args:
            sender (str): Username of sender
            receiver (str): Username of receiver (None for group messages)
            message_text (str): The message content
            is_group (bool): Whether this is a group message
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.connect()
            if conn is None:
                return False
            
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (sender_username, receiver_username, message_text, is_group_message)
                VALUES (?, ?, ?, ?)
            ''', (sender, receiver, message_text, 1 if is_group else 0))
            
            conn.commit()
            conn.close()
            
            log_info(f"Message saved: {sender} -> {receiver if receiver else 'GROUP'}")
            return True
            
        except Exception as e:
            log_error(f"Error saving message: {e}")
            return False
    
    def get_group_history(self, limit=50):
        """
        Retrieve group chat history.
        
        Args:
            limit (int): Maximum number of messages to retrieve
        
        Returns:
            list: List of message dictionaries
        """
        try:
            conn = self.connect()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT sender_username, message_text, timestamp
                FROM messages
                WHERE is_group_message = 1
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in rows:
                messages.append({
                    'sender': row['sender_username'],
                    'content': row['message_text'],
                    'timestamp': row['timestamp']
                })
            
            log_info(f"Retrieved {len(messages)} group messages")
            return messages
            
        except Exception as e:
            log_error(f"Error retrieving group history: {e}")
            return []
    
    def get_private_history(self, user1, user2, limit=50):
        """
        Retrieve private chat history between two users.
        
        Args:
            user1 (str): First username
            user2 (str): Second username
            limit (int): Maximum number of messages to retrieve
        
        Returns:
            list: List of message dictionaries
        """
        try:
            conn = self.connect()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT sender_username, receiver_username, message_text, timestamp
                FROM messages
                WHERE is_group_message = 0
                AND (
                    (sender_username = ? AND receiver_username = ?)
                    OR
                    (sender_username = ? AND receiver_username = ?)
                )
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (user1, user2, user2, user1, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in rows:
                messages.append({
                    'sender': row['sender_username'],
                    'receiver': row['receiver_username'],
                    'content': row['message_text'],
                    'timestamp': row['timestamp']
                })
            
            log_info(f"Retrieved {len(messages)} private messages between {user1} and {user2}")
            return messages
            
        except Exception as e:
            log_error(f"Error retrieving private history: {e}")
            return []
    
    def add_user(self, username):
        """
        Add a new user to the database.
        
        Args:
            username (str): Username to add
        
        Returns:
            bool: True if successful
        """
        try:
            conn = self.connect()
            if conn is None:
                return False
            
            cursor = conn.cursor()
            
            # Insert or update last_seen if user already exists
            cursor.execute('''
                INSERT INTO users (username, first_seen, last_seen)
                VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(username) 
                DO UPDATE SET last_seen = CURRENT_TIMESTAMP
            ''', (username,))
            
            conn.commit()
            conn.close()
            
            log_info(f"User added/updated: {username}")
            return True
            
        except Exception as e:
            log_error(f"Error adding user: {e}")
            return False
    
    def update_user_last_seen(self, username):
        """
        Update the last_seen timestamp for a user.
        
        Args:
            username (str): Username to update
        
        Returns:
            bool: True if successful
        """
        try:
            conn = self.connect()
            if conn is None:
                return False
            
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users
                SET last_seen = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (username,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            log_error(f"Error updating last_seen: {e}")
            return False
    
    def get_all_users(self):
        """
        Get list of all users who have ever connected.
        
        Returns:
            list: List of usernames
        """
        try:
            conn = self.connect()
            if conn is None:
                return []
            
            cursor = conn.cursor()
            
            cursor.execute('SELECT username FROM users ORDER BY username')
            rows = cursor.fetchall()
            conn.close()
            
            usernames = [row['username'] for row in rows]
            return usernames
            
        except Exception as e:
            log_error(f"Error getting all users: {e}")
            return []
    
    def get_message_count(self):
        """
        Get total number of messages in database.
        
        Returns:
            int: Total message count
        """
        try:
            conn = self.connect()
            if conn is None:
                return 0
            
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM messages')
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
            
        except Exception as e:
            log_error(f"Error getting message count: {e}")
            return 0
    
    def delete_old_messages(self, days=30):
        """
        Delete messages older than specified days.
        
        Args:
            days (int): Number of days to keep
        
        Returns:
            int: Number of messages deleted
        """
        try:
            conn = self.connect()
            if conn is None:
                return 0
            
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM messages
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            log_info(f"Deleted {deleted_count} old messages (older than {days} days)")
            return deleted_count
            
        except Exception as e:
            log_error(f"Error deleting old messages: {e}")
            return 0
    
    def clear_all_messages(self):
        """
        Clear all messages from database (use with caution!).
        
        Returns:
            bool: True if successful
        """
        try:
            conn = self.connect()
            if conn is None:
                return False
            
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages')
            conn.commit()
            conn.close()
            
            log_info("All messages cleared from database")
            return True
            
        except Exception as e:
            log_error(f"Error clearing messages: {e}")
            return False
    
    def get_database_stats(self):
        """
        Get database statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        try:
            conn = self.connect()
            if conn is None:
                return {}
            
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute('SELECT COUNT(*) as count FROM users')
            user_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM messages')
            message_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM messages WHERE is_group_message = 1')
            group_message_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM messages WHERE is_group_message = 0')
            private_message_count = cursor.fetchone()['count']
            
            conn.close()
            
            stats = {
                'total_users': user_count,
                'total_messages': message_count,
                'group_messages': group_message_count,
                'private_messages': private_message_count
            }
            
            return stats
            
        except Exception as e:
            log_error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """
        Close database connection.
        """
        if self.connection:
            self.connection.close()
            log_info("Database connection closed")


# ==================== TEST CODE ====================

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Database Module")
    print("=" * 50)
    
    # Create database instance
    db = Database()
    
    # Test adding users
    print("\n1. Adding users...")
    db.add_user("Alice")
    db.add_user("Bob")
    db.add_user("Charlie")
    
    # Test saving messages
    print("\n2. Saving messages...")
    db.save_message("Alice", None, "Hello everyone!", is_group=True)
    db.save_message("Bob", None, "Hi Alice!", is_group=True)
    db.save_message("Alice", "Bob", "Hey Bob, how are you?", is_group=False)
    db.save_message("Bob", "Alice", "I'm good, thanks!", is_group=False)
    
    # Test retrieving group history
    print("\n3. Retrieving group history...")
    group_msgs = db.get_group_history()
    for msg in group_msgs:
        print(f"  [{msg['timestamp']}] {msg['sender']}: {msg['content']}")
    
    # Test retrieving private history
    print("\n4. Retrieving private history between Alice and Bob...")
    private_msgs = db.get_private_history("Alice", "Bob")
    for msg in private_msgs:
        print(f"  [{msg['timestamp']}] {msg['sender']} -> {msg['receiver']}: {msg['content']}")
    
    # Test getting all users
    print("\n5. All users in database...")
    users = db.get_all_users()
    print(f"  Users: {users}")
    
    # Test database stats
    print("\n6. Database statistics...")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("Database test complete!")
    print("=" * 50)
