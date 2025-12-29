from django.urls import path
from . import views

urlpatterns = [
    path("api/books/", views.api_books, name="api_books"),
    path("api/issue/", views.api_issue_book, name="api_issue_book"),
]
