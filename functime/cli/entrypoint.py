import typer

from ._deploy import deploy_cli
from ._list import list_cli
from ._login import login_cli
from ._usage import usage_cli


def version_callback(value: bool):
    if value:
        __version__ = "0.1.0"

        typer.echo(f"functime-client version: {__version__}")
        raise typer.Exit()


entrypoint_cli_typer = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
    help="""
    Functime is the fastest time series forecasting library.

    See the website at https://functime.ai/ for documentation and more information.
    """,
)


@entrypoint_cli_typer.callback()
def functime(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=version_callback),
):
    pass


entrypoint_cli_typer.add_typer(deploy_cli)
entrypoint_cli_typer.command("login", help="Authenticate and login with Auth0.")(
    login_cli
)
entrypoint_cli_typer.command("list", help="List deployed estimators.")(list_cli)
entrypoint_cli_typer.command("usage", help="View your usage.")(usage_cli)
entrypoint_cli = typer.main.get_command(entrypoint_cli_typer)
entrypoint_cli.list_commands(None)  # type: ignore

if __name__ == "__main__":
    # this module is only called from tests, otherwise the parent package __init__.py is used as the entrypoint
    entrypoint_cli()