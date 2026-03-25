
import datetime
import logging
from datetime import timedelta

import phonenumbers
from phonenumbers import NumberParseException
from django.db.models import QuerySet

from api.exceptions import BookingValidationError
from db.models import Booking, Table

logger = logging.getLogger(__name__)


class BookingService:
    def create(
        self,
        table: Table,
        date: datetime.datetime,
        client_name: str,
        client_phone: str,
    ) -> Booking:
        """
        Create booking and check for conflicts.
        """
        self._validate_create(table, date, client_name, client_phone)

        booking = Booking.objects.create(
            table=table,
            date=date,
            client_name=client_name,
            client_phone=client_phone,
        )
        logger.info("Booking created: id=%s table=%s date=%s", booking.id, table.id, date)

        return booking

    def _validate_create(
        self,
        table: Table,
        date: datetime.datetime,
        client_name: str,
        client_phone: str,
    ) -> None:
        if date < datetime.datetime.now():
            logger.warning("Booking rejected: date in the past: %s", date)

            raise BookingValidationError(
                field="date",
                message="Booking date cannot be in the past."
            )

        start = date - timedelta(hours=2)
        end = date + timedelta(hours=2)

        if Booking.objects.filter(table=table, date__gte=start, date__lte=end).exists():
            logger.warning("Booking rejected: table %s already booked at %s", table.id, date)

            raise BookingValidationError(
                field="date",
                message="Table is already booked within ±2 hours of the requested time."
            )

        client_name = client_name.strip()
        if len(client_name) < 2:
            raise BookingValidationError(
                field="client_name",
                message="Name must be at least 2 characters"
            )

        try:
            parsed = phonenumbers.parse(client_phone, None)
            is_valid_phone_number = phonenumbers.is_valid_number(parsed)
        except NumberParseException:
            is_valid_phone_number = False

        if not is_valid_phone_number:
            raise BookingValidationError(
                field="client_phone",
                message="Enter a valid international phone number (e.g. +380991234567)."
            )


class TableService:
    def get_available(self, date: datetime.datetime) -> QuerySet[Table]:
        """
        Get available tables for booking within ±2 hours of the requested time.
        """
        start = date - timedelta(hours=2)
        end = date + timedelta(hours=2)

        booked_ids = Booking.objects.filter(
            date__gte=start,
            date__lte=end
        ).values_list(
            "table_id",
            flat=True
        )

        return Table.objects.exclude(id__in=booked_ids)
