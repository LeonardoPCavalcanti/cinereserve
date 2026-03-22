from rest_framework import serializers

from apps.seats.serializers import SeatStatusSerializer

from .models import CinemaSession


class _MovieNestedSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    poster_url = serializers.URLField(allow_null=True, required=False)


class _RoomNestedSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class CinemaSessionListSerializer(serializers.ModelSerializer):
    movie = _MovieNestedSerializer(read_only=True)
    room = _RoomNestedSerializer(read_only=True)

    class Meta:
        model = CinemaSession
        fields = [
            "id",
            "movie",
            "room",
            "start_time",
            "end_time",
            "language",
            "format",
        ]


class CinemaSessionDetailSerializer(serializers.ModelSerializer):
    movie = _MovieNestedSerializer(read_only=True)
    room = _RoomNestedSerializer(read_only=True)

    class Meta:
        model = CinemaSession
        fields = [
            "id",
            "movie",
            "room",
            "start_time",
            "end_time",
            "language",
            "format",
            "is_active",
            "created_at",
            "updated_at",
        ]


class SessionSeatMapSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    room = serializers.CharField()
    seats = SeatStatusSerializer(many=True)
