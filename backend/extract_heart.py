import os
from rembg import remove
from PIL import Image

def process_image(input_path, output_path):
    print(f"Processing image: {input_path}")
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path, "PNG")
        print(f"Successfully saved transparent image to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    # We will use one of the previously generated images in temp, assuming the user's latest upload is there.
    # Looking at the user's latest message, they uploaded 'vision_image_0_48ac5049-7fd9-411a-82ff-baf1bd6a7ec4.png', but that failed.
    # The actual vision image path is slightly different, let's just find it in temp.
    temp_dir = r"C:\Users\haari\.gemini\antigravity\temp"
    out_dir = r"C:\Codes\Codecrux\frontend\public"
    
    # ensure output dir exists
    os.makedirs(out_dir, exist_ok=True)
    
    # find png in temp
    target_img = None
    for f in os.listdir(temp_dir):
        if f.endswith('.png') and 'vision_image' in f:
            target_img = os.path.join(temp_dir, f)
            # get the latest one by modification time
            break
            
    if target_img:
        print(f"Found input image: {target_img}")
        out_file = os.path.join(out_dir, "realistic_heart.png")
        process_image(target_img, out_file)
    else:
        print("Could not find the uploaded image in temp directory.")
