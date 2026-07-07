from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Budget, Category, Expense, ExpenseInstallment, User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["email"].label = "Correo electrónico"
        self.fields["email"].required = False
        self.fields["password1"].label = "Contraseña temporal"
        self.fields["password2"].label = "Confirmar contraseña temporal"


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ("name", "description")
        labels = {
            "name": "Nombre del presupuesto",
            "description": "Descripción",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class BudgetAssignForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Usuario",
    )

    def __init__(self, *args, **kwargs):
        budget = kwargs.pop("budget", None)
        super().__init__(*args, **kwargs)
        already_members = User.objects.none()
        if budget:
            already_members = budget.members.all()
        self.fields["user"].queryset = User.objects.exclude(
            pk__in=already_members.values("pk")
        ).exclude(is_superuser=True)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
        labels = {"name": "Nombre de la categoría"}


class ExpenseForm(forms.ModelForm):
    installments_total = forms.IntegerField(
        required=False,
        min_value=1,
        label="Cantidad de cuotas",
        initial=1,
    )

    class Meta:
        model = Expense
        fields = (
            "description",
            "category",
            "expense_date",
            "payment_type",
            "total_amount",
        )
        labels = {
            "description": "Descripción",
            "category": "Categoría",
            "expense_date": "Fecha del gasto",
            "payment_type": "Tipo de pago",
            "total_amount": "Monto total",
        }
        widgets = {
            "expense_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        budget = kwargs.pop("budget", None)
        super().__init__(*args, **kwargs)
        if budget:
            self.fields["category"].queryset = budget.categories.all()
        if not self.instance.pk:
            self.fields["payment_type"].initial = "cash"


class InstallmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        n = kwargs.pop("n", 1)
        super().__init__(*args, **kwargs)
        for i in range(1, n + 1):
            self.fields[f"installment_{i}"] = forms.DecimalField(
                max_digits=12,
                decimal_places=2,
                label=f"Monto cuota {i}",
            )


class DateRangeForm(forms.Form):
    date_from = forms.DateField(
        label="Desde",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label="Hasta",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
