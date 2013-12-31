#!/usr/bin/env python

# -u turns off character translation to allow transmission
# of gzip compressed content on Windows and OS/2
#!/path/to/python -u

import os
import sys

# Uncomment this line to add the directory your config.py file is in to the
# Python path:
#sys.path.append("%(basedir)s")

# Uncomment this line to add the Douglas codebase directory to the Python
# path in the case that Douglas isn't already on the Python path:
#sys.path.append("/path/to/douglas")


# -------------------------------------------------------
# You shouldn't have to adjust anything below this point.
# -------------------------------------------------------



# this allows for a config.py override
script = os.environ.get('SCRIPT_FILENAME', None)
if script is not None:
    script = script[0:script.rfind("/")]
    sys.path.insert(0, script)

# this allows for grabbing the config based on the DocumentRoot
# setting if you're using apache
root = os.environ.get('DOCUMENT_ROOT', None)
if root is not None:
    sys.path.insert(0, root)

# Settings are now in config.py, you should disable access to it by htaccess
# (make it executable or deny access)
from config import py as cfg

from douglas.app import run_cgi

if __name__ == '__main__':
    run_cgi(cfg)
