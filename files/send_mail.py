import boto3

CHARSET = "UTF-8"

table_header = ('service', 'Resource ID')

def send_email(from_address, to_address, deleted_resources, skip_delete_resources, notify_resources, check_resources):
    subject = "AWS: Auto clean resource data"
    verified = verify_email_identity(from_address)

    if verified:
        html_body = get_email_body(deleted_resources, skip_delete_resources, notify_resources, check_resources)
        send_html_email(from_address, to_address, subject, html_body)
    else:
        print("Warn: Sending email notification failed as Email address is not verified yet")


def send_html_email(from_address, to_address, subject, html_body):
    ses_client = boto3.client("ses", region_name="us-west-1")

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                to_address,
            ],
        },
        Message={
            "Subject": {
                "Charset": CHARSET,
                "Data": subject,
            },
            "Body": {
                "Html": {"Charset": CHARSET, "Data": html_body}
            },
        },
        Source=from_address,
    )
    print(response)

def create_table(header: list, data: list):
    table = "<table>\n"

    # Create the table's column headers
    table += "  <tr>\n"
    for column in header:
        table += "    <th>{0}</th>\n".format(column.strip())
    table += "  </tr>\n"

    # Create the table's row data
    for row in data:
        table += "  <tr>\n"
        for column in row:
            table += "    <td>{0}</td>\n".format(column.strip())
        table += "  </tr>\n"

    table += "</table>"

    return table

def get_email_body(deleted_resources, skip_delete_resources, notify_resources, check_resources):
    html_body = ""

    if deleted_resources:
        title = "<p> Here is the list of deleted resources </p>"
        table = create_table(table_header, deleted_resources)
        html_body = html_body + title + table + "<p></p>"

    if skip_delete_resources:
        title = "<p> Here is the list of skipped deletion resources </p>"
        table = create_table(table_header, skip_delete_resources)
        html_body = html_body + title + table + "<p></p>"

    if notify_resources:
        title = "<p> Here is the list of resources for notification</p>"
        table = create_table(table_header, notify_resources)
        html_body = html_body + title + table + "<p></p>"

    if check_resources:
        title = "<p> Here is the list of resources to check for issues</p>"
        table = create_table(table_header, notify_resources)
        html_body = html_body + title + table + "<p></p>"

    return html_body

def verify_email_identity(email_address):
    ses_client = boto3.client("ses", region_name="us-west-1")
    response = ses_client.list_verified_email_addresses()
    if email_address in response['VerifiedEmailAddresses']:
        return True

    response = ses_client.verify_email_identity(
        EmailAddress=email_address
    )
    print("email verification response", response)

    return False
