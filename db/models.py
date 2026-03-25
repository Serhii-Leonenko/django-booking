from django.db import models


class Table(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Booking(models.Model):
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    date = models.DateTimeField()
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "table"], name="unique_table_date"
            )
        ]

    def __str__(self):
        return f"{self.client_name} - {self.table}"
