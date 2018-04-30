#
# Sets the environment variables needed for Heroku.
#
# SHOULD NOT BE IN VERSION CONTROL.
#

heroku git:remote -a seer-autohub
heroku config:set GOOGLE_GEOCODE_KEY=AIzaSyDWDzHgqayktuDGcUq_vH838JdxtIIU1rw
heroku config:set GOOGLE_PLACES_KEY=AIzaSyAWTwR_P9HUGhRzti1JepPNlx20Csb_nac
heroku config:set GOOGLE_ELEVATION_KEY=AIzaSyDBC7eEy7H1KX9P8tyzsKGkYfA6cJjDHss