import json
from tests.chalicelib.aws.test_client_default import TestClientDefault
from chalicelib.aws.gds_iam_client import GdsIamClient


class TestGdsIamClient(TestClientDefault):
    @classmethod
    def setUp(self):
        """
        """
        self.client = GdsIamClient(self.app)
        self.client.chain = {
            "account": "123456789012",
            "chain_role": "SecurityAuditChain",
            "target_role": "SecurityAudit"
        }

    def test_init_client(self):
        self.assertIn("list_roles", dir(self.client))

    def test_parse_arn_components(self):
        arn = "arn:aws:iam:[region]:123456789012:user/user@domain.com"
        parsed = self.client.parse_arn_components(arn)
        self.assertEqual(parsed["account"], "123456789012")
        self.assertEqual(parsed["region"], "[region]")
        self.assertEqual(parsed["resource"], "user/user@domain.com")
        self.assertEqual(parsed["resource_components"]["name"], "user@domain.com")
        self.assertEqual(parsed["resource_components"]["type"], "user")

    def test_get_assumable_roles(self):
        policy_document = '''{
            "Document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "1",
                        "Effect": "Allow",
                        "Action": "sts:AssumeRole",
                        "Resource": [
                            "arn:aws:iam::123456789012:role/SecurityAudit",
                            "arn:aws:iam::234567890123:role/OtherRole",
                            "arn:aws:iam::345678901234:role/SecurityAudit",
                            "arn:aws:iam::456789012345:role/SecurityAudit"
                        ]
                    },
                    {
                        "Sid": "2",
                        "Effect": "Deny",
                        "Action": "sts:AssumeRole",
                        "Resource": [
                            "arn:aws:iam::567890123456:role/SecurityAudit"
                        ]
                    },
                    {
                        "Sid": "2",
                        "Effect": "Allow",
                        "Action": "sts:AssumeRole",
                        "Resource": [
                            "arn:aws:iam::678901234567:role/SecurityAudit"
                        ]
                    },
                    {
                        "Sid": "2",
                        "Effect": "Allow",
                        "Action": "sts:AssumeRole",
                        "Resource": [
                            "arn:aws:iam::789012345678:role/OtherRole2"
                        ]
                    }
                ]
            },
            "VersionId": "v1",
            "IsDefaultVersion": true,
            "CreateDate": "2019-07-19T16:14:12Z"
        }'''

        policy_version = json.loads(policy_document)

        self.assertEqual(type(policy_version), dict)
        assumable_roles = self.client.get_assumable_roles(policy_version)

        #Y
        self.assertIn("arn:aws:iam::123456789012:role/SecurityAudit", assumable_roles)
        self.assertIn("arn:aws:iam::345678901234:role/SecurityAudit", assumable_roles)
        self.assertIn("arn:aws:iam::456789012345:role/SecurityAudit", assumable_roles)
        self.assertIn("arn:aws:iam::678901234567:role/SecurityAudit", assumable_roles)
        self.assertIn("arn:aws:iam::234567890123:role/OtherRole", assumable_roles)
        self.assertIn("arn:aws:iam::789012345678:role/OtherRole2", assumable_roles)

        #N Statement effect is Deny
        self.assertNotIn("arn:aws:iam::567890123456:role/SecurityAudit", assumable_roles)

    def test_get_role_accounts(self):

        roles = [
            "arn:aws:iam::123456789012:role/SecurityAudit",
            "arn:aws:iam::345678901234:role/SecurityAudit",
            "arn:aws:iam::456789012345:role/SecurityAudit",
            "arn:aws:iam::678901234567:role/SecurityAudit",
            "arn:aws:iam::234567890123:role/OtherRole"
            "arn:aws:iam::789012345678:role/OtherRole2"
        ]
        accounts = self.client.get_role_accounts(roles)

        # These should be included as they are instances of the SecurityAudit role
        self.assertIn("123456789012", accounts)
        self.assertIn("345678901234", accounts)
        self.assertIn("456789012345", accounts)
        self.assertIn("678901234567", accounts)

        # These should be excluded as they are not the SecurityAudit role
        self.assertNotIn("234567890123", accounts)
        self.assertNotIn("789012345678", accounts)
