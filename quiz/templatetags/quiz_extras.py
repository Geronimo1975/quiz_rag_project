# quiz/templatetags/quiz_extras.py
from django import template

register = template.Library()

@register.filter
def result_color(score):
    """Return Bootstrap color class based on score"""
    if score >= 80:
        return "success"
    elif score >= 60:
        return "warning"
    else:
        return "danger"

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    return float(value) * float(arg)

@register.filter
def divide(value, arg):
    """Divides the value by the argument"""
    return float(value) / float(arg)

@register.filter
def percentage(value, total):
    """Calculates what percentage value is of total"""
    return (float(value) / float(total)) * 100
