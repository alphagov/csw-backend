/**
    Wrapper tasks to group common build and deploy functions.
 */
const gulp = require('gulp');

gulp.task('environment.assets', gulp.series(
    'copy.assets',
    'sass.csw',
    'concat.js'
));
// Create the settings and parameters for a new environment
gulp.task('environment.setup', gulp.series(
    'environment.settings',
    'environment.params',
    'environment.tfvars',
    'environment.assets'
));

// Load settings for an existing environment into your clone
gulp.task('environment.load', gulp.series(
    'environment.settings',
    'environment.tfvars',
    'environment.terraform_init',
    'environment.terraform_output',
    'environment.chalice_config',
    'environment.assets'
));

// Build a new environment from scratch
gulp.task('environment.build', gulp.series(
    'environment.setup',
    'environment.terraform',
    'environment.chalice_s3_deploy',
    'environment.database_build'
));

// Build a new environment's infrastructure from scratch
// No chalice deploy
// No database bootstrapping
gulp.task('environment.infrastructure', gulp.series(
    'environment.setup',
    'environment.terraform'
));

// Separate
gulp.task('environment.redeploy', gulp.series(
    'environment.assets',
    'environment.database_migrate',
    'environment.chalice_s3_deploy',
    'environment.database_define_criteria'
));

// Re-copy assets
// Re-compile CSS
// Re-apply terraform
// Re-deploy chalice
gulp.task('environment.deploy', gulp.series(
    'environment.terraform',
    'environment.redeploy'
));

// Delete chalice and destroy terraformed environment in AWS
// Chalice.destroy wrappers the methods to sync the statefile with S3
// Leaves settings in tact
gulp.task('environment.cleanup', gulp.series(
    'environment.chalice_s3_delete',
    'environment.terraform_init',
    'environment.terraform_destroy'
));