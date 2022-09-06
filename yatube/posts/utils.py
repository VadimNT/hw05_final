from django.conf import settings
from django.core.paginator import Paginator


def get_paginator(request, data) -> Paginator:
    paginator = Paginator(data, settings.NUMS_OF_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj
