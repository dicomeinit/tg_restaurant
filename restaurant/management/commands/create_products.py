import json

from django.conf import settings
from django.core.management import BaseCommand

from restaurant.models import Product


class Command(BaseCommand):
    help = "Create products"

    def handle(self, *args, **options):
        with open(settings.BASE_DIR / "data" / "products.json") as f:
            data = json.load(f)

        for item in data:
            Product.objects.get_or_create(
                name=item["name"],
                defaults=dict(
                    price=item["price"],
                    description=item["description"],
                    image_url=item["image_url"],
                    product_type=item["product_type"],
                ),
            )
        self.stdout.write(self.style.SUCCESS("Products created"))
