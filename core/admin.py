from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Competition, Vote, Company, CustomUser


class CompanyFilterMixin:
    """Mixin para filtrar por compañía del usuario"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'ADMIN':
            return qs
        return self.filter_by_company(qs, request.user.company)
    
    def filter_by_company(self, qs, company):
        """Filtra queryset por compañía - debe ser implementado por subclases"""
        return qs


@admin.register(Company)
class CompanyAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
    def filter_by_company(self, qs, company):
        """Los usuarios solo ven su propia compañía"""
        return qs.filter(id=company.id)


@admin.register(CustomUser)
class CustomUserAdmin(CompanyFilterMixin, UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'company')}),
    )
    list_display = UserAdmin.list_display + ('role', 'company',)
    list_filter = UserAdmin.list_filter + ('role', 'company',)
    search_fields = UserAdmin.search_fields + ('role', 'company__name',)
    
    def filter_by_company(self, qs, company):
        """Los usuarios solo ven usuarios de su compañía"""
        return qs.filter(company=company)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra opciones de compañía"""
        if db_field.name == "company" and not (request.user.is_superuser or request.user.role == 'ADMIN'):
            kwargs["queryset"] = Company.objects.filter(id=request.user.company.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Competition)
class CompetitionAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'creator', 'company_display')
    list_filter = ('start_date', 'end_date', 'creator__company',)
    search_fields = ('name', 'creator__username',)
    fields = ('name', 'start_date', 'end_date', 'creator',)
    
    def filter_by_company(self, qs, company):
        """Los usuarios solo ven competencias de su compañía"""
        return qs.filter(creator__company=company)
    
    def company_display(self, obj):
        """Muestra la compañía en la lista"""
        return obj.creator.company.name if obj.creator and obj.creator.company else '-'
    company_display.short_description = 'Empresa'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra opciones de creador"""
        if db_field.name == "creator" and not (request.user.is_superuser or request.user.role == 'ADMIN'):
            kwargs["queryset"] = CustomUser.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Vote)
class VoteAdmin(CompanyFilterMixin, admin.ModelAdmin):
    list_display = ('title', 'competition', 'voter', 'nominee', 'is_public', 'company_display')
    list_filter = ('competition', 'voter', 'nominee', 'is_public', 'competition__creator__company')
    search_fields = ('title', 'competition__name', 'voter__username', 'nominee__username',)
    fields = ('competition', 'title', 'description', 'award', 'is_public', 'voter', 'nominee',)
    
    def filter_by_company(self, qs, company):
        """Los usuarios solo ven votos de su compañía"""
        return qs.filter(competition__creator__company=company)
    
    def company_display(self, obj):
        """Muestra la compañía en la lista"""
        return obj.competition.creator.company.name if obj.competition.creator and obj.competition.creator.company else '-'
    company_display.short_description = 'Empresa'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra opciones de competencia, votante y nominado"""
        if not (request.user.is_superuser or request.user.role == 'ADMIN'):
            if db_field.name == "competition":
                kwargs["queryset"] = Competition.objects.filter(creator__company=request.user.company)
            elif db_field.name in ["voter", "nominee"]:
                kwargs["queryset"] = CustomUser.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

