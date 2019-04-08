const express = require('express');
const nunjucks = require('nunjucks');
const fs = require("fs");
const path = require("path");
const AWS = require('aws-sdk');
AWS.config.update({region:'eu-west-1'});

const encrypter = require('./modules/kms-encrypter');
const heartbeat = require('./modules/aws-heartbeat');
const templater = require('./modules/csw-template-data');
const app = express();
const port = 3000;

const env = nunjucks.configure('templates', {
    express: app,
    autoescape: true
});

env.addFilter('datetime', function(str) {
    return templater.format_date_string(str);
});

env.addFilter('aws_account_id', function(account) {
    if (account) account = account.padStart(12, '0');
    return account;
});

app.set('view engine', 'html');

app.use('/assets', express.static('assets'));

/*
In the interests of encryption you run the express server
through aws-vault or similar so you can only render audit
results for the current account assumed through aws-vault
 */
//app.get('/', async (req, res) => {
//    const directoryPath = path.join(__dirname, '../cli/results');
//    //passsing directoryPath and callback function
//    let files = await fs.readdir(directoryPath, function (err, files) {
//        let accounts = [], i = 0;
//        for (i=0; i<files.length;i++) {
//            if (files[i].match(/^\d{12}$/)) {
//                accounts.push(files[i]);
//            }
//        }
//        accounts.sort();
//        res.render('cli_account_list.html', {
//            title: 'Acoounts: Cloud Security Watch',
//            asset_path: '/assets',
//            accounts: accounts
//        });
//    });
//
//});

app.get('/', async (req, res) => {
    const sts = new AWS.STS();
    await sts.getCallerIdentity({}, async function(err, data) {
        if (err) {
            console.log(err, err.stack); // an error occurred
        } else {
            let account = data["Account"];
            const directoryPath = path.join(__dirname, '../cli/results/'+account);
            await fs.readdir(directoryPath, function (err, files) {
                let audits = [], i = 0;
                for (i=0; i<files.length;i++) {
                    if (files[i].match(/^\d{4}-\d{2}-\d{2}/)) {
                        audits.push(files[i]);
                    }
                }
                audits.sort(function(a, b){return b>a});
                res.render('cli_audit_list.html', {
                    mode: 'express',
                    hide_login: true,
                    title: 'Acoount audits: Cloud Security Watch',
                    asset_path:'/assets',
                    account: account,
                    audits: audits
                });
            });
        };
    });
});

app.get('/accounts/:account/audit/:audit', async (req, res) => {
    let account = req.params.account;
    let auditDate = req.params.audit;
    let filePath = path.join(__dirname, '../cli/results/'+account, auditDate, 'audit.enc');
    console.log(filePath);
    let auditData = await encrypter.fileDecrypt(account, filePath);
    let audit = await encrypter.jsonParse(auditData);
    //res.send(auditData);
    let data = {
        mode: 'express',
        hide_login: true,
        title: 'Account audits: Cloud Security Watch',
        base_path: '/accounts/'+account+'/audit/'+auditDate,
        asset_path: '/assets',
        account: account,
        audit_date: auditDate,
        audit: audit
    };
    let templateData = templater.audit_status(data);

    res.render('audit_status.html', templateData);
});

app.get('/accounts/:account/audit/:audit/raw', async (req, res) => {
    let account = req.params.account;
    let auditDate = req.params.audit;
    let filePath = path.join(__dirname, '../cli/results/'+account, auditDate, 'audit.enc');
    console.log(filePath);
    let auditData = await encrypter.fileDecrypt(account, filePath);
    let audit = await encrypter.jsonParse(auditData);
    //res.send(auditData);
    /*
    let data = {
        mode: 'express',
        hide_login: true,
        title: 'Account audits: Cloud Security Watch',
        base_path: '/accounts/'+account+'/audit/'+auditDate,
        asset_path: '/assets',
        account: account,
        audit: audit,
        audit_date: auditDate
    };
    let templateData = templater.audit_status(data);
    res.render('cli_audit_raw.html', templateData);
    */
    res.json(audit);
});

app.get('/accounts/:account/audit/:audit/check/:checkId/:status', async (req, res) => {
    let account = req.params.account;
    let auditDate = req.params.audit;
    let checkId = req.params.checkId;
    let status = req.params.status;
    let filePath = path.join(__dirname, '../cli/results/'+account, auditDate, 'audit.enc');
    console.log(filePath);
    let auditData = await encrypter.fileDecrypt(account, filePath);
    let audit = await encrypter.jsonParse(auditData);
    //res.send(auditData);
    let data = {
        mode: 'express',
        hide_login: true,
        title: 'Account audits: Cloud Security Watch',
        base_path: '/accounts/'+account+'/audit/'+auditDate,
        asset_path: '/assets',
        account: account,
        audit: audit,
        audit_date: auditDate,
        check_id: checkId,
        status_name: status
    };
    let templateData = templater.check_status_resources(data);

    res.render('check_status_resources.html', templateData);
});



app.get('/test/decrypt', async (req, res) => {
    try {
        let testFile = path.join(__dirname, '../cli/results/489877524855/2019-04-03T18:56:00/audit.enc');
        console.log(testFile)
        const plain = await encrypter.fileDecrypt("489877524855", testFile);
        res.send(plain);
    } catch(err) {
        console.log("Error", err.stack);
    }


});

let server = app.listen(port, () => console.log(`CSW listening on port ${port}!`));

/**
    When running a local dev server through AWS vault the session can expire
    frequently. This heartbeat function calls STS GetCallerIdentity
    regularly as a heartbeat keep-alive type thing.

    It doesn't work if you have an intermittent internet connection
 */
heartbeat.keepAlive(server);