import datetime

from library.models import Book, Category
from library.services import scrape_book_info
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
    
    def validate_url(self, value):
        return value

    def create(self, validated_data):
        url = validated_data.get("url")
        try:
            book, created = scrape_book_info(url)
        except Exception as e:
            raise serializers.ValidationError(f"Error scraping book: {str(e)}")
        self.created = created
        return book
