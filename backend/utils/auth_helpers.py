import bcrypt
import re

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Valid"

ALLOWED_EXTENSIONS = {
    "image": {"png", "jpg", "jpeg", "gif", "webp"},
    "video": {"mp4", "avi", "mov", "mkv"},
    "document": {"pdf", "doc", "docx", "txt"}
}

def allowed_file(filename: str, file_type: str = None) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    if file_type:
        return ext in ALLOWED_EXTENSIONS.get(file_type, set())
    all_allowed = set().union(*ALLOWED_EXTENSIONS.values())
    return ext in all_allowed

def get_file_type(filename: str) -> str:
    if "." not in filename:
        return "unknown"
    ext = filename.rsplit(".", 1)[1].lower()
    for ftype, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return ftype
    return "unknown"
