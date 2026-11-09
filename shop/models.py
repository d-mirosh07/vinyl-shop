from django.conf import settings
from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="albums")

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="wishlisted",
    )

    class Meta:
        unique_together = ("user", "album")

    def __str__(self):
        return f"{self.user} - {self.album}"
