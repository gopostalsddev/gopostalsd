"""Explicit administrative commands for post-migration application data."""

import os

import click

from server.startup import bootstrap_required_data
from server.startup_admin import ensure_production_admin


def register_commands(app) -> None:
    """Register idempotent commands without running them during app creation."""

    @app.cli.command("bootstrap-data")
    @click.option(
        "--enable-categories-if-none/--no-enable-categories-if-none",
        default=False,
        help="Enable all categories only when the database currently has none enabled.",
    )
    def bootstrap_data_command(enable_categories_if_none: bool) -> None:
        """Initialize required data after `flask db upgrade`."""
        try:
            result = bootstrap_required_data(
                enable_categories_if_none=enable_categories_if_none
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

        click.echo(
            "Application data bootstrap complete "
            f"(pricing_policy_created={result['pricing_policy_created']})."
        )

    @app.cli.command("bootstrap-admin")
    def bootstrap_admin_command() -> None:
        """Create the configured production admin after migrations/bootstrap."""
        if not os.getenv("ADMIN_EMAIL") or not os.getenv("ADMIN_PASSWORD"):
            raise click.ClickException(
                "ADMIN_EMAIL and ADMIN_PASSWORD must be supplied for this one-time command."
            )

        if not ensure_production_admin(app):
            raise click.ClickException("Production admin bootstrap failed.")

        click.echo("Production admin bootstrap complete.")
