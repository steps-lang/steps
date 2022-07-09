"""
Session definitions for nox.

Run ``nox -l`` to obtain a list of all sessions.
Run ``nox -s <session_name>`` to run a specific session.
"""
import multiprocessing
import pathlib
import shutil
import subprocess
import typing

import nox



STATIC_DIRECTORY: pathlib.Path = pathlib.Path('.') / 'static'
SITE_DIRECTORY: pathlib.Path = pathlib.Path('.') / 'target' / 'site'
DIST_DIRECTORY: pathlib.Path = pathlib.Path('.') / 'target' / 'dist'
TEST_REPORT_DIRECTORY: pathlib.Path = pathlib.Path('.') / 'target' / 'test'
LINT_REPORT_DIRECTORY: pathlib.Path = pathlib.Path('.') / 'target' / 'lint'

def run_python_module(
        ctx: nox.Session,
        module_name: str,
        *args: typing.Any,
) -> None:
    """Run a Python module with the given arguments."""
    python_command: str = 'python'
    python_args: typing.List[str] = []
    python_args += ['-m', module_name]
    python_args += map(str, args)
    if ctx is None:
        subprocess.run([python_command] + python_args)
    else:
        ctx.run(python_command, *python_args)

def do_build_wheel(ctx: nox.Session) -> None:
    """Build a wheel package."""
    ctx.install('build')
    output_directory: pathlib.Path = DIST_DIRECTORY
    output_directory.mkdir(parents = True, exist_ok = True)
    run_python_module(ctx, 'build', '-o', output_directory)

@nox.session
def run_web(ctx: nox.Session) -> None:
    """Run the web page using the Python http server."""
    port: int = 8000
    directory: pathlib.Path = SITE_DIRECTORY

    #run_python_module(ctx, 'http.server', '--directory', directory, port)
    httpd = multiprocessing.Process(
            target=run_python_module,
            args=(None, 'http.server', '--directory', directory, port),
    )
    try:
        httpd.start()
        run_python_module(None, 'webbrowser', '-t', f'http://localhost:{port}')
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        httpd.join()

@nox.session
def build_web(ctx: nox.Session) -> None:
    """Prepare target directory for running the web site."""
    do_build_wheel(ctx)
    
    SITE_DIRECTORY.mkdir(parents = True, exist_ok = True)

    for file_path in DIST_DIRECTORY.glob('steps-*.whl'):
        ctx.log(f'Copying {file_path}')
        shutil.copy(file_path, SITE_DIRECTORY / file_path.name)

    for file_path in STATIC_DIRECTORY.glob('*'):
        ctx.log(f'Copying {file_path}')
        shutil.copy(file_path, SITE_DIRECTORY / file_path.name)

@nox.session
def build_wheel(ctx: nox.Session) -> None:
    """Build a Pyodide package."""
    do_build_wheel(ctx)

@nox.session
def test(ctx: nox.Session) -> None:
    """Run unit tests."""
    TEST_REPORT_DIRECTORY.mkdir(exist_ok=True, parents=True)
    ctx.install(
            'pytest',
            'pytest-cov',
            'pytest-bdd',
            'pytest-html',
            '.')

    args = [ 
            '--cov=steps',
            '--cov-report=term',
            f'--cov-report=html:{TEST_REPORT_DIRECTORY/"cov-html"}',
            f'--cov-report=xml:{TEST_REPORT_DIRECTORY}/coverage.xml',
            f'--html={TEST_REPORT_DIRECTORY/"html"/"index.html"}',
    ]
    if ctx.posargs:
        args += ctx.posargs

    ctx.run('pytest', *args)

@nox.session
def lint(ctx: nox.Session) -> None:
    """Run multiple linters."""
    LINT_REPORT_DIRECTORY.mkdir(exist_ok=True, parents=True)
    ctx.install(
            'pylama[all]',
            )

    args = [
            '--report', f'{LINT_REPORT_DIRECTORY/"lint-report.json"}',
    ]
    if ctx.posargs:
        args += ctx.posargs

    ctx.run('pylama', *args)

