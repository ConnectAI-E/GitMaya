import logging

import click
from app import app, db
from model.schema import IMApplication, ObjID


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

    application = (
        db.session.query(IMApplication).filter(IMApplication.app_id == app_id).first()
    )
    if not application:
        application = IMApplication(
            id=ObjID.new_id(),
            app_id=app_id,
            app_secret=app_secret,
            extra=dict(encrypt_key=encrypt_key, verification_token=verification_token),
        )
        db.session.add(application)
        db.session.commit()
    else:
        db.session.query(IMApplication).filter(
            IMApplication.id == application.id,
        ).update(
            dict(
                app_id=app_id,
                app_secret=app_secret,
                extra=dict(
                    encrypt_key=encrypt_key, verification_token=verification_token
                ),
            )
        )
        db.session.commit()
    click.echo(f"webhook: \n{host}/api/feishu/hook/{app_id}")

    click.confirm("success to save feishu app?", abort=True)
    click.echo(f"you can publish you app.")
