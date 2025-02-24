import io
import logging

import pandas as pd
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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()
        action = "created" if serializer.created else "updated"
        book_serializer = BookSerializer(book)
        return Response(
            {"detail": f"Book {action} successfully.", "book": book_serializer.data},
            status=status.HTTP_200_OK,
        )
