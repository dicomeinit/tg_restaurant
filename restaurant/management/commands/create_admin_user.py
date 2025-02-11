from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = "Create admin user"

    def handle(self, *args, **options):
        if not User.objects.filter(username=settings.ADMIN_USERNAME).exists():
            User.objects.create_superuser(
                username=settings.ADMIN_USERNAME, email=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD
            )
            self.stdout.write(self.style.SUCCESS("Admin user created"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists"))
