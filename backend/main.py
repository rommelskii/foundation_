from face import *
from ultralytics import YOLO
from PIL import Image

def main():
    frame_dir = './images/faces_image.jpg'

    try:
        img_pil = Image.open(frame_dir)
        img_pil = img_pil.convert("RGB")
    except Exception as e:
        printf("Error: cannot convert frame to image")

    coords = media_get_coords(img_pil)
   # UNCOMMENT FOR YOLO INFERENCE
   # model_dir = './models/yolov8n-face.pt'
   # model = YOLO(model_dir)
   # results = frame_gen(model, img_pil)
   # coords = yolo_get_coords(results)

    draw_circle(coords,100,img_pil)
    img_pil.show()

if __name__ == "__main__":
    main()
    
