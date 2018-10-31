const gulp = require('gulp');

// Create the settings and parameters for a new environment
gulp.task('environment.setup', gulp.series(
    'environment.settings',
    'environment.params',
    'environment.tfvars',
    'copy.assets',
    'sass.csw'
));

// Load settings for an existing environment into your clone
gulp.task('environment.load', gulp.series(
    'environment.settings',
    'environment.tfvars',
    'environment.terraform_init',
    'environment.terraform_output',
    'environment.chalice_config',
    'copy.assets',
    'sass.csw'
));

// Build a new environment from scratch
gulp.task('environment.build', gulp.series(
    'environment.setup',
    'environment.terraform',
    'environment.chalice'
));

// Re-copy assets
// Recompile CSS
// Re-apply terraform
// Re-deploy chalice
gulp.task('environment.deploy', gulp.series(
    'copy.assets',
    'sass.csw',
    'environment.terraform',
    'environment.chalice'
));

// Delete chalice and destroy terraformed environment in AWS
// Leaves settings in tact
gulp.task('environment.cleanup', gulp.series(
    'environment.chalice_delete',
    'environment.terraform_destroy'
));