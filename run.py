import os
from dotenv import load_dotenv
from flask import Flask
from routers import admin_router
from services.user_service import UserService
from routers import account_router
from routers import auth_router
from routers import user_router
from routers import transaction_router
from shared.error_handlers import register_error_handlers

load_dotenv('.env')  # Load secrets
load_dotenv('.flaskenv')  # Load Flask settings

# Environment-specific overrides
env = os.getenv('FLASK_ENV', 'development').lower()
if env == 'testing':
    load_dotenv('.env.test', override=True)  # Testing overrides all
elif env == 'production':
    load_dotenv('.env.prod', override=True)  # Production overrides


def create_app():
    app = Flask(__name__)
    
     # =============== Security Configuration ===============
    # app.config.update(
    #     SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-123'),
    #     SESSION_COOKIE_HTTPONLY=True,
    #     TOKEN_EXPIRES=60*60 # 1 hour in seconds
    
    # ) 
    
    
    # =============== Admin Initialization ===============
    # if os.getenv('CREATE_ADMIN', 'true').lower() == 'true':
    if os.getenv('FLASK_ENV') == 'development':
        try:
            UserService().create_initial_admin()
            app.logger.info("Admin user initialized")
        except Exception as e:
            app.logger.warning(f"Admin init: {str(e)}")
    
    # =============== Blueprint Registration ===============
    blueprints = [
        user_router,
        auth_router,
        admin_router,
        account_router,
        transaction_router
    ]
    
    for bp in blueprints:
        app.register_blueprint(bp, url_prefix='/api/v1')
    
    register_error_handlers(app)
    
    # =============== Environment-Specific Configuration ===============
    # Configure auto-reload settings & Enable debug mode
    if app.env == 'development':
        app.config.update(
            TEMPLATES_AUTO_RELOAD=True,
            SEND_FILE_MAX_AGE_DEFAULT=0,
            DEBUG=True,
            EXPLAIN_TEMPLATE_LOADING=True
        )
        
        # Enable better debug output
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
        
    #should uncomment for production settings    
    # elif app.config['FLASK_ENV'] == 'production':
    #     app.config.update(
    #         DEBUG=False,
    #         TESTING=False,
    #         PROPAGATE_EXCEPTIONS=True # Better error handling in production
    #     )
    
    return app

#==============================================================

if __name__ == '__main__':  
    app = create_app()
    
    # =============== Production Safety Checks ===============
    # if app.config['FLASK_ENV'] == 'production':
    #     assert os.getenv('SECRET_KEY') is not None, 'SECRET_KEY must be set in production'
    #     assert os.getenv('DATABASE_URL') is not None, 'DATABASE_URL must be set in production'
    #     assert not app.debug, 'Debug mode must be disabled in production'
    
    
     # =============== Server Configuration ===============   
# Development server configuration
    print(f"\n🚀 Running in {app.config['ENV'].upper()} mode at http://{os.getenv('HOST', '127.0.0.1')}:{os.getenv('PORT', 5000)}/\n")
    
    app.run(
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 5000)),
        debug=app.debug,
        use_reloader=True
        reloader_type='watchdog' 
        extra_files=[
            # Include environment files
            '.env', 
            '.flaskenv',
            
            # Recursively find all Python files
            *[os.path.join(root, f) 
            for root, _, files in os.walk('.') 
            for f in files if f.endswith('.py')]
        ] 
    )




        
