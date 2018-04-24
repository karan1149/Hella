#
# Deploys the SeeR AutoHub to heroku.
#
# Usage: ./bin/deploy.sh <git branch to deploy>
#

# Go to the root of the repo
cd ..

# Push AutoHub submodule to Heroku
heroku git:remote -a seer-autohub
git push heroku `git subtree split --prefix autohub $1`:master

# Go back to zoo
cd autohub/