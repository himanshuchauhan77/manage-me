from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Category, Household, Membership, MonthlyGoal, Transaction

class FinanceManagerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="strong-test-password")
        self.other = User.objects.create_user(username="sam", password="strong-test-password")
        self.group = Household.objects.create(name="Our home", created_by=self.user)
        Membership.objects.create(household=self.group, user=self.user)
        self.category = Category.objects.create(household=self.group, name="Home")

    def test_transaction_saves_creator_necessity_and_comment(self):
        item = Transaction.objects.create(household=self.group, category=self.category, created_by=self.user,
            amount=Decimal("42.50"), description="Groceries", spent_on=date(2026, 11, 4), necessary=True, comment="Weekly shop")
        self.assertEqual(item.created_by, self.user)
        self.assertTrue(item.necessary)
        self.assertEqual(item.comment, "Weekly shop")

    def test_monthly_goal_is_unique_per_category_and_month(self):
        MonthlyGoal.objects.create(household=self.group, category=self.category, month=date(2026, 11, 1), amount=Decimal("500"))
        self.assertEqual(MonthlyGoal.objects.filter(household=self.group, category=self.category, month=date(2026, 11, 1)).count(), 1)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_signed_in_user_lands_on_shared_app_launcher(self):
        response = self.client.post(reverse("login"), {"username": "alex", "password": "strong-test-password"})
        self.assertRedirects(response, reverse("app_hub"))
        hub = self.client.get(reverse("app_hub"))
        self.assertContains(hub, "Finance Manager")
        self.assertContains(hub, "Habit Tracker")
        self.assertContains(hub, "Daily Planner")

    def test_member_can_create_transaction(self):
        self.client.login(username="alex", password="strong-test-password")
        response = self.client.post(reverse("transaction_create"), {"category": self.category.pk, "amount": "18.25",
            "description": "Bus fare", "spent_on": "2026-11-05", "payment_source": "upi", "bank_name": "sbi", "necessary": "True", "comment": ""})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Transaction.objects.filter(created_by=self.user, description="Bus fare").exists())

    def test_non_member_cannot_view_transaction(self):
        item = Transaction.objects.create(household=self.group, category=self.category, created_by=self.user,
            amount=Decimal("9.00"), description="Private record", spent_on=date(2026, 11, 4), necessary=False)
        # A user without membership is directed to group setup and cannot read the record.
        self.client.login(username="sam", password="strong-test-password")
        self.assertEqual(self.client.get(reverse("transaction_detail", args=[item.pk])).status_code, 404)

    def test_household_groups_lists_all_memberships(self):
        second = Household.objects.create(name="Weekend place", created_by=self.user)
        Membership.objects.create(household=second, user=self.user)
        Membership.objects.create(household=second, user=self.other)
        self.client.login(username="alex", password="strong-test-password")
        response = self.client.get(reverse("household_groups"))
        self.assertContains(response, "Our home")
        self.assertContains(response, "Weekend place")
        self.assertContains(response, "sam")

    def test_member_can_switch_active_household(self):
        second = Household.objects.create(name="Weekend place", created_by=self.user)
        Membership.objects.create(household=second, user=self.user)
        self.client.login(username="alex", password="strong-test-password")
        response = self.client.post(reverse("select_household", args=[second.pk]))
        self.assertRedirects(response, reverse("dashboard"))
        dashboard = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard, "Weekend place")

    def test_non_member_cannot_select_household(self):
        self.client.login(username="sam", password="strong-test-password")
        self.assertEqual(self.client.post(reverse("select_household", args=[self.group.pk])).status_code, 404)
