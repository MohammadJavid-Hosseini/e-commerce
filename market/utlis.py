from rest_framework.pagination import PageNumberPagination


class LargePaginatioinSettings(PageNumberPagination):
    page_size = 10
    max_page_size = 50


class SmallPaginatioinSettings(PageNumberPagination):
    page_size = 5
    max_page_size = 15
