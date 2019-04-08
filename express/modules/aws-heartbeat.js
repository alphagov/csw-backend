const AWS = require('aws-sdk');
const schedule = require('node-schedule');
/**
    When running a local dev server through AWS vault the session can expire
    frequently. This heartbeat function calls STS GetCallerIdentity
    regularly as a heartbeat keep-alive type thing.

    It doesn't work if you have an intermittent internet connection
 */
heartbeat = {
    credentials: null,
    keepAlive: function(server) {
        schedule.scheduleJob('0 */1 * * * *', function(fireDate){
            let sts = new AWS.STS({correctClockSkew: true});
            let now = new Date();
            let dateString = now.toLocaleString('en-GB', { hour12:false });
            if (!this.credentials) {
                let creds = {
                    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
                    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
                    sessionToken: process.env.AWS_SESSION_TOKEN
                };
                this.credentials = new AWS.Credentials(creds);
            } else {
                let awsCreds = this.credentials;
                this.credentials.refreshPromise()
                .then(function(err) {
                    if (err) console.log(err);
                    else {
                        console.log('Refreshed credentials');
                        process.env.AWS_SESSION_TOKEN = this.sessionToken;
                    }
                });
            }
            sts.getCallerIdentity({}, function(err, data) {
                if (err) {
                    //console.log(err, err.stack); // an error occurred
                    console.log(`Heartbeat failed: Exiting`);
                    server.close();
                } else {
                    let account = data["Account"];
                    console.log(`Heartbeat: Refreshed session for account: ${account} at: ${dateString}`);
                };

            });
        });
    }
}
module.exports = heartbeat;