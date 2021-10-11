import sys
import json
import logging

import boto3

NOTIFICATION_SOURCE = "escribele.a.alfonso@gmail.com"
NOTIFICATION_TEMPLATE_NAME = "catalog-demo-notification-template"
NOTIFICATION_SUBJECT = "A fellow admin modified a product"

NOTIFICATION_TEMPLATE = {
    "TemplateName": NOTIFICATION_TEMPLATE_NAME,
    "SubjectPart": NOTIFICATION_SUBJECT,
    "HtmlPart": """
        <h3>A fellow admin modified a product</h3>
        <dl>
            <dt>User</dt>
            <dd>{{user}}</dd>

            <dt>Change</dt>
            <dd>{{change}}</dd>
        </dl>
    """
}


def notify_via_email(ses_client, addressee, user, change):
    template_data = {
        "user": user,
        "change": change
    }
    response = ses_client.send_templated_email(
        Source=NOTIFICATION_SOURCE,
        Destination={
            "ToAddresses": [addressee],
        },
        Template=NOTIFICATION_TEMPLATE_NAME,
        TemplateData=json.dumps(template_data)
    )

    logging.info(response)


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) < 2 or sys.argv[1] != "--upload-template":
        print("Usage: python notification.py --upload-template")
    else:
        # Create SES client
        ses = boto3.client('ses')
        response = ses.create_template(
            Template=NOTIFICATION_TEMPLATE
        )

        print(response)
