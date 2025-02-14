from django.contrib import admin

from .models import RejectedComment, TootsTracker


@admin.register(RejectedComment)
class RejectedCommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'related_page',
        'submit_date',
        'ip_address',
        'name',
        'email',
        'url',
        'comment',
    )

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.get_fields()]

    def has_add_permission(self, request):
        return False


@admin.register(TootsTracker)
class TootsTrackerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_run_at')
    readonly_fields = ('last_run_at',)

    def has_add_permission(self, request):
        return False
