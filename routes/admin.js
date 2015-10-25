var express = require('express');
var router = express.Router();
var swig = require('swig');
var mysql = require("mysql");


/* GET users listing. */
router.get('/', function(req, res, next) {
  con.connect();
  con.query("select count(*) as number, DATE_FORMAT(event_date, '%Y%m%d') AS event_date from fall_event where event_date > '2015-01-00' AND event_date < '2015-02-00' GROUP BY event_date order by event_date;",function(err,rows){
    if(err) {
      console.log(err);
      throw err;
    }

    console.log(rows);

    var x = new Array();
    var y = new Array();
    for (var i = 0; i < rows.length; i++) {
      x.push(rows[i].event_date);
      y.push(rows[i].number);
    }
    var html = swig.renderFile('./html/admin.html', {
      x: x,
      y: y
    });
    res.send(html);

  });
  con.end();
});

// First you need to create a connection to the db
var con = mysql.createConnection({
  host: "127.0.0.1",
  user: "hh-falls",
  password: "1qaz@WSX",
  database: "falls"
});

module.exports = router;
