import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

    # **Draw candidate images and vertical separators**
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

        # **Draw vertical line after each candidate answer except the last**
        if candidate_idx < 7:
            separator_x = (candidate_idx + 1) * width
            draw.line([(separator_x, start_row), (separator_x, canvas_height)], fill=0, width=2)

    # Save the final image
    try:
        img.save(output_path)
        print(f"Saved RPM question image: {output_path}")
    except Exception as e:
        print(f"Error saving RPM question image at {output_path}: {e}")


def unpack_npz_to_png(npz_file, output_path):
    """
    Unpacks an .npz file and saves its contents as .png images.
    Creates an RPM question layout for the "image" key.
    
    Parameters:
        npz_file (str): Path to the .npz file.
        output_dir (str): Directory to save the .png images.
    """
    data = np.load(npz_file)
    for key in data.files:
        array = data[key]

        # Skip scalars or invalid shapes
        if array.shape == ():
            print(f"Skipping key '{key}': Scalar value")
            print(f"Value: {array}")
            continue


        if key == "image" and len(array.shape) == 3:  # RPM question layout for "image" key
            print(f"Processing RPM question image: {key}")
            save_rpm_question_image(array, output_path)
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
                print(f"\n\nProcessing: {npz_path}")
                npz_path_split = npz_path.split("/")
                print(f"npz_path_split: {npz_path_split}")
                config = npz_path_split[-3] + "_" + npz_path_split[-2]
                fname = npz_path_split[-1].split(".")[0]
                output_path = os.path.join(output_dir, f"{config}_{fname}.png")
                if os.path.isdir(output_path):
                    print(f"Error: '{output_path}' is a directory, not a file path!")

                print(f"Output path: {output_path}")
                unpack_npz_to_png(npz_path, output_path)


# Example usage
input_directory = "../3_comp/input_data/"
output_directory = "../3_comp/output_data/" 
process_npz_files_in_directory(input_directory, output_directory)
