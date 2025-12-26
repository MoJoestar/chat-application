"""
Encryption and Security Functions
This file handles message encryption and decryption for secure communication.
"""

from cryptography.fernet import Fernet
import base64
import os
from shared.utils import log_info, log_error, log_warning


class Encryption:
    """
    Handles encryption and decryption of messages using Fernet (symmetric encryption).
    Fernet uses AES 128 bit encryption in CBC mode with PKCS7 padding.
    """
    
    def __init__(self, key=None):
        """
        Initialize encryption with a key.
        
        Args:
            key (bytes): Encryption key. If None, a new key is generated.
        """
        if key is None:
            self.key = Encryption.generate_key()
            log_warning("New encryption key generated. Share this key between client and server.")
        else:
            self.key = key
        
        self.cipher = Fernet(self.key)
        log_info("Encryption initialized")
    
    @staticmethod
    def generate_key():
        """
        Generate a new encryption key.
        
        Returns:
            bytes: New encryption key
        """
        key = Fernet.generate_key()
        log_info("New encryption key generated")
        return key
    
    @staticmethod
    def save_key_to_file(key, filename="encryption.key"):
        """
        Save encryption key to a file.
        
        Args:
            key (bytes): Encryption key to save
            filename (str): Filename to save to
        
        Returns:
            bool: True if successful
        """
        try:
            with open(filename, 'wb') as key_file:
                key_file.write(key)
            log_info(f"Encryption key saved to {filename}")
            return True
        except Exception as e:
            log_error(f"Error saving key to file: {e}")
            return False
    
    @staticmethod
    def load_key_from_file(filename="encryption.key"):
        """
        Load encryption key from a file.
        
        Args:
            filename (str): Filename to load from
        
        Returns:
            bytes: Encryption key or None if failed
        """
        try:
            if not os.path.exists(filename):
                log_warning(f"Key file {filename} not found")
                return None
            
            with open(filename, 'rb') as key_file:
                key = key_file.read()
            log_info(f"Encryption key loaded from {filename}")
            return key
        except Exception as e:
            log_error(f"Error loading key from file: {e}")
            return None
    
    def encrypt(self, message):
        """
        Encrypt a message.
        
        Args:
            message (str or bytes): Message to encrypt
        
        Returns:
            bytes: Encrypted message
        """
        try:
            # Convert string to bytes if needed
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            encrypted = self.cipher.encrypt(message)
            return encrypted
        except Exception as e:
            log_error(f"Error encrypting message: {e}")
            return None
    
    def decrypt(self, encrypted_message):
        """
        Decrypt a message.
        
        Args:
            encrypted_message (bytes): Encrypted message
        
        Returns:
            str: Decrypted message
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_message)
            return decrypted.decode('utf-8')
        except Exception as e:
            log_error(f"Error decrypting message: {e}")
            return None
    
    def encrypt_to_string(self, message):
        """
        Encrypt message and return as base64 string for easy transmission.
        
        Args:
            message (str): Message to encrypt
        
        Returns:
            str: Base64 encoded encrypted message
        """
        try:
            encrypted = self.encrypt(message)
            if encrypted:
                return base64.b64encode(encrypted).decode('utf-8')
            return None
        except Exception as e:
            log_error(f"Error encrypting to string: {e}")
            return None
    
    def decrypt_from_string(self, encrypted_string):
        """
        Decrypt message from base64 string.
        
        Args:
            encrypted_string (str): Base64 encoded encrypted message
        
        Returns:
            str: Decrypted message
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_string.encode('utf-8'))
            return self.decrypt(encrypted_bytes)
        except Exception as e:
            log_error(f"Error decrypting from string: {e}")
            return None
    
    def get_key(self):
        """
        Get the encrypt
