from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album, Artist, Genre, Wishlist
from .serializers import AlbumSerializer, ArtistSerializer, GenreSerializer


class ArtistListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        albums = Album.objects.all()

        search = request.query_params.get("search")
        artist_id = request.query_params.get("artist_id")
        genre_id = request.query_params.get("genre_id")

        if search:
            albums = albums.filter(title__icontains=search)
        if artist_id:
            albums = albums.filter(artist_id=artist_id)
        if genre_id:
            albums = albums.filter(genre_id=genre_id)

        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlbumDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user)
        albums = [item.album for item in items]
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            album = Album.objects.get(pk=request.data.get("album"))
        except (Album.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Платівку не знайдено"}, status=404)

        Wishlist.objects.get_or_create(user=request.user, album=album)
        return Response(AlbumSerializer(album).data, status=201)


class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        deleted, _ = Wishlist.objects.filter(user=request.user, album_id=pk).delete()
        if deleted == 0:
            return Response({"error": "Платівки немає у списку бажаного"}, status=404)
        return Response(status=204)
