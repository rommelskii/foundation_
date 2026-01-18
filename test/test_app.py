import pytest
import requests
from backend.app.vision.inference import YOLO_MODEL 
from backend.app.utils.env_helper import EnvVars
from backend.app.utils.pillow_handler import encode_pillow_to_base64, decode_base64_to_pillow
from PIL import Image

TEST_IMAGE = "test/test_assets/people.jpg"
envs = EnvVars()

@pytest.fixture(scope="class")
def api_request_setup():
    url = f"http://localhost:{envs.API_PORT}/"
    api_route = url + 'api/'
    vision_route = url + 'vision/'
    yolo_route = vision_route + 'yolo'
    media_route = vision_route + 'media'
    return api_route, yolo_route, media_route

class TestApiRequests:
    def health_check(self, api_request_setup):
        api_route, _, _ = api_request_setup
        response = requests.get(api_route)
        assert response.status_code == 200

    def test_upload_and_yolo(self, api_request_setup):
        _, yolo_route, _ = api_request_setup
        with Image.open(TEST_IMAGE) as img:
            assert img.format in ["JPEG", "JPG", "PNG"]
            b64_string = encode_pillow_to_base64(img)
            payload = {"b64_input": b64_string}
            response = requests.post(yolo_route, json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "b64_output" in data
        assert data["b64_output"] != None

    def test_upload_and_media(self, api_request_setup):
        _, _, media_route = api_request_setup
        with Image.open(TEST_IMAGE) as img:
            assert img.format in ["JPEG", "JPG", "PNG"]
            b64_string = encode_pillow_to_base64(img)
            payload = {"b64_input": b64_string}
            response = requests.post(media_route, json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "b64_output" in data
        assert data["b64_output"] != None



        


