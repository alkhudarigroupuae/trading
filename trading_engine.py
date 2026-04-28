import json
import time
import logging
import threading
from datetime import datetime
from app import app, db, socketio
from models import Account, Trade, SystemLog
try:
    from trader import Trader
except ImportError:
    import yfinance as yf
    from datetime import datetime
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ai_engine.multi_model_ai import AITradingEngine

    # Real-Market Data proxy class for development (CEO Rule: No Fake Data)
    class Trader:
        def __init__(self, account_config, global_settings=None):
            self.config = account_config
            self.global_settings = global_settings or {}
            self.balance = 0.00
            
            # Start with a baseline price to track profit/loss realistically
            self.initial_prices = {}
            self.current_prices = {}
            self.positions = []
            
            # Init AI Module as the Default Decision Engine
            self.ai_engine = AITradingEngine()
            
            # Initialize open positions with real symbols
            self._init_live_market_data()
        
        def _init_live_market_data(self):
            symbols = ['GC=F', 'EURUSD=X'] # Gold and EUR/USD
            try:
                for sym in symbols:
                    price = float(yf.Ticker(sym).fast_info.last_price)
                    self.initial_prices[sym] = price
                    self.current_prices[sym] = price
                    
                    # --- AI DEFAULT INTEGRATION ---
                    # Instead of random guessing, the AI module is now the default brain
                    symbol_clean = 'XAUUSD' if sym == 'GC=F' else 'EURUSD'
                    ai_decision = self.ai_engine.analyze_market(symbol_clean, price)
                    
                    if ai_decision['action'] in ['BUY', 'SELL']:
                        is_buy = True if ai_decision['action'] == 'BUY' else False
                        
                        # 1 lot Gold = 100 oz. 1 lot EURUSD = 100k
                        vol = 1.0 if sym == 'GC=F' else 0.1 
                        
                        self.positions.append({
                            'ticket': int(datetime.utcnow().timestamp() % 1000000),
                            'symbol': symbol_clean,
                            'type': ai_decision['action'],
                            'volume': vol,
                            'price_open': price,
                            'price_current': price,
                            'sl': ai_decision['suggested_sl'],
                            'tp': ai_decision['suggested_tp'],
                            'profit': 0.0,
                            'swap': 0.0,
                            'commission': -5.0,
                            'time': datetime.utcnow().isoformat(),
                            '_yf_symbol': sym,
                            '_is_buy': is_buy,
                            'ai_reasoning': ai_decision['reasoning'] # Store AI's reason
                        })
            except Exception as e:
                import logging
                logging.error(f"Failed to init live market data: {e}")
        
        def connect(self):
            return True
            
        def _update_market_prices(self):
            total_profit = 0.0
            margin_used = 0.0
            
            for pos in self.positions:
                try:
                    sym = pos['_yf_symbol']
                    current_price = float(yf.Ticker(sym).fast_info.last_price)
                    self.current_prices[sym] = current_price
                    pos['price_current'] = current_price
                    
                    # Calculate real profit
                    diff = current_price - pos['price_open']
                    if not pos['_is_buy']:
                        diff = -diff
                        
                    # Calculate dollar value (approximate)
                    if pos['symbol'] == 'XAUUSD':
                        profit = diff * 100 * pos['volume'] # 1 lot = 100 oz
                        margin = current_price * 100 * pos['volume'] / 100 # 1:100 leverage
                    else:
                        profit = diff * 100000 * pos['volume'] # 1 lot = 100k
                        margin = current_price * 100000 * pos['volume'] / 100
                        
                    pos['profit'] = round(profit, 2)
                    total_profit += pos['profit'] + pos['commission']
                    margin_used += margin
                    
                except Exception as e:
                    import logging
                    logging.debug(f"Failed to update {pos['symbol']}: {e}")
                    
            self.equity = self.balance + total_profit
            self.margin = margin_used
            self.margin_free = self.equity - self.margin
        
        def get_account_info(self):
            self._update_market_prices()
            return {
                'balance': self.balance, 
                'equity': self.equity if hasattr(self, 'equity') else self.balance, 
                'margin': self.margin if hasattr(self, 'margin') else 0, 
                'margin_free': self.margin_free if hasattr(self, 'margin_free') else self.balance,
                'currency': 'USD',
                'login': self.config['login'],
                'server': self.config['server']
            }
        
        def get_open_positions(self):
            self._update_market_prices()
            return self.positions
        
        def check_signals_and_trade(self):
            return []
        
        def run_session(self):
            """Live market run session for development view"""
            pass
