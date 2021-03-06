import flask 
import logging
from waitress import serve
from flask import jsonify, request
from WebProcessor import WebProcessor

FORMAT = '%(asctime)s  %(levelname)s : %(module)s -> %(funcName)s -> %(message)s'
logging.basicConfig(filename="application.log", level=logging.INFO, format=FORMAT)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>UNKNOWN RESOURCE</h1><p>The resource could not be found.</p>", 404

@app.route('/', methods=['GET'])
def home():
    html = """
<!DOCTYPE html>
<html>
<title>WebAPI</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<body>  
	<h1>Simple API to check website details</h1>	
	<p>	- get amount of HTML tags used on the page </p>
	<p> - where the domain was registered? </p>
	<p> - get IP address of the domain </p>	
	<p> - who is the owner of the IP? </p>
	<p> - webserver type / programming language </p>
	<h1> Usage:</h1>
	<p>1) http://$YOUR_IP_OR_DOMAIN:8080/api/v1/checkpage?url=$URL_TO_CHECK_HERE</p>
	<p>Upon request you'll receive an ID to use in getpageinfo method</p>
	<p>2) http://$YOUR_IP_OR_DOMAIN:8080/api/v1/getpageinfo?id=$ID</p>
	<p>3) http://$YOUR_IP_OR_DOMAIN:8080/api/v1/getall</p>
	<p>Upon request you'll receive the list of IDs to use in getpageinfo method</p>
	<h1> Example:</h1>	
	<p>1) http://127.0.0.1:8080/api/v1/checkpage?url=https://www.w3schools.com/python/default.asp</p>	
	<p>2) http://127.0.0.1:8080/api/v1/getpageinfo?id=12</p>
	<p>3) http://127.0.0.1:8080/api/v1/getall</p>
</body>
</html>
    """
    return html

@app.route('/api/v1/checkpage', methods=['GET'])
def checkPage():
    try:
        logging.info('Request to endpoing /checkpage')
        if 'url' in request.args:
            url = str(request.args['url'])
            WebProcessor.getInfo(url)
            WebProcessor.getTags(url)
            WebProcessor.getTechStack(url)
            last_id = WebProcessor.insertData(url)
            if last_id:
                outcome = {
                    "Result": "Success!",
                    "Website ID": last_id,
                    "To get results use": "/api/v1/getpageinfo?id=$YOUR_ID_HERE"
                }
                return jsonify(outcome)
        else:
            logging.error('URL cannot be None')

    except Exception as e:
        logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        outcome = {
            "Result": "FAIL. Please check application.log for details"
        }
        return jsonify(outcome)
    

@app.route('/api/v1/getpageinfo', methods=['GET'])
def getPageInfo():
    try:
        logging.info('Request to endpoing /getpageinfo')
        if 'id' in request.args:
            id = int(request.args['id'])
        else:
            logging.error('ID cannot be None')

        outcome = WebProcessor.selectById(id)
        return jsonify(outcome)
    except Exception as e:
        logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        outcome = {
            "Result": "FAIL. Please check application.log for details"
        }
        return jsonify(outcome)

@app.route('/api/v1/getall', methods=['GET'])
def getAll():
    try:
        logging.info('Request to endpoing /getall')
        outcome = WebProcessor.selectList()
        return jsonify(outcome)
    except Exception as e:
        logging.exception(f"Exception: {e} \n Full stack trace:", exc_info=2)
        outcome = {
            "Result": "FAIL. Please check application.log for details"
        }
        return jsonify(outcome)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port='8080')