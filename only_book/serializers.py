import re
from decimal import Decimal

from rest_framework import serializers
from . import models

class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Author
        fields = ('name', 'birth_date', 'biography', 'books_count')

    def get_books_count(self, obj):
        return obj.books.count()

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = models.Book
        fields = ('title', 'author', 'isbn', 'price', 'stock', 'is_in_stock')

    def get_is_in_stock(self, obj):
        if obj.stock > 0:
            return True
        else:
            return False

    def validate_isbn(self, value):
        if not re.match(r'^\d{13}$', value):
            return serializers.ValidationError("ISBN 13 ta raqamdan tashkil topgan bo'lishi kerak")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderItem
        fields = ('id', 'book', 'quantity', 'subtotal')


    def get_subtotal(self, obj):
        return Decimal(obj.book.price) * obj.quantity

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Miqdori 0 teng bo'lishi mumkin emas.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    subtotal = OrderItemSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'user', 'books', 'created_at', 'total_price')

    def get_total_price(self):
        total_price = 0
        for price in self.subtotal.subtotal:
            total_price += price
        return total_price

    def validate_books(self, value):
        for order_item in value:
            book = order_item['book']
            quantity = order_item['quantity']

            if book.stock < quantity:
                raise serializers.ValidationError(
                    f"Bazada etarlicha emas '{book.title}'. Qolgan soni {book.stock}."
                )

        return value