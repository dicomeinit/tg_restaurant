from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Create all staff for restaurant"

    def handle(self, *args, **options):
        # run command to create admin user
        call_command("create_admin_user")
        # create products
        call_command("create_products")
        # create menu
        call_command("create_menu")
