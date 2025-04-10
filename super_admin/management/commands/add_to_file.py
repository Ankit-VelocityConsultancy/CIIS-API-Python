from django.core.management.base import BaseCommand
from super_admin.views import Test

class Command(BaseCommand):
    help = 'Adds data to the file'

    def handle(self, *args, **options):
        Test(None)