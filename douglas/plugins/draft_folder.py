import os

from douglas import tools
from douglas.entries.base import EntryBase
from douglas.entries.fileentry import FileEntry


TRIGGER = 'draft'
INIT_KEY = 'draft_folder_file_initiated'


def is_trigger(pyhttp, config):
    trigger = config.get("draft_trigger", TRIGGER)
    if not trigger.startswith("/"):
        trigger = "/" + trigger

    return pyhttp["PATH_INFO"].startswith(trigger)


def cb_filelist(args):
    req = args['request']

    pyhttp = req.get_http()
    data = req.get_data()
    config = req.get_configuration()

    if not is_trigger(pyhttp, config):
        return

    data[INIT_KEY] = 1
    draftdir = config['draftdir']
    draftdir = draftdir.replace('/', os.sep)

    if not draftdir.endswith(os.sep):
        draftdir += os.sep

    if not os.path.exists(draftdir):
        return

    pathinfo = pyhttp.get("PATH_INFO", "")
    path, ext = os.path.splitext(pathinfo)
    draft_name = pyhttp["PATH_INFO"][len("/" + TRIGGER) + 1:]

    if not draft_name:
        trigger = config.get('draft_trigger', TRIGGER)

        entry = EntryBase(req)
        entry['title'] = 'Drafts'
        entry['filename'] = 'drafts'
        entry['file_path'] = 'drafts'
        entry._id = 'drafts'

        files = os.listdir(draftdir)

        baseurl = config.get('base_url', '')
        output = []
        output.append('<ul>')
        for fn in files:
            fn, ext = os.path.splitext(fn)
            output.append('<li><a href="%s/%s/%s.html">%s</a></li>' %
                          (baseurl, trigger, fn, fn))
        output.append('</ul>')
        entry.set_data('\n'.join(output))
        return [entry]

    # FIXME - need to do a better job of sanitizing
    draft_name = draft_name.replace(os.sep, '/')

    if draft_name.endswith(os.sep):
        draft_name = draft_name[:-1]
    if draft_name.find('/') > 0:
        draft_name = draft_name[draft_name.rfind('/'):]

    # If the draft has a theme, we use that. Otherwise we default to
    # the default theme.
    draft_name, theme = os.path.splitext(draft_name)
    if theme:
        data["theme"] = theme[1:]

    ext = tools.what_ext(data["extensions"].keys(), draftdir + draft_name)

    if not ext:
        return []

    data['root_datadir'] = draft_name + '.' + ext
    data['bl_type'] = 'file'
    filename = draftdir + draft_name + '.' + ext

    if not os.path.isfile(filename):
        return []

    fe = FileEntry(req, filename, draftdir)

    trigger = config.get("draft_trigger", TRIGGER)

    fe["absolute_path"] = trigger
    fe["fn"] = draft_name
    fe["file_path"] = trigger + "/" + draft_name

    # FIXME - this is icky
    config['blog_title'] = 'DRAFT : ' + config.get('blog_title', '')

    return [fe]


def cb_staticrender_filelist(args):
    req = args["request"]

    config = req.get_configuration()
    filelist = args["filelist"]

    draftdir = config['draftdir']
    draftdir = draftdir.replace('/', os.sep)

    if not draftdir.endswith(os.sep):
        draftdir += os.sep

    if not os.path.exists(draftdir):
        return

    drafts = os.listdir(draftdir)

    if not drafts:
        return

    themes = config.get('static_themes', ['html'])
    trigger = '/' + config.get('draft_trigger', TRIGGER)

    for mem in drafts:
        dir_, fn = os.path.split(mem)
        fn, ext = os.path.splitext(fn)
        for theme in themes:
            filelist.append((trigger + '/' + fn + '.' + theme, ''))
