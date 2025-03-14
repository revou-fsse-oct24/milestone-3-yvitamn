from flask import Flask
from routers.router import router
from shared.error_handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.register_blueprint(router)
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




        
