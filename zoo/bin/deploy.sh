#
# Deploys the Model Zoo to heroku.
#
# Usage: ./bin/deploy.sh <git branch to deploy>
#

# Go to the root of the repo
cd ..

# Push Zoo submodule to Heroku
git push heroku `git subtree split --prefix zoo $1`:master

# Go back to root
cd zoo/