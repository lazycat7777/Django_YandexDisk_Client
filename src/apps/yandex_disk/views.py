import logging
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .services.cache_service import CacheService
from .services.cloud_api_service import CloudAPIClient
from .services.resource_service import ResourceFilter, ResourceSyncService

logger = logging.getLogger(__name__)


@csrf_protect
def index(request):
    """
    Главная страница для просмотра файлов.
    """
    if request.method == "POST":
        token = request.POST.get("token")
        if token:
            request.session["auth_token"] = token
            sync_service = ResourceSyncService(CloudAPIClient(token))
            sync_service.get_resources(token, force_sync=True)
        return redirect('file_list')
    return render(request, "base.html")


@csrf_protect
def file_list(request):
    """
    Страница со списком файлов.
    """
    token = request.session.get("auth_token")
    if not token:
        return redirect('index')

    filter_mode = request.GET.get("filter", "all")
    client = CloudAPIClient(token)
    sync_service = ResourceSyncService(client)
    resources = sync_service.get_resources(token)

    resource_filter = ResourceFilter()
    filtered_resources = resource_filter.filter_resources(
        resources, filter_mode)

    return render(
        request,
        "yandex_disk/file_list.html",
        {"resources": filtered_resources, "filter_mode": filter_mode},
    )


@csrf_protect
def download_files(request):
    """
    Скачивание выбранных файлов.
    """
    if request.method == "POST":
        token = request.session.get("auth_token")
        selected_indices = [int(idx)
                            for idx in request.POST.getlist("selected_files")]
        current_filter = request.POST.get("current_filter", "all")

        cached_resources = CacheService.get_cached_resources(token)
        if not cached_resources:
            return redirect('index')

        resource_filter = ResourceFilter()
        filtered_resources = resource_filter.filter_resources(
            cached_resources, current_filter)

        download_links = []
        client = CloudAPIClient(token)
        for idx in selected_indices:
            if 0 <= idx < len(filtered_resources):
                resource = filtered_resources[idx]
                try:
                    download_link = client.get_download_link(resource.path)
                    download_links.append(download_link)
                except Exception as e:
                    logger.error(
                        f"Ошибка при получении ссылки для ресурса {resource.name}: {e}"
                    )
                    return render(request, "base.html", {"error": f"Ошибка при скачивании ресурса {resource.name}"})

        if download_links:
            response_content = "<html><body>"
            for link in download_links:
                response_content += f'<script>window.open("{link}", "_blank");</script>'
            response_content += f'<script>window.location.href = "/files/?filter={current_filter}";</script>'
            response_content += "</body></html>"
            return HttpResponse(response_content)

    return redirect('file_list')
