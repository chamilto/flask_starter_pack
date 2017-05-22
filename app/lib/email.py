from flask import current_app as app
import requests


def send_email(to=None, subject=None, body=None):
    if not all([to, subject, body]):
        raise ValueError('Missing argument.')

    domain = app.config['FROM_EMAIL_DOMAIN']
    from_address = '{address}@{domain}'.format(
        address=app.config['FROM_EMAIL_ADDRESS'],
        domain=domain)

    return requests.post(
        'https://api.mailgun.net/v3/{email_domain}/messages'.format(
            email_domain=domain),
        auth=("api", app.config['MAIL_GUN_KEY']),
        data={"from": from_address,
              "to": to,
              "subject": subject,
              "text": body})
