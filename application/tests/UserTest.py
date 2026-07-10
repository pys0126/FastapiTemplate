"""
商城模块测试
"""
from fastapi.testclient import TestClient
from application.tests import with_test
from httpx2 import Response


@with_test()
def user_list_test(test_client: TestClient) -> dict:
    """用户列表测试"""
    response: Response = test_client.get("/user/all", params={
        "page": 1,
        "page_size": 10
    })
    return response.json()


if __name__ == "__main__":
    user_list_test()
