from decimal import Decimal

from django.db.transaction import commit
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from . import serializers
from . import models
from .serializers import BookSerializer, AuthorSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def book_list(request):
    if request.method == 'GET':
        books = models.Book.objects.all()
        serializer = serializers.BookSerializer(books, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                author = request.data.get('author')
                author_instance = get_object_or_404(models.Author, name=author)
                serializer.save(author=author_instance)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def order_create(request, pk):
    if request.method == 'GET':
        orders = models.OrderItem.objects.all()
        serializer = serializers.OrderSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user

        books_data = request.data.get('books', [])
        total_price = 0

        if not books_data:
            return Response({"detail": "No books specified for the order."}, status=status.HTTP_400_BAD_REQUEST)

        order_items = []

        for book_data in books_data:
            quantity = book_data.get('quantity')

            if not quantity:
                return Response({"detail": "Book ID and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)

            book = models.Book.objects.filter(pk=pk).first()
            if not book:
                return Response({"detail": f"Book with ID {pk} not found."}, status=status.HTTP_404_NOT_FOUND)

            if book.stock < int(quantity):
                return Response(
                    {"detail": f"Not enough stock for {book.title}. Only {book.stock} available."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            price_decimal = Decimal(str(book.price))
            quantity_decimal = Decimal(quantity)

            total_price += price_decimal * quantity_decimal

            order_items.append(models.OrderItem(book=book, quantity=quantity))

        order = models.Order.objects.create(user=user, total_price=total_price)

        for item in order_items:
            item.order = order
            item.save()

        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def author_detail(request, pk):
    if request.method == 'GET':
        author = get_object_or_404(models.Author, pk=pk)
        serializer = serializers.AuthorSerializer(author)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            author = get_object_or_404(models.Author, pk=pk)
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def author_create(request):
    if request.method == 'GET':
        authors = models.Author.objects.all()
        serializer = serializers.AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
