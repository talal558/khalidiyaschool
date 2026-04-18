from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from schoolaccounts.models import UserProfile

User = get_user_model()

VALID_ROLES = [r[0] for r in UserProfile.ROLES]


class Command(BaseCommand):
    help = "تعيين دور لمستخدم: assign_role <username> <role>"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="اسم المستخدم")
        parser.add_argument(
            "role",
            type=str,
            choices=VALID_ROLES,
            help=f"الدور المطلوب: {', '.join(VALID_ROLES)}",
        )

    def handle(self, *args, **options):
        username = options["username"]
        role = options["role"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"المستخدم '{username}' غير موجود.")

        profile, created = UserProfile.objects.get_or_create(user=user)
        old_role = profile.role
        profile.role = role
        profile.save()

        action = "تم إنشاء ملف و" if created else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{action}تعيين دور '{role}' للمستخدم '{username}' "
                f"(كان: '{old_role}') بنجاح."
            )
        )
