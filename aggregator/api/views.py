from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework import status
from django.http import HttpResponse
import uuid
import os
import csv

class UploadView(APIView):
   """
   View for file uploads. API endpoint for /api/v1/upload/
   """
   parser_classes = (FormParser, MultiPartParser, )


   def post(self, request, format=None):
      """
      Accept file that has been sent via chunk encoded file.

      Sample cURL command:
      -------------------
         curl -i -F file=@<path_to_csv_file> -F "format=<csv or json>" \
               <host>/api/v1/upload/

      Request Fields:
      --------------
         file:    Path to the file on the client
         format:  csv or json
         
      Response Fields:
      -------------
         status: Indicates whether the file was successfully uploaded
         url:    upload url. Currently a GET on this path is not implemented,
                 because the user might not want to wish to see his uploaded
                 file again.
                 But this would be straightforward to implement.
         token:  A GUID string identifying the unique location of file upload.
                 We use this track state in otherwise stateless REST Framework.

      Response:
      ---------
         {"status":"Accepted",
          "url":"/upload/666b3b22-f161-11e5-9670-060c1144530b",
          "token":"666b3b22-f161-11e5-9670-060c1144530b"}
      """
      response = StreamFile(request.FILES['file'], request.data['format'])


      return Response(response)



class AggregateView(APIView):
   """
   View for uploaded file aggregation. API endpoint for /api/v1/aggregate/
   """

   def post(self, request, format=None):
      """
      Group and aggregate on the user posted values on the files
      previously uploaded.

      Sample cURL command:
      -------------------
         curl -d "token=666b3b22-f161-11e5-9670-060c1144530b&aggOn=count&grpOn=last_name&outType=csv"
                  <host>/api/v1/aggregate/

      Request Fields:
      --------------
         token:   GUID that was generated and returned during the POST /api/v1/upload
         grpOn:   Specify the field in the file that we should perform grouping on.
         aggOn:   Specify the field in the grouped file which we should aggregate.
         outType: Specify the format of results needed. Valid choices are csv or json

      Response:
      --------
         Either json or csv aggregated response. Depends on the value of outType

      """
      token = request.data['token']
      groupOn = request.data['grpOn']
      aggregateOn = request.data['aggOn']
      outputFormat = request.data['outType']
      response = Aggregate(token, groupOn, aggregateOn, outputFormat)
      if outputFormat == "csv":
         return response
      return Response(response)



def StreamFile(fileObj, fileFormat):
   """
      Stub function to handle POST data to api/v1/upload/
   """
   # Generate Token
   token = str(uuid.uuid1())
   uploadFile = os.path.join('/var/www/html/media', token, "data." + fileFormat)
   os.makedirs(os.path.dirname(uploadFile))
   with open(uploadFile, 'wb+') as fileHnd:
      # Upload files in chunks so that we don't overwhelm the server memory util
      for chunk in fileObj.chunks():
         fileHnd.write(chunk)
   # File upload complete
   # Build response dict
   response = {}
   response['status'] = 'Accepted'
   response['token'] = token
   response['url'] = '<url>/upload/' + token
   return response



def Aggregate(token, groupOn, aggregateOn, outputFormat):
   """
      Stub function to handle POST data to api/v1/aggregate/
   """
   parser_classes = (JSONParser,  )
   response = {}
   # Broiler plate code to figure out where the test data lives.
   UPLOAD_ROOT = '/var/www/html/media'
   dataSrcDir = os.path.join(UPLOAD_ROOT, token)
   dataSrcFile = os.listdir(dataSrcDir)[0]
   dataSrcFile = os.path.join(dataSrcDir, dataSrcFile)

   # Start processing
   with open(dataSrcFile) as f:
      # Read only the first line to get column names.
      # Don't do readlines() or read() here as it will overwhelm the server.
      rowHeader = f.readline()
      rowHeader = rowHeader.strip().split(',')

      # Identify the index of the grouping and aggregating data.
      groupOnKeyID = rowHeader.index(groupOn)
      aggregateOnKeyID = rowHeader.index(aggregateOn)

      # Process the line by line. Lazy loading here to avoid High Memory Util
      for rawData in f:
         data = rawData.strip().split(',')
         (groupKey, aggregateVal) = (data[groupOnKeyID],
                                     int(data[aggregateOnKeyID]))
         if groupKey in response:
            response[groupKey] = response[groupKey] + aggregateVal
         else:
            response[groupKey] = aggregateVal

   if outputFormat == "json":
      return response
   if outputFormat == "csv":
      csvResponse = HttpResponse(content_type='text/csv')
      csvResponse['Content-Disposition'] = 'attachment; ' +
                                           'filename="somefilename.csv"'
      writer = csv.writer(csvResponse)
      for (key, value) in response.iteritems():
         writer.writerow([key, value])
      return csvResponse

