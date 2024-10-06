import requests
import os
# from fastapi.testclient import TestClient


# API_BASE_URL = 'http://127.0.0.1:8000'
API_BASE_URL = 'http://44.203.65.128'


def test_hw_api():
    url = f"{API_BASE_URL}/"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


def test_translate_text_api():
    url = f"{API_BASE_URL}/text_translate"
    payload = {
        "text": "胫骨平台骨折是指胫骨（小腿的骨头）上部涉及膝关节的骨折。",
        "source_lang": "auto",
        "target_lang": "en"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":

    print('API_BASE_URL:', API_BASE_URL)

    test_hw_api()

    test_translate_text_api()
