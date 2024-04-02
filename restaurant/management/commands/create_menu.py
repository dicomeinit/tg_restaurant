import datetime

from django.core.management import BaseCommand
from django.utils import timezone

from restaurant.models import Menu, Product


class Command(BaseCommand):
    help = "Create menu"

    def handle(self, *args, **options):
        last_date = Menu.objects.order_by("-date").values_list("date", flat=True)
        last_date = last_date[0] if last_date.exists() else None
        if last_date:
            next_date = last_date + datetime.timedelta(days=1)
        else:
            next_date = timezone.now().date()

        products_for_menu = []
        for product_type in Product.PRODUCT_TYPE_CHOICES:
            products = Product.objects.filter(product_type=product_type[0]).order_by("?")[:2]
            products_for_menu.extend(products)

        tomorrow_str = next_date.strftime("%d-%m-%Y")

        menu_name = f"Menu for {tomorrow_str}"

        menu = Menu.objects.create(name=menu_name, date=next_date)
        menu.products.set(products_for_menu)

        self.stdout.write(self.style.SUCCESS(f"{menu_name} created"))
