/**
    Copy the relevant parts of the govuk-frontend codebase into the deployed
    chalicelib directory
 */
var gulp = require("gulp");

gulp.task("copy.assets_files", function() {
  // place code for your default task here
  return gulp
    .src(["node_modules/govuk-frontend/assets/**"])
    .pipe(gulp.dest("../chalice/chalicelib/assets/govuk-frontend/assets"));
});

gulp.task("copy.assets_scripts", function() {
  return gulp
    .src(["node_modules/govuk-frontend/*.js"])
    .pipe(gulp.dest("../chalice/chalicelib/assets/govuk-frontend"));
});

gulp.task(
  "copy.assets",
  gulp.series("copy.assets_files", "copy.assets_scripts")
);
