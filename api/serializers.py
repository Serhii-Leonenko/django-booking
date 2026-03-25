import datetime

from rest_framework import serializers

from db.models import Table


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ("id", "name")


class AvailableTablesQuerySerializer(serializers.Serializer):
    date = serializers.DateTimeField()

    def validate_date(self, value):
        if value < datetime.datetime.now():
            raise serializers.ValidationError("Date cannot be in the past.")
        return value


class BookingCreateRequestSerializer(serializers.Serializer):
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())
    date = serializers.DateTimeField()
    client_name = serializers.CharField(min_length=2)
    client_phone = serializers.CharField(max_length=20)


class BookingCreateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    table = serializers.IntegerField(source="table_id")
    date = serializers.DateTimeField()
    client_name = serializers.CharField()
    client_phone = serializers.CharField()
