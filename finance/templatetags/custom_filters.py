from django import template
from builtins import abs as builtin_abs
from decimal import Decimal
from datetime import datetime

register = template.Library()


@register.filter
def to(value, arg):
    """
    Creates a range from value to arg (inclusive).
    Usage: {% for i in 1|to:5 %} will iterate from 1 to 5.
    """
    return range(int(value), int(arg) + 1)


@register.filter(name='absolute')
def absolute(value):
    """
    Returns the absolute value of a number.
    Usage: {{ value|absolute }}
    """
    try:
        return builtin_abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies the value by the argument.
    Usage: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
    
@register.filter
def get_range(start, end):
    return range(start, end)    


@register.filter(name='percentage')
def percentage(value, total):
    """
    Calculates the percentage of value against total.
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name='currency')
def currency(value, symbol='Shs.'):
    """
    Formats a number as currency with the given symbol.
    Usage: {{ value|currency:"$" }} or {{ value|currency }}
    """
    try:
        value = float(value)
        return f"{symbol} {value:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0.00"


@register.filter(name='month_name')
def month_name(month_number):
    """
    Returns the month name for a given month number.
    Usage: {{ 1|month_name }} returns "January"
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    try:
        index = int(month_number) - 1
        if 0 <= index < 12:
            return months[index]
        return ""
    except (ValueError, TypeError):
        return ""


@register.filter(name='format_date')
def format_date(value, format_string="%b %d, %Y"):
    """
    Formats a date with the specified format string.
    Usage: {{ value|format_date:"%Y-%m-%d" }}
    """
    if not value:
        return ""
    
    try:
        if isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%d")
        return value.strftime(format_string)
    except (ValueError, TypeError, AttributeError):
        return str(value)


@register.filter(name='trend_indicator')
def trend_indicator(value):
    """
    Returns a Bootstrap icon class based on whether the value is positive, negative, or zero.
    Usage: {{ value|trend_indicator }}
    """
    try:
        value = float(value)
        if value > 0:
            return "bi bi-arrow-up-circle-fill text-success"
        elif value < 0:
            return "bi bi-arrow-down-circle-fill text-danger"
        else:
            return "bi bi-dash-circle-fill text-secondary"
    except (ValueError, TypeError):
        return "bi bi-dash-circle-fill text-secondary"


@register.filter(name='percent_change')
def percent_change(current, previous):
    """
    Calculates the percentage change between current and previous values.
    Usage: {{ current|percent_change:previous }}
    """
    try:
        current = float(current)
        previous = float(previous)
        
        if previous == 0:
            if current > 0:
                return 100.0
            elif current == 0:
                return 0.0
            else:
                return -100.0
                
        return ((current - previous) / abs(previous)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0