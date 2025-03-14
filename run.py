from flask import Flask
from routers.router import router
from shared.error_handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.register_blueprint(router)
    register_error_handlers(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    #(host='0.0.0.0', port=5000, debug=True)





        
