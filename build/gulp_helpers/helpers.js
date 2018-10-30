const exec = require('child-process-promise').exec;
const awsParamStore = require('aws-param-store');
const AWS = require('aws-sdk');
const Input = require('prompt-input');

var helpers = {

    getRootPath: function() {

        var root_path = __dirname;

        root_path.split('/');
        dirs.pop();
        dirs.pop();
        root_path = dirs.join('/');

        return root_path
    },

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
            console.log(err.stderr);
            return file.data;
          }
	    );

	    return after;
	},

	getJsonDataInPipelinePromise: function(task, dir, file, property) {

	    var during = this.runTaskPromise(task, dir);

	    var after = during.then(
          function(out) {
            console.log("SUCCESS");
            //console.log(out);
            file.data[property] = JSON.parse(out.stdout);
            return file.data;
          },
          function(err) {
            console.log("FAILURE");
            console.log(err.stderr);
            return file.data;
          }
        );

        return after;
	},

	getTerraformOutputInPipelinePromise: function(dir, file) {

	    var task = 'terraform output -json';
  	    var working = dir;
  	    var property = "terraform";

  	    var promise = helpers.getJsonDataInPipelinePromise(task, working, file, property)
  	    .then(
  	      function(output) {
  	        for(param in file.data[property]) {
  	            file.data[param] = file.data[property][param].value;
  	        }
  	        delete file.data[property];
  	        return file.data;
  	      },
  	      function(error) {
  	        console.log("FAILURE");
  	        console.log(err.stderr);
            return file.data;
  	      }
  	    );

        return promise;
	},

	getParameterPromise: function(parameter, region) {

		var promise = awsParamStore.getParameter(parameter, { region: region })

    	var getValue = promise.then(function(parameter) {
      		return parameter.Value;
    	});

    	return getValue;
	},

	getParameterInPipelinePromise: function(parameter, region, file, property) {

	    var promise = this.getParameterPromise(parameter, region);

	    var after = promise.then(
	      function(value) {
            file.data[property] = value;
            return file.data;
	      },
	      function(err) {
	        console.log('FAILURE');
	        console.log(err.stderr);
	      }
	    );

	    return after;
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

	setParameterInPipelinePromise: function(name, value, region, file, property) {

		var promise = this.setParameterPromise(name, value, region)
		.then(
	  	  function(response) {
	  	  	file.data[property] = value;
            return file.data;
	      },
	      function(err) {
	        console.log('FAILURE');
	        console.log(err.stderr);
	      }
	    );

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
	},

	getAwsAccountIdPromise: function() {

	    var sts = new AWS.STS();

	    var request = sts.getCallerIdentity();
	    var promise = request.promise()
	    .then(
	    	function(data) {
	      	  return data.Account;
	    	},
		    function(error) {
		      /* handle the error */
		      console.log('Failed to get host_account_id from STS GetCallerIdentity');
		      console.log(error.stderr);
		      return null;
		    }
		);

		return promise;
	},

	removePropertiesInPipeline: function(data, remove) {
		// remove the listed properties from the data object
		
		for(item in data) {
	        if (remove.indexOf(item)>=0) {
	          delete(data[item]);
	        }
	    }
	    return data
	},

	removeExceptPropertiesInPipeline: function(data, expected) {
		// remove any properties not listed in expected from the data object
	    
	    for (item in data) {
	      if (expected.indexOf(item) < 0) {
	        delete data[item];
	      }
	    }

	    return data
	},

	lambdaInvokePromise: function(function_name, directory, payload, file, output_file) {

        var payload_string = JSON.stringify(payload);
        var task = "aws lambda invoke --function-name "+function_name+" --payload '" + payload_string + "' "+output_file;

        return this.runTaskInPipelinePromise(task, directory, file);
	},

	psqlExecuteInPipelinePromise: function(path, command, file) {

	    var tunnel = file.data.bastion_public_ip;
        // TODO is this right? Should we assume this
        // or prompt user for the ssh key
        // or write .ssh/config
        var key = file.data.ssh_public_key_path.replace(/\.pub$/,'');
        var host = file.data.rds_connection_string;
        var username = 'root';
        var password = file.data.postgres_root_password;
        var database = 'postgres';

        var task = " python psql_tunnel.py ";
        task += " --tunnel "+tunnel;
        task += " --key \""+key+"\"";
        task += " --host "+host;
        task += " --user "+username;
        task += " --password \""+password+"\"";
        task += " --database postgres";
        task += " --command \""+command+"\""

        console.log(path + ": " + task);

        return this.runTaskInPipelinePromise(task, path, file);

	}

};

module.exports = helpers;