from django import template

register = template.Library()

@register.filter
def divisible(value, arg):
    """Divide the value by arg and return the result"""
    try:
        return (float(value) / float(arg)) * 100
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def percentage(value):
    """Format a number as a percentage"""
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0%"