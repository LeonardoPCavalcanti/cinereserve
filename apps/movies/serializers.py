from rest_framework import serializers

from apps.movies.models import Movie


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration_minutes",
            "genre",
            "director",
            "poster_url",
            "release_date",
        ]


class MovieDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration_minutes",
            "genre",
            "director",
            "cast",
            "poster_url",
            "release_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
