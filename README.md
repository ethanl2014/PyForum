# PyForum

Flask-based forum web app

Can be viewed here: https://ethansforum.herokuapp.com/

To run offline:
'''
Clone repository and install requirements (I recommend using virtual environment)
open command prompt and navigate to repository (cd here etc.) ("open" venv if using)
set FLASK_APP=forum.py
flask run
'''

To run your own on heroku:
'''
Create heroku account and install the CLI from heroku website
Clone this repository
Create Procfile in it that contains
	web: flask db upgrade; gunicorn forum:app
{if you haven't made a procfile before, open a text editor like notepad, paste the above, then save as "Procfile" with no file extension}

Open command prompt:
  navigate to this repository (cd PyForum etc.)
	heroku login (self-explanatory, allows heroku commands later on)
	git init .
	git add . 
	git commit -a -m "heroku commit" (these three commands set up repository to be "pushed" to heroku later on
	heroku apps:create forumname (replace forumname with the name you want in the url, must be unique so you can't choose ethansforum if your name is ethan :p)
	heroku addons:add heroku-postgresql:hobby-dev (base repository has sqlite for ease of use but heroku does not guarantee constant hd memory so postgresql db server is setup instead) 
	heroku config:set LOG_TO_STDOUT=1 (heroku is setup to send everything to stdout so this command sends our logs there so we can read if there is problem)
	heroku addons:create searchbox:starter (base repository uses installed "localhost" elasticsearch. for web use we need online elasticsearch which we can get thru searchbox) 
	heroku config:get SEARCHBOX_URL (will return an elasticsearch url)
	heroku config:set ELASTICSEARCH_URL={whatever url the above command gave you, no brackets} (sets or elasticsearch to go there instead of localhost)

  curl -XPUT 'localhost:9200/post?pretty' -H 'Content-Type: application/json' -d'{"settings" : {"index" : {"number_of_shards" : 5, 	"number_of_replicas" : 1 }}}'                                                              
    replacing localhost:9200 with the elasticsearch url from above
    (this is necessary because normal elasticsearch will auto create an index if there isn't one, but searchbox will not. If you get an error along the lines of "no post index" when   
    searching, look up this step

  heroku config:set FLASK_APP=forum.py
	git push heroku master
  heroku open
'''
