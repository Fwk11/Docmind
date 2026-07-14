import hashlib
import os
import hmac

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
        return f"{salt}:{hashed}"

    def verify_password(self, password: str) -> bool:
        try:
            salt, stored_hash = self.hashed_password.split(":", 1)
            computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
            return hmac.compare_digest(computed, stored_hash)
        except (ValueError, AttributeError):
            return False