"""
Session definitions for nox.

Run ``nox -l`` to obtain a list of all sessions.
Run ``nox -s <session_name>`` to run a specific session.
"""
import nox

@nox.session
def run(ctx: nox.Session) -> None:
    """Run the web page using the Python http server."""
    ctx.run('python', 'scripts/serve_and_browse.py', 'static/index.html')
