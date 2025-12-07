from django.contrib import admin
from .models import UserProfile, Observation, TimelineEvent, ConsentPolicy, DoctorShareLink, ApiClientToken, AuditLog, Document, DocumentChunk, MemoryEpisode, MemorySemantic


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
  list_display = ('user',)
  search_fields = ('user__username',)


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
  list_display = ('user', 'code', 'value', 'unit', 'taken_at', 'source')
  list_filter = ('code', 'unit', 'source')
  search_fields = ('user__username', 'code')


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
  list_display = ('user', 'kind', 'occurred_at')
  list_filter = ('kind',)
  search_fields = ('user__username', 'kind')


@admin.register(ConsentPolicy)
class ConsentPolicyAdmin(admin.ModelAdmin):
  list_display = ('user', 'resource', 'purpose', 'allowed', 'expires_at')
  list_filter = ('allowed', 'resource')
  search_fields = ('user__username', 'resource', 'purpose')


@admin.register(DoctorShareLink)
class DoctorShareLinkAdmin(admin.ModelAdmin):
  list_display = ('user', 'token', 'scope', 'expires_at', 'revoked')
  list_filter = ('scope', 'revoked')
  search_fields = ('user__username', 'token')


@admin.register(ApiClientToken)
class ApiClientTokenAdmin(admin.ModelAdmin):
  list_display = ('user', 'token', 'scopes', 'active', 'expires_at', 'created_at')
  list_filter = ('active',)
  search_fields = ('user__username', 'token')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
  list_display = ('created_at', 'user', 'actor_role', 'resource', 'action', 'success', 'status_code')
  list_filter = ('resource', 'action', 'success', 'actor_role')
  search_fields = ('user__username', 'resource', 'action', 'path')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
  list_display = ('user', 'title', 'source', 'created_at')
  search_fields = ('user__username', 'title', 'source',)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
  list_display = ('user', 'document', 'chunk_index', 'created_at')
  search_fields = ('user__username', 'document__title')


@admin.register(MemoryEpisode)
class MemoryEpisodeAdmin(admin.ModelAdmin):
  list_display = ('user', 'kind', 'occurred_at')
  list_filter = ('kind',)
  search_fields = ('user__username', 'kind', 'content')


@admin.register(MemorySemantic)
class MemorySemanticAdmin(admin.ModelAdmin):
  list_display = ('user', 'key', 'updated_at')
  search_fields = ('user__username', 'key')
