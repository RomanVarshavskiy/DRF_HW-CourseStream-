from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создаёт администратора-суперпользователя с предопределёнными данными."

    def handle(self, *args, **options):
        user = User.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="Adminov",
        )
        user.set_password("1234admin")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully created admin with email {user.email}"))
