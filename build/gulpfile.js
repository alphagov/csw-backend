const gulp = require('gulp');
const helpers = {
	runTaskPromise: function(task, dir) {

		var during = exec(task, { cwd: dir, stdio: 'inherit' });

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
	},

	getParameterPromise: function(parameter) {

		var promise = awsParamStore.getParameter( '/csw/google/api-credentials', { region: file.data.region })

    	promise.then(function(parameter) {
      		file.data.google_creds = parameter.Value.replace(/\"/g,"'");
      		return file.data;
    	});

    	return promise;
	}
};
const reqDir = require('require-dir'), tasks = reqDir('gulp_tasks/');


gulp.task('default', gulp.series('copy.assets','sass.csw'));
