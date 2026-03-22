from rest_framework import serializers

from .models import Room, Seat, SeatStatus


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "total_rows", "seats_per_row"]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "row", "number", "seat_label"]


class SeatStatusSerializer(serializers.ModelSerializer):
    seat_id = serializers.UUIDField(source="seat.id")
    row = serializers.CharField(source="seat.row")
    number = serializers.IntegerField(source="seat.number")
    label = serializers.CharField(source="seat.seat_label")

    class Meta:
        model = SeatStatus
        fields = ["seat_id", "row", "number", "label", "status"]
