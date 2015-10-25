var express = require('express');
var router = express.Router();
var swig = require('swig');


/* GET home page. */
router.get('/', function(req, res, next) {
  var html = swig.renderFile('./html/index.html');
  res.send(html);
});

router.get('/user', function(req, res, next) {

});

module.exports = router;

