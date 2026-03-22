from rest_framework import serializers

from apps.tickets.models import Ticket


class ReservationCreateSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    seat_id = serializers.UUIDField()


class ReservationResponseSerializer(serializers.Serializer):
    reservation_id = serializers.UUIDField()
    session_id = serializers.UUIDField()
    seat_id = serializers.UUIDField()
    seat_label = serializers.CharField()
    locked_until = serializers.DateTimeField()
    status = serializers.CharField()


class CheckoutSerializer(serializers.Serializer):
    reservation_id = serializers.UUIDField()


class SessionNestedSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    movie_title = serializers.CharField(source="movie.title")
    start_time = serializers.DateTimeField()
    room = serializers.CharField(source="room.name")
    format = serializers.CharField()


class CheckoutResponseSerializer(serializers.Serializer):
    ticket_id = serializers.UUIDField(source="id")
    ticket_code = serializers.CharField()
    session = SessionNestedSerializer()
    seat_label = serializers.CharField(source="seat.seat_label")
    purchased_at = serializers.DateTimeField()


class TicketSerializer(serializers.ModelSerializer):
    session = SessionNestedSerializer(read_only=True)
    seat_label = serializers.CharField(source="seat.seat_label", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_code",
            "session",
            "seat_label",
            "status",
            "purchased_at",
        ]
        read_only_fields = fields
