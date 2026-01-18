import tkinter as tk
from tkinter import filedialog
import base64
import io
import requests
from PIL import Image, UnidentifiedImageError

# ==========================================
# CONFIGURATION
# Change this to your actual API endpoint URL
API_URL = "http://localhost:8080/media"
# ==========================================


def select_image_file() -> str:
    """Opens a system file dialog to choose an image."""
    # Initialize Tkinter root window and hide it immediately
    root = tk.Tk()
    root.withdraw()

    print("Please select an image file...")
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("All files", "*.*")
        ]
    )
    return file_path


def encode_image_to_b64(file_path: str) -> str:
    """Reads an image file and converts it to a raw base64 string."""
    try:
        # Open the image using Pillow to ensure it's valid
        with Image.open(file_path) as img:
            # Create a memory buffer to hold image data
            buffered = io.BytesIO()
            # Save image as PNG into the buffer to standardize transport format
            # (PNG is lossless, good for intermediaries)
            img.save(buffered, format="PNG")
            # Get bytes content, encode to b64, convert to string
            img_b64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            print(f"-> Image encoded successfully ({len(img_b64_str)} chars).")
            return img_b64_str
            
    except UnidentifiedImageError:
        print("Error: The selected file is not a valid image recognized by Pillow.")
        exit(1)
    except Exception as e:
        print(f"Error during encoding: {e}")
        exit(1)


def send_to_api(b64_input_str: str) -> str:
    """Sends base64 string to API and returns the output base64 string."""
    payload = {
        "b64_input": b64_input_str
    }

    print(f"-> Sending request to {API_URL}...")
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        # Raise an exception if the server returned a 4XX or 5XX error
        response.raise_for_status()

        # Attempt to parse JSON response
        data = response.json()

        output_b64 = data.get("b64_output")
        if not output_b64:
            print("Error: API response did not contain key 'b64_output'.")
            print("Full response:", data)
            exit(1)
            
        print(f"<- Received valid response from API ({len(output_b64)} chars).")
        return output_b64

    except requests.exceptions.RequestException as e:
        print(f"\nConnection Error: Could not connect to API endpoint.")
        print(f"Details: {e}")
        exit(1)
    except requests.exceptions.JSONDecodeError:
        print("\nError: API returned invalid JSON.")
        print("Response text:", response.text)
        exit(1)


def display_b64_image(b64_output_str: str):
    """Decodes a base64 string and displays it using the default image viewer."""
    print("-> Decoding and displaying result...")
    try:
        # 1. Decode the string into raw bytes
        img_bytes = base64.b64decode(b64_output_str)

        # 2. Wrap bytes in a BytesIO buffer so Pillow can treat it like a file
        img_buffer = io.BytesIO(img_bytes)

        # 3. Open as a PIL Image object
        img = Image.open(img_buffer)

        # 4. Show the image using the OS default application
        img.show()
        print("Done!")

    except base64.binascii.Error:
        print("Error: Could not decode output. The string returned by the API is not valid Base64.")
    except UnidentifiedImageError:
        print("Error: Decoded bytes result in an invalid image format.")


# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
if __name__ == "__main__":
    # 1. Select File
    image_path = select_image_file()
    if not image_path:
        print("No file selected. Exiting.")
        exit()

    # 2. Encode Local Image
    b64_input = encode_image_to_b64(image_path)

    # 3. Send to API and receive response
    b64_output = send_to_api(b64_input)

    # 4. Display Result
    display_b64_image(b64_output)
