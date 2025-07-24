from pathlib import Path
from dotenv import load_dotenv
import os

# .env dosyasının yolunu belirle
env_path = Path(__file__).resolve().parent / '.env'
# .env dosyasını yükle
load_dotenv(dotenv_path=env_path)

# Debug amaçlı kontrol edebilirsin
print("DEBUG: env_path =", env_path)
print("DEBUG: DATABASE_URL =", os.getenv("DATABASE_URL"))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
