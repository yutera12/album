from fastapi.testclient import TestClient
from main import app


GET_ENDPOINTS = [
    "/is-admin",
    "/thumbnail-random",
    "/thumbnail-random/tag-1",
    "/photo/month/20260101",
    "/video/tag/tag-1/section/section-1",
    "/tag-list",
    "/birthdays",
    "/year-month-map",
]

POST_ENDPOINTS = [
    "/set-tag",
    "/set-favorite"
]


client = TestClient(app)

def test_protected_get_api_without_token():
    for endpoint in GET_ENDPOINTS:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_protected_post_api_without_token():
    for endpoint in POST_ENDPOINTS:
        response = client.post(endpoint)
        assert response.status_code == 401
