from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.errorhandler(404)
def home():
    return render_template('home.html')

@app.route("/design")
def design_scenario():
    return render_template('design_scenario.html', import_scenario=False)

@app.route("/configure")
def configure_scenario():
    return render_template('configure_scenario.html', import_scenario=False)

@app.route("/import")
def import_scenario():
    return render_template('import_scenario.html', import_scenario=True)
