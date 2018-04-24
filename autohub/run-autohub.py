from autohub import app

import config

#
# This is the (dev) entry point of the application. 
# Nothing else should be in this file. 
#

if __name__ == "__main__":
  app.run(host=config.DEBUG_ADDR, port=config.DEBUG_PORT, debug=True)