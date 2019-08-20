import boto3
import os
import base64
from cryptography.fernet import Fernet

class KmsEncrypter:
    def __init__(self, app):
        self.app = app
        self.config_file = "config/accounts.json"
        self.config = None
        self.client = boto3.client(
            'kms',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            aws_session_token=os.environ['AWS_SESSION_TOKEN']
        )

    def read_kms_config(self):
        try:
            if self.config is None:
                account_config_json = self.app.utilities.read_file(self.config_file)
                self.config = self.app.utilities.from_json(account_config_json)
        except Exception as err:
            self.config = []
        return self.config

    def save_kms_config(self):
        data = self.app.utilities.to_json(self.config, True)
        self.app.utilities.write_file(self.config_file, data)

    def get_account_kms_key(self, account):
        """
        Read from config or create a KMS key,
        update config and return ID
        """
        config = self.read_kms_config()
        kms_key_id = None
        for item in config:
            if item["account"] == account:
                kms_key_id = item["kms_key_id"]

        if kms_key_id is None:
            kms_key_id = self.create_account_kms_key(account)
            config.append({
                "account": account,
                "kms_key_id": kms_key_id
            })
            self.save_kms_config()
        return kms_key_id

    def create_account_kms_key(self, account):
        response = self.client.create_key(
            Description='CloudSecurityWatch - Local data',
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS',
            Tags=[
                {
                    'TagKey': 'Application',
                    'TagValue': 'CloudSecurityWatch'
                },
                {
                    'TagKey': 'Purpose',
                    'TagValue': 'Local storage'
                }
            ]
        )
        kms_key_id = response['KeyMetadata']['KeyId']
        return kms_key_id

    def encrypt(self, account, data):
        kms_key_id = self.get_account_kms_key(account)
        encoded = data.encode('utf8')
        response = self.client.encrypt(
            KeyId=kms_key_id,
            Plaintext=encoded
        )
        output = response['CiphertextBlob']
        return output

    def decrypt(self, data):
        response = self.client.decrypt(
            CiphertextBlob=data
        )
        output = response['Plaintext']
        decoded = output.decode('utf8')
        return decoded

    def generate_fernet_key(self):
        key = Fernet.generate_key()
        return key

    def get_fernet_key(self, account):
        config = self.read_kms_config()
        key = None
        for item in config:
            if item["account"] == account:
                if "key" in item:
                    fernet_key = item["key"]
                    decoded = base64.b64decode(fernet_key)
                    key = self.decrypt(decoded)

        if key is None:
            key = self.generate_fernet_key().decode('utf8')
            encrypted_key = self.encrypt(account, key)
            self.set_fernet_key(account, encrypted_key)
        return key.encode('utf8')

    def set_fernet_key(self, account, key):
        config = self.read_kms_config()
        for item in config:
            if item["account"] == account:
                item["key"] = base64.b64encode(key).decode('utf8')
        self.save_kms_config()

    def fernet_encrypt(self, account, data):
        key = self.get_fernet_key(account)
        cipher_suite = Fernet(key)
        cipher_data = cipher_suite.encrypt(data.encode('utf8'))
        return cipher_data

    def fernet_decrypt(self, account, data):
        key = self.get_fernet_key(account)
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(data).decode('utf8')
        return plain_text
