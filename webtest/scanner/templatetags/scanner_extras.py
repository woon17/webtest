from django import template
import json

register = template.Library()

@register.filter(name='stringToDict')
def stringToDict(value):
    if isinstance(value, str):
        return json.loads(value).items
    return value.items
