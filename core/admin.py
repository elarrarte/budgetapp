from django.contrib import admin

from .models import Budget, BudgetMembership, Category, Expense, ExpenseInstallment, User

admin.site.register(User)
admin.site.register(Budget)
admin.site.register(BudgetMembership)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(ExpenseInstallment)
