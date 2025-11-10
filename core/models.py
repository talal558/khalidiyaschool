from django.db import models

class SchoolConfig(models.Model):
    name = models.CharField(max_length=150, default="مدرسة الخالدية الابتدائية")
    timezone = models.CharField(max_length=50, default="Asia/Riyadh")

    def __str__(self):
        return self.name
