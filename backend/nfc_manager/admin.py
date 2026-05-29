from django.contrib import admin
from .models import NFCBatch, NFCItem, Moment

@admin.register(NFCBatch)
class NFCBatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'support_type', 'quantity', 'created_at']
    search_fields = ['name']

@admin.register(NFCItem)
class NFCItemAdmin(admin.ModelAdmin):
    list_display = ['public_token', 'batch', 'status', 'user', 'created_at']
    list_filter = ['status', 'batch']
    search_fields = ['public_token']

@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ['id', 'nfc_item', 'title', 'is_active', 'updated_at']
    search_fields = ['title']