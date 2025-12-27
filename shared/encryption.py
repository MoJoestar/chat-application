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
        Get the encryption key.
        
        Returns:
            bytes: The encryption key
        """
        return self.key
    
    def get_key_string(self):
        """
        Get the encryption key as a base64 string.
        
        Returns:
            str: Base64 encoded key
        """
        return base64.b64encode(self.key).decode('utf-8')


# ==================== GLOBAL ENCRYPTION INSTANCE ====================

# Create a default encryption key file if it doesn't exist
KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'encryption.key')

# Try to load existing key, or generate new one
if os.path.exists(KEY_FILE):
    SHARED_KEY = Encryption.load_key_from_file(KEY_FILE)
    if SHARED_KEY is None:
        SHARED_KEY = Encryption.generate_key()
        Encryption.save_key_to_file(SHARED_KEY, KEY_FILE)
else:
    SHARED_KEY = Encryption.generate_key()
    Encryption.save_key_to_file(SHARED_KEY, KEY_FILE)

# Create global encryption instance
encryptor = Encryption(SHARED_KEY)

log_info(f"Global encryption initialized with shared key from {KEY_FILE}")


# ==================== HELPER FUNCTIONS ====================

def encrypt_message(message):
    """
    Encrypt a message using the global encryptor.
    
    Args:
        message (str): Message to encrypt
    
    Returns:
        str: Encrypted message as base64 string
    """
    return encryptor.encrypt_to_string(message)


def decrypt_message(encrypted_message):
    """
    Decrypt a message using the global encryptor.
    
    Args:
        encrypted_message (str): Encrypted message as base64 string
    
    Returns:
        str: Decrypted message
    """
    return encryptor.decrypt_from_string(encrypted_message)


# ==================== TEST CODE ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Encryption Module")
    print("=" * 60)
    
    # Test encryption
    print("\n1. Testing encryption...")
    original = "Hello, this is a secret message!"
    print(f"Original: {original}")
    
    encrypted = encrypt_message(original)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_message(encrypted)
    print(f"Decrypted: {decrypted}")
    
    if original == decrypted:
        print("✓ Encryption/Decryption successful!")
    else:
        print("✗ Encryption/Decryption failed!")
    
    # Test key persistence
    print("\n2. Testing key persistence...")
    key1 = encryptor.get_key_string()
    print(f"Current key: {key1[:20]}...")
    
    # Test with different instance
    print("\n3. Testing with new instance...")
    enc2 = Encryption(SHARED_KEY)
    encrypted2 = enc2.encrypt_to_string("Another message")
    decrypted2 = encryptor.decrypt_from_string(encrypted2)
    print(f"Cross-instance decryption: {decrypted2}")
    
    if decrypted2 == "Another message":
        print("✓ Key sharing works correctly!")
    else:
        print("✗ Key sharing failed!")
    
    print("\n" + "=" * 60)
    print("Encryption test complete!")
    print("=" * 60)
