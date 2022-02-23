import jinja2
import markupsafe
import wtforms

FIELD_TEMPLATE = jinja2.Template("""<div class="field">
{% for error in form.errors[field] %}
  <div class="error">{{ error }}</div>
{% endfor %}
  {{ form[field].label }}
{% if form[field].description %}
  <div class="hint">{{ form[field].description }}</div>
{% endif %}
  {{ form[field] }}
</div>
""")

CHECK_TEMPLATE = jinja2.Template("""
{% if form[field].description %}
  <p class="hint">{{ form[field].description }}</p>
{% endif %}
<div class="check field">
{% for error in form.errors[field] %}
  <div class="error">{{ error }}</div>
{% endfor %}
  {{ form[field] }}{{ form[field].label }}
</div>
""")

def init_app(app):
    @app.template_filter('datetime')
    def datetime(value, format='%Y-%m-%d at %H:%M:%S'):
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('field')
    def field(form, field):
        if isinstance(form[field], wtforms.BooleanField):
            template = CHECK_TEMPLATE
        else:
            template = FIELD_TEMPLATE
        text = template.render(form=form, field=field)
        return markupsafe.Markup(text)

    @app.template_filter('float')
    def floot(value, decimals=2):
        if value is None:
            return ''
        f = '{:.%df}' % decimals
        return f.format(value)

    # https://stackoverflow.com/a/39596504
    suffixes = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']

    @app.template_filter('ordinal')
    def ordinal(number):
        if 10 < number % 100 < 14:
            return str(number) + 'th'
        return str(number) + suffixes[number % 10]

    @app.template_filter('percent')
    def percent(number):
        if number is None:
            return ''
        return str(round(number * 100)) + '%'
