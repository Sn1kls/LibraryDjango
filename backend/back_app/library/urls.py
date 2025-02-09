from django.urls import include, path
from library.views import (
    BookAdminViewSet,
    BookListView,
    BooksByCategoryView,
    CategoryListView,
    ExportBooksXLSXView,
    ScrapeBookInfoView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("admin/books", BookAdminViewSet, basename="book-admin")

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("books/", BookListView.as_view(), name="book-list"),
    path(
        "categories/<uuid:category_id>/books/",
        BooksByCategoryView.as_view(),
        name="books-by-category",
    ),
    path("export-books/", ExportBooksXLSXView.as_view(), name="export-books"),
    path("scrape-book-info/", ScrapeBookInfoView.as_view(), name="scrape-book-info"),
    path("", include(router.urls)),
]
