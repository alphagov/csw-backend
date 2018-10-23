# GdsSqsClient
# extends GdsAwsClient
# implements aws sqs endpoint queries

import os
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSqsClient(GdsAwsClient):

    # get-queue-url
    # --queue-name < value >
    def get_queue_url(self, queue_name):

        try:

            self.app.log.debug("Try getting queue URL for: " + queue_name)
            region = os.environ["CSW_REGION"]
            default_session = self.get_session()
            caller = self.get_caller_details(default_session)
            account = caller.Account
            queue_url = f"https://{region}.queue.amazonaws.com/{account}/{queue_name}"

            self.app.log.debug("Queue URL: " + queue_url)

        except Exception as err:
            self.app.log.error("Failed to get queue URL: " + str(err))
            queue_url = None

        return queue_url

    # send-message
    # --queue-url < value >
    # --message-body < value >
    def send_message(self, queue_url, body):

        try:

            sqs = self.get_default_client('sqs', 'eu-west-1')

            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=body
            )

            message_id = response['MessageId']
        except Exception as err:
            self.app.log.error("Failed to send SQS message: " + str(err))
            message_id = None

        return message_id
