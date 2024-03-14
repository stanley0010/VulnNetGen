from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/create")
def create_scenario():
    return render_template('create_scenario.html', title="Create Scenario")

@app.route("/import")
def import_scenario():
    return render_template('import_scenario.html', title="Import Scenario")