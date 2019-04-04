const AWS = require('aws-sdk');
const schedule = require('node-schedule');
/**
    When running a local dev server through AWS vault the session can expire
    frequently. This heartbeat function calls STS GetCallerIdentity
    regularly as a heartbeat keep-alive type thing.

    It doesn't work if you have an intermittent internet connection
 */
heartbeat = {
    keepAlive: function(server) {
        schedule.scheduleJob('0 */1 * * * *', function(fireDate){
            let sts = new AWS.STS();
            sts.getCallerIdentity({}, function(err, data) {
                if (err) {
                    //console.log(err, err.stack); // an error occurred
                    console.log('Heartbeat failed: Exiting');
                    server.close();
                } else {
                    let account = data["Account"];
                    console.log('Heartbeat: Refreshed session for account: '+ account);
                };

            });
        });
    }
}
module.exports = heartbeat;