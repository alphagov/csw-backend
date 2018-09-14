from chalicelib.aws.gds_sqs_client import GdsSqsClient
from chalicelib.models import DatabaseHandle

def audit_lambda_audit_active_accounts(app):
    db = None
    try:
        status = False
        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        AccountSubscription = dbh.get_model("AccountSubscription")
        AccountAudit = dbh.get_model("AccountAudit")
        active_accounts = (AccountSubscription.select().where(AccountSubscription.active == True))

        items = []
        # .order_by(User.username)

        # create SQS message
        sqs = GdsSqsClient(app)

        app.log.debug("Invoke SQS client")

        app.log.debug("Set prefix: " + app.prefix)

        queue_url = sqs.get_queue_url(f"{app.prefix}-audit-account-queue")

        app.log.debug("Retrieved queue url: " + queue_url)

        for account in active_accounts:

            app.log.debug("Audit account: " + account.account_name)
            items.append(account.serialize())

            # create a new empty account audit record
            audit = AccountAudit.create(
                account_subscription_id=account
            )

            app.log.debug("Created audit record")

            message_body = app.utilities.to_json(audit.serialize())

            app.log.debug("Sending SQS message with body: " + message_body)

            message_id = sqs.send_message(
                queue_url,
                message_body
            )

            if message_id is not None:
                app.log.debug("Sent SQS message: " + message_id)
            else:
                raise Exception("Message ID empty from SQS send_message")

        status = True
        db.close()

    except Exception as err:

        app.log.error("Failed to start audit: " + str(err))
        status = False
        items = []
        if db is not None:
            db.rollback()
            db.close()

    return status