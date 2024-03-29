from django.contrib import admin

from .models import Subscription, SubscriptionsTracker


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'created', 'modified')


@admin.register(SubscriptionsTracker)
class SubscriptionsTrackerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_run_at')
    readonly_fields = ('last_run_at',)

    def has_add_permission(self, request):
        return False
