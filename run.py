from flask import Flask
from routers.app import router

def create_app():
    app = Flask(__name__)
    app.register_blueprint(router)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    #(host='0.0.0.0', port=5000, debug=True)





        
