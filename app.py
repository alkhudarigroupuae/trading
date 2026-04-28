import os
import logging
from dotenv import load_load
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "forex-trading-bot-secret-key-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:////Users/mac/Documents/trae_projects/LLM-TradeBot/forex_bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', 
                   engineio_logger=False, logger=False, ping_timeout=60, ping_interval=25)

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# Import routes
import routes
import websocket_handler

# --- RENDER PRODUCTION SETUP ---
# Start the Trading Engine background thread automatically if we are running in a production server (Gunicorn)
import os
import threading
from trading_engine import TradingEngine

def start_background_engine():
    import time
    time.sleep(3) # Wait for Flask to initialize
    engine = TradingEngine()
    engine.start()

# Check if running under Gunicorn or explicitly asked to run background
if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER'):
    logging.info("Production environment detected. Starting background Trading Engine...")
    bg_thread = threading.Thread(target=start_background_engine, daemon=True)
    bg_thread.start()
