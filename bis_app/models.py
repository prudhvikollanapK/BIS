from django.db import models
from django.contrib.auth.models import User

class BlockedDomain(models.Model):
    domain = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_domains')

    def __str__(self):
        return f"{self.domain} - {self.user.username}"
