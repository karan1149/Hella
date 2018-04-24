

# Go to the root of the repo
cd ..

# Push Zoo submodule to Heroku
git push heroku `git subtree split --prefix zoo $1`:master

# Go back to root
cd zoo/