from .models import Membership


def get_active_household(request):
    """Return the signed-in user's selected household, falling back to their first."""
    if hasattr(request, "_finance_active_household"):
        return request._finance_active_household
    household = None
    if request.user.is_authenticated:
        memberships = Membership.objects.filter(user=request.user).select_related("household")
        active_id = request.session.get("active_household_id")
        membership = memberships.filter(household_id=active_id).first() if active_id else None
        if membership is None:
            membership = memberships.first()
            if membership:
                request.session["active_household_id"] = membership.household_id
        household = membership.household if membership else None
    request._finance_active_household = household
    return household


def active_household_context(request):
    return {"active_household": get_active_household(request)}
