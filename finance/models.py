import secrets
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

class Household(models.Model):
    """A flexible group of people sharing a financial view."""
    name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=12, unique=True, editable=False, default="")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="households_created")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(8)[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Membership(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["household", "user"], name="unique_household_member")]
        ordering = ["joined_at"]

class Category(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=60)
    color = models.CharField(max_length=7, default="#5b7cfa", help_text="Hex color, e.g. #5b7cfa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["household", "name"], name="unique_category_per_household")]

    def __str__(self):
        return self.name

class Transaction(models.Model):
    PAYMENT_SOURCES = [
        ("upi", "UPI"),
        ("credit_card", "Credit card"),
        ("debit_account", "Debit account"),
        ("other", "Cash / other"),
    ]
    BANKS = [
        ("sbi", "SBI"),
        ("axis", "Axis Bank"),
        ("hsbc", "HSBC"),
        ("hdfc", "HDFC Bank"),
        ("icici", "ICICI Bank"),
        ("kotak", "Kotak Mahindra Bank"),
        ("other", "Other"),
    ]
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="finance_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.CharField(max_length=120)
    spent_on = models.DateField(db_index=True)
    payment_source = models.CharField(max_length=20, choices=PAYMENT_SOURCES, default="upi")
    bank_name = models.CharField(max_length=20, choices=BANKS, blank=True, default="")
    necessary = models.BooleanField("Do you think it's necessary to spend?", choices=[(True, "Yes"), (False, "No")])
    comment = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_on", "-created_at"]
        indexes = [models.Index(fields=["household", "spent_on"])]

    def __str__(self):
        return f"{self.description} — {self.amount}"

    def get_absolute_url(self):
        return reverse("transaction_detail", args=[self.pk])

class MonthlyGoal(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="goals")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="goals")
    month = models.DateField(help_text="Use the first day of the month")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        ordering = ["-month", "category__name"]
        constraints = [models.UniqueConstraint(fields=["household", "category", "month"], name="unique_monthly_category_goal")]

    def __str__(self):
        return f"{self.category}: {self.month:%B %Y}"
