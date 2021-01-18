# PyForum

Flask-based forum web app

Can be viewed here: https://ethansforum.herokuapp.com/

To run offline:

'''''

1) Clone repository and install requirements (I recommend using virtual environment)

2) Open command prompt and navigate to repository (cd here etc.) ("open" venv if using)

3) Set FLASK_APP=forum.py

4) Flask run

'''''

To run your own on heroku:

'''''

1) Create heroku account and install the CLI from heroku website

2) Clone this repository

3) Create Procfile in it that contains

		web: flask db upgrade; gunicorn forum:app
	
{if you haven't made a procfile before, open a text editor like notepad, paste the above, then save as "Procfile" with no file extension}

4) Open command prompt:

5) Navigate to this repository (cd PyForum etc.)
  
6) Heroku login (self-explanatory, allows heroku commands later on)
	
7) Git init .
	
8) Git add . 
	
9) Git commit -a -m "heroku commit" (these three commands set up repository to be "pushed" to heroku later on
	
10) Heroku apps:create forumname (replace forumname with the name you want in the url, must be unique so you can't choose ethansforum if your name is ethan :p)
	
11) Heroku addons:add heroku-postgresql:hobby-dev (base repository has sqlite for ease of use but heroku does not guarantee constant hd memory so postgresql db server is setup instead) 

12) Heroku config:set LOG_TO_STDOUT=1 (heroku is setup to send everything to stdout so this command sends our logs there so we can read if there is problem)
	
13) Heroku addons:create searchbox:starter (base repository uses installed "localhost" elasticsearch. for web use we need online elasticsearch which we can get thru searchbox) 

14) Heroku config:get SEARCHBOX_URL (will return an elasticsearch url)
	
15) Heroku config:set ELASTICSEARCH_URL={whatever url the above command gave you, no brackets} (sets or elasticsearch to go there instead of localhost)

16) Curl -XPUT 'localhost:9200/post?pretty' -H 'Content-Type: application/json' -d'{"settings" : {"index" : {"number_of_shards" : 5, 	"number_of_replicas" : 1 }}}' 
  
   replacing localhost:9200 with the elasticsearch url from above
    
   (this is necessary because normal elasticsearch will auto create an index if there isn't one, but searchbox will not. If you get an error along the lines of "no post index" when   
    searching, look up this step

17) Heroku config:set FLASK_APP=forum.py
  
18) Git push heroku master
	
19) Heroku open
  
'''''
