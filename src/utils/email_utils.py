from jinja2 import Environment, FileSystemLoader, select_autoescape


def send_template_email(**kwargs):
    """Sends an email using a template."""
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("index.html")
    return template.render(**kwargs)
