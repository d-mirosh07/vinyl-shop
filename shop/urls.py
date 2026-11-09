from django.urls import path

from .views import (
    AlbumDetailView,
    AlbumListView,
    ArtistDetailView,
    ArtistListView,
    GenreListView,
    WishlistDetailView,
    WishlistView,
)

urlpatterns = [
    path("artists/", ArtistListView.as_view()),
    path("artists/<int:pk>/", ArtistDetailView.as_view()),
    path("genres/", GenreListView.as_view()),
    path("albums/", AlbumListView.as_view()),
    path("albums/<int:pk>/", AlbumDetailView.as_view()),
    path("wishlist/", WishlistView.as_view()),
    path("wishlist/<int:pk>/", WishlistDetailView.as_view()),
]
