from flask import Flask, render_template, redirect, flash, session, request
import multiprocessing
from gestureRecognitionClass import *

app = Flask(__name__)
app.secret_key = 'xdcgvbhjnk=-0i98765trfvcbnhmkp7890659'

inputQueue = multiprocessing.Queue()

GR = GestureRecognition()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/serverApp')
def serverApp():
    return render_template('server_app.html')

@app.route('/clientApp')
def clientApp():
    return render_template('client_app.html')

@app.route('/serverApp',  methods=['POST'])
def startRecoeding():
    gestLabel = request.form['name']
    gestName = request.form['number']
    return redirect('/serverApp#arduino')

@app.route('/connectToDevice')
def connectToDevice():
    GR.connectToDevice()
    return redirect('/serverApp#arduino')

@app.route('/refreshDevice')
def refreshDevice():
    GR.train()
    return redirect('/serverApp#arduino')

@app.route('/recordGestures')
def recordGestures():
    GR.recordGesture()
    return redirect('/serverApp#arduino')

@app.route('/predictGestures')
def predictGestures():
    GR.startPredicting()
    return redirect('/serverApp#arduino')

@app.route('/closeForm')
def closeForm():
    return redirect('/serverApp#arduino')

if __name__ == "__main__":
    app.run(debug=True)

