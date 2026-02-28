import cv2
import numpy as np

# Load the image
img = cv2.imread(r"C:\Users\haari\.gemini\antigravity\brain\5fabebf2-6291-4536-861f-f6eaf2db5098\media__1772215500628.png", cv2.IMREAD_UNCHANGED)

if img is not None:
    # Convert to grayscale to find the black background
    gray = cv2.cvtColor(img, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.shape[2] == 3 else cv2.COLOR_BGRA2GRAY)
    
    # Threshold the image to create a mask where the black background is 0 and the rest is 255
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    
    # Create an alpha channel based on the mask
    b, g, r = cv2.split(img)[:3]
    alpha = mask
    
    # Merge the channels back together with the alpha channel
    rgba = cv2.merge([b, g, r, alpha])
    
    # Save the transparent image
    cv2.imwrite(r"C:\Codes\Codecrux\frontend\public\realistic_heart.png", rgba)
    print("Successfully saved transparent heart sprite.")
else:
    print("Failed to load image.")
