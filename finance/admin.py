from django.contrib import admin
from .models import Category, Household, Membership, MonthlyGoal, Transaction

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name", "created_by__username")
    readonly_fields = ("invite_code", "created_at")
    inlines = (MembershipInline,)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("description", "amount", "category", "household", "created_by", "spent_on", "necessary")
    list_filter = ("household", "category", "necessary", "spent_on")
    search_fields = ("description", "comment", "created_by__username")

admin.site.register(Category)
admin.site.register(MonthlyGoal)
