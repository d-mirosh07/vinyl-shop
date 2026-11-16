import logging

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album, Artist, Genre, Wishlist
from .serializers import AlbumSerializer, ArtistSerializer, GenreSerializer

logger = logging.getLogger(__name__)


class ArtistListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()
            logger.info(f"Artist created: id={artist.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(
            f"Artist creation rejected: invalid fields {list(serializer.errors.keys())}"
        )
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
            genre = serializer.save()
            logger.info(f"Genre created: id={genre.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(
            f"Genre creation rejected: invalid fields {list(serializer.errors.keys())}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            logger.warning(f"Artist not found: id={pk}")
            return Response({"error": "Виконавця не знайдено"}, status=404)

        serializer = ArtistSerializer(artist)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            logger.warning(f"Artist not found for update: id={pk}")
            return Response({"error": "Виконавця не знайдено"}, status=404)

        serializer = ArtistSerializer(artist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Artist updated: id={pk}")
            return Response(serializer.data)
        logger.warning(
            f"Artist update rejected: id={pk}, invalid fields {list(serializer.errors.keys())}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            logger.warning(f"Artist not found for deletion: id={pk}")
            return Response({"error": "Виконавця не знайдено"}, status=404)

        if artist.albums.exists():
            logger.warning(
                f"Artist not deleted: id={pk} has {artist.albums.count()} albums"
            )
            return Response(
                {"error": "Неможливо видалити виконавця, у нього є платівки"},
                status=409,
            )

        artist.delete()
        logger.info(f"Artist deleted: id={pk}")
        return Response(status=204)


class AlbumListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Список платівок",
        description="Доступний без токена. Параметри можна поєднувати.",
        parameters=[
            OpenApiParameter("search", str, description="Текст у назві платівки"),
            OpenApiParameter("artist_id", int, description="Номер виконавця"),
            OpenApiParameter("genre_id", int, description="Номер жанру"),
        ],
        responses=AlbumSerializer(many=True),
    )
    def get(self, request):
        search = request.query_params.get("search")
        artist_id = request.query_params.get("artist_id")
        genre_id = request.query_params.get("genre_id")

        logger.debug(
            f"Album list: search={repr(search)}, artist_id={artist_id}, genre_id={genre_id}"
        )

        albums = Album.objects.all()
        if search:
            albums = albums.filter(title__icontains=search)
        if artist_id:
            albums = albums.filter(artist_id=artist_id)
        if genre_id:
            albums = albums.filter(genre_id=genre_id)

        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Додати платівку",
        description="Потрібен токен: Authorization: Bearer <access>.",
        request=AlbumSerializer,
        responses={
            201: AlbumSerializer,
            400: OpenApiResponse(description="Неправильні дані (помилки по полях)"),
            401: OpenApiResponse(description="Немає токена або він недійсний"),
        },
        examples=[
            OpenApiExample(
                "Приклад запиту",
                value={
                    "title": "Thriller",
                    "price": "899.00",
                    "in_stock": True,
                    "artist": 1,
                    "genre": 1,
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            album = serializer.save()
            user_id = request.user.id if request.user.is_authenticated else None
            logger.info(f"Album created: id={album.id}, user_id={user_id}")
            return Response(serializer.data, status=201)
        logger.warning(
            f"Album creation rejected: invalid fields {list(serializer.errors.keys())}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlbumDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Одна платівка",
        description="Доступна без токена.",
        parameters=[
            OpenApiParameter(
                "pk", int, OpenApiParameter.PATH, description="Номер платівки"
            )
        ],
        responses={
            200: AlbumSerializer,
            404: OpenApiResponse(description='{"error": "Платівку не знайдено"}'),
        },
    )
    def get(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            logger.warning(f"Album not found: id={pk}")
            return Response({"error": "Платівку не знайдено"}, status=404)

        serializer = AlbumSerializer(album)
        return Response(serializer.data)

    @extend_schema(
        summary="Змінити платівку",
        description="Потрібен токен. Можна передати лише ті поля, які змінюються.",
        parameters=[
            OpenApiParameter(
                "pk", int, OpenApiParameter.PATH, description="Номер платівки"
            )
        ],
        request=AlbumSerializer,
        responses={
            200: AlbumSerializer,
            400: OpenApiResponse(description="Неправильні дані (помилки по полях)"),
            401: OpenApiResponse(description="Немає токена або він недійсний"),
            404: OpenApiResponse(description='{"error": "Платівку не знайдено"}'),
        },
    )
    def patch(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            logger.warning(f"Album not found for update: id={pk}")
            return Response({"error": "Платівку не знайдено"}, status=404)

        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Album updated: id={pk}")
            return Response(serializer.data)
        logger.warning(
            f"Album update rejected: id={pk}, invalid fields {list(serializer.errors.keys())}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Видалити платівку",
        description="Потрібен токен.",
        parameters=[
            OpenApiParameter(
                "pk", int, OpenApiParameter.PATH, description="Номер платівки"
            )
        ],
        responses={
            204: OpenApiResponse(description="Видалено, відповіді немає"),
            401: OpenApiResponse(description="Немає токена або він недійсний"),
            404: OpenApiResponse(description='{"error": "Платівку не знайдено"}'),
        },
    )
    def delete(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            logger.warning(f"Album not found for deletion: id={pk}")
            return Response({"error": "Платівку не знайдено"}, status=404)

        album.delete()
        logger.info(f"Album deleted: id={pk}")
        return Response(status=204)


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Список бажаного",
        description="Платівки поточного користувача. Потрібен токен.",
        responses={
            200: AlbumSerializer(many=True),
            401: OpenApiResponse(description="Немає токена або він недійсний"),
        },
    )
    def get(self, request):
        items = Wishlist.objects.filter(user=request.user)
        albums = [item.album for item in items]
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Додати платівку в бажане",
        description="Потрібен токен. Повторне додавання дублікатів не створює.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"album": {"type": "integer", "example": 1}},
                "required": ["album"],
            }
        },
        responses={
            201: AlbumSerializer,
            401: OpenApiResponse(description="Немає токена або він недійсний"),
            404: OpenApiResponse(description='{"error": "Платівку не знайдено"}'),
        },
    )
    def post(self, request):
        try:
            album = Album.objects.get(pk=request.data.get("album"))
        except (Album.DoesNotExist, ValueError, TypeError):
            logger.warning(
                f"Wishlist add failed (album not found): album_id={request.data.get('album')}, user_id={request.user.id}"
            )
            return Response({"error": "Платівку не знайдено"}, status=404)

        Wishlist.objects.get_or_create(user=request.user, album=album)
        logger.info(f"Wishlist add: album_id={album.id}, user_id={request.user.id}")
        return Response(AlbumSerializer(album).data, status=201)


class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Прибрати платівку з бажаного",
        description="Потрібен токен. pk це номер платівки, а не запису у списку.",
        parameters=[
            OpenApiParameter(
                "pk", int, OpenApiParameter.PATH, description="Номер платівки"
            )
        ],
        responses={
            204: OpenApiResponse(description="Видалено, відповіді немає"),
            401: OpenApiResponse(description="Немає токена або він недійсний"),
            404: OpenApiResponse(
                description='{"error": "Платівки немає у списку бажаного"}'
            ),
        },
    )
    def delete(self, request, pk):
        deleted, _ = Wishlist.objects.filter(user=request.user, album_id=pk).delete()
        if deleted == 0:
            logger.warning(
                f"Wishlist remove failed (not in wishlist): album_id={pk}, user_id={request.user.id}"
            )
            return Response({"error": "Платівки немає у списку бажаного"}, status=404)

        logger.info(f"Wishlist remove: album_id={pk}, user_id={request.user.id}")
        return Response(status=204)
