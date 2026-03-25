import logging
import time

from django.db import connection

from config.settings import PERFORMANCE_TIME, PERFORMANCE_COUNT_QUERIES

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """
    Контроль за швидкістю виконання запитів та захист від витіків запитів в БД
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.info = {}

    def __call__(self, request):
        start = time.time()
        start_queries = len(connection.queries)
        response = self.get_response(request)
        end_queries = len(connection.queries)

        count_queries = end_queries - start_queries
        execution_time = int(time.time() - start)

        if (
            count_queries > PERFORMANCE_COUNT_QUERIES
            or execution_time > PERFORMANCE_TIME
        ):
            self.info["queries"] = count_queries
            self.info["time"] = execution_time
            logger.warning(self.info)
        return response

    def process_view(self, request, view_func, *args, **kwargs):
        self.info["module"] = f"{view_func.__module__}.{view_func.__name__}"
        self.info["request_path_info"] = request.path_info
