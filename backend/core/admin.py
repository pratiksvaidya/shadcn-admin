from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import SimpleListFilter
from .models import (
    Agency,
    AgencyUser,
    Customer,
    Business,
    Document,
    BusinessDocument,
    Field,
    FieldValue,
    UploadedBusinessDocument,
    Policy,
)

class AgencyUserInline(admin.TabularInline):
    model = AgencyUser
    extra = 1
    fields = ('user', 'role', 'is_primary')
    autocomplete_fields = ['user']

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'website', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone_number')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AgencyUserInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address', 'website')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AgencyUser)
class AgencyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency', 'role', 'is_primary', 'created_at')
    list_filter = ('role', 'is_primary', 'agency', 'created_at')
    search_fields = ('user__username', 'user__email', 'agency__name')
    ordering = ('agency', 'user')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['user', 'agency']
    raw_id_fields = ('user', 'agency')
    fieldsets = (
        (None, {
            'fields': ('user', 'agency')
        }),
        ('Role Information', {
            'fields': ('role', 'is_primary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'agency')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'get_agency', 'get_created_by', 'created_at')
    list_filter = ('created_at', 'agency')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'agency__name')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('agency', 'created_by')
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number')
        }),
        ('Agency Information', {
            'fields': ('agency', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('agency', 'created_by')

    def get_agency(self, obj):
        return obj.agency.name if obj.agency else '-'
    get_agency.short_description = 'Agency'
    get_agency.admin_order_field = 'agency__name'

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else '-'
    get_created_by.short_description = 'Created By'
    get_created_by.admin_order_field = 'created_by__username'

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'email', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone_number', 'customer__first_name', 'customer__last_name')
    ordering = ('name',)
    raw_id_fields = ('customer',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ('business', 'document', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('business__name', 'document__name')
    raw_id_fields = ('business', 'document')

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_id', 'document', 'field_type', 'is_required')
    list_filter = ('field_type', 'is_required', 'document')
    search_fields = ('name', 'field_id', 'document__name')
    raw_id_fields = ('document',)

@admin.register(FieldValue)
class FieldValueAdmin(admin.ModelAdmin):
    list_display = ('field', 'business', 'value', 'source', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('field__name', 'business__name', 'value')
    raw_id_fields = ('field', 'business')

@admin.register(UploadedBusinessDocument)
class UploadedBusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'business__name')
    raw_id_fields = ('business',)

class AgencyFilter(SimpleListFilter):
    title = 'Agency'
    parameter_name = 'agency'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value
        for the option that will appear in the URL query. The second element is the
        human-readable name for the option that will appear in the right sidebar.
        """
        agencies = Agency.objects.filter(
            users=request.user,
            is_active=True
        ).order_by('name')
        return [(str(agency.id), agency.name) for agency in agencies]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string
        and retrievable via `self.value()`.
        """
        if self.value():
            return queryset.filter(business__customer__agency_id=self.value())
        return queryset

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        'policy_type_display',
        'business_name',
        'policy_number',
        'carrier',
        'annual_premium',
        'effective_date',
        'expiration_date',
        'is_active',
    )
    list_filter = (
        'policy_type',
        'carrier',
        'effective_date',
        'expiration_date',
        AgencyFilter,
    )
    search_fields = (
        'policy_number',
        'carrier',
        'business__name',
        'business__agency__name',
    )
    autocomplete_fields = ['business']
    raw_id_fields = ['documents']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('business', 'policy_type', 'policy_number')
        }),
        ('Policy Details', {
            'fields': ('carrier', 'annual_premium')
        }),
        ('Dates', {
            'fields': ('effective_date', 'expiration_date')
        }),
        ('Documents', {
            'fields': ('documents',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def policy_type_display(self, obj):
        return obj.get_policy_type_display()
    policy_type_display.short_description = 'Type'
    policy_type_display.admin_order_field = 'policy_type'

    def business_name(self, obj):
        return obj.business.name
    business_name.short_description = 'Business'
    business_name.admin_order_field = 'business__name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('business') 