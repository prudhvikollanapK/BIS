# bis_app/admin.py

from django.contrib import admin
from .models import BlockedDomain

class BlockedDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'user', 'description', 'added_on')
    search_fields = ('domain', 'user__username')
    list_filter = ('user', 'added_on')

admin.site.register(BlockedDomain, BlockedDomainAdmin)
