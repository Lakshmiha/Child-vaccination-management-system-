from django import template

register = template.Library()

@register.filter
def filter_by_status(appointments, status):
    """
    Returns items whose .status equals the given status.
    Works with QuerySets or lists.
    """
    if not appointments:
        return []
    try:
        return [a for a in appointments if getattr(a, "status", None) == status]
    except Exception:
        return []