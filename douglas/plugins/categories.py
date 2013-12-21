"""
Summary
=======

Walks through your blog root figuring out all the categories you have
and how many entries are in each category.  It generates html with
this information and stores it in the ``$(categorylinks)`` variable
which you can use in your head or foot templates.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.pycategories`` to the ``load_plugins`` list
   in your ``config.py`` file.


Configuration
=============

There is no configuration.


Usage
=====

Categories plugin provides an HTML version of the categories in a list
form. You can use it in your template like this::

    {{ categories.as_list()|safe }}


Alternatively, you can build the categories HTML yourself::

    {% for cat, count in categories.categorydata %}
        ....
    {% endfor %}

"""

__description__ = "Builds a list of categories."
__category__ = "category"
__license__ = "MIT"

import os

from douglas import tools


def parents(category):
    category = [cat for cat in category.split('/') if cat]
    for i in range(len(category) + 1):
        yield '/'.join(category[:i])


class CategoryManager(object):
    def __init__(self, request):
        self.request = request
        self._categorydata = None


    @property
    def categorydata(self):
        if self._categorydata is None:
            config = self.request.get_configuration()
            root = config["datadir"]

            # Build the list of all entries in the datadir
            entry_list = tools.get_entries(config, root)

            # Peel off the root dir from the list of entries
            entry_list = [mem[len(root) + 1:] for mem in entry_list]

            # Map categories to counts.
            category_map = {}
            for mem in entry_list:
                mem = os.path.dirname(mem)
                for par in parents(mem):
                    category_map[par] = category_map.get(par, 0) + 1

            self._categorydata = sorted(category_map.items())
        return self._categorydata

    def as_list(self):
        config = self.request.get_configuration()
        baseurl = config.get('base_url', '')

        start_t = '<ul class="categorygroup">'
        begin_t = '<li><ul class="categorygroup">'
        item_t = (
            '<li>'
            '<a href="%(base_url)s/%(fullcategory)sindex.%(theme)s">'
            '%(subcategory)s'
            '</a>'
            '(%(count)d)</li>')
        end_t = '</ul></li>'
        finish_t = '</ul>'

        theme = self.request.get_theme()

        categorydata = self.categorydata

        output = []
        indent = 0

        output.append(start_t)

        # Generate each item in the list
        for name, count in categorydata:
            namelist = name.split(os.sep)

            if not name:
                tab = ""
            else:
                tab = len(namelist) * "&nbsp;&nbsp;"

            if namelist != ['']:
                if indent > len(namelist):
                    for i in range(indent - len(namelist)):
                        output.append(end_t)

                elif indent < len(namelist):
                    for i in range(len(namelist) - indent):
                        output.append(begin_t)

            # Build the dict with the values for substitution
            d = {'base_url': baseurl,
                 'fullcategory': tools.urlencode_text(name + '/'),
                 'subcategory': tools.urlencode_text(namelist[-1] + '/'),
                 'theme': theme,
                 'count': count,
                 'indent': tab}

            # This prevents a double / in the root category url
            if name == '':
                d['fullcategory'] = name

            # Toss it in the thing
            output.append(item_t % d)

            if namelist != ['']:
                indent = len(namelist)

        output.append(end_t * indent)
        output.append(finish_t)

        # then we join the list and that's the final string
        return '\n'.join(output)


def cb_context_processor(args):
    context = args['context']
    request = args['request']
    context['categories'] = CategoryManager(request)
    return args
