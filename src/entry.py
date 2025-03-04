import os
import webbrowser
from threading import Timer

from app import app

debug = True


def open_browser() -> None:
    # XXX: runs twice without this check
    # https://stackoverflow.com/a/9476701
    if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new_tab('http://localhost:8050')


if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=debug)
