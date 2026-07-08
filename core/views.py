import calendar
from datetime import date

from django.contrib import messages
from django.db.models import Sum

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    BudgetAssignForm,
    BudgetForm,
    CategoryForm,
    CustomUserCreationForm,
    ExpenseForm,
)
from .models import Budget, Category, Expense, ExpenseInstallment, User


def is_admin(user):
    return user.is_staff


class CustomLoginView(LoginView):
    template_name = "core/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.force_password_change:
            return reverse("password_change")
        if user.is_staff:
            return reverse("admin_panel")
        return reverse("dashboard")


@login_required
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.force_password_change = False
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña cambiada correctamente.")
            if user.is_staff:
                return redirect("admin_panel")
            return redirect("dashboard")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "core/password_change.html", {"form": form})


@login_required
def toggle_theme(request):
    new = "light" if request.user.theme == "dark" else "dark"
    request.user.theme = new
    request.user.save(update_fields=["theme"])
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required
def set_accent(request, color):
    if color in ["primary", "danger", "warning", "success", "secondary"]:
        request.user.accent_color = color
        request.user.save(update_fields=["accent_color"])
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("admin_panel")
    budgets = request.user.budgets.all()
    now_local = timezone.localtime()
    current_month = now_local.month
    current_year = now_local.year

    budget_data = []
    for b in budgets:
        total = (
            ExpenseInstallment.objects.filter(
                expense__budget=b,
                effective_date__year=current_year,
                effective_date__month=current_month,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        budget_data.append({"budget": b, "month_total": total})

    return render(
        request,
        "core/dashboard.html",
        {
            "budget_data": budget_data,
            "current_month": current_month,
            "current_year": current_year,
        },
    )


@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    users = User.objects.filter(is_staff=False)
    budgets = Budget.objects.all()
    return render(
        request,
        "core/admin_panel.html",
        {"users": users, "budgets": budgets},
    )


@login_required
@user_passes_test(is_admin)
def admin_user_create(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.force_password_change = True
            user.save()
            messages.success(
                request, f"Usuario '{user.username}' creado correctamente."
            )
            return redirect("admin_panel")
    else:
        form = CustomUserCreationForm()
    return render(request, "core/admin_user_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def budget_list(request):
    budgets = Budget.objects.all()
    return render(request, "core/budget_list.html", {"budgets": budgets})


@login_required
@user_passes_test(is_admin)
def budget_create(request):
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.created_by = request.user
            budget.save()
            messages.success(
                request, f"Presupuesto '{budget.name}' creado correctamente."
            )
            return redirect("budget_list")
    else:
        form = BudgetForm()
    return render(request, "core/budget_form.html", {"form": form, "editing": False})


@login_required
@user_passes_test(is_admin)
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Presupuesto actualizado.")
            return redirect("budget_list")
    else:
        form = BudgetForm(instance=budget)
    return render(request, "core/budget_form.html", {"form": form, "editing": True})


@login_required
@user_passes_test(is_admin)
def budget_assign(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == "POST":
        form = BudgetAssignForm(request.POST, budget=budget)
        if form.is_valid():
            user = form.cleaned_data["user"]
            budget.members.add(user, through_defaults={"added_by": request.user})
            messages.success(
                request, f"Usuario '{user.username}' asignado a '{budget.name}'."
            )
            return redirect("budget_list")
    else:
        form = BudgetAssignForm(budget=budget)
    return render(
        request,
        "core/budget_assign.html",
        {"form": form, "budget": budget},
    )


@login_required
@user_passes_test(is_admin)
def budget_members(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    memberships = budget.budgetmembership_set.select_related("user", "added_by").all()
    return render(
        request,
        "core/budget_members.html",
        {"budget": budget, "memberships": memberships},
    )


@login_required
@user_passes_test(is_admin)
def budget_member_remove(request, pk, user_pk):
    budget = get_object_or_404(Budget, pk=pk)
    user = get_object_or_404(User, pk=user_pk)
    budget.members.remove(user)
    messages.success(request, f"Usuario '{user.username}' removido del presupuesto.")
    return redirect("budget_members", pk=pk)


def _get_budget_or_404(budget_pk, user):
    budget = get_object_or_404(Budget, pk=budget_pk)
    if not user.is_staff and not budget.members.filter(pk=user.pk).exists():
        raise Http404
    return budget


@login_required
def budget_dashboard(request, pk):
    budget = _get_budget_or_404(pk, request.user)
    now_local = timezone.localtime()
    m = request.GET.get("month")
    y = request.GET.get("year")
    if m and y:
        month, year = int(m), int(y)
        request.session[f"dash_month_{pk}"] = month
        request.session[f"dash_year_{pk}"] = year
    else:
        month = request.session.get(f"dash_month_{pk}", now_local.month)
        year = request.session.get(f"dash_year_{pk}", now_local.year)

    installments = ExpenseInstallment.objects.filter(
        expense__budget=budget,
        effective_date__year=year,
        effective_date__month=month,
    ).select_related(
        "expense", "expense__category", "expense__created_by"
    ).prefetch_related("expense__installments")

    total = sum(i.amount for i in installments)

    by_category_data = {}
    for inst in installments:
        cat_name = inst.expense.category.name if inst.expense.category else "Sin categoría"
        cat_color = inst.expense.category.color if inst.expense.category else "#6c757d"
        cat = by_category_data.setdefault(
            cat_name,
            {"total": 0, "count": 0, "color": cat_color},
        )
        cat["total"] += inst.amount
        cat["count"] += 1

    by_payment = {"cash": 0, "card": 0}
    for inst in installments:
        t = inst.expense.payment_type
        by_payment[t] = by_payment.get(t, 0) + inst.amount

    categories_data = [
        {
            "name": name,
            "total": data["total"],
            "count": data["count"],
            "percentage": round(data["total"] / total * 100, 1) if total else 0,
            "color": data["color"],
        }
        for name, data in sorted(by_category_data.items())
    ]

    return render(
        request,
        "core/budget_dashboard.html",
        {
            "budget": budget,
            "installments": installments,
            "categories_data": categories_data,
            "by_payment": by_payment,
            "total": total,
            "month": month,
            "year": year,
            "months": range(1, 13),
            "years": range(2020, 2031),
        },
    )


@login_required
def category_list(request, budget_pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    categories = budget.categories.all()
    return render(
        request,
        "core/category_list.html",
        {"budget": budget, "categories": categories},
    )


@login_required
def category_create(request, budget_pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.budget = budget
            cat.created_by = request.user
            cat.save()
            messages.success(request, f"Categoría '{cat.name}' creada.")
            return redirect("category_list", budget_pk=budget.pk)
    else:
        form = CategoryForm()
    return render(
        request,
        "core/category_form.html",
        {"form": form, "budget": budget, "editing": False},
    )


@login_required
def category_edit(request, budget_pk, pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    cat = get_object_or_404(Category, pk=pk, budget=budget)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada.")
            return redirect("category_list", budget_pk=budget.pk)
    else:
        form = CategoryForm(instance=cat)
    return render(
        request,
        "core/category_form.html",
        {"form": form, "budget": budget, "editing": True},
    )


@login_required
def category_delete(request, budget_pk, pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    cat = get_object_or_404(Category, pk=pk, budget=budget)
    cat.delete()
    messages.success(request, "Categoría eliminada.")
    return redirect("category_list", budget_pk=budget.pk)


@login_required
def expense_list(request, budget_pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    now_local = timezone.localtime()
    m = request.GET.get("month")
    y = request.GET.get("year")
    if m and y:
        month, year = int(m), int(y)
        request.session[f"exp_month_{budget_pk}"] = month
        request.session[f"exp_year_{budget_pk}"] = year
    else:
        month = request.session.get(f"exp_month_{budget_pk}", now_local.month)
        year = request.session.get(f"exp_year_{budget_pk}", now_local.year)

    expenses = Expense.objects.filter(
        budget=budget,
        expense_date__year=year,
        expense_date__month=month,
    ).select_related(
        "category", "created_by"
    ).prefetch_related("installments")

    return render(
        request,
        "core/expense_list.html",
        {
            "budget": budget,
            "expenses": expenses,
            "month": month,
            "year": year,
            "months": range(1, 13),
            "years": range(2020, 2031),
        },
    )


@login_required
def expense_create(request, budget_pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, budget=budget)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.created_by = request.user
            expense.save()
            if expense.payment_type == "card":
                n = form.cleaned_data["installments_total"]
                amount = form.cleaned_data["installment_amount"]
                _create_card_installments(expense, amount, n)
                messages.success(request, "Gasto con tarjeta registrado.")
            else:
                _create_cash_installment(expense, form.cleaned_data["amount"])
                messages.success(request, "Gasto registrado.")
            if "_addanother" in request.POST:
                return redirect("expense_create", budget_pk=budget.pk)
            return redirect("expense_list", budget_pk=budget.pk)
    else:
        form = ExpenseForm(budget=budget)
    return render(
        request,
        "core/expense_form.html",
        {"form": form, "budget": budget, "editing": False},
    )


def _create_cash_installment(expense, amount):
    ExpenseInstallment.objects.create(
        expense=expense,
        installment_number=1,
        amount=amount,
        effective_date=expense.expense_date,
    )


def _create_card_installments(expense, amount, n):
    d = expense.expense_date
    for i in range(1, n + 1):
        m = d.month + i
        y = d.year
        if m > 12:
            m -= 12
            y += 1
        last_day = calendar.monthrange(y, m)[1]
        day = min(d.day, last_day)
        effective_date = date(y, m, day)
        ExpenseInstallment.objects.create(
            expense=expense,
            installment_number=i,
            amount=amount,
            effective_date=effective_date,
        )


@login_required
def expense_edit(request, budget_pk, pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense, budget=budget)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.save()
            expense.installments.all().delete()
            if expense.payment_type == "card":
                n = form.cleaned_data["installments_total"]
                amount = form.cleaned_data["installment_amount"]
                _create_card_installments(expense, amount, n)
            else:
                _create_cash_installment(expense, form.cleaned_data["amount"])
            messages.success(request, "Gasto actualizado.")
            return redirect("expense_list", budget_pk=budget.pk)
    else:
        form = ExpenseForm(instance=expense, budget=budget)
    return render(
        request,
        "core/expense_form.html",
        {"form": form, "budget": budget, "editing": True, "expense": expense},
    )


@login_required
def expense_delete(request, budget_pk, pk):
    budget = _get_budget_or_404(budget_pk, request.user)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)
    expense.delete()
    messages.success(request, "Gasto eliminado.")
    return redirect("expense_list", budget_pk=budget.pk)



