from django.contrib import admin
from django.db.models import F, FloatField, Sum
from django.utils.html import escape, mark_safe

from restaurant.models import Menu, Order, OrderItem, Product, TelegramUser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "product_type", "is_active", "created_at")
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        size = 250
        return mark_safe(f'<img src="{escape(obj.image_url)}" width="{size}" height="{size}"/>')

    image_tag.short_description = "Image"
    image_tag.allow_tags = True


class MenuProductInline(admin.TabularInline):
    model = Menu.products.through
    extra = 0


@admin.register(Menu)
class MenuProductAdmin(admin.ModelAdmin):
    inlines = (MenuProductInline,)
    list_display = ("name", "created_at")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "created_at")
    inlines = (OrderItemInline,)
    readonly_fields = ("total_amount",)

    def total_amount(self, order: Order) -> str:
        result = (
            Order.objects.filter(pk=order.pk)
            .annotate(total=Sum(F("items__product_price") * F("items__quantity"), output_field=FloatField()))
            .values_list("total", flat=True)
        )
        value = round(result[0], 2)
        return mark_safe(f"<b>{value}</b>")

    total_amount.short_description = mark_safe("<b>Total Amount</b>")
    total_amount.allow_tags = True


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "product_price", "quantity")


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "telegram_user_id", "is_banned", "created_at")
    readonly_fields = ("telegram_user_id",)
