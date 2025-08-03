import cv2
import numpy as np
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
def calculate_mse(original, stego):
    #print((original.astype("int")))
    #print("stego image", stego.astype("int"))
    mse = np.sum((original.astype("int") - stego.astype("int")) ** 2)
    print(mse)
    mse /= float(original.shape[0] * original.shape[1])
    
    return mse

def calculate_psnr(mse, max_pixel_value=255):
    if mse == 0:
        return float('inf')  # PSNR is infinite if MSE is zero
    psnr = 20 * np.log10(max_pixel_value / np.sqrt(mse))
    return psnr

def main(im1,im2):
    # Replace 'original_image_path' and 'stego_image_path' with the paths of your original and stego images
    original_image_path = im1
    stego_image_path = im2

    # Load images
    original_image = cv2.imread(original_image_path)
    stego_image = cv2.imread(stego_image_path)

    # Check if images are loaded successfully
    if original_image is None or stego_image is None:
        print("Error: Couldn't load images.")
        return

    # Resize stego image to match the dimensions of the original image
    stego_image = cv2.resize(stego_image, (original_image.shape[1], original_image.shape[0]))

    # Calculate MSE
    mse = calculate_mse(original_image, stego_image)
    print(f"Mean Squared Error (MSE): {mse}")

    # Calculate PSNR
    psnr = calculate_psnr(mse)
    print(f"Peak Signal-to-Noise Ratio (PSNR): {psnr} dB")

if __name__ == "__main__":
    im1="C:/Users/patel/Music/final project/project/project/imsecure/res/th2.png"
    im2="C:/Users/patel/Downloads/extract (2).png"
    main(im1,im2)
