Description:
============

This project implements a RESTful data aggregator. We upload a file with a large number of records 64MM either as a csv or a json file.
We specify a column to group on, a column to aggregate. We return the aggregated data in either csv or json. 

RESTful Endpoints:
================
POST /api/v1/upload/ The endpoint to upload a large file. (Either csv or json)
POST api/v1/aggregate/ The endpoint to perform aggregation on the previously uploaded file.

Usage Example:
==============

1. Upload File:
---------------
  Request:    curl -i -F file=@<path_to_csv_file> -F "format=<csv or json>" <host>/api/v1/upload/
  Response:   {"status":"Accepted",
               "url":"/upload/666b3b22-f161-11e5-9670-060c1144530b",
               "token":"666b3b22-f161-11e5-9670-060c1144530b"}
  On successful upload the server returns a token back to the client. The client has to send a token to the server when it wants to perform aggregation

2. Aggregate File:
-----------------
  Request:   curl -d "token=666b3b22-f161-11e5-9670-060c1144530b&aggOn=count&grpOn=last_name&outType=csv" <host>/api/v1/aggregate/
  Response:  Either csv or json aggregated stream file download.

  The client passes the token, groupOn, AggregateOn parameters and Type to indicate the format it expects the results back in.


  Sample File:
  ------------
  first_name,last_name,count<br>
  Luke,Skywalker,42<br>
  Leia,Skywalker,10<br>
  Anakin,Skywalker,20<br>
  Admiral,Ackbar,10<br>
  Admiral,Tharwn,10<br>
  Kylo,Ren,100<br>
  
  Command:
  -------
  groupOn=last_name , aggregateOn=count
  
  Output:
  -------
  Skywalker:72<br>
  Ackbar:10<br>
  Thrawn:10<br>
  Ren:100


File Description:
==================
All the functionality can be found in: RESTfulDataAggregator/aggregator/api/views.py
Routing rules are in: RESTfulDataAggregator/aggregator/aggregator/urls.py

Utils:
======
You can also find utils folder which has test data generation scripts.

Sample Use:
-----------

python RESTfulDataAggregator/utils/TestDataGenerator/dataGenerator.py --fileType csv --fileSize 10
We specify the file type and the size of the test data file in MB. The script generates first_name,last_name,count csv file
of the required size by randomizing the data from 
RESTfulDataAggregator/utils/TestDataGenerator/firstNames.in and
RESTfulDataAggregator/utils/TestDataGenerator/lastNames.in

You can find the output of this script at: RESTfulDataAggregator/utils/DataSource/TestData.csv

For a 1GB test data we have a whopping 64MM records and the aggregation happens in about 30 seconds on an AWS EC2 Instance

