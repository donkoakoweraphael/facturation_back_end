import os
from pathlib import Path
from dotenv import load_dotenv


current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd
env_vars = current_dir / ".env"
load_dotenv(env_vars)


PORT = os.getenv("PORT")
EMAIL_SERVER = os.getenv("SERVER")
EMAIL_SENDER = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
