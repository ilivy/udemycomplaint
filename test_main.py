from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# async def test_post_login_error():
#     data = {
#         "email": "noemail@gmail.com",
#         "password": "123"
#     }
#     response = await client.post("/login/", json=data)
#     assert response.status_code == 400
#     message = response.json().get("detail")[0].get("msg")
#     assert message == "Wrong email or password"
#
#
# async def test_post_login_success():
#     data = {
#         "email": "andy@gmail.com",
#         "password": "andy@gmail.com"
#     }
#     response = await client.post("/login/", json=data)
#     assert response.status_code == 200


def test_get_all_complaints():
    response = client.get("/complaints/")
    assert response.status_code == 403
