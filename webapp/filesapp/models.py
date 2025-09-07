from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    FILE_TYPES = (
        ('rozvaha', 'Rozvaha'),
        ('vykaz', 'Výkaz zisku a ztráty'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.FileField(upload_to='pdf/')
    csv_file = models.FileField(upload_to='csv/', blank=True, null=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='rozvaha')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    year = models.IntegerField(null=True, blank=True)  # 👈 přidané pole

    def save(self, *args, **kwargs):
        if self.uploaded_at and not self.year:
            self.year = self.uploaded_at.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.file_type} - {self.original_file.name}"

class ClientCoachRelation(models.Model):
    coach = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coached_clients"
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_coach"
    )

    def __str__(self):
        return f"Kouč {self.coach.username} → Klient {self.client.username}"