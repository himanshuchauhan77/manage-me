from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Household, MonthlyGoal, Transaction

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ("name",)

class JoinHouseholdForm(forms.Form):
    invite_code = forms.CharField(max_length=12)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "color")
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ("category", "amount", "description", "spent_on", "payment_source", "bank_name", "necessary", "comment")
        labels = {"payment_source": "Debit source", "bank_name": "Bank (optional for cash / other)"}
        widgets = {"spent_on": forms.DateInput(attrs={"type": "date"}), "comment": forms.Textarea(attrs={"rows": 3})}

class MonthlyGoalForm(forms.ModelForm):
    class Meta:
        model = MonthlyGoal
        fields = ("category", "month", "amount")
        widgets = {"month": forms.DateInput(attrs={"type": "date"})}
