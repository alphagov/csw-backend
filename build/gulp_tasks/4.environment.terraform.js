/**
  Run terraform init, plan, apply and destroy from the var files defined. 
*/
const os = require('os');
const fs = require('fs');
const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const rename = require('gulp-rename');
const exec = require('child-process-promise').exec;
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

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

    var task = 'terraform init -backend-config='+terraform_path+'/backend.tfvars -reconfigure';
    var working = terraform_path+tool_path;

    return helpers.runTaskInPipelinePromise(task, working, file);

  }));

  return pipeline;
});

gulp.task('environment.terraform_output', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;

  // Load settings file
  var pipeline = gulp.src(settings_file)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get terraform output and add to file.data
  .pipe(data(function(file) {

    var working = terraform_path+tool_path;

  	var promise = helpers.getTerraformOutputInPipelinePromise(working, file);

    return promise;
  }))
  .pipe(modifyFile(function(content, path, file)  {
    return JSON.stringify(file.data, null, 4);
  }))
  .pipe(gulp.dest(environment_path));

  return pipeline;
});

gulp.task('environment.terraform_plan', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;

  // Load settings file
  var pipeline = gulp.src(settings_file)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get RDS root password from parameter store
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/root';
    var property = 'postgres_root_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  .pipe(data(function(file) {

  	var task = 'terraform plan -var-file='+terraform_path+'/apply.tfvars -var \'postgres_root_password='+file.data.postgres_root_password+'\'';
  	var working = terraform_path+tool_path;

    return helpers.runTaskInPipelinePromise(task, working, file);

  }));

  return pipeline;
});

gulp.task('environment.terraform_apply', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;

  // Load settings file
  var pipeline = gulp.src(settings_file)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get RDS root password from parameter store
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/root';
    var property = 'postgres_root_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  .pipe(data(function(file) {

  	var task = 'terraform apply -var-file='+terraform_path+'/apply.tfvars -var \'postgres_root_password='+file.data.postgres_root_password+'\' -auto-approve';
  	var working = terraform_path+tool_path;

  	return helpers.runTaskInPipelinePromise(task, working, file);

  }));
  return pipeline;
});

gulp.task('environment.terraform_destroy', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;

  // Load settings file
  var pipeline = gulp.src(settings_file)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get RDS root password from parameter store
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/root';
    var property = 'postgres_root_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  .pipe(data(function(file) {

    var task = 'terraform destroy -var-file='+terraform_path+'/apply.tfvars -var \'postgres_root_password='+file.data.postgres_root_password+'\' -auto-approve';
  	var working = terraform_path+tool_path;

  	return helpers.runTaskInPipelinePromise(task, working, file);
  }));
  return pipeline;
});

gulp.task('environment.terraform_ssh', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var home = os.homedir();
  console.log(home);

  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;

  // Load settings file
  var pipeline = gulp.src(home+'/.ssh/config')
  .pipe(data(function(file) {
    // make .ssh/config writable
    fs.chmodSync(home+'/.ssh/config', 0600);
    // read env settings file into file.data
    file.data = JSON.parse(fs.readFileSync(settings_file));
    return file.data;
  }))
  .pipe(modifyFile(function(content, path, file) {

    var i,j,lines,line,env_start,env_end,line_start,line_end, found, removed, remove, shh_key;

    env_start = '# ' + file.data.prefix + ' start #';
    env_end = '# ' + file.data.prefix + ' end #';
    lines = content.split(/\n/);

    found = false;

    for (i in lines) {

        line = lines[i].trim();

        if (line == env_start) {
            found = true;
            line_start = i;
        } else if (line == env_end) {
            line_end = i;
        }

    }

    if (found) {
        console.log('start: '+line_start + ' end: '+line_end);
        remove = (line_end + 1 - line_start);
        removed = lines.splice(line_start, remove);
        console.log(removed);
    }
    ssh_key = file.data.ssh_public_key_path.replace(/\.pub$/,'');

    // build environment config
    lines.push(env_start);
    lines.push('Host '+file.data.prefix+'.bst');
    lines.push('    User ubuntu');
    lines.push('    HostName '+file.data.bastion_public_ip);
    lines.push('    IdentityFile '+ssh_key);
    lines.push('');
    lines.push('Host '+file.data.prefix+'.dev');
    lines.push('    User ubuntu');
    lines.push('    HostName '+file.data.developer_ip);
    lines.push('    IdentityFile '+ssh_key);
    lines.push('    ProxyCommand ssh '+file.data.prefix+'.bst nc %h %p');
    lines.push(env_end);
    lines.push('');

    console.log(lines);
    return lines.join('\n');
  }))
  .pipe(gulp.dest(home+'/.ssh'))
  .pipe(data(function(file) {
    // reset file permissions
    fs.chmodSync(home+'/.ssh/config', 0400);
    return file.data;
  }))
  .pipe(data(function(file) {
    hostname = file.data.prefix+".dev"
    task = "ssh "+hostname+" -C \"sudo hostname "+hostname+"\"";
    return helpers.runTaskInPipelinePromise(task, environment_path, file);
  }));

  return pipeline;

});


gulp.task('environment.terraform', gulp.series(
    'environment.terraform_init',
    'environment.terraform_apply',
    'environment.terraform_output',
    'environment.terraform_ssh'
));

