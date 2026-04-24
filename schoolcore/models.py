from django.db import models
from khalidiyaschool.utils.images import convert_image_to_webp


class SchoolConfig(models.Model):
    name     = models.CharField(max_length=150, default="مدرسة الخالدية الابتدائية")
    timezone = models.CharField(max_length=50, default="Asia/Riyadh")
    logo     = models.ImageField("شعار المدرسة", upload_to="school/logo/", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            try:
                old = SchoolConfig.objects.get(pk=self.pk)
                if old.logo and old.logo != self.logo:
                    old.logo.delete(save=False)
            except SchoolConfig.DoesNotExist:
                pass
        if self.logo and not self.logo.name.endswith(".webp"):
            convert_image_to_webp(self.logo, upload_path="school/logo/")
        super().save(*args, **kwargs)
