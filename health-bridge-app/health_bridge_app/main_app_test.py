import requests
import os
# from fastapi.testclient import TestClient


API_BASE_URL = 'http://127.0.0.1:8000'


def test_hw_api():
    url = f"{API_BASE_URL}/"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":

    print('API_BASE_URL:', API_BASE_URL)

    test_hw_api()
