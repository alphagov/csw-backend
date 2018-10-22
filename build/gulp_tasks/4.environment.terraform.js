/**
  Run terraform init, plan, apply and destroy from the var files defined. 
*/
const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const exec = require('child-process-promise').exec;

gulp.task('environment.terraform_init', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(gulp.symlink(terraform_path))
  .pipe(data(function(file) {
    
    var during = exec('terraform init -backend-config='+terraform_path+'/backend.tfvars -reconfigure', { cwd: terraform_path+tool_path, stdio: 'inherit' });

    var execProcess = during.childProcess;
    execProcess.stdout.on('data', function (data) {
      console.log(data.toString());
    });

    var after = during.then(
      function(out) {
        console.log("SUCCESS");
        console.log(out.stdout);
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        return file.data;
      }
    );

    return after;
  }));

  return pipeline;
});

gulp.task('environment.terraform_output', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(gulp.symlink(terraform_path))
  .pipe(data(function(file) {
    
    var during = exec('terraform output', { cwd: terraform_path+tool_path, stdio: 'inherit' });

    var execProcess = during.childProcess;
    execProcess.stdout.on('data', function (data) {
      console.log(data.toString());
    });

    var after = during.then(
      function(out) {
        console.log("SUCCESS");
        console.log(out.stdout);
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        return file.data;
      }
    );

    return after;
  }));

  return pipeline;
});

gulp.task('environment.terraform_plan', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(data(function(file) {
  	var during = exec('terraform plan -var-file='+terraform_path+'/apply.tfvars', { cwd: terraform_path+tool_path, stdio: 'inherit' });

    var execProcess = during.childProcess;
    execProcess.stdout.on('data', function (data) {
      console.log(data.toString());
    });

    var after = during.then(
      function(out) {
        console.log("SUCCESS");
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        return file.data;
      }
    );

    return after;
  }));

  return pipeline;
});

gulp.task('environment.terraform_apply', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(data(function(file) {
  	var during = exec('terraform apply -var-file='+terraform_path+'/apply.tfvars -auto-approve', { cwd: terraform_path+tool_path, stdio: 'inherit' });

    var execProcess = during.childProcess;
    execProcess.stdout.on('data', function (data) {
      console.log(data.toString());
    });

    var after = during.then(
      function(out) {
        console.log("SUCCESS");
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        return file.data;
      }
    );

    return during;

  }));
  return pipeline;
});

gulp.task('environment.terraform_destroy', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(data(function(file) {
    var during = exec('terraform destroy -var-file='+terraform_path+'/apply.tfvars -auto-approve', { cwd: terraform_path+tool_path, stdio: 'inherit' });

    var execProcess = during.childProcess;
    execProcess.stdout.on('data', function (data) {
      console.log(data.toString());
    });

    var after = during.then(
      function(out) {
        console.log("SUCCESS");
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        return file.data;
      }
    );

    return during;
  }));
  return pipeline;
});

gulp.task('environment.terraform', gulp.series('environment.terraform_init','environment.terraform_apply'));