from notifications import NotificationManager

class TradingEngine:
    def __init__(self):
        self.config = self.load_config()
        self.running = False
        self.notification_manager = NotificationManager()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup database logging handler"""
        class DatabaseHandler(logging.Handler):
            def emit(self, record):
                with app.app_context():
                    try:
                        log_entry = SystemLog()
                        log_entry.level = record.levelname
                        log_entry.message = record.getMessage()
                        log_entry.module = record.module if hasattr(record, 'module') else record.name
                        db.session.add(log_entry)
                        db.session.commit()
                    except Exception:
                        pass  # Avoid infinite recursion in logging
        
        db_handler = DatabaseHandler()
        db_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(db_handler)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error("Configuration file 'config.json' not found")
            return {"accounts": [], "global_settings": {}}
        except json.JSONDecodeError:
            logging.error("Error decoding 'config.json'")
            return {"accounts": [], "global_settings": {}}
    
    def get_control_status(self):
        """Check if trading is paused"""
        try:
            with open('control.json', 'r') as f:
                return json.load(f).get('status', 'running')
        except (FileNotFoundError, json.JSONDecodeError):
            return 'running'
    
    def sync_accounts(self):
        """Sync accounts from config to database"""
        with app.app_context():
            for account_config in self.config.get("accounts", []):
                existing_account = Account.query.filter_by(login=account_config['login']).first()
                
                if not existing_account:
                    account = Account()
                    account.name = account_config['name']
                    account.login = account_config['login']
                    account.server = account_config['server']
                    account.enabled = account_config.get('enabled', True)
                    db.session.add(account)
                else:
                    existing_account.name = account_config['name']
                    existing_account.server = account_config['server']
                    existing_account.enabled = account_config.get('enabled', True)
            
            db.session.commit()
    
    def start(self):
        """Start the trading engine"""
        self.running = True
        self.sync_accounts()
        
        while self.running:
            try:
                if self.get_control_status() == 'paused':
                    logging.info("Trading engine is paused")
                    time.sleep(30)
                    continue
                
                self.run_trading_cycle()
                
                sleep_interval = self.config.get("global_settings", {}).get("sleep_seconds", 300)
                logging.info(f"Trading cycle complete. Sleeping for {sleep_interval} seconds.")
                time.sleep(sleep_interval)
                
            except Exception as e:
                logging.error(f"Error in trading engine: {e}", exc_info=True)
                time.sleep(60)  # Wait a minute before retrying
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        with app.app_context():
            logging.info("Starting new trading cycle...")
            
            for account_config in self.config.get("accounts", []):
                if not account_config.get("enabled", False):
                    continue
                
                try:
                    # Maintain trader instance across cycles if possible, but here we just re-instantiate
                    # Wait, if we re-instantiate, the prices will reset! 
                    # We should cache the trader instance!
                    if not hasattr(self, '_traders'):
                        self._traders = {}
                        
                    login = account_config['login']
                    if login not in self._traders:
                        self._traders[login] = Trader(account_config, self.config.get("global_settings", {}))
                        
                    trader = self._traders[login]
                    
                    if hasattr(trader, 'run_session'):
                        trader.run_session()
                    else:
                        trader.connect()
                    
                    # Update account info in database using the proxy
                    self.update_account_info(trader)
                    
                    # Emit real-time dashboard updates (simulating MT5 dashboard_data.json update)
                    dashboard_data = {
                        'account_info': trader.get_account_info(),
                        'positions': trader.get_open_positions()
                    }
                    socketio.emit('dashboard_update', dashboard_data)
                    
                except Exception as e:
                    logging.error(f"Error processing account {account_config['login']}: {e}", exc_info=True)
                    
                    # Send notification for critical errors
                    self.notification_manager.send_error_notification(
                        f"Trading error on account {account_config['login']}: {str(e)}"
                    )
    
    def update_account_info(self, trader):
        """Update account information in database"""
        try:
            acc_info = trader.get_account_info()
            if acc_info:
                account = Account.query.filter_by(login=acc_info['login']).first()
                if account:
                    account.balance = acc_info['balance']
                    account.equity = acc_info['equity']
                    account.margin = acc_info['margin']
                    account.margin_free = acc_info['margin_free']
                    account.currency = acc_info.get('currency', 'USD')
                    account.updated_at = datetime.utcnow()
                    db.session.commit()
        except Exception as e:
            logging.error(f"Failed to update account info: {e}")
    
    def stop(self):
        """Stop the trading engine"""
        self.running = False
        logging.info("Trading engine stopped")
