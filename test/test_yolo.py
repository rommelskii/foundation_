import pytest
from backend.env_helper import EnvVars
from ultralytics import YOLO
from PIL import Image

envs = EnvVars()
TEST_IMAGE = "test/test_assets/people.jpg"

@pytest.fixture(scope="class")
def yolo_setup():
    envs = EnvVars()
    model = YOLO(envs.MODEL_DIR)
    frame = Image.open(TEST_IMAGE)
    return model, frame

class TestYoloInference:
    def test_yolo_initialization(self, yolo_setup):
        model, _ = yolo_setup
        assert model is not None

    def test_yolo_inference(self, yolo_setup):
        model, frame = yolo_setup
        results = model.predict(frame)
        assert len(results) > 0
        assert len(results[0].boxes) > 0
