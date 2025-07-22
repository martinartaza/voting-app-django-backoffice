from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Competition, Vote, Company, CustomUser

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'company')}),
    )
    list_display = UserAdmin.list_display + ('role', 'company',)
    list_filter = UserAdmin.list_filter + ('role', 'company',)
    search_fields = UserAdmin.search_fields + ('role', 'company__name',)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'creator',)
    list_filter = ('start_date', 'end_date', 'creator__company',)
    search_fields = ('name', 'creator__username',)
    fields = ('name', 'start_date', 'end_date', 'creator',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'competition', 'voter', 'nominee', 'is_public',)
    list_filter = ('competition', 'voter', 'nominee', 'is_public',)
    search_fields = ('title', 'competition__name', 'voter__username', 'nominee__username',)
    fields = ('competition', 'title', 'description', 'award', 'is_public', 'voter', 'nominee',)

