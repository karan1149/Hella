from zoo import app

#
# This is the (dev) entry point of the application.
# Nothing else should be in this file.
#

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)