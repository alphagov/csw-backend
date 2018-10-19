var gulp = require('gulp');
var exec = require('gulp-exec');
var data = require('gulp-data');
var args = require('yargs').argv;

gulp.task('environment.terraform', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/')
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  console.log(root_path);

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(gulp.symlink(terraform_path))
  .pipe(exec(
  	'cd '+terraform_path+tool_path+' && terraform init -backend-config='+terraform_path+'/backend.tfvars -reconfigure'
  ))
  .pipe(exec.reporter())
  .pipe(exec(
  	'cd '+terraform_path+tool_path+' && terraform plan -var-file='+terraform_path+'/apply.tfvars'
  ))
  .pipe(exec.reporter());

  return pipeline;
});