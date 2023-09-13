import re
import bcrypt

def hash_pass(password):
    salt =bcrypt.gensalt()
    hash_pass = bcrypt.hashpw(password.encode(),salt)
    
    return hash_pass.decode()

def is_pass_match(enter_pass,stored_hash):
    stored_hash_bytes =stored_hash.encode()
    return bcrypt.checkpw(enter_pass.encode(),stored_hash_bytes)
    
def is_strong_password(password):
    min_length = 8
    require_uppercase = True
    require_lowercase = True
    require_digit = True
    require_special_char = True

    if len(password) < min_length:
        return False

    if require_uppercase and not any(char.isupper() for char in password):
        return False

    if require_lowercase and not any(char.islower() for char in password):
        return False

    if require_digit and not any(char.isdigit() for char in password):
        return False

    if require_special_char and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True
