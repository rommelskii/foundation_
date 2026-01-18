import os
from pathlib import Path
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'

load_dotenv(dotenv_path=env_path)

print(os.getenv("MODEL_DIR"))
