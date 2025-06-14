from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Custom template filter to get a value from a dictionary."""
    return dictionary.get(key, '')