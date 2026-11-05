from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CategoryForm, HouseholdForm, JoinHouseholdForm, MonthlyGoalForm, SignUpForm, TransactionForm
from .context import get_active_household
from .models import Category, Household, Membership, MonthlyGoal, Transaction

@login_required
def app_hub(request):
    return render(request, "finance/app_hub.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("app_hub")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("app_hub")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def household_setup(request):
    create_form, join_form = HouseholdForm(prefix="create"), JoinHouseholdForm(prefix="join")
    if request.method == "POST" and "create-name" in request.POST:
        create_form = HouseholdForm(request.POST, prefix="create")
        if create_form.is_valid():
            household = create_form.save(commit=False)
            household.created_by = request.user
            household.save()
            Membership.objects.create(household=household, user=request.user)
            for name, color in [("Home", "#6c7cf4"), ("Utilities", "#f3a858"), ("Personal", "#38a58b")]:
                Category.objects.create(household=household, name=name, color=color)
            request.session["active_household_id"] = household.pk
            return redirect("dashboard")
    elif request.method == "POST":
        join_form = JoinHouseholdForm(request.POST, prefix="join")
        if join_form.is_valid():
            household = Household.objects.filter(invite_code__iexact=join_form.cleaned_data["invite_code"].strip()).first()
            if household:
                Membership.objects.get_or_create(household=household, user=request.user)
                request.session["active_household_id"] = household.pk
                return redirect("dashboard")
            join_form.add_error("invite_code", "No group matches that invite code.")
    return render(request, "finance/household_setup.html", {"create_form": create_form, "join_form": join_form})


@login_required
def household_groups(request):
    active_household = get_active_household(request)
    memberships = Membership.objects.filter(user=request.user).select_related("household").prefetch_related("household__memberships__user")
    active_id = active_household.pk if active_household else None
    return render(request, "finance/household_groups.html", {"memberships": memberships, "active_id": active_id})


@login_required
@require_POST
def select_household(request, pk):
    membership = get_object_or_404(Membership, user=request.user, household_id=pk)
    request.session["active_household_id"] = membership.household_id
    messages.success(request, f"Switched to {membership.household.name}.")
    return redirect("dashboard")


@login_required
def dashboard(request):
    household = get_active_household(request)
    if not household:
        return redirect("household_groups")
    today = timezone.localdate()
    month_start = today.replace(day=1)
    transactions = Transaction.objects.filter(household=household, spent_on__year=today.year, spent_on__month=today.month).select_related("category", "created_by")
    total = transactions.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    category_rows = []
    for category in Category.objects.filter(household=household):
        spent = transactions.filter(category=category).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        goal = MonthlyGoal.objects.filter(household=household, category=category, month=month_start).first()
        category_rows.append({"category": category, "spent": spent, "goal": goal.amount if goal else None,
                              "percent": min(int(spent / goal.amount * 100), 100) if goal and goal.amount else 0})
    return render(request, "finance/dashboard.html", {"household": household, "total": total, "category_rows": category_rows,
        "recent": Transaction.objects.filter(household=household).select_related("category", "created_by")[:8],
        "month_label": today.strftime("%B %Y"), "members": household.memberships.select_related("user")})


@login_required
def transaction_list(request):
    household = get_active_household(request)
    if not household: return redirect("household_groups")
    items = Transaction.objects.filter(household=household).select_related("category", "created_by")
    return render(request, "finance/transactions.html", {"transactions": items})


@login_required
def transaction_create(request):
    household = get_active_household(request)
    if not household: return redirect("household_groups")
    form = TransactionForm(request.POST or None)
    form.fields["category"].queryset = Category.objects.filter(household=household)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.household, item.created_by = household, request.user
        item.save()
        messages.success(request, "Transaction saved.")
        return redirect("dashboard")
    return render(request, "finance/form.html", {"form": form, "title": "Add transaction"})


@login_required
def transaction_detail(request, pk):
    item = get_object_or_404(Transaction.objects.select_related("category", "created_by"), pk=pk, household=get_active_household(request))
    return render(request, "finance/transaction_detail.html", {"item": item})


@login_required
def transaction_edit(request, pk):
    household = get_active_household(request)
    item = get_object_or_404(Transaction, pk=pk, household=household)
    form = TransactionForm(request.POST or None, instance=item)
    form.fields["category"].queryset = Category.objects.filter(household=household)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("transaction_detail", pk=item.pk)
    return render(request, "finance/form.html", {"form": form, "title": "Edit transaction"})


@login_required
@require_POST
def transaction_delete(request, pk):
    get_object_or_404(Transaction, pk=pk, household=get_active_household(request)).delete()
    messages.success(request, "Transaction deleted.")
    return redirect("transaction_list")


@login_required
def category_list(request):
    household = get_active_household(request)
    if not household: return redirect("household_groups")
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False); category.household = household; category.save()
        return redirect("category_list")
    return render(request, "finance/categories.html", {"categories": Category.objects.filter(household=household), "form": form})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, household=get_active_household(request))
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid(): form.save(); return redirect("category_list")
    return render(request, "finance/form.html", {"form": form, "title": "Edit category"})


@login_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, household=get_active_household(request))
    if category.transactions.exists():
        messages.error(request, "This category has transactions. Remove those transactions before deleting it.")
        return redirect("category_list")
    category.delete()
    return redirect("category_list")


@login_required
def goal_list(request):
    household = get_active_household(request)
    if not household: return redirect("household_groups")
    form = MonthlyGoalForm(request.POST or None)
    form.fields["category"].queryset = Category.objects.filter(household=household)
    if request.method == "POST" and form.is_valid():
        goal = form.save(commit=False); goal.household = household; goal.month = goal.month.replace(day=1)
        MonthlyGoal.objects.update_or_create(household=household, category=goal.category, month=goal.month, defaults={"amount": goal.amount})
        return redirect("goal_list")
    return render(request, "finance/goals.html", {"goals": MonthlyGoal.objects.filter(household=household).select_related("category"), "form": form})


@login_required
@require_POST
def goal_delete(request, pk):
    get_object_or_404(MonthlyGoal, pk=pk, household=get_active_household(request)).delete()
    return redirect("goal_list")


@login_required
def analytics(request):
    household = get_active_household(request)
    if not household: return redirect("household_groups")
    today = timezone.localdate()
    months = []
    for offset in range(5, -1, -1):
        month_index = today.year * 12 + today.month - 1 - offset
        year, month0 = divmod(month_index, 12); month = month0 + 1
        amount = Transaction.objects.filter(household=household, spent_on__year=year, spent_on__month=month).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        goal = MonthlyGoal.objects.filter(household=household, month=date(year, month, 1)).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        months.append({"label": date(year, month, 1).strftime("%b"), "spent": amount, "goal": goal})
    scale = max([max(row["spent"], row["goal"]) for row in months] or [Decimal("1")])
    for row in months:
        row["spent_pct"] = max(2, int(row["spent"] / scale * 100))
        row["goal_pct"] = max(2, int(row["goal"] / scale * 100))
    return render(request, "finance/analytics.html", {"months": months, "household": household})
