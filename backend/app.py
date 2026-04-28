from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Config
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

jwt = JWTManager(app)

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Register blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.chat_routes import chat_bp
from routes.report_routes import report_bp
from routes.upload_routes import upload_bp
from routes.export_routes import export_bp
from routes.admin_routes import admin_bp
from routes.health_routes import health_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(chat_bp, url_prefix="/api/chat")
app.register_blueprint(report_bp, url_prefix="/api/report")
app.register_blueprint(upload_bp, url_prefix="/api/upload")
app.register_blueprint(export_bp, url_prefix="/api/export")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(health_bp, url_prefix="/api/health")

@app.route("/")
def index():
    return {"message": "AI Public Health Chatbot API", "status": "running"}, 200

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
