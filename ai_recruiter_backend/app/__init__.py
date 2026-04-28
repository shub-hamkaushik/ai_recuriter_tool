from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import settings
from app.models import Base, engine
from app.schema import ensure_schema

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key
app.config['SECRET_KEY'] = settings.secret_key
app.config['MAX_CONTENT_LENGTH'] = settings.max_upload_mb * 1024 * 1024

CORS(app)
jwt = JWTManager(app)

# Import models before table creation so SQLAlchemy knows every mapped table.
from app.models import audit_log, candidate, job, match_result, system_setting, user

Base.metadata.create_all(bind=engine)
ensure_schema(engine)

# Import routes after app creation to avoid circular imports.
from app.routes import auth_routes, candidate_routes, dashboard_routes, job_routes, matching_routes, settings_routes

app.register_blueprint(auth_routes.bp, url_prefix='/auth')
app.register_blueprint(candidate_routes.bp, url_prefix='/candidates')
app.register_blueprint(dashboard_routes.bp, url_prefix='/dashboard')
app.register_blueprint(job_routes.bp, url_prefix='/jobs')
app.register_blueprint(matching_routes.bp, url_prefix='/matching')
app.register_blueprint(settings_routes.bp, url_prefix='/settings')

@app.route('/')
def index():
    return {'message': 'AI Recruiter API'}
