var gulp = require('gulp');
var reqDir = require('require-dir'), tasks = reqDir('gulp_tasks/');

gulp.task('default', gulp.series('copy.assets','sass.csw'));
