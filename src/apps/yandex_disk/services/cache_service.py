import logging
from typing import List, Optional
from django.core.cache import cache
from ..models import Resource

logger = logging.getLogger(__name__)


class CacheService:
    CACHE_KEY_PREFIX = "resources:"

    @staticmethod
    def get_cache_key(token: str) -> str:
        """
        Формирует ключ для кэша на основе токена.
        :param token: Токен авторизации.
        :return: Ключ для кэша.
        """
        return f"{CacheService.CACHE_KEY_PREFIX}{token}"

    @staticmethod
    def get_cached_resources(token: str) -> Optional[List[Resource]]:
        """
        Получает список ресурсов из кэша.
        :param token: Токен авторизации.
        :return: Список объектов Resource или None.
        """
        cache_key = CacheService.get_cache_key(token)
        logger.info(f"Попытка получения ресурсов из кэша: {cache_key}")
        return cache.get(cache_key)

    @staticmethod
    def update_cache(token: str, resources: List[Resource]) -> None:
        """
        Обновляет кэш списком ресурсов.
        :param token: Токен авторизации.
        :param resources: Список объектов Resource.
        """
        cache_key = CacheService.get_cache_key(token)
        logger.info(f"Обновление кэша: {cache_key}")
        cache.set(cache_key, resources)

    @staticmethod
    def invalidate_cache(token: str) -> None:
        """
        Очищает кэш для указанного токена.
        :param token: Токен авторизации.
        """
        cache_key = CacheService.get_cache_key(token)
        logger.info(f"Очистка кэша: {cache_key}")
        cache.delete(cache_key)
