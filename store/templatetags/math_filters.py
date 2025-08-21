from django import template
register = template.Library()

@register.filter(name="sub")
def sub(a, b):
    """Return a - b (formatted to 2 decimal places)."""
    try:
        result = float(a) - float(b)
        return f"{result:.2f}"
    except (TypeError, ValueError):
        return "0.00"