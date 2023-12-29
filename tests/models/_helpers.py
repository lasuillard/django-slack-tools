from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.db.models import Model
    from factory.django import DjangoModelFactory


class ModelTestBase:
    model_cls: type[Model]
    factory_cls: type[DjangoModelFactory]

    # NOTE: Below tests do some simple sanity checks only, extra test details should be provided by inherited classes
    @pytest.mark.django_db()
    def test_instance_creation(self) -> None:
        obj = self.factory_cls.create()
        assert isinstance(obj, self.model_cls)
