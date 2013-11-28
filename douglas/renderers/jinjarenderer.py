import os.path

from jinja2 import BaseLoader, Environment, TemplateNotFound

from douglas.renderers.base import RendererBase
from douglas.tools import run_callback


class ThemeLoader(BaseLoader):
    def __init__(self, themepath):
        self.path = themepath

    def get_source(self, environment, template):
        path = os.path.join(self.path, template)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)


def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    return template_name.endswith(('.html', '.htm', 'xml', 'rss'))


class Renderer(RendererBase):
    def build_context(self):
        """Returns a context consisting of filters and variables"""
        parsevars = dict()
        parsevars.update(self._request.config)
        parsevars.update(self._request.data)
        return parsevars

    def get_content_type(self, themedir, theme):
        path = os.path.join(themedir, theme, 'content_type')
        if os.path.exists(path):
            return open(path, 'r').read().strip()
        return 'text/html'

    def render(self, render_headers=True):
        """
        Do final rendering.

        :arg render_headers: whether (True) or not (False) to show the
            headers
        """
        # if we've already rendered, then we don't want to do so again
        if self.rendered:
            return

        config = self._request.get_configuration()
        data = self._request.get_data()

        themedir = config.get('themedir')
        theme = data.get("theme") or "html"

        data['content-type'] = self.get_content_type(themedir, theme)

        if render_headers:
            self.add_header('Content-type', data['content-type'])
            self.show_headers()

        if self._content:
            content = self._content
            if not isinstance(content, list):
                content = [content]

            context = self.build_context()
            context['content'] = content

            # Allow plugins to alter the context adding additional
            # bits
            args = {'context': context}
            args = run_callback(
                "context_processor",
                args,
                mappingfunc=lambda x,y:y,
                defaultfunc=lambda x:x)

            context = args['context']

            env = Environment(
                autoescape=guess_autoescape,
                loader=ThemeLoader(os.path.join(themedir, theme)),
                extensions=['jinja2.ext.autoescape']
            )
            template = env.get_template('index.' + theme)
            self.write(template.render(context))

        self.rendered = 1
