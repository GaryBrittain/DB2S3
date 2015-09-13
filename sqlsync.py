import MySQLdb as db

HOST = ""
PORT = 
USER = ""
PASSWORD = ""
DB = ""

def post_file (path, filename):

  try:
    conn = db.Connection(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
    dbhandler = conn.cursor(db.cursors.DictCursor)
    sql = ("INSERT INTO db2s3 (PATH, FILENAME, DROPBOX_DOWNLOADED) VALUES('%s','%s', NOW())")%(path, filename)
    dbhandler.execute(sql)
    conn.commit()
    conn.close()

  except Exception as e:
    with open("errors.txt", "a") as err:
      err.write('Failed to upload meta to database for: '+str(path)+"\n")
      err.close()

def next_file_to_process():

  try:
    conn = db.Connection(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
    dbhandler = conn.cursor(db.cursors.DictCursor)
    sql = ("SELECT PATH, FILENAME FROM db2s3 WHERE S3_UPLOADED IS NULL")
    dbhandler.execute(sql)
    return dbhandler.fetchall()
    conn.close()
  except:
    return 'failure'

def s3_uploaded_confirm(path):
  try:
    conn = db.Connection(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
    dbhandler = conn.cursor(db.cursors.DictCursor)
    sql = ("UPDATE db2s3 SET S3_UPLOADED = NOW() WHERE PATH = '%s'")%(path)
    dbhandler.execute(sql)
    conn.commit()
    conn.close()
  except Exception as e:
    with open("errors.txt", "a") as err:
      err.write('Failed to update S3 date in db for: '+str(path)+"\n")
      err.close()

def check_lock():

  try:
    conn = db.Connection(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
    dbhandler = conn.cursor(db.cursors.DictCursor)
    sql = ("SELECT LOCKED FROM PROCESS_LOCK")
    dbhandler.execute(sql)
    lock = dbhandler.fetchone()
    return lock["LOCKED"]
    conn.close()
  except:
    return 1
