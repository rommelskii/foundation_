from PIL import Image
import base64
import io

def encode_pillow_to_base64(pil_img, format: str = "PNG") -> str:
    """
    Transforms a Pillow image to a base64 string via IO buffering.

    Arguments:
        pil_img: Pillow image object
        format (str): image format (JPG, PNG, etc.)
    """
    buffered = io.BytesIO()
    pil_img.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    
    return base64_string

def decode_base64_to_pillow(base64_string: str) -> Image.Image:
    """
    Transforms a base-64 string to a Pillow image object.

    Arguments:
        base64_string (str): inbound base-64 string from HTTP payload
    """

    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    img_bytes = base64_b64decode(base64_string)
    img_buffer = io.BytesIO(img_bytes)
    pil_img = Image.open(img_buffer)

    return pil_img




