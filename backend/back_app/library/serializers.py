from library.models import Book, Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "publication_date",
            "category",
            "category_id",
            "description",
        ]

    def create(self, validated_data):
        category_id = validated_data.pop("category_id")
        category = Category.objects.get(id=category_id)
        book = Book.objects.create(category=category, **validated_data)
        return book

    def update(self, instance, validated_data):
        if "category_id" in validated_data:
            category_id = validated_data.pop("category_id")
            instance.category = Category.objects.get(id=category_id)
        return super().update(instance, validated_data)


class BookInfoScrapeSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)


class ExternalBookInfoSerializer(serializers.Serializer):
    isbn = serializers.CharField(max_length=20, help_text="ISBN книжки")
