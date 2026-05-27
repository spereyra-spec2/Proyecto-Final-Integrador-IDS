from flask import Flask, render_template, send_from_directory

app = Flask(
    __name__,
    template_folder="templates/html"
)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/profesor-equipos")
def profesor_equipos():
    return render_template("profesor-equipos.html")

@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory("templates/css", filename)

@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory("templates/js", filename)

if __name__ == "__main__":
    app.run("127.0.0.1", port=5000, debug=True)