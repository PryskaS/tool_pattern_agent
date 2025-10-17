import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    A pytest fixture that loads environment variables from a .env file
    before any tests run.
    
    scope="session": Ensures this runs only once per test session.
    autouse=True: Ensures it's automatically used for all tests without
                  needing to be explicitly requested.
    """
    load_dotenv()