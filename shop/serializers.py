from rest_framework import serializers

from .models import Album, Artist, Genre


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "name"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["id", "title", "price", "in_stock", "artist", "genre"]
