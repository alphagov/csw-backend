/**
  Define a .chalice/config.json config file from the terraform outputs and environment settings
*/
const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const exec = require('child-process-promise').exec;
const awsParamStore = require('aws-param-store');
const fs = require('fs');

console.log(process.cwd());
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");


gulp.task('environment.chalice_config', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var settings_file = root_path + '/environments/'+env+'/settings.json';
  var default_chalice_config = root_path + '/environments/example/.chalice/config.json';
  var target_chalice_path = root_path + '/environments/'+env+'/.chalice';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default chalice config file

  var pipeline = gulp.src(default_chalice_config)
  .pipe(data(function(file) {

    var task = 'terraform output -json';
  	var working = terraform_path+tool_path;

  	return helpers.getJsonDataInPipelinePromise(task, working, file);

  }))
  .pipe(data(function(file) {
    // read env settings file into file.data
    file.data.settings = JSON.parse(fs.readFileSync(settings_file));
    console.log(file.data.settings);
    return file.data;
  }))
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/user';
    var property = 'postgres_user_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.settings.region, file, property);

  }))
  .pipe(modifyFile(function(content, path, file) {

    function renameProperty(object, oldName, newName) {
      object[newName] = object[oldName];
      delete(object[oldName]);
    }

    // set stage name = env
    file.data.config = JSON.parse(content);
    renameProperty(file.data.config.stages, '<env>', env);

    // set database credentials
    file.data.config.stages[env].environment_variables.CSW_ENV = file.data.settings.prefix;
    file.data.config.stages[env].environment_variables.CSW_PASSWORD = file.data.postgres_user_password;
    file.data.config.stages[env].environment_variables.CSW_HOST = file.data.rds_connection_string.value;

    var subnets = [
      file.data.public_subnet_1_id.value,
      file.data.public_subnet_2_id.value
    ];
    var security_groups = [
      file.data.public_security_group_id.value,
    ];

    for (lambda in file.data.config.stages[env].lambda_functions) {
      console.log(lambda);
      file.data.config.stages[env].lambda_functions[lambda].subnet_ids = subnets;
      file.data.config.stages[env].lambda_functions[lambda].security_group_ids = security_groups;
    }

    file.data.content = JSON.stringify(file.data.config, null, 4);
    return file.data.content;
  }))
  .pipe(gulp.dest(target_chalice_path));

  return pipeline;
});


gulp.task('environment.chalice_deploy', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var chalice_path = root_path + '/chalice';
  var settings_file = root_path + '/environments/'+env+'/settings.json';
  var chalice_config = root_path + '/environments/'+env+'/.chalice';
  var tool_path = '/csw-infra/tools/'+tool;


  var pipeline = gulp.src(chalice_config)
  // symlink .chalice folder into csw-backend/chalice folder
  .pipe(gulp.symlink(chalice_path))
  // execute the chalice deploy function for stage=env
  .pipe(data(function(file) {
    
    var task = 'chalice deploy --stage='+env;

    return helpers.runTaskInPipelinePromise(task, chalice_path, file);
  }));

  return pipeline;

});


gulp.task('environment.chalice_delete', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var chalice_path = root_path + '/chalice';
  var settings_file = root_path + '/environments/'+env+'/settings.json';
  var chalice_config = root_path + '/environments/'+env+'/.chalice';
  var tool_path = '/csw-infra/tools/'+tool;


  var pipeline = gulp.src(chalice_config)
  // symlink .chalice folder into csw-backend/chalice folder
  .pipe(gulp.symlink(chalice_path))
  // execute the chalice deploy function for stage=env
  .pipe(data(function(file) {
    
    var task = 'chalice delete --stage='+env;

    return helpers.runTaskInPipelinePromise(task, chalice_path, file);
  }));

  return pipeline;

});
