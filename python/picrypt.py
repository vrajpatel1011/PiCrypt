import sys
import os
import random
from PIL import Image
import numpy as np
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import zlib
from getpass import getpass

def encrypt_data(data, public_key):
    # Generate a random session key
    session_key = os.urandom(32)  # 32 bytes for 256-bit key
    
    # Derive a symmetric key from the session key
    salt = os.urandom(16)  # 16 bytes for 128-bit salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100,  # Increased iterations for added security
        backend=default_backend()
    )
    key = kdf.derive(session_key)
    
    # Encrypt the data with AES
    iv = os.urandom(16)  # 16 bytes for 128-bit IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Encrypt the session key with RSA
    encrypted_session_key = public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted_session_key, salt, iv, encrypted_data

def decrypt_data(encrypted_session_key, salt, iv, encrypted_data, private_key):
    # Decrypt the session key with RSA
    session_key = private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Derive the symmetric key from the session key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100,  # Increased iterations for added security
        backend=default_backend()
    )
    key = kdf.derive(session_key)
    
    # Decrypt the data with AES
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    
    return decrypted_data

def compute_seed_from_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width + height

def hide_file_in_png(image_path, file_to_hide, output_image_path, public_key_path):
    # Load the public key
    with open(public_key_path, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    # Use the sum of the image dimensions as the seed
    seed = compute_seed_from_image_dimensions(image_path)
    prng = random.Random(seed)  # Create a new instance of a random number generator
    # Read the original image
    img = Image.open(image_path)


    # Check if the image is in a mode that can be converted to RGB or RGBA
    if img.mode not in ['RGB', 'RGBA', 'P', 'L']:
        raise ValueError("Image mode must be RGB, RGBA, P (palette-based), or L (grayscale).")

    # Convert to RGB if it's P or L mode (palette-based or grayscale)
    if img.mode in ['P', 'L'] or img.mode != 'RGBA':
        img = img.convert('RGBA')

    #check format of image
    extension_to_format = {'.tga': 'TGA', '.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG', '.bmp': 'BMP', '.tif': 'TIFF', '.tiff': 'TIFF'}
    host_format = img.format or extension_to_format.get(os.path.splitext(image_path)[1].lower())
    supported_formats = {'TGA', 'TIFF', 'BMP', 'PNG', 'JPG', 'JPEG'}
    if host_format not in supported_formats:
        raise ValueError(f"Unsupported image format: {host_format}")

        
    pixels = np.array(img)

    # Read the file to hide
    with open(file_to_hide, 'rb') as f:
        file_bytes = f.read()
    
    # Compress the file
    compressed_data = zlib.compress(file_bytes)

    # Encrypt the compressed data
    encrypted_session_key, salt, iv, encrypted_data = encrypt_data(compressed_data, public_key)
    

    # Concatenate the encrypted session key, salt, iv, and encrypted data
    data_to_encode = (encrypted_session_key + salt + iv + encrypted_data)
    
    # Calculate the number of pixels needed
    file_size = len(data_to_encode)
    num_pixels_required = file_size * 8  # 8 bits per byte
    if num_pixels_required > pixels.size // 4:  # Divide by 4 for RGBA channels
        raise ValueError("Image is not large enough to hide the file.")

    # Generate a list of unique indices to hide the data
    pixel_indices = list(range(pixels.size // 4))
    prng.shuffle(pixel_indices)  # Shuffle using the seeded PRNG
   
    # Embed the file size in the first 64 pixels (8 bytes for file size)
    for i in range(64):
        idx = pixel_indices[i]
        bit = (file_size >> (63 - i)) & 0x1
        if (pixels[idx // pixels.shape[1], idx % pixels.shape[1], 0] & 0x1) != bit:
            pixels[idx // pixels.shape[1], idx % pixels.shape[1], 0] ^= 0x1
    # Embed each bit of the data to encode in the image using LSB matching
    for i, byte in enumerate(data_to_encode):
        for bit in range(8):
            idx = pixel_indices[64 + i * 8 + bit]
            if (pixels[idx // pixels.shape[1], idx % pixels.shape[1], 0] & 0x1) != ((byte >> (7 - bit)) & 0x1):
                pixels[idx // pixels.shape[1], idx % pixels.shape[1], 0] ^= 0x1
    
    # Save the new image
    new_img = Image.fromarray(pixels, 'RGBA')
    if host_format in {'PNG', 'BMP', 'TGA', 'TIFF'}:
        new_img.save(output_image_path, format=host_format, optimize=True)
    elif host_format in {'JPG ','JPEG'}:
        new_img = new_img.convert("RGB")
        new_img.save(output_image_path, format=host_format, optimize=True)
    else:
        raise ValueError(f"Unsupported image format: {host_format}")

    print(f"File has been successfully hidden.")


def extract_file_from_png(image_path, output_file_path, private_key_path):
    # Load the private key
    #passphrase = getpass("Enter the private key passphrase: ")
    passphrase='picrypt'
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=passphrase.encode(),
            backend=default_backend()
        )
    
    # Determine the size of the encrypted session key based on the private key size
    encrypted_session_key_size = private_key.key_size // 8
    
    # Use the sum of the image dimensions as the seed
    seed = compute_seed_from_image_dimensions(image_path)
    prng = random.Random(seed)  # Create a new instance of a random number generator


    # Read the steganographed image
    img = Image.open(image_path)
    if img.mode not in ['RGB', 'RGBA']:
        raise ValueError("Image must be in RGB or RGBA format.")
    
    # Convert to RGBA if not already in that format
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    pixels = np.array(img)
    
    # Flatten the image array for easier processing
    flat_pixels = pixels.flatten()
    
    # Use only the red channel for RGBA
    channel_multiplier = 4

    # Extract the file size from the first 64 pixels
    file_size = 0
    for i in range(64):
        file_size = (file_size << 1) | (flat_pixels[i * channel_multiplier] & 0x1)
    
    # Calculate the number of bytes that can be extracted
    num_bytes_to_extract = file_size
    
    # Prepare a list to store the extracted bytes
    extracted_bytes = []
    

    # Generate a list of unique indices to extract the data
    pixel_indices = list(range(pixels.size // 4))
    prng.shuffle(pixel_indices)  # Shuffle using the seeded PRNG

    # Extract the file size from the first 64 pixels
    file_size = 0
    for i in range(64):
        idx = pixel_indices[i]
        file_size = (file_size << 1) | (pixels[idx // pixels.shape[1], idx % pixels.shape[1], 0] & 0x1)

    # Calculate the number of bytes that can be extracted
    num_bytes_to_extract = file_size
    print(num_bytes_to_extract)
    # Extract the hidden bits and reconstruct the bytes using the same indices
    extracted_bytes = []
    for i in range(num_bytes_to_extract):
        byte = 0
        for bit in range(8):
            idx = pixel_indices[64 + i * 8 + bit]
            byte = (byte << 1) | (pixels[idx // pixels.shape[1], idx % pixels.shape[1], 0] & 0x1)
        extracted_bytes.append(byte)
    
    # Convert the extracted bytes to a byte array
    data_to_decode = bytes(extracted_bytes)    
    # Extract the session key, salt, iv, and encrypted data
    
    encrypted_session_key = data_to_decode[0: encrypted_session_key_size]
    salt = data_to_decode[encrypted_session_key_size:  encrypted_session_key_size + 16]
    iv = data_to_decode[encrypted_session_key_size + 16: encrypted_session_key_size + 32]
    encrypted_data = data_to_decode[encrypted_session_key_size + 32:]
    print(len(encrypted_session_key))
    # Decrypt the data
    decrypted_data = decrypt_data(encrypted_session_key, salt, iv, encrypted_data, private_key)
    
    # Decompress the decrypted data
    decompressed_data = zlib.decompress(decrypted_data)
    # If no output file path is provided, use the extracted filename
    if not output_file_path:
        output_file_path = os.path.join(os.getcwd(), "extract.png")
        
    # Write the decompressed data to the output file
    with open(output_file_path, 'wb') as f:
        f.write(decompressed_data)

    print(f"File extracted to {output_file_path}")


def main():
    if ("hide" == sys.argv[1]):
        hide_file_in_png(sys.argv[2],sys.argv[3],sys.argv[5],sys.argv[4])
    elif("extract" == sys.argv[1]):
        extract_file_from_png(sys.argv[2],sys.argv[4],sys.argv[3])
    else:
        print("error")

if __name__ == '__main__':
    main()