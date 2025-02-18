import datetime
import io
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.db.models.functions import ExtractYear
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from library.models import Book, Category
from library.serializers import (
    BookInfoScrapeSerializer,
    BookSerializer,
    CategorySerializer,
)
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category__id"]
    search_fields = ["title", "author"]

    def get_queryset(self):
        queryset = super().get_queryset().annotate(year=ExtractYear("publication_date"))
        year_from = self.request.query_params.get("year_from")
        year_to = self.request.query_params.get("year_to")
        if year_from and year_to:
            queryset = queryset.filter(year__gte=year_from, year__lte=year_to)
        return queryset


class BooksByCategoryView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Book.objects.filter(category__id=category_id)


class BookAdminViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.IsAdminUser]


class ExportBooksXLSXView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        df = pd.DataFrame(serializer.data)

        with io.BytesIO() as buffer:
            writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
            df.to_excel(writer, index=False, sheet_name="Books")
            writer.close()
            buffer.seek(0)

            response = HttpResponse(
                buffer.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="books.xlsx"'
            return response


class ScrapeBookInfoView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BookInfoScrapeSerializer

    @swagger_auto_schema(
        operation_description="Scraping book information by URL and saving (or updating) it in the database",
        request_body=BookInfoScrapeSerializer,
        responses={200: "Scraped book info and saved/updated in DB"},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data.get("url")

        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Error querying URL {url}: {e}")
            return Response(
                {"detail": f"Error querying URL: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("h1")
        meta_description = soup.find("meta", attrs={"name": "description"})
        scraped_title = title_tag.text.strip() if title_tag else "Unknown"
        scraped_description = (
            meta_description["content"].strip()
            if meta_description and meta_description.get("content")
            else ""
        )

        default_category, _ = Category.objects.get_or_create(name="Scraped")

        book, created = Book.objects.update_or_create(
            title=scraped_title,
            category=default_category,
            defaults={
                "author": "Unknown",
                "publication_date": datetime.date.today(),
                "description": scraped_description,
            },
        )
        action = "created" if created else "updated"
        logger.info(f"Book '{scraped_title}' {action} successfully.")

        book_serializer = BookSerializer(book)
        return Response(
            {"detail": f"Book {action} successfully.", "book": book_serializer.data},
            status=status.HTTP_200_OK,
        )
