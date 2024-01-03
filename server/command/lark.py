import logging

import click
from app import app
from model.team import save_im_application


# create command function
@app.cli.command(name="larkapp")
@click.option("-a", "--app-id", "app_id", required=True, prompt="Feishu(Lark) APP ID")
@click.option(
    "-s", "--app-secret", "app_secret", required=True, prompt="Feishu(Lark) APP SECRET"
)
@click.option(
    "-e", "--encrypt-key", "encrypt_key", default="", prompt="Feishu(Lark) ENCRYPT KEY"
)
@click.option(
    "-v",
    "--verification-token",
    "verification_token",
    default="",
    prompt="Feishu(Lark) VERIFICATION TOKEN",
)
@click.option("-h", "--host", "host", default="https://testapi.gitmaya.com")
def create_lark_app(app_id, app_secret, encrypt_key, verification_token, host):
    # click.echo(f'create_lark_app {app_id} {app_secret} {encrypt_key} {verification_token} {host}')
    permissions = "\n\t".join(
        [
            "contact:contact:readonly_as_app",
            "im:chat",
            "im:message",
            "im:resource",
        ]
    )
    events = "\n\t".join(
        [
            "im.message.receive_v1",
        ]
    )
    click.echo(f"need permissions: \n{permissions}\n")
    click.echo(f"need events: \n{events}\n")
    click.echo(f"webhook: \n{host}/api/feishu/oauth")

    save_im_application(
        None, "lark", app_id, app_secret, encrypt_key, verification_token
    )
    click.echo(f"webhook: \n{host}/api/feishu/hook/{app_id}")

    click.confirm("success to save feishu app?", abort=True)
    click.echo(f"you can publish you app.")
