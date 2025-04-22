from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class ResourceManager(models.Manager):
    def bulk_create_or_update(self, resources: list[dict]):
        """
        Массовое создание или обновление ресурсов.
        :param resources: Список словарей с данными ресурсов.
        """
        resource_paths = [r['path'] for r in resources]

        existing_resources = {
            res.path: res
            for res in self.filter(path__in=resource_paths)
        }

        create_objs = []
        update_objs = []

        for data in resources:
            path = data['path']
            if path in existing_resources:
                resource = existing_resources[path]
                resource.name = data['name']
                resource.type = data['type']
                resource.created = data['created']
                resource.modified = data['modified']
                update_objs.append(resource)
            else:
                create_objs.append(Resource(**data))

        with transaction.atomic():
            if create_objs:
                self.bulk_create(create_objs)

            if update_objs:
                self.bulk_update(update_objs, fields=[
                                 'name', 'type', 'created', 'modified'])


class Resource(models.Model):
    """
    Модель для хранения информации о ресурсах (файлах и папках).
    """
    class ResourceType(models.TextChoices):
        FILE = "file", _("Файл")
        DIRECTORY = "dir", _("Папка")

    name = models.CharField(max_length=255, verbose_name=_("Имя"))
    type = models.CharField(
        max_length=255,
        choices=ResourceType.choices,
        verbose_name=_("Тип")
    )
    path = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Путь"),
        db_index=True
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        db_index=True
    )
    modified = models.DateTimeField(
        verbose_name=_("Дата модификации"),
        db_index=True
    )

    objects: ResourceManager = ResourceManager()

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"

    class Meta:
        verbose_name = _("Ресурс")
        verbose_name_plural = _("Ресурсы")
        indexes = [
            models.Index(fields=['path']),
            models.Index(fields=['created']),
            models.Index(fields=['modified']),
        ]
