import hashlib
import hmac


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return hash_value(f"pwd::{password}")


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)
