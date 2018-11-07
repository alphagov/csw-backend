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
    'environment.chalice_s3_deploy',
    'environment.database_build'
));

// Re-copy assets
// Re-compile CSS
// Re-apply terraform
// Re-deploy chalice
gulp.task('environment.deploy', gulp.series(
    'copy.assets',
    'sass.csw',
    'environment.terraform',
    'environment.chalice_s3_deploy'
));

// Delete chalice and destroy terraformed environment in AWS
// Chalice.destroy wrappers the methods to sync the statefile with S3
// Leaves settings in tact
gulp.task('environment.cleanup', gulp.series(
    'environment.chalice_s3_delete',
    'environment.terraform_destroy'
));