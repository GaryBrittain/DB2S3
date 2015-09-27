import dropbox
import sys
from sqlsync import *
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
from pushover import message
import json

if check_lock() == 1:
  print 'Database is locked or unreachable, quitting...'
  sys.exit()

conn = S3Connection('', '')
pb = conn.get_bucket('')

access_token = 'YOUR DROPBOX APP'

client = dropbox.client.DropboxClient(access_token)
curr_cursor_file = open("cursor.txt", "r") 
curr_cursor = curr_cursor_file.read()
curr_cursor_file.close()

next_cursor = client.delta(curr_cursor, '/Camera Uploads')
curr_cursor_file = open("cursor.txt", "w") 
curr_cursor_file.write(next_cursor['cursor'])
curr_cursor_file.close()

new_files = 0
 
if len(next_cursor['entries']) > 0:
 for entry in next_cursor['entries']:
  if entry[1] != None:
    cur_path = entry[0]
    cur_file = cur_path.rsplit("/",1)[1]
    print 'processing file ['+str(new_files+1)+']: ' + cur_file
    post_file(cur_path, cur_file)
    new_files += 1
  else:
    print entry[0] + " has been removed."    
    with open("errors.txt", "a") as err:
      err.write('File removed from dropbox: '+str(entry[0])+"\n")
      err.close()
else:
  print "No files have changed."

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

  processed += 1
  cPath = i["PATH"]
  cFile = i["FILENAME"]
  print ' '
  print 'Processing ' + str("{:,}".format(processed)) + ' of ' + str("{:,}".format(workload)) + ': ' + cPath
  meta = client.metadata(cPath)
  bytes = meta['bytes']
  print meta['size']
#100MB chunks
  chunk_size = 104857600
  chunk_loops = int(bytes / chunk_size) + 1
  current = 0
  chunk_loop = 1
  out = open(cFile, 'wb')
  try:
    while (bytes > current):
      print 'Downloading chunk %s of %s' % (chunk_loop, chunk_loops)
      chunk_loop += 1
      f = client.get_file(cPath, rev=None, start=current, length=chunk_size)
      out.write(f.read())
      current += chunk_size
  except:
    failed += 1
    print 'Error downloading ' + cPath
    with open("errors.txt", "a") as err:
      err.write('Could not download from dropbox file: '+str(cPath)+"\n")
      err.close()
    continue
  print 'Downloaded'
  out.close()
  filesize = os.path.getsize(cFile)
  if bytes != filesize:
    print 'Downloaded file corrupted'
    failed += 1
    continue
  k = Key(pb)
  k.name = cPath
  try:
    k.set_contents_from_filename(cFile, encrypt_key=True)
    os.remove(cFile)
    print 'Uploaded'
    s3_uploaded_confirm(cPath, meta['size'], meta['bytes'], meta['rev'], meta['revision'], meta['mime_type'], meta['modified'], meta['client_mtime'])
    uploaded = uploaded + 1
  except:
    print 'Error uploading ' + cPath

try:
  k.name='/db2s3/cursor.txt'
  k.set_contents_from_filename('cursor.txt', encrypt_key=True)
except:
  print 'could not copy cursor key to S3'

print '******************************'
summary = """%s new files found
%s files uploaded
%s failures - check errors.txt for info"""%(new_files,uploaded,failed)

message(summary)

print 'Finished!'
print summary
