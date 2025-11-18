from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css):
    # Evita erro se receber SafeString ou HTML
    try:
        existing = field.field.widget.attrs.get("class", "")
    except AttributeError:
        return field

    new_classes = f"{existing} {css}".strip()
    return field.as_widget(attrs={"class": new_classes})


@register.filter(name='add_placeholder')
def add_placeholder(field, text):
    # Mesma proteção contra SafeString
    try:
        widget = field.field.widget
    except AttributeError:
        return field

    return field.as_widget(attrs={
        **widget.attrs,
        "placeholder": text
    })
