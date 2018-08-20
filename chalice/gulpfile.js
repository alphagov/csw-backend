var gulp = require('gulp');
var sass = require('gulp-sass');

gulp.task('default', function() {
  // place code for your default task here
});

gulp.task('copy_templates', function() {
  // place code for your default task here
  gulp.src(['node_modules/govuk-frontend/**/*'])
  .pipe(gulp.dest('chalicelib/templates/govuk-frontend'));

  gulp.src(['node_modules/govuk-frontend/assets'])
  .pipe(gulp.dest('chalicelib/templates'));
});

gulp.task('sass.gov', function () {
  return gulp.src('chalicelib/templates/govuk-frontend/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('chalicelib/templates/govuk-frontend'));
});

gulp.task('sass.csw', function () {
  return gulp.src('chalicelib/templates/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('chalicelib/templates'));
})