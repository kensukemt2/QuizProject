# pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class LeaderboardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': (self.page.paginator.count // self.page_size) + (1 if self.page.paginator.count % self.page_size > 0 else 0),
            'current_page': self.page.number,
            'results': data
        })