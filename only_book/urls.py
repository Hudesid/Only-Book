from django.urls import path
from . import views

urlpatterns = [
    path('book/list/', views.book_list, name='book_list'),
    path('author/detail/', views.author_detail, name='author_detail'),
    path('author/create/', views.author_create, name='author_create'),
    path('order/create/<int:pk>/', views.order_create, name='order_create')
]