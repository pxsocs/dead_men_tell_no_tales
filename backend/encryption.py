from cryptography.fernet import Fernet
import base64, hashlib


def encrypt_file(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        file_data = file.read()
    # encrypt data
    encrypted_data = f.encrypt(file_data)
    # write the encrypted file
    with open(filename, "wb") as file:
        file.write(encrypted_data)


def decrypt_file(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    print(decrypted_data)


def encrypt_string(s, key):
    f = Fernet(key)
    # encrypt data
    encrypted_data = f.encrypt(s.encode())
    return encrypted_data


def decrypt_string(encrypted_data, key):
    f = Fernet(key)
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    return (decrypted_data)


# Receives a password in string format
# and translates to key64
def string_to_key64(s):
    s = s.encode()
    key = hashlib.md5(s).hexdigest()
    key64 = base64.urlsafe_b64encode(key.encode("utf-8"))
    return key64
