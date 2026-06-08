from django.db import models
from django.contrib.auth.models import User


class UserAPIKey(models.Model):
    PROVIDER_CHOICES = [
        ('deepseek', 'DeepSeek'),
        ('qwen', '千问 (Qwen)'),
        ('openai', 'GPT (OpenAI)'),
        ('claude', 'Claude (Anthropic)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=512)
    base_url = models.URLField(blank=True, null=True)
    model_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'provider')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} - {self.get_provider_display()}"
