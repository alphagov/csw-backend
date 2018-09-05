# GdsSqsClient
# extends GdsAwsClient
# implements aws sqs endpoint queries

from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSqsClient(GdsAwsClient):

    # get-queue-url
    # --queue-name < value >
    def get_queue_url(self, session, queue_name):

        try:
            sqs = self.get_boto3_session_client('sqs', session)

            response = sqs.get_queue_url(
                QueueName=queue_name
            )

            queue_url = response['QueueUrl']
        except Exception as err:
            queue_url = None

        return queue_url

    # send-message
    # --queue-url < value >
    # --message-body < value >
    def send_message(self, session, queue_url, body):

        try:
            sqs = self.get_boto3_session_client('sqs', session)

            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=body
            )

            message_id = response['MessageId']
        except Exception as err:
            message_id = None

        return message_id

