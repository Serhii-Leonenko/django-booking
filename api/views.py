from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.exceptions import BookingValidationError
from api.pagination import TablePagination
from api.serializers import (
    AvailableTablesQuerySerializer,
    BookingCreateRequestSerializer,
    BookingCreateResponseSerializer,
    TableSerializer,
)
from api.services import BookingService, TableService
from db.models import Table


class BookingViewSet(viewsets.ViewSet):
    booking_service = BookingService()

    @extend_schema(
        request=BookingCreateRequestSerializer,
        responses={201: BookingCreateResponseSerializer},
    )
    def create(self, request):
        serializer = BookingCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = self.booking_service.create(**serializer.validated_data)
        except BookingValidationError as e:
            raise ValidationError(
                {
                    e.field: e.message
                }
            )

        return Response(
            BookingCreateResponseSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )


class TableViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    pagination_class =  TablePagination
    table_service = TableService()

    @extend_schema(
        parameters=[AvailableTablesQuerySerializer],
        responses={200: TableSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def available(self, request):
        """
        Returns a list of available tables for a given date within ±2 hours.
        """
        query_serializer = AvailableTablesQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        tables = self.table_service.get_available(query_serializer.validated_data["date"])
        serializer = self.get_serializer(tables, many=True)

        return Response(serializer.data)
