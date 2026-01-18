import pytest
from backend.app.utils.env_helper import EnvVars
#from backend.app.vision.inference import YOLO_MODEL 
from backend.app.vision.inference import media_get_coords 
from PIL import Image

TEST_IMAGE = "test/test_assets/people.jpg"

@pytest.fixture(scope="class")
def media_setup():
    frame = Image.open(TEST_IMAGE)
    return frame

class TestMediaInference:
    def test_media_inference(self, media_setup):
        frame = media_setup 
        results = media_get_coords(frame)
        assert results is not None
        assert len(results) > 0
