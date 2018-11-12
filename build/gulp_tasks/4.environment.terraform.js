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
  
  var config = helpers.getConfigLocations(env, tool);
  console.log(config);

  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(gulp.symlink(config.paths.terraform))
  .pipe(data(function(file) {

    var task = 'terraform init -backend-config='+config.paths.terraform+'/backend.tfvars -reconfigure';
    //var working = terraform_path+tool_path;
    var working = config.paths.terraform_tool;

    return helpers.runTaskInPipelinePromise(task, working, file);

  }));

  return pipeline;
});

gulp.task('environment.terraform_output', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 

  /*
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;
  */
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get terraform output and add to file.data
  .pipe(data(function(file) {

    //var working = terraform_path+tool_path;
    var working = config.paths.terraform_tool;

  	var promise = helpers.getTerraformOutputInPipelinePromise(working, file);

    return promise;
  }))
  .pipe(modifyFile(function(content, path, file)  {
    return JSON.stringify(file.data, null, 4);
  }))
  .pipe(gulp.dest(config.paths.environment));

  return pipeline;
});

gulp.task('environment.terraform_plan', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 

  /*
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;
  */
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.files.environment_settings)
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

  	var task = 'terraform plan -var-file='+config.paths.terraform+'/apply.tfvars -var \'postgres_root_password='+file.data.postgres_root_password+'\'';
  	//var working = terraform_path+tool_path;
  	var working = config.paths.terraform_tool;

    return helpers.runTaskInPipelinePromise(task, working, file);

  }));

  return pipeline;
});

gulp.task('environment.terraform_apply', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 

  /*
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;
  */
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.files.environment_settings)
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

  	var task = 'terraform apply -var-file='+config.paths.terraform+'/apply.tfvars -var \'postgres_root_password='+file.data.postgres_root_password+'\' -auto-approve';
  	//var working = terraform_path+tool_path;
  	var working = config.paths.terraform_tool;

  	return helpers.runTaskInPipelinePromise(task, working, file);

  }));
  return pipeline;
});

gulp.task('environment.terraform_destroy', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 

  /*
  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;
  */
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.files.environment_settings)
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

    var task = 'terraform destroy -var-file='+config.paths.terraform+'/apply.tfvars -var \'postgres_root_password='+file.data.postgres_root_password+'\' -auto-approve';
  	//var working = terraform_path+tool_path;
  	var working = config.paths.terraform_tool;

  	return helpers.runTaskInPipelinePromise(task, working, file);
  }));
  return pipeline;
});

gulp.task('environment.terraform_ssh', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  /*
  console.log(home);

  var root_path = helpers.getRootPath();

  var environment_path = root_path + '/environments/'+env;
  var terraform_path = environment_path+'/terraform';
  var settings_file = environment_path+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;
  */
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.paths.home+'/.ssh/config')
  .pipe(data(function(file) {
    // make .ssh/config writable
    fs.chmodSync(config.paths.home+'/.ssh/config', 0600);
    // read env settings file into file.data
    file.data = JSON.parse(fs.readFileSync(config.files.environment_settings));
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

    var domain = file.data.tool+'.'+env;
    var bastion = "bast."+domain;
    var developer = "dev."+domain;
    // build environment config
    lines.push(env_start);
    lines.push('Host '+bastion);
    lines.push('    User ubuntu');
    lines.push('    HostName '+file.data.bastion_public_ip);
    lines.push('    IdentityFile '+ssh_key);
    lines.push('');
    lines.push('Host '+developer);
    lines.push('    User ubuntu');
    lines.push('    HostName '+file.data.developer_ip);
    lines.push('    IdentityFile '+ssh_key);
    lines.push('    ProxyCommand ssh '+bastion+' nc %h %p');
    lines.push(env_end);
    lines.push('');

    console.log(lines);
    return lines.join('\n');
  }))
  .pipe(gulp.dest(config.paths.home+'/.ssh'))
  .pipe(data(function(file) {
    // reset file permissions
    fs.chmodSync(config.paths.home+'/.ssh/config', 0400);
    return file.data;
  }))
  .pipe(data(function(file) {
    var domain = file.data.tool+'.'+env;
    var hostname = "dev."+domain;
    var prompt = hostname.replace(/\./g,'-');
    var task = "scp build/gulp_helpers/devbox_bootstrap.sh "+hostname+":~ubuntu";
    return helpers.runTaskInPipelinePromise(task, config.paths.root, file);
  }))
  .pipe(data(function(file) {
    var domain = file.data.tool+'.'+env;
    var hostname = "dev."+domain;
    var prompt = hostname.replace(/\./g,'-');
    var task = "ssh "+hostname+" -C \"bash ~ubuntu/devbox_bootstrap.sh "+prompt+"\"";
    return helpers.runTaskInPipelinePromise(task, config.paths.root, file);
  }));

  return pipeline;

});


gulp.task('environment.terraform', gulp.series(
    'environment.terraform_init',
    'environment.terraform_apply',
    'environment.terraform_output',
    'environment.terraform_ssh'
));

