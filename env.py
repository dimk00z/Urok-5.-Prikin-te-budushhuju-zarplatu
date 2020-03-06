from os import getenv
from pathlib import Path
from dotenv import load_dotenv


def get_data_from_env(data_name):
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    return getenv(data_name)
