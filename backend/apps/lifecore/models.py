from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


def generate_token_hex():
    return uuid.uuid4().hex


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    demographics = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)


class Observation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=64)
    value = models.FloatField()
    unit = models.CharField(max_length=32)
    taken_at = models.DateTimeField()
    source = models.CharField(max_length=64, default='user_documents')
    extra = models.JSONField(default=dict, blank=True)

class Condition(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    color = models.CharField(max_length=16, default='#64748b')
    aliases = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.name


class TimelineEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField()
    # Enhancements
    category = models.CharField(max_length=32, default='general')
    severity = models.CharField(max_length=16, null=True, blank=True)
    related_conditions = models.JSONField(default=list, blank=True)
    data_summary = models.JSONField(default=dict, blank=True)

class EventCondition(models.Model):
    event = models.ForeignKey(TimelineEvent, on_delete=models.CASCADE, related_name='conditions_link')
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name='event_links')

    class Meta:
        unique_together = (('event', 'condition'),)
        indexes = [
            models.Index(fields=['condition']),
            models.Index(fields=['event']),
        ]


class ConsentPolicy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.CharField(max_length=64)
    purpose = models.CharField(max_length=64)
    allowed = models.BooleanField(default=False)
    scope = models.CharField(max_length=64, default='read')
    expires_at = models.DateTimeField(null=True, blank=True)


class DoctorShareLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, default=generate_token_hex)
    scope = models.CharField(max_length=64, default='read_only')
    scope_meta = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)


class ApiClientToken(models.Model):
    ROLE_CHOICES = (
        ('patient', 'patient'),
        ('doctor', 'doctor'),
        ('admin', 'admin'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, default=generate_token_hex)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='patient')
    scopes = models.CharField(max_length=128, default='read')
    active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    actor_role = models.CharField(max_length=16, default='patient')
    resource = models.CharField(max_length=64)
    action = models.CharField(max_length=64)
    success = models.BooleanField(default=True)
    status_code = models.IntegerField(default=200)
    method = models.CharField(max_length=8, default='GET')
    path = models.CharField(max_length=255, default='')
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['resource', 'action']),
            models.Index(fields=['created_at']),
        ]


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=255, blank=True, default='user_upload')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (user={self.user_id})"


class DocumentChunk(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    text = models.TextField()
    embedding = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'chunk_index')
        indexes = [
            models.Index(fields=['user', 'document']),
        ]


class MemoryEpisode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=64, default='chat')
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'kind', 'occurred_at']),
        ]


class MemorySemantic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=128)
    value = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'key')
        indexes = [
            models.Index(fields=['user', 'key']),
        ]
