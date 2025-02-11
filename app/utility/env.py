import os

from dotenv import load_dotenv


def get_key() -> str:
    """
    Retrieves the API key from the environment variables.

    Returns:
        str: The API key for accessing the OMDB API.
    """
    load_dotenv()

    return os.getenv('key')
