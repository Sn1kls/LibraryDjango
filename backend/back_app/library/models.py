import uuid

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_date = models.DateField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="books"
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
