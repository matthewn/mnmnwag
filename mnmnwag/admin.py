from django.contrib import admin

from .models import TweetsTracker


@admin.register(TweetsTracker)
class TweetsTrackerAdmin(admin.ModelAdmin):
    readonly_fields = ('last_run_at',)

    def has_add_permission(self, request):
        return False
