from django.db import models


class Product(models.Model):

    PRODUCT_FIRST = "first"
    PRODUCT_SECOND = "second"
    PRODUCT_DRINK = "drink"
    PRODUCT_DESSERT = "dessert"

    PRODUCT_TYPES = [
        PRODUCT_FIRST,
        PRODUCT_SECOND,
        PRODUCT_DRINK,
        PRODUCT_DESSERT,
    ]

    PRODUCT_TYPE_CHOICES = (
        (PRODUCT_FIRST, "First"),
        (PRODUCT_SECOND, "Second"),
        (PRODUCT_DRINK, "Drink"),
        (PRODUCT_DESSERT, "Dessert"),
    )

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    image_url = models.URLField()

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name="menus")
    date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    name = models.CharField(max_length=100)
    telegram_user_id = models.IntegerField()
    is_banned = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<TgUser {self.telegram_user_id}: {self.name}>"


class Order(models.Model):

    NEW = "new"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELED = "canceled"

    ORDER_STATUS_CHOICES = (
        (NEW, "New"),
        (IN_PROGRESS, "In Progress"),
        (DELIVERED, "Delivered"),
        (CANCELED, "Canceled"),
    )

    tg_user = models.ForeignKey(TelegramUser, on_delete=models.DO_NOTHING)
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=NEW)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    product_price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"OrderItem {self.pk}"
