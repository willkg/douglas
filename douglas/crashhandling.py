"""
This module has the code for handling crashes.

.. Note::

   This is a leaf node module! It should never import other Douglas
   modules or packages.
"""

import StringIO
import cgi
import sys
import traceback

_e = cgi.escape


class Response(object):
    """This is a minimal response that is returned by the crash
    handler.
    """
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

        self.seek = body.seek
        self.read = body.read


class CrashHandler(object):
    def __init__(self, httpresponse=False, environ=None):
        """
        :arg httpresponse: boolean representing whether when
            handling a crash, we do http response headers
        """
        self.httpresponse = httpresponse

        if environ:
            self.environ = environ
        else:
            self.environ = {}

    def __call__(self, exc_type, exc_value, exc_tb):
        response = self.handle(exc_type, exc_value, exc_tb)
        if self.httpresponse:
            response.headers.append(
                "Content-Length: {0}".format(self.httpresponse.body.len))
        sys.output.write("HTTP/1.0 {0}\n".format(response.status))
        for key, val in response.headers.items():
            sys.output.write("{0}: {1}\n".format(key, val))
        sys.output.write("\n")
        sys.output.write(response.body.read())
        sys.output.flush()

    def handle_by_response(self, exc_type, exc_value, exc_tb):
        """Returns a basic response object holding crash information
        for display.
        """
        headers = {}
        output = StringIO.StringIO()

        headers["Content-Type"] = "text/html"
        # FIXME - are there other userful headers?

        try:
            import douglas
            version = douglas.__version__
        except:
            version = "unknown"

        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

        http_environ = ""
        for key, val in self.environ.items():
            http_environ += "{0}: {1}\n".format(_e(repr(key)), _e(repr(val)))

        output.write("""
        <html>
        <head>
        <title>HTTP 500: Oops!</title>
        </head>
        <body>
        <h1>HTTP 500: GAH!</h1>
        <p>
        A problem has occurred while Douglas was rendering
        this page.
        </p>
        <p>
        If this is your blog and you've just upgraded Douglas,
        check the documentation for changes you need to make to your
        config.py, douglas.cgi, blog.ini, plugins, and theme
        files.
        </p>
        <p>
        Here is some useful information to track down the root cause
        of the problem:
        </p>
        <div style="border: 1px solid black; padding: 10px;">

        <p>Douglas version: {version}</p>
        <p>Python version: {python_version}</p>
        <p>Error traceback:</p>
        <pre>
        {traceback}
        </pre>

        <p>HTTP environment:</p>
        <pre>
        {http_environ}
        </pre>
        </div>
        </body>
        </html>
        """.format(
            version=_e(version),
            python_version=_e(sys.version),
            traceback=tb,
            http_environ=http_environ))

        headers["Content-Length"] = str(output.len)
        return Response("500 Server Error", headers, output)


def enable_excepthook(httpresponse=False):
    """This attaches the crashhandler to the sys.excepthook.
    This will handle any exceptions thrown that don't get
    handled anywhere else.

    If you're running Douglas as a WSGI application or as a CGI
    script, you should create a ``CrashHandler`` instance and call
    ``handle_by_response`` directly.  See douglas.app.DouglasWSGIApp.

    """
    sys.excepthook = CrashHandler(httpresponse=httpresponse)
