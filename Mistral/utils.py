import base64
import csv

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None
    
def save_csv(data, file_path):
    """Save the data to a CSV file."""
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"Data saved to {file_path}")
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")

def save_results(data, file_path):
    """Save the results to a CSV file."""
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["index", "image_path", "correct_answer", "prediction", "correct", "answer"])
            writer.writerows(data)
        # print(f"Results saved to {file_path}")
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")

def load_csv(file_path):
    """Load data from a CSV file."""
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            data = list(reader)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None