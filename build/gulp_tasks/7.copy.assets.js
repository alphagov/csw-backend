var gulp = require('gulp');

gulp.task('copy.assets', function() {
  // place code for your default task here
  gulp.src(['node_modules/govuk-frontend/assets/**'])
  .pipe(gulp.dest('../chalice/chalicelib/assets/govuk-frontend/assets'));

  gulp.src(['node_modules/govuk-frontend/*.js'])
  .pipe(gulp.dest('../chalice/chalicelib/assets/govuk-frontend'))
});