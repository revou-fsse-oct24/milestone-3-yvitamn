import os
from flask import Flask
from services.user_service import UserService
from routers.account_router import account_router
from routers.auth_router import auth_router
from routers.user_router import user_router
from routers.transaction_router import transaction_router
from shared.error_handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    
    #Initialize admin user
    UserService().create_initial_admin()
    
    #Register blueprint
    app.register_blueprint(user_router)
    app.register_blueprint(auth_router)
    app.register_blueprint(account_router)
    app.register_blueprint(transaction_router)
    register_error_handlers(app)
    
    # Configure auto-reload settings
    app.debug = True  # Enable debug mode
    app.config.update(
        TEMPLATES_AUTO_RELOAD=True,
        SEND_FILE_MAX_AGE_DEFAULT=0
    )
    
    return app

if __name__ == '__main__':
    
    app = create_app()
       
    print(f"Running in {os.getenv('FLASK_ENV', 'production')} mode")
    # Run with watchdog and deep monitoring
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True,
        reloader_type='watchdog',
        extra_files=[
            './services/**/*.py',
            './models/**/*.py',
            './repos/**/*.py',
            './shared/*.py',
            './routers/*.py',
            './db/*.py',
            './static/*.py',
            './assets/*.py',
        ]
    )




        
