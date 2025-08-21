from django import template
from store.models import Category

register = template.Library()

@register.simple_tag
def category():
    return Category.objects.filter(parent=None)
    
