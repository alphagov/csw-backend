from tests.chalicelib.aws.test_client_default import TestClientDefault
from chalicelib.aws.gds_aws_client import GdsAwsClient


class TestGdsAwsClient(TestClientDefault):
    @classmethod
    def setUp(self):
        """
        """
        self.client = GdsAwsClient(self.app)

    def test_init_client(self):
        self.assertIn("parse_arn_components", dir(self.client))

    def test_parse_arn_components(self):
        arn = "arn:aws:iam:[region]:123456789012:user/user@domain.com"
        parsed = self.client.parse_arn_components(arn)
        self.assertEqual(parsed["account"], "123456789012")
        self.assertEqual(parsed["region"], "[region]")
        self.assertEqual(parsed["resource"], "user/user@domain.com")

    def test_to_camel_case(self):
        snake_case_test = "snake_case_test"
        lower_case_test = "lower case test"
        camel_case_test = "CamelCaseTest"
        upper_case_test = "UPPER CASE TEST"
        title_case_test = "Title Case Test"

        self.assertEqual(self.client.to_camel_case(snake_case_test, True), "SnakeCaseTest")
        self.assertEqual(self.client.to_camel_case(lower_case_test, False), "lowerCaseTest")
        self.assertEqual(self.client.to_camel_case(camel_case_test, True), "CamelCaseTest")
        self.assertEqual(self.client.to_camel_case(upper_case_test, False), "upperCaseTest")
        self.assertEqual(self.client.to_camel_case(title_case_test, True), "TitleCaseTest")

    def test_tag_list_to_dict(self):
        tags = [
            {
                "Key": "test_key_1",
                "Value": "test_val_1"
            },
            {
                "Key": "test_key_2",
                "Value": "test_val_2"
            }
        ]
        lookup = self.client.tag_list_to_dict(tags)
        self.assertIn("test_key_1", lookup)
        self.assertEqual(lookup["test_key_1"], "test_val_1")
        self.assertIn("test_key_2", lookup)
        self.assertEqual(lookup["test_key_2"], "test_val_2")