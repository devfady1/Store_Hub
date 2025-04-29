from django import template

register = template.Library()

STATUS_MAP = {
    'pending': ('pending', 'pending'),
    'in_progress': ('processing', 'Processing'),
    'completed': ('completed', 'completed'),
    'cancelled': ('cancelled', 'cancelled'),
}

@register.filter
def status_class(value):
    return STATUS_MAP.get(value, ('unknown', ''))[0]

@register.filter
def status_label(value):
    return STATUS_MAP.get(value, ('', ''))[1]
