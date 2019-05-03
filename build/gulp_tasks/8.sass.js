/**
    Compile the default govuk-frontend SASS and
    any extensions added by CSW and save
    compiled CSS to deployed chalicelib folder
 */
var gulp = require("gulp");
var sass = require("gulp-sass");

gulp.task("sass.gov", function() {
  return gulp
    .src("node_modules/govuk-frontend/*.scss")
    .pipe(sass().on("error", sass.logError))
    .pipe(gulp.dest("../chalice/chalicelib/assets/govuk-frontend"));
});

gulp.task("sass.csw", function() {
  return gulp
    .src("*.scss")
    .pipe(sass().on("error", sass.logError))
    .pipe(gulp.dest("../chalice/chalicelib/assets"));
});
