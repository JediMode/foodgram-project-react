from foodgram.settings import OBJECTS_PER_PAGE
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = OBJECTS_PER_PAGE
    page_size_query_param = 'limit'
