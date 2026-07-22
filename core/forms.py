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
    def __init__(self, *args, **kwargs):
        self.budget = kwargs.pop("budget", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = ("name", "color")
        labels = {"name": "Nombre de la categoría", "color": "Color"}
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if name and self.budget:
            qs = Category.objects.filter(name__iexact=name, budget=self.budget)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error(
                    "name",
                    "Ya existe una categoría con este nombre en el presupuesto.",
                )
        return cleaned_data


class ExpenseForm(forms.ModelForm):
    amount = forms.CharField(
        required=False, label="Monto",
    )
    installments_total = forms.IntegerField(
        required=False,
        min_value=1,
        label="Cantidad de cuotas",
        initial=1,
        widget=forms.HiddenInput(),
    )
    installment_amount = forms.CharField(
        required=False,
        label="Monto por cuota",
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Expense
        fields = (
            "description",
            "category",
            "expense_date",
            "payment_type",
        )
        labels = {
            "description": "Descripción",
            "category": "Categoría",
            "expense_date": "Fecha de creación",
            "payment_type": "Tipo de pago",
        }
        widgets = {
            "expense_date": forms.DateInput(attrs={"placeholder": "dd/mm/aaaa"}),
        }

    def __init__(self, *args, **kwargs):
        budget = kwargs.pop("budget", None)
        super().__init__(*args, **kwargs)
        if budget:
            self.fields["category"].queryset = budget.categories.all()
        if not self.instance.pk:
            self.fields["payment_type"].initial = "cash"
        if self.instance.pk:
            installments = self.instance.installments.all()
            if installments:
                first = installments.first()
                if self.instance.payment_type == "card":
                    self.fields["installments_total"].initial = installments.count()
                    self.fields["installment_amount"].initial = first.amount
                else:
                    self.fields["amount"].initial = first.amount

    def clean_amount(self):
        value = self.cleaned_data.get("amount")
        if not value:
            return None
        try:
            return int(str(value).replace(".", ""))
        except (ValueError, TypeError):
            return value

    def clean_installment_amount(self):
        value = self.cleaned_data.get("installment_amount")
        if not value:
            return None
        try:
            return int(str(value).replace(".", ""))
        except (ValueError, TypeError):
            return value

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get("payment_type")
        amount = cleaned_data.get("amount")
        n = cleaned_data.get("installments_total")
        if payment_type == "card":
            inst_amount = cleaned_data.get("installment_amount")
            if not n or not inst_amount:
                raise forms.ValidationError(
                    "Para pagos con tarjeta debe indicar cantidad de cuotas y monto por cuota."
                )
        elif not amount:
            raise forms.ValidationError("Debe indicar el monto.")
        return cleaned_data

