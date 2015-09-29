# DB2S3
Backup dropbox files to AWS S3/Glacier

These instructions are not yet complete, but close...

I fired up an EC2 instance for the first use as it could power through the thousands of files around 10 times faster than I could get from our broadband connection. EC2 processed just over 30GB in around two hours.

Firstly, create an app on Dropbox and take a note of the keys. Also create a new bucket on Amazon S3  and get/create access keys for your account.

Next you need to setup a MySQL database and run all the scripts in the SQL folder.

Enter the Dropbox, AWS and database details into process.py

Optionally run the web file from a webserver if you find that a useful way to keep an eye on progress.

Set the value of process lock table to 0. If you want to stop the processing part way through update it to 1.

That should be it, kick it off by issuing: python process.py
