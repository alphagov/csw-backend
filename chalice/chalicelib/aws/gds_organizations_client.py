"""
GdsOrganizationsClient
extends GdsAwsClient
implements aws Key Management Service endpoint queries
"""
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsOrganizationsClient(GdsAwsClient):
    """
    The organizations client gives us access to list accounts linked
    to the parent organization account
    """

    def list_accounts(self, session):
        """Get a list of AWS organization linked accounts.
        :param session: The boto3 session to use for the connection
        :returns: A list of accounts
        :rtype: list
        """
        client = self.get_boto3_session_client("organizations", session)

        results = client.list_accounts(MaxResults=20)
        accounts = results["Accounts"]

        while "NextToken" in results:
            results = client.list_accounts(
                MaxResults=20, NextToken=results["NextToken"]
            )
            accounts += results["Accounts"]

        return accounts
