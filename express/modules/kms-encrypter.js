const fs = require('fs');
const fernet = require('fernet');
const path = require("path");
const AWS = require('aws-sdk');

const encrypter = {
    readFile: async function(path, encoding) {
        if (!encoding) encoding = 'utf8';
        return new Promise((resolve, reject) => {
            fs.readFile(path, encoding, (err, data) => {
                if (err) reject(err)
                else resolve(data)
            })
        });
    },
    jsonParse: async function(data) {
        let parsed = null
        try {
            parsed = JSON.parse(data);
        } catch (err) {
            console.log(err);
        }
        return parsed;
    },
    getAccountSettings: async function(account, config) {
        return config.find(function(item) {
            return item.account == account;
        });
    },
    getKmsDecryptParams: async function(accountSettings) {
        let encrypted = Buffer.from(accountSettings.key, 'base64');
        params = {'CiphertextBlob': encrypted};
        return params;
    },
    keyDecrypt: async function(account) {
        try {
            let configFile = path.join(__dirname, '../../cli/config/accounts.json');
            let configData = await this.readFile(configFile);
            let config = await this.jsonParse(configData);
            let accountSettings = await this.getAccountSettings(account, config);
            let params = await this.getKmsDecryptParams(accountSettings);
            let data = await this.kmsDecrypt(params)
            return data.Plaintext.toString('utf8');
        } catch(err) {
            console.log("Error", err.stack);
            return null;
        }
    },
    kmsDecrypt: async function(params) {
        return new Promise((resolve, reject) => {
            const kms = new AWS.KMS();
            kms.decrypt(params, async function(err, data) {
                if (err) reject(err)
                else resolve(data)
            });
        });
    },
    getFernetSecret: async function(key) {
        return new fernet.Secret(key);
    },
    getFernetToken: async function(secret, data) {
        return new fernet.Token({
            secret: secret,
            token: data,
            ttl: 0
        });
    },
    dataDecrypt: async function(account, data) {
        try {
            let key = await this.keyDecrypt(account);
            let secret = await this.getFernetSecret(key);
            let token = await this.getFernetToken(secret, data);
            let plain = token.decode();
            return plain;
        } catch(err) {
            console.log(err, err.stack);
        }
    },
    fileDecrypt: async function(account, file) {
        try {
            let data = await this.readFile(file, 'utf8');
            let plain = await this.dataDecrypt(account, data);
            return plain;
        } catch(err) {
            console.log(err, err.stack);
            return null;
        }
    }
};

module.exports = encrypter;