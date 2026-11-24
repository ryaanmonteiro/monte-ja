from django import template

register = template.Library()


@register.filter
def estrelas(nota):
    """Converte 4 em '★★★★☆'."""
    try:
        n = max(0, min(5, int(nota)))
    except (TypeError, ValueError):
        n = 0
    return "★" * n + "☆" * (5 - n)
