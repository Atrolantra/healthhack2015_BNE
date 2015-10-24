var express = require('express');
var router = express.Router();
var swig = require('swig');


/* GET home page. */
router.get('/', function(req, res, next) {
  var html = swig.renderFile('./html/index.html');
  res.send(html);
});

module.exports = router;
