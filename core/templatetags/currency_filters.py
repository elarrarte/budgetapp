from django import template

register = template.Library()


@register.filter
def format_amount(value):
    if value is None:
        return "0"
    if isinstance(value, str):
        value = value.replace(".", "")
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)
