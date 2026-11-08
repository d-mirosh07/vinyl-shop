from django.urls import path

from .views import (
    AlbumDetailView,
    AlbumListView,
    ArtistDetailView,
    ArtistListView,
    GenreListView,
)

urlpatterns = [
    path("artists/", ArtistListView.as_view()),
    path("genres/", GenreListView.as_view()),
    path("artists/<int:pk>/", ArtistDetailView.as_view()),
    path("albums/", AlbumListView.as_view()),
    path("albums/<int:pk>/", AlbumDetailView.as_view()),
]
