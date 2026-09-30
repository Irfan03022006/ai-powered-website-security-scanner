"""
AI-Powered Website Security Scanner - Flask application entry point.

Run with:
    python app.py

This is an educational, defensive security tool. Only scan websites you
own or are explicitly authorized to test.
"""

from flask import Flask, render_template

from config import Config
from models.database import db
from routes.scan_routes import scan_bp
from routes.report_routes import report_bp
from routes.comparison_routes import comparison_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(scan_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(comparison_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard/<int:scan_id>")
    def dashboard(scan_id):
        return render_template("dashboard.html", scan_id=scan_id)

    @app.route("/findings/<int:scan_id>")
    def findings_page(scan_id):
        return render_template("findings.html", scan_id=scan_id)

    @app.route("/history")
    def history():
        return render_template("history.html")

    # ---- Friendly error handlers (never expose stack traces) ----

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", message="The page or resource you requested was not found."), 404

    @app.errorhandler(429)
    def rate_limited(_e):
        return render_template("error.html", message="Too many requests. Please slow down and try again shortly."), 429

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("error.html", message="Something went wrong on our end. Please try again."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
