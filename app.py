"""Flask entry. Canonical: src.web."""
from src.web import app  # noqa

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
