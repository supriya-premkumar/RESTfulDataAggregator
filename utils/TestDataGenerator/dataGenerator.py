from argparse import ArgumentParser
import random
import os
import sys
parser = ArgumentParser()
parser.add_argument('--fileType', dest='fileType', required=True,
                    choices=['csv', 'json'],
                    help=r'Output File Type')
parser.add_argument('--fileSize', dest='fileSize', required=True,
                    type=float,
                    help=r'Output File Size in MB')

args = parser.parse_args()
outFileName = "TestData" + "." + args.fileType
outFile = os.path.join(os.path.dirname(os.getcwd()),
                                       "DataSource",
                                       outFileName)
try:
   with open("firstNames.in", 'rb') as first,\
        open("lastNames.in", 'rb') as last,\
        open(outFile, 'wb') as out:
      firstNames = first.readlines()
      lastNames = last.readlines()
      csvLine = "first_name,last_name,count"
      out.write(csvLine + "\n")
      if (args.fileType == "json"):
         print "Not Implmented Yet!"
         sys.exit(0)
      for (firstName, lastName)  in zip(firstNames, lastNames):
         if (args.fileType == "csv"):
            while(out.tell() < args.fileSize*1024*1024):
               csvLine = random.choice(firstNames).strip() + "," + \
                         random.choice(lastNames).strip() + "," + \
                         str(random.randint(0, 100))
               out.write(csvLine + "\n")
            #print >> out, firstName.strip() + lastName.strip()
         elif (args.fileType == "json"):
            pass
      if(args.fileType=="csv"):
         print "CSV File of %sMB generated at:../DataSource/TestData.csv" \
               % args.fileSize


except IOError as e:
   print "Could not open: %s" % e.strerror
