from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    force_password_change = models.BooleanField(default=True)
    theme = models.CharField(
        max_length=10,
        default="dark",
        choices=[("dark", "Oscuro"), ("light", "Claro")],
        verbose_name="tema",
    )
    accent_color = models.CharField(
        max_length=10,
        default="primary",
        choices=[
            ("primary", "Azul"),
            ("danger", "Rojo"),
            ("warning", "Naranja"),
            ("success", "Verde"),
            ("violet", "Violeta"),
            ("secondary", "Gris"),
        ],
        verbose_name="color de acento",
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"


class Budget(models.Model):
    name = models.CharField(max_length=200, verbose_name="nombre")
    description = models.TextField(blank=True, verbose_name="descripción")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_budgets",
        verbose_name="creado por"
    )
    members = models.ManyToManyField(
        User, through="BudgetMembership", through_fields=("budget", "user"),
        related_name="budgets"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado el")

    class Meta:
        verbose_name = "presupuesto"
        verbose_name_plural = "presupuestos"

    def __str__(self):
        return self.name


class BudgetMembership(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="added_memberships",
        verbose_name="agregado por"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="agregado el")

    class Meta:
        unique_together = ("budget", "user")
        verbose_name = "membresía"
        verbose_name_plural = "membresías"

    def __str__(self):
        return f"{self.user} → {self.budget}"


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="nombre")
    color = models.CharField(max_length=7, default="#000000", verbose_name="color")
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name="categories"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado el")

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        unique_together = ("name", "budget")

    def __str__(self):
        return f"{self.name} ({self.budget.name})"


class Expense(models.Model):
    PAYMENT_CASH = "cash"
    PAYMENT_CARD = "card"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Efectivo"),
        (PAYMENT_CARD, "Tarjeta"),
    ]

    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name="expenses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="expenses"
    )
    description = models.CharField(max_length=300, verbose_name="descripción")
    expense_date = models.DateField(verbose_name="fecha del gasto")
    payment_type = models.CharField(
        max_length=4, choices=PAYMENT_CHOICES, verbose_name="tipo de pago"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado el")

    @property
    def installment_amount(self):
        inst = self.installments.first()
        return inst.amount if inst else 0

    class Meta:
        verbose_name = "gasto"
        verbose_name_plural = "gastos"
        ordering = ["-expense_date"]

    def __str__(self):
        return f"{self.description}"


class ExpenseInstallment(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="installments"
    )
    installment_number = models.PositiveSmallIntegerField(
        verbose_name="número de cuota"
    )
    amount = models.IntegerField(verbose_name="monto")
    effective_date = models.DateField(verbose_name="fecha efectiva")

    class Meta:
        verbose_name = "cuota"
        verbose_name_plural = "cuotas"
        ordering = ["effective_date", "installment_number"]

    def __str__(self):
        return f"Cuota {self.installment_number} de {self.expense.description}"
