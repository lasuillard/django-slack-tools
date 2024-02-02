from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

if TYPE_CHECKING:
    from typing import Literal

    from django.contrib.admin import ModelAdmin
    from django.core.handlers.wsgi import WSGIRequest
    from django.db.models import Model
    from django.test.client import Client
    from factory.django import DjangoModelFactory


class ModelAdminTestBase:
    admin_cls: type[ModelAdmin]
    model_cls: type[Model]
    factory_cls: type[DjangoModelFactory]

    pytestmark = pytest.mark.django_db()

    def _reverse(
        self,
        view: Literal["changelist", "change", "delete", "history", "add"],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Helper method returns reverse URL For admin view. e.g. `"/admin/django_slack_tools/slackmessage/add"`.

        Any additional arguments will be passed to `django.urls.reverse()`.
        """
        app_label = self.model_cls._meta.app_label
        model_name = self.model_cls._meta.model_name
        return reverse(f"admin:{app_label}_{model_name}_{view}", *args, **kwargs)

    def _get_messages(
        self,
        wsgi_request: WSGIRequest,
    ) -> list[str]:
        """Helper method to get all messages."""
        return [str(m) for m in get_messages(wsgi_request)]

    # NOTE: Below tests do some simple sanity checks only, extra test details should be provided by inherited classes

    def test_changelist(self, admin_client: Client) -> None:
        self.factory_cls.create_batch(size=3)
        url = self._reverse("changelist")

        # Test visit
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_change(self, admin_client: Client) -> None:
        obj = self.factory_cls.create()
        url = self._reverse("change", kwargs={"object_id": obj.id})

        # Test visit
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_delete(self, admin_client: Client) -> None:
        obj = self.factory_cls.create()
        url = self._reverse("delete", kwargs={"object_id": obj.id})

        # Visit object deletion page
        response = admin_client.get(url)
        assert response.status_code == 200

        # Delete object
        response = admin_client.delete(url)
        assert response.status_code == 200

    def test_history(self, admin_client: Client) -> None:
        obj = self.factory_cls.create()
        url = self._reverse("history", kwargs={"object_id": obj.id})

        # Test visit
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_add(self, admin_client: Client) -> None:
        url = self._reverse("add")

        # Test visit
        response = admin_client.get(url)
        assert response.status_code == 200


class ModelTestBase:
    model_cls: type[Model]
    factory_cls: type[DjangoModelFactory]

    pytestmark = pytest.mark.django_db()

    # NOTE: Below tests do some simple sanity checks only, extra test details should be provided by inherited classes

    def test_instance_creation(self) -> None:
        obj = self.factory_cls.create()
        assert isinstance(obj, self.model_cls)
