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
