import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from restaurant.models import Menu, Order, OrderItem, Product, TelegramUser


class ProductRequestSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    date = serializers.DateField(format="%Y-%m-%d")

    def validate_date(self, value: datetime.date):
        if value < timezone.now().date():
            raise ValidationError("Bad date")
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Menu
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        read_only_fields = ["order", "product_price"]
        write_only_fields = ["product_id", "quantity"]
        exclude = ["order"]

    def validate_quantity(self, value):
        if value < 1:
            raise ValidationError("Quantity must be greater than 0")
        return value

    def validate_product_id(self, value):
        if not Product.objects.filter(
            pk=value, menus__date=timezone.now().date() + datetime.timedelta(days=1)
        ).exists():
            raise ValidationError("Product not found")
        return value


class OrderRequestSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True)
    user_id = serializers.IntegerField()
    username = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    order_id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ["items", "user_id", "username", "phone"]

    def create(self, validated_data):
        items = validated_data.pop("items")
        telegram_user_id = validated_data.pop("user_id")
        telegram_user, _ = TelegramUser.objects.get_or_create(
            telegram_user_id=telegram_user_id, defaults={"name": validated_data.pop("username")}
        )
        order = Order.objects.create(tg_user=telegram_user, **validated_data)
        new_items = []
        for item in items:
            product = item["product"]
            order_item = OrderItem.objects.create(
                order=order, product=product, product_price=product.price, quantity=item["quantity"]
            )
            new_items.append(order_item)
        validated_data["order_id"] = order.id
        validated_data["status"] = order.status
        validated_data["user_id"] = telegram_user_id
        validated_data["items"] = new_items
        validated_data["total_price"] = self.calculate_total_price(items)
        return validated_data

    def calculate_total_price(self, items):
        total_price = 0
        for item in items:
            total_price += item["product"].price * item["quantity"]
        return total_price
