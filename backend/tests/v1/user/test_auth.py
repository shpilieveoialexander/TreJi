import random

from fastapi import status

from db import constants
from service.core.security import create_tmp_token, hash_password
from tests import factories
from tests.conftests import TestCase
from tests.factories.utils import fake
from tests.utils import get_headers, get_refresh_headers


class ManagerSignUpTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/auth/manager-sign-up/"

    def test_success_manager_sign_up(self) -> None:
        password = fake.password
        data = {
            "name": fake.name(),
            "email": f"{random.randint(1, 999)}{fake.email()}",
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_manager_sign_up_with_user_exists_email(self) -> None:
        factories.UserFactory()
        exist_user = factories.UserFactory()
        password = fake.password
        data = {
            "name": fake.name(),
            "email": exist_user.email,
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        resp_data = response.json()
        assert response.status_code == status.HTTP_409_CONFLICT
        assert resp_data["detail"] == f"User with email {exist_user.email} exists"

    def test_invalid_manager_sign_up_with_not_email_string(self) -> None:
        password = fake.password
        data = {
            "name": fake.name(),
            "email": fake.name,
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_manager_sign_up_without_password(self) -> None:
        data = {"name": fake.name(), "email": fake.name}
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_manager_sign_up_too_short_name(self) -> None:
        password = fake.password
        data = {
            "name": random.randint(1, 999),
            "email": f"{random.randint(1, 999)}{fake.email()}",
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_manager_sign_up_too_short_password(self) -> None:
        password = fake.password(length=5)
        data = {
            "name": fake.name,
            "email": f"{random.randint(1, 999)}{fake.email()}",
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class DeveloperInvitationTestCase(TestCase):
    def setUp(self) -> None:
        self.manager = factories.UserFactory(status=constants.UserStatus.MANAGER)
        self.url = "/api/v1/auth/developer-invitation/"

    def test_success_developer_invitation(self) -> None:
        data = {
            "name": fake.name(),
            "email": f"{random.randint(1, 999)}{fake.email()}",
        }
        response = self.client.post(
            self.url, json=data, headers=get_headers(self.manager.id)
        )
        response.json()
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_developer_invitation_user_exist_in_db(self) -> None:
        user = factories.UserFactory(status=constants.UserStatus.MANAGER)
        data = {
            "name": user.name,
            "email": user.email,
        }
        response = self.client.post(
            self.url, json=data, headers=get_headers(self.manager.id)
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_409_CONFLICT
        assert resp_data["detail"] == f"User with email {user.email} exists"

    def test_invalid_developer_invitation_user_sender_is_not_manager(self) -> None:
        user = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        data = {
            "name": fake.name(),
            "email": f"{random.randint(1, 999)}{fake.email()}",
        }
        response = self.client.post(self.url, json=data, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_developer_invitation_to_short_name(self) -> None:

        data = {
            "name": random.randint(1, 999),
            "email": f"{random.randint(1, 999)}{fake.email()}",
        }
        response = self.client.post(
            self.url, json=data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_developer_invitation_non_email_string(self) -> None:
        data = {
            "name": fake.name(),
            "email": fake.name(),
        }
        response = self.client.post(
            self.url, json=data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class DeveloperSignUpTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/auth/developer-sign-up/"

    def test_success_developer_sign_up(self) -> None:
        user = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        password = fake.password
        data = {
            "token": create_tmp_token(user.id),
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_developer_sign_up_invalid_token(self) -> None:
        password = fake.password
        data = {
            "token": fake.name(),
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        resp_data = response.json()
        assert response.status_code == status.HTTP_409_CONFLICT
        assert resp_data["detail"] == f"User does not exists or token expired"

    def test_invalid_developer_sign_up_too_short_password(self) -> None:
        user = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        password = fake.password(length=5)
        data = {
            "token": create_tmp_token(user.id),
            "password": password,
            "password_confirm": password,
        }
        response = self.client.post(self.url, data=data)
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_developer_sign_up_password_missmatch(self) -> None:
        user = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        data = {
            "token": create_tmp_token(user.id),
            "password": fake.password(),
            "password_confirm": fake.password(),
        }
        response = self.client.post(self.url, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class RefreshTokenTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/auth/refresh-token/"

    def test_success_refresh_token(self) -> None:
        user = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        response = self.client.post(self.url, headers=get_refresh_headers(user.id))
        resp_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert resp_data["access_token"] is not None
        assert resp_data["refresh_token"] is not None

    def test_fail_refresh_token_with_invalid_user_id(self) -> None:
        response = self.client.post(
            self.url, headers=get_refresh_headers(random.randint(1, 999))
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert resp_data["detail"] == "User blocked or not found"

    def test_fail_with_invalid_refresh_token(self) -> None:
        response = self.client.post(
            self.url, headers={"Authorization": f"Bearer {fake.word()}"}
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert resp_data["detail"] == "Could not validate credentials"

    def test_fail_refresh_token_without_headers(self) -> None:
        response = self.client.post(self.url)
        resp_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp_data["detail"] == "Not authenticated"


class LoginTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/auth/access-token"
        self.data = {
            "email": f"{random.randint(1, 999)}{fake.email()}",
            "password": fake.password(),
        }

    def test_success_login(self) -> None:
        factories.UserFactory(
            email=self.data["email"], password=hash_password(self.data["password"])
        )
        response = self.client.post(self.url, data=self.data)
        resp_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert resp_data["access_token"] is not None
        assert resp_data["refresh_token"] is not None

    def test_fail_login_with_wrong_email(self) -> None:
        factories.UserFactory(
            email=fake.email(), password=hash_password(fake.password())
        )
        response = self.client.post(self.url, data=self.data)
        resp_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert resp_data["detail"] == "User not found"

    def test_fail_login_with_wrong_password(self) -> None:
        factories.UserFactory(
            email=self.data["email"], password=hash_password(fake.password())
        )
        response = self.client.post(self.url, data=self.data)
        resp_data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert resp_data["detail"] == "Invalid credentials"
