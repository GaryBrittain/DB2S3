import dropbox
import sys
from sqlsync import *
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
from pushover import message

conn = S3Connection('', '')
pb = conn.get_bucket('backup--dropbox')

access_token = ''

client = dropbox.client.DropboxClient(access_token)
curr_cursor_file = open("cursor.txt", "r")
curr_cursor = curr_cursor_file.read()
curr_cursor_file.close()

next_cursor = client.delta(curr_cursor, '/Camera Uploads')
curr_cursor_file = open("cursor.txt", "w")
curr_cursor_file.write(next_cursor['cursor'])
curr_cursor_file.close()

new_files = 1

if len(next_cursor['entries']) > 0:
 for entry in next_cursor['entries']:
  if entry[1] != None:
    cur_path = entry[0]
    cur_file = cur_path.rsplit("/",1)[1]
    print 'processing file ['+str(new_files)+']: ' + cur_file
    post_file(cur_path, cur_file)
    new_files = new_files + 1
  else:
    print entry[0] + " has been removed."
    with open("errors.txt", "a") as err:
      err.write('File removed from dropbox: '+str(entry[0])+"\n")
      err.close()
else:
  print "No files have changed."
  new_files = 0

uploaded = 0
failed = 0

path = next_file_to_process()
workload = len(path)
processed = 0

for i in path:
  if check_lock() == 1:
    print 'Process locked by database, terminating...'
    message('Process locked by database, terminating...')
    break

  processed = processed + 1
  cPath = i["PATH"]
  cFile = i["FILENAME"]
  print '.'
  print 'Processing ' + str("{:,}".format(processed)) + ' of ' + str("{:,}".format(workload)) + ': ' + cPath
  out = open(cFile, 'wb')
  try:
    with client.get_file(cPath) as f:
      out.write(f.read())
      print 'Downloaded'
  except:
    failed = failed + 1
    print 'Error downloading ' + cPath
    with open("errors.txt", "a") as err:
      err.write('Could not download from dropbox file: '+str(cPath)+"\n")
      err.close()
    continue
  k = Key(pb)
  k.name = cPath
  try:
    k.set_contents_from_filename(cFile)
    os.remove(cFile)
    print 'Uploaded'
    s3_uploaded_confirm(cPath)
    uploaded = uploaded + 1
  except:
    print 'Error uploading ' + cPath

print '******************************'
summary = """%s new files found
%s files uploaded
%s failures - check errors.txt for info"""%(new_files,uploaded,failed)

message(summary)

print 'Finished!'
print summary
