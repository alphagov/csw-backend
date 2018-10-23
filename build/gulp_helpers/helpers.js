const exec = require('child-process-promise').exec;
const awsParamStore = require('aws-param-store');
const AWS = require('aws-sdk');
const Input = require('prompt-input');

var helpers = {

	runTaskPromise: function(task, dir) {

		var during = exec(task, { cwd: dir, stdio: 'inherit' });

	    var execProcess = during.childProcess;
	    execProcess.stdout.on('data', function (data) {
	      console.log(data.toString());
	    });

	    return during;
	},

	runTaskInPipelinePromise: function(task, dir, file) {

	    var during = this.runTaskPromise(task, dir);

	    var after = during.then(
          function(out) {
            console.log("SUCCESS");
            console.log(out.stdout);
            return file.data;
          },
          function(err) {
            console.log("FAILURE");
            console.log(err);
            return file.data;
          }
	    );

	    return after;
	},

	getJsonDataInPipelinePromise: function(task, dir, file) {

	    var during = this.runTaskPromise(task, dir);

	    var after = during.then(
          function(out) {
            console.log("SUCCESS");
            //console.log(out);
            file.data = JSON.parse(out.stdout);
            return file.data;
          },
          function(err) {
            console.log("FAILURE");
            console.log(err);
            return file.data;
          }
        );

        return after;
	},

	getParameterPromise: function(parameter, region) {

		var promise = awsParamStore.getParameter(parameter, { region: region })

    	var getValue = promise.then(function(parameter) {
      		parameter.Value;
    	});

    	return getValue;
	},

	getParameterInPipelinePromise: function(parameter, region, file, property) {

	    var promise = this.getParameterPromise(parameter, region);

	    promise.then(
	      function(value) {
            file.data[property] = value;
            return file.data;
	      },
	      function(err) {
	        console.log('FAILURE');
	        console.log(err);
	      }
	    );

	    return promise;
	},

	setParameterPromise: function(name, value, region) {

		var ssm = new AWS.SSM({region: region});
		
		var params = {
	      Name: name,
	      Type: 'SecureString',
	      Value: value,
	      Overwrite: true
	    };

    	var request = ssm.putParameter(params);
    	var promise = request.promise();

    	return promise;
	},

	promptInputPromise: function(name, prompt, file) {

		var input = new Input({
	      name: name,
	      message: prompt
	    });

	    var promise = input.run()
	    .then(function(answer) {
	      console.log(answer);
	      // TODO validate answer format
	      file.data[name] = answer;
	    });

	    return promise;
	}

};

module.exports = helpers;