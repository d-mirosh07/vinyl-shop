from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album, Artist, Genre
from .serializers import AlbumSerializer, ArtistSerializer, GenreSerializer


class ArtistListView(APIView):
    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreListView(APIView):
    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistDetailView(APIView):
    def get(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response({"error": "Виконавця не знайдено"}, status=404)

        serializer = ArtistSerializer(artist)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response({"error": "Виконавця не знайдено"}, status=404)

        serializer = ArtistSerializer(artist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response({"error": "Виконавця не знайдено"}, status=404)

        if artist.albums.exists():
            return Response(
                {"error": "Неможливо видалити виконавця, у нього є платівки"},
                status=409,
            )

        artist.delete()
        return Response(status=204)


class AlbumListView(APIView):
    def get(self, request):
        albums = Album.objects.all()
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlbumDetailView(APIView):
    def get(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        serializer = AlbumSerializer(album)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        album.delete()
        return Response(status=204)
