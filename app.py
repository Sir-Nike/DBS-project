from flask import Flask
from config import Config
from db import close_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register DB teardown — closes connection after every request
    app.teardown_appcontext(close_db)

    # Register blueprints
    from blueprints.auth.routes    import auth_bp
    from blueprints.teacher.routes import teacher_bp
    from blueprints.student.routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')

    return app


if __name__ == '__main__':
    app = create_app()
    # host='0.0.0.0' makes Flask visible on LAN (hotspot)
    # so students can connect via your IP address
    app.run(host='0.0.0.0', port=5000, debug=True)
