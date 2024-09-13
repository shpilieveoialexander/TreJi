import random

from fastapi import status

from db import constants
from tests import factories
from tests.conftests import TestCase
from tests.factories.utils import fake
from tests.utils import get_headers


class TaskCreateTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/task/"
        self.manager = factories.UserFactory(status=constants.UserStatus.MANAGER)

    def test_success_manager_task_create(self) -> None:
        input_data = {
            "name": fake.name(),
            "description": fake.name(),
            "responsible_person_id": self.manager.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.post(
            self.url, json=input_data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_manager_task_create_without_description(self) -> None:
        input_data = {
            "name": fake.name(),
            "responsible_person_id": self.manager.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.post(
            self.url, json=input_data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_manager_task_create_without_to_long_description(self) -> None:
        input_data = {
            "name": fake.name(),
            "description": fake.password(length=1000),
            "responsible_person_id": self.manager.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.post(
            self.url, json=input_data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_manager_task_create_creator_developer(self) -> None:
        creator = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        input_data = {
            "name": fake.name(),
            "description": fake.password(length=1000),
            "responsible_person_id": self.manager.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.post(
            self.url, json=input_data, headers=get_headers(creator.id)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TaskUpdateTestCase(TestCase):
    def setUp(self) -> None:

        self.manager = factories.UserFactory(status=constants.UserStatus.MANAGER)
        self.task = factories.TaskFactory(
            responsible_person_id=self.manager.id, created_by=self.manager.id
        )
        self.url = f"/api/v1/task/{self.task.id}"

    def test_success_manager_task_update(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        input_data = {
            "name": fake.name(),
            "description": fake.name(),
            "responsible_person_id": developer.id,
            "status": constants.TaskStatus.IN_PROGRESS.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.put(
            self.url, json=input_data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_manager_task_update_creator_developer(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        input_data = {
            "name": fake.name(),
            "description": fake.name(),
            "responsible_person_id": developer.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.put(
            self.url, json=input_data, headers=get_headers(developer.id)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_manager_task_update_too_long_description(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        input_data = {
            "name": fake.name(),
            "description": fake.password(length=1000),
            "responsible_person_id": developer.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.put(
            self.url, json=input_data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_manager_task_update_without_description(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        input_data = {
            "name": fake.name(),
            "responsible_person_id": developer.id,
            "status": constants.TaskStatus.TODO.value,
            "priority": constants.Priority.LOW.value,
        }
        response = self.client.put(
            self.url, json=input_data, headers=get_headers(self.manager.id)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TaskDeleteTestCase(TestCase):
    def setUp(self) -> None:

        self.manager = factories.UserFactory(status=constants.UserStatus.MANAGER)
        self.task = factories.TaskFactory(
            responsible_person_id=self.manager.id, created_by=self.manager.id
        )
        self.url = f"/api/v1/task/{self.task.id}"

    def test_success_manager_task_delete(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)

        response = self.client.delete(self.url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_invalid_manager_task_delete(self) -> None:
        f"/api/v1/task/{random.randint(0, 999)}"
        response = self.client.delete(self.url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TaskAssignTestCase(TestCase):
    def setUp(self) -> None:

        self.manager = factories.UserFactory(status=constants.UserStatus.MANAGER)
        self.task = factories.TaskFactory(
            responsible_person_id=self.manager.id, created_by=self.manager.id
        )

    def test_success_manager_task_assign_developer(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        url = f"/api/v1/task/{self.task.id}/user/{developer.id}/"
        response = self.client.post(url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_manager_task_assign_developer_does_not_exist(self) -> None:
        url = f"/api/v1/task/{self.task.id}/user/{random.randint(0, 999)}/"
        response = self.client.post(url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_manager_task_assign_task_does_not_exist(self) -> None:
        developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        url = f"/api/v1/task/{random.randint(0, 999)}/user/{developer.id}/"
        response = self.client.post(url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TaskUnassignTestCase(TestCase):
    def setUp(self) -> None:
        self.manager = factories.UserFactory(status=constants.UserStatus.MANAGER)
        self.developer = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        self.task = factories.TaskFactory(
            responsible_person_id=self.manager.id, created_by=self.manager.id
        )
        self.task_executors = factories.TaskExecutors(
            task_id=self.task.id, user_id=self.developer.id
        )

    def test_success_manager_task_unassign_developer(self) -> None:
        url = f"/api/v1/task/{self.task.id}/user/{self.developer.id}/"
        response = self.client.delete(url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_invalid_manager_task_unassign_by_developer(self) -> None:
        fake_mager = factories.UserFactory(status=constants.UserStatus.DEVELOPER)
        url = f"/api/v1/task/{self.task.id}/user/{self.developer.id}/"
        response = self.client.delete(url, headers=get_headers(fake_mager.id))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_manager_task_unassign_developer_fake_task_id(self) -> None:
        url = f"/api/v1/task/{random.randint(0, 999)}/user/{self.developer.id}/"
        response = self.client.delete(url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_manager_task_unassign_developer_fake_user_id(self) -> None:
        url = f"/api/v1/task/{self.task.id}/user/{random.randint(0,999)}/"
        response = self.client.delete(url, headers=get_headers(self.manager.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
