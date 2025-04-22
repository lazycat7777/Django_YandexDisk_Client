from typing import List
from django.core.cache import cache
from ..models.resource import Resource
from .cloud_api_service import CloudAPIClient


class ResourceFilter:
    """
    Сервис для фильтрации ресурсов.
    """

    def __init__(self):
        self.filters: dict[str, set[str]] = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx',
                          '.ppt', '.pptx', '.odt', '.ods', '.odp'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
            'videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        }

    def filter_resources(
        self,
        resources: List[Resource],
        filter_type: str
    ) -> List[Resource]:
        """
        Фильтрует ресурсы по типу.
        :param resources: Список объектов Resource.
        :param filter_type: Тип фильтра.
        :return: Отфильтрованный список ресурсов.
        """
        if filter_type == 'all':
            return resources
        if filter_type in ('folders', 'files'):
            return [r for r in resources if r.type == ('dir' if filter_type == 'folders' else 'file')]
        extensions = self.filters.get(filter_type, set())
        return [r for r in resources if any(r.name.lower().endswith(ext) for ext in extensions)]


class ResourceSyncService:
    """
    Сервис для синхронизации данных между кэшем, базой данных и Яндекс.Диском.
    """

    def __init__(self, client: CloudAPIClient):
        """
        Инициализация сервиса.
        :param client: Клиент API Яндекс.Диска.
        """
        self.client = client

    def get_resources(self, token: str, force_sync: bool = False) -> List[Resource]:
        """
        Получает список ресурсов с возможностью принудительной синхронизации.
        :param token: Токен авторизации.
        :param force_sync: Принудительная синхронизация.
        :return: Список ресурсов.
        """
        cached_resources = cache.get(f"resources:{token}")
        if not cached_resources or force_sync:
            return self._sync_and_cache_resources(token)
        return cached_resources

    def _sync_and_cache_resources(self, token: str) -> List[Resource]:
        """
        Синхронизирует данные с Яндекс.Диском и обновляет кэш.
        :param token: Токен авторизации.
        :return: Список ресурсов.
        """
        resources = list(self.client.fetch_all_resources())
        cache.set(f"resources:{token}", resources)
        return resources
