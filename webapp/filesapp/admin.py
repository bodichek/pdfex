from django.contrib import admin
from .models import ClientCoachRelation

@admin.register(ClientCoachRelation)
class ClientCoachRelationAdmin(admin.ModelAdmin):
    list_display = ("coach", "client")
    search_fields = ("coach__username", "client__username")