var gulp = require('gulp');
var sass = require('gulp-sass');

gulp.task('default', ['copy_assets','sass.csw'], function() {
  // place code for your default task here
});

gulp.task('copy_assets', function() {
  // place code for your default task here
  gulp.src(['node_modules/govuk-frontend/assets/**'])
  .pipe(gulp.dest('../chalice/chalicelib/assets/govuk-frontend/assets'));

  gulp.src(['node_modules/govuk-frontend/*.js'])
  .pipe(gulp.dest('../chalice/chalicelib/assets/govuk-frontend'))
});

gulp.task('sass.gov', function () {
  return gulp.src('node_modules/govuk-frontend/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('../chalice/chalicelib/assets/govuk-frontend'));
});

gulp.task('sass.csw', function () {
  return gulp.src('*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('../chalice/chalicelib/assets'));
})