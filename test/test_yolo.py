import pytest
from backend.app.utils.env_helper import EnvVars
from backend.app.vision.inference import YOLO_MODEL 
from PIL import Image

TEST_IMAGE = "test/test_assets/people.jpg"

@pytest.fixture(scope="class")
def yolo_setup():
    frame = Image.open(TEST_IMAGE)
    return YOLO_MODEL, frame

class TestYoloInference:
    def test_yolo_initialization(self, yolo_setup):
        model, _ = yolo_setup
        assert model is not None

    def test_yolo_inference(self, yolo_setup):
        model, frame = yolo_setup
        results = model.predict(frame)
        assert len(results) > 0
        assert len(results[0].boxes) > 0
