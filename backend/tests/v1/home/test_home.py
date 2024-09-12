from fastapi import status

from tests.conftests import TestCase


class HomeTestCase(TestCase):
    def test_success_response(self):
        response = self.client.get(f"/")
        resp_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert "backend_status" in resp_data
        assert "Backend" in resp_data["backend_status"]["message"]
