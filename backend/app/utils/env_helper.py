"""
file: env_helper.py

Contains the class for storing the environment variables. This is just an interface with the Python dotenv API
to extract contents from the .env file found in the backend/ folder.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class EnvVars:
    def __init__(self):
        current_dir = Path(__file__).resolve().parent.parent.parent
        env_path = current_dir / '.env'
        load_dotenv(dotenv_path=env_path)

        self.FLASK_APP = os.getenv("FLASK_APP")
        self.API_PORT = os.getenv("API_PORT")
        self.YOLO_MODEL = os.getenv("YOLO_MODEL")
        self.MEDIA_TASK = os.getenv("MEDIA_TASK")
        self.MODEL_DIR = os.getenv("MODEL_DIR")
        self.MEDIA_DIR = os.getenv("MEDIA_DIR")
        self.PROJECT_VER = os.getenv("PROJECT_VER")
