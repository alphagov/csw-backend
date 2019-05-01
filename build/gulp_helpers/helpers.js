const exec = require("child-process-promise").exec;
const awsParamStore = require("aws-param-store");
const AWS = require("aws-sdk");
const Input = require("prompt-input");
const fs = require("fs");
const os = require("os");

var helpers = {
  getRootPath: function() {
    var root_path = __dirname;

    var dirs = root_path.split("/");
    dirs.pop();
    dirs.pop();
    root_path = dirs.join("/");

    return root_path;
  },

  getConfigLocations: function(env, tool) {
    var root_path = this.getRootPath();

    var config = {
      env: env,
      tool: tool,
      paths: {},
      files: {}
    };

    config.paths.home = os.homedir();
    config.paths.root = root_path;
    // default files
    config.files.default_settings =
      root_path + "/environments/example/settings.json";
    config.files.default_chalice_config =
      root_path + "/environments/example/.chalice/config.json";

    // terraform root folder
    config.paths.environment = root_path + "/environments/" + env;
    config.files.environment_settings =
      root_path + "/environments/" + env + "/settings.json";
    // terraform root folder
    config.paths.terraform = root_path + "/environments/" + env + "/terraform";
    config.paths.terraform_tool =
      config.paths.terraform + "/csw-infra/tools/" + tool;
    config.files.terraform_apply = config.paths.terraform + "/apply.tfvars";
    config.files.terraform_backend = config.paths.terraform + "/backend.tfvars";
    // chalice config path
    config.paths.chalice_environment =
      root_path + "/environments/" + env + "/.chalice";
    config.paths.chalice_code = root_path + "/chalice";
    config.paths.chalice_deployed =
      config.paths.chalice_environment + "/deployed";
    config.files.chalice_config =
      config.paths.chalice_environment + "/config.json";
    config.files.chalice_deployed =
      config.paths.chalice_deployed + "/" + env + ".json";

    // S3 states
    config.files.s3_tfstate = "staging/" + tool + "/" + env + ".tfstate";
    config.files.s3_chalice_state =
      "staging/csw/chalice/" + tool + "/" + env + ".json";

    return config;
  },

  runTaskPromise: function(task, dir) {
    var during = exec(task, { cwd: dir, stdio: "inherit" });

    var execProcess = during.childProcess;
    execProcess.stdout.on("data", function(data) {
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
        if (file.data) {
          file.data.task_output = out.stdout;
        }
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
    var task = "terraform output -json";
    var working = dir;
    var property = "terraform";

    var promise = helpers
      .getJsonDataInPipelinePromise(task, working, file, property)
      .then(
        function(output) {
          for (param in file.data[property]) {
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
    var promise = awsParamStore.getParameter(parameter, { region: region });

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
        console.log("FAILURE");
        console.log(err.stderr);
      }
    );

    return after;
  },

  setParameterPromise: function(name, value, region) {
    var ssm = new AWS.SSM({ region: region });

    var params = {
      Name: name,
      Type: "SecureString",
      Value: value,
      Overwrite: true
    };

    var request = ssm.putParameter(params);
    var promise = request.promise();

    return promise;
  },

  setParameterInPipelinePromise: function(name, value, region, file, property) {
    var promise = this.setParameterPromise(name, value, region).then(
      function(response) {
        file.data[property] = value;
        return file.data;
      },
      function(err) {
        console.log("FAILURE");
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

    var promise = input.run().then(function(answer) {
      console.log(answer);
      // TODO validate answer format
      file.data[name] = answer;
    });

    return promise;
  },

  getAwsAccountIdPromise: function() {
    var sts = new AWS.STS();

    var request = sts.getCallerIdentity();
    var promise = request.promise().then(
      function(data) {
        return data.Account;
      },
      function(error) {
        /* handle the error */
        console.log("Failed to get host_account_id from STS GetCallerIdentity");
        console.log(error.stderr);
        return null;
      }
    );

    return promise;
  },

  s3UploadPromise: function(file) {
    var s3 = new AWS.S3({ region: file.data.region });

    var params = {
      Body: file.data.content,
      Bucket: file.data.bucket_name,
      Key: file.data.key
    };
    var request = s3.putObject(params);
    var promise = request.promise().then(
      function(data) {
        console.log(data);
        return file.data;
      },
      function(error) {
        /* handle the error */
        console.log("Failed to upload to S3");
        console.log(error.stderr);
        return file.data;
      }
    );

    return promise;
  },

  s3DownloadPromise: function(file) {
    var s3 = new AWS.S3({ region: file.data.region });

    var params = {
      Bucket: file.data.bucket_name,
      Key: file.data.key,
      ResponseContentType: "text/plain"
    };

    var request = s3.getObject(params);
    var promise = request.promise().then(
      function(data) {
        console.log(data);
        file.data.content = data.Body.toString("utf-8");
        return file.data;
      },
      function(error) {
        /* handle the error */
        console.log("Failed to download from S3");
        console.log(error.stderr);
        file.data.content = "";
        return file.data;
      }
    );

    return promise;
  },

  s3DeletePromise: function(file) {
    var s3 = new AWS.S3({ region: file.data.region });

    var params = {
      Bucket: file.data.bucket_name,
      Key: file.data.key
    };

    var request = s3.deleteObject(params);
    var promise = request.promise().then(
      function(data) {
        return file.data;
      },
      function(error) {
        /* handle the error */
        console.log("Failed to delete from S3");
        console.log(error);
        return file.data;
      }
    );

    return promise;
  },

  removePropertiesInPipeline: function(data, remove) {
    // remove the listed properties from the data object

    for (item in data) {
      if (remove.indexOf(item) >= 0) {
        delete data[item];
      }
    }
    return data;
  },

  removeExceptPropertiesInPipeline: function(data, expected) {
    // remove any properties not listed in expected from the data object

    for (item in data) {
      if (expected.indexOf(item) < 0) {
        delete data[item];
      }
    }

    return data;
  },

  lambdaInvokePromise: function(
    function_name,
    directory,
    payload,
    file,
    output_file
  ) {
    var payload_string = JSON.stringify(payload);
    var task =
      "aws lambda invoke --function-name " +
      function_name +
      " --payload '" +
      payload_string +
      "' " +
      output_file;

    return this.runTaskInPipelinePromise(task, directory, file);
  },

  psqlExecuteInPipelinePromise: function(
    path,
    command,
    file,
    user,
    password,
    database
  ) {
    var tunnel = file.data.bastion_public_ip;
    // TODO is this right? Should we assume this
    // or prompt user for the ssh key
    // or write .ssh/config
    var key = file.data.ssh_public_key_path.replace(/\.pub$/, "");
    var host = file.data.rds_connection_string;
    var username = typeof user == "undefined" ? "root" : user;
    var password =
      typeof password == "undefined"
        ? file.data.postgres_root_password
        : password;
    var database = typeof database == "undefined" ? "postgres" : database;

    var task = " python psql_tunnel.py ";
    task += " --tunnel " + tunnel;
    task += ' --key "' + key + '"';
    task += " --host " + host;
    task += " --user " + username;
    task += ' --password "' + password + '"';
    task += ' --database "' + database + '"';
    task += ' --command "' + command + '"';

    console.log(path + ": " + task);

    return this.runTaskInPipelinePromise(task, path, file);
  },

  psqlExecuteScriptInPipelinePromise: function(
    path,
    script,
    file,
    user,
    password,
    database
  ) {
    var tunnel = file.data.bastion_public_ip;
    // TODO is this right? Should we assume this
    // or prompt user for the ssh key
    // or write .ssh/config
    var key = file.data.ssh_public_key_path.replace(/\.pub$/, "");
    var host = file.data.rds_connection_string;
    var username = typeof user == "undefined" ? "root" : user;
    var password =
      typeof password == "undefined"
        ? file.data.postgres_root_password
        : password;
    var database = typeof database == "undefined" ? "postgres" : database;

    console.log(database + " " + username + " " + script);
    var task = " python psql_tunnel.py ";
    task += " --tunnel " + tunnel;
    task += ' --key "' + key + '"';
    task += " --host " + host;
    task += " --user " + username;
    task += ' --password "' + password + '"';
    task += ' --database "' + database + '"';
    task += ' --script "' + script + '"';

    return this.runTaskInPipelinePromise(task, path, file);
  }
};

module.exports = helpers;
