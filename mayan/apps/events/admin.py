from django.contrib import admin

from .models import EventType


class EventTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('name', '__str__')


admin.site.register(EventType, EventTypeAdmin)
