Intelligence
============

A.K.A Macro Analysis. This module examines the social data on a high level to determine key findings about the conversations and populations as a whole. Example output include mention trends, geo distribution, and emotions breakdown.

Local Installation:
------------------

```shell
sudo pip install -r requirements.txt
```


Local Deployment:
----------------

To run Flask developement server:
```shell
python app.py [--prod]
```

To run Gunicorn (production) server:
```shell
gunicorn app:app --bind localhost:5001
```
*Gunicorn server requires env variable TEST=1 to run in test mode*


Intelligence Workers
=============
A celery job queue running on Heroku to do the heavy liftings.

Iron.io
------------
* MQ: intelligence
* Cache: 
  * intelligence-tasks - help Intelligence to keep track of running tasks
  * intelligence - store return values of celery tasks


Export Workers
============
A celery job queue and an Nginx server running on DigitalOcean (export.getsoshio.com) to generate exports and provide downloads.

Iron.io
-------------
* MQ: export
* Cache:
  * intelligence-tasks - sharing with Intelligence Workers to keep track of running tasks
  * intelligence - store return values (in this case, download urls) of celery tasks

Celery
------------
Managed by **supervisor**. Auto recovery from crash and auto start on boot.
* include **celeryd.conf** in **supervisord.conf** (in /etc/supervisor/).

Nginx
-----------
Serving files in **downloads** folder in the project directory.

Crontab
-----------
Clean up files older than 30 minutes every 15 minutes
> \*/15 \* \* \* \* find /home/tech/intelligence/downloads/\* -mmin +30 -exec rm {} \\;

SSL certificate (Self-signed)
----------
Located at /etc/nginx/ssl
* server.crt : the certificate
* server.key  : private key
* server.key.org : pass-phrase-enabled private key (pass-phrase: soshiotech)


