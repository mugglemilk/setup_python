from flask import Flask, send_from_directory
import os
from api.synonym.repository import SynonymRepository
from api.synonym.service import SynonymService
from api.synonym.routes import bp as synonym_bp
from api.poem.routes import bp as poem_bp

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')


def create_app():
    app = Flask(__name__)

    repo = SynonymRepository()
    app.config['SYNONYM_SERVICE'] = SynonymService(repo)

    app.register_blueprint(synonym_bp, url_prefix='/api')
    app.register_blueprint(poem_bp, url_prefix='/api')

    @app.route('/')
    def home():
        return send_from_directory(FRONTEND_DIR, 'symnonym.html')

    @app.route('/dictionary')
    def dictionary():
        return send_from_directory(FRONTEND_DIR, 'dictionary.html')

    @app.route('/poem')
    def poem():
        return send_from_directory(FRONTEND_DIR, 'poem.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
