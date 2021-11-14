import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.send_from_directory('.', 'index.html')

@app.route('/view.html')
def view():
    return flask.send_from_directory('.', 'view.html')  
    
@app.route('/go')
def go():
    out_dir = "ha" 
    return flask.redirect('/view.html?out_dir=' + out_dir)
    

app.run(host='0.0.0.0', port=81, debug=True)
