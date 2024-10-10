from flask import Flask, render_template, request, url_for, redirect, flash, send_file, Response
from xml.dom import minidom
import graphviz
import os


app = Flask(__name__)
app.secret_key = 'claveSeguraIPC2$$$$$'

@app.route('/')
def listar():
    return render_template('index.html')

if __name__ == '__main__':
    slc = 0

    app.run(debug=True)