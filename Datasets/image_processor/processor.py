import os
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

def save_rpm_question_image(array, output_path):
    """
    Creates an RPM-style image layout from the input array and saves it.
    
    Parameters:
        array (numpy.ndarray): 3D array of shape (16, height, width).
        output_path (str): Path to save the combined image.
    """
    # Validate array shape
    if array.shape[0] != 16 or len(array.shape) != 3:
        raise ValueError("Expected an array with shape (16, height, width) for RPM format.")
    
    num_images, height, width = array.shape
    grid_size = 3  # 3x3 grid for the matrix

    # Calculate dimensions for the final composite image
    text_height = int(height * 0.2)  # Space for text below answers
    canvas_height = grid_size * height + height + text_height
    canvas_width = max(grid_size * width, 8 * width)  # Ensure room for all candidates
    canvas = np.ones((canvas_height, canvas_width), dtype=np.uint8) * 255  # White background

    # Place the first 8 images into the 3x3 matrix
    for idx in range(8):
        row = idx // grid_size
        col = idx % grid_size
        start_row = row * height
        start_col = col * width
        canvas[start_row:start_row + height, start_col:start_col + width] = array[idx]

    # Add "X" in the missing cell
    x_start_row = 2 * height
    x_start_col = 2 * width
    x_center = (x_start_row + x_start_row + height) // 2
    y_center = (x_start_col + x_start_col + width) // 2

    for i in range(-15, 16):  # Drawing the "X"
        if 0 <= x_center + i < canvas.shape[0] and 0 <= y_center + i < canvas.shape[1]:
            canvas[x_center + i, y_center + i] = 0
            canvas[x_center + i, y_center - i] = 0

    # Convert to PIL image
    img = Image.fromarray(canvas, mode='L')  
    draw = ImageDraw.Draw(img)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("0xProtoNerdFont-Regular.ttf", size=int(height * 0.3))
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default(size=int(height * 0.3))

    # Draw a black separator line between the matrix and candidate answers
    separator_y = grid_size * height - 5  # Position of the line
    draw.line([(0, separator_y), (canvas_width, separator_y)], fill=0, width=2)  # Black line

    # Define answer labels
    answer_labels = "ABCDEFGH"

    # **Fix: Use PIL to paste the candidate images**
    for idx in range(8, num_images):
        candidate_idx = idx - 8
        start_col = candidate_idx * width
        start_row = grid_size * height

        # Convert the candidate answer to a PIL image before pasting
        candidate_img = Image.fromarray(array[idx], mode='L')
        img.paste(candidate_img, (start_col, start_row))

        # Add label below the candidate image
        label_x = start_col + width // 2
        label_y = start_row + height + 5  
        draw.text((label_x, label_y), answer_labels[candidate_idx], fill=0, font=font, anchor="mm")

    # Save the final image
    try:
        img.save(output_path)
        print(f"Saved RPM question image: {output_path}")
    except Exception as e:
        print(f"Error saving RPM question image at {output_path}: {e}")

def save_image_from_array(array, output_path, enhance_contrast=False):
    """
    Saves a NumPy array as a .png image after normalization and optional contrast enhancement.
    
    Parameters:
        array (numpy.ndarray): Input array to save as an image.
        output_path (str): Path to save the .png image.
        enhance_contrast (bool): Whether to apply contrast enhancement.
    """

    # Normalize the array if required
    if array.max() > 255 or array.min() < 0:
        array = 255 * (array - array.min()) / (array.max() - array.min())
    
    # Convert to uint8
    array = array.astype(np.uint8)
    
    try:
        # Handle different image modes
        if len(array.shape) == 2:  # Grayscale
            image = Image.fromarray(array, mode='L')
        elif len(array.shape) == 3 and array.shape[2] in [3, 4]:  # RGB or RGBA
            image = Image.fromarray(array, mode='RGB' if array.shape[2] == 3 else 'RGBA')
        else:
            raise ValueError(f"Unsupported array shape {array.shape}")
        
        # Optionally enhance contrast
        if enhance_contrast:
            image = ImageOps.autocontrast(image)
        
        image.save(output_path)
        print(f"Saved {output_path}")
    except Exception as e:
        print(f"Error saving image at {output_path}: {e}")

def unpack_npz_to_png(npz_file, output_dir):
    """
    Unpacks an .npz file and saves its contents as .png images.
    Creates an RPM question layout for the "image" key.
    
    Parameters:
        npz_file (str): Path to the .npz file.
        output_dir (str): Directory to save the .png images.
    """
    os.makedirs(output_dir, exist_ok=True)
    data = np.load(npz_file)
    output_img_fname = output_dir.split("/")[1:]
    output_img_fname = "_".join(output_img_fname)

    input_file_name = os.path.basename(npz_file)
    input_file_name = os.path.splitext(input_file_name)[0]

    output_file_name = os.path.join(output_dir, f"{input_file_name}.png")

    for key in data.files:
        array = data[key]

        # Skip scalars or invalid shapes
        if array.shape == ():
            print(f"Skipping key '{key}': Scalar value")
            print(f"Value: {array}")
            continue


        if key == "image" and len(array.shape) == 3:  # RPM question layout for "image" key
            print(f"Processing RPM question image: {key}")
            rpm_path = os.path.join(output_dir, f"{output_img_fname}.png")
            save_rpm_question_image(array, rpm_path)
        elif len(array.shape) == 2:  # Directly save 2D arrays (grayscale images)
            save_image_from_array(array, os.path.join(output_dir, f"{key}.png"))
        elif len(array.shape) == 3:  # Save individual slices for other keys
            for i in range(array.shape[0]):
                slice_path = os.path.join(output_dir, f"{key}_slice_{i}.png")
                save_image_from_array(array[i], slice_path)
        else:
            print(f"Skipping key '{key}': Invalid array shape {array.shape}")


def process_npz_files_in_directory(input_dir, output_dir):
    """
    Recursively searches for .npz files in the input directory,
    and unpacks them to the output directory.
    
    Parameters:
        input_dir (str): Directory to search for .npz files.
        output_dir (str): Directory to save the unpacked images.
    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".npz"):
                npz_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                print(f"\n\nProcessing: {npz_path}")
                unpack_npz_to_png(npz_path, output_subdir)


# Example usage
input_directory = "../3_comp/input_data/"
output_directory = "../3_comp/output_data/" 
process_npz_files_in_directory(input_directory, output_directory)
