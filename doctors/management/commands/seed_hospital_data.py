from django.core.management.base import BaseCommand

from doctors.seed_data import seed_default_doctors_and_staff


class Command(BaseCommand):
    help = "Seed default doctors and doctor staff users."

    def handle(self, *args, **options):
        result = seed_default_doctors_and_staff()

        self.stdout.write(
            self.style.SUCCESS(
                f"Doctors created={result['created_doctors']}, updated={result['updated_doctors']}; "
                f"staff users created={result['created_users']}, updated={result['updated_users']}"
            )
        )
