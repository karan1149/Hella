#
# Deploys the Model Zoo to heroku.
#
# Usage: ./bin/deploy.sh <git branch to deploy>
#

# Push Zoo submodule to Heroku
heroku git:remote -a seer-models
git push heroku $1:master
