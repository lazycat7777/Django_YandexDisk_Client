import logging
from typing import Generator
from requests import Session, RequestException
from ..models.resource import Resource

logger = logging.getLogger(__name__)


class CloudAPIException(Exception):
    """Базовый класс для ошибок."""
    pass


class AuthError(CloudAPIException):
    """Ошибка авторизации (код 401)."""
    pass


class InvalidResponse(CloudAPIException):
    """Ошибка при получении невалидного ответа."""
    pass


class CloudAPIClient:
    API_BASE_URL = "https://cloud-api.yandex.net/v1/disk"
    BATCH_SIZE = 100

    def __init__(self, auth_token: str):
        """
        Инициализация клиента API Яндекс.Диска.
        :param auth_token: Токен авторизации.
        """
        self.auth_token = auth_token
        self.http_session = Session()
        self.http_session.headers.update(
            {"Authorization": f"OAuth {auth_token}"}
        )

    def validate_token(self) -> bool:
        """
        Проверяет валидность токена авторизации.
        :return: True, если токен действителен.
        """
        try:
            response = self.http_session.get(f"{self.API_BASE_URL}/")
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                raise AuthError("Неверный токен авторизации")
            else:
                raise InvalidResponse(
                    f"Неожиданный статус-код: {response.status_code}"
                )
        except RequestException as e:
            raise CloudAPIException(f"Ошибка запроса: {e}")

    def fetch_all_resources(self, resource_path: str = "/") -> Generator[Resource, None, None]:
        """
        Рекурсивно получает все ресурсы (файлы и папки) на диске.
        :param resource_path: Путь к текущей директории.
        :return: Генератор объектов Resource.
        """
        url = f"{self.API_BASE_URL}/resources"
        params = {"path": resource_path, "limit": 100}
        while True:
            try:
                response = self.http_session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("_embedded", {}).get("items", [])
                    for item in items:
                        resource, _ = Resource.objects.update_or_create(
                            path=item["path"],
                            defaults={
                                "name": item["name"],
                                "type": item["type"],
                                "created": item["created"],
                                "modified": item["modified"],
                            },
                        )
                        yield resource
                        if item.get("type") == "dir":
                            yield from self.fetch_all_resources(item.get("path"))
                    next_page = data.get("_embedded", {}).get("next")
                    if not next_page:
                        break
                    url = next_page
                elif response.status_code == 401:
                    raise AuthError("Неверный токен авторизации")
                else:
                    raise InvalidResponse(
                        f"Неожиданный статус-код: {response.status_code}"
                    )
            except RequestException as e:
                raise CloudAPIException(f"Ошибка запроса: {e}")

    def get_download_link(self, resource_path: str) -> str:
        """
        Получает прямую ссылку для скачивания файла.
        :param resource_path: Путь к файлу на Яндекс.Диске.
        :return: Прямая ссылка для скачивания.
        """
        url = f"{self.API_BASE_URL}/resources/download"
        params = {"path": resource_path}
        try:
            response = self.http_session.get(url, params=params)
            if response.status_code == 200:
                download_link = response.json().get("href")
                if not download_link:
                    raise ValueError("Ссылка для скачивания не найдена.")
                return download_link
            elif response.status_code == 401:
                raise AuthError("Неверный токен авторизации")
            else:
                raise InvalidResponse(
                    f"Неожиданный статус-код: {response.status_code}")
        except RequestException as e:
            raise CloudAPIException(f"Ошибка запроса: {e}")
