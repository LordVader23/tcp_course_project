from django import template

register = template.Library()


@register.filter
def modulo(num, val):
    return num % val


@register.filter
def div_nr(num, val):
    return num // val


@register.filter
def multi(num, val):
    return num * val
