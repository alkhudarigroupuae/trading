"""
AI Core Engine for Alkhudari Trading
This module handles all AI/LLM integrations for market analysis and signal generation.
"""

import logging
import json
import requests
import os

class AITradingEngine:
    def _get_ai_config(self):
        # 1. Try to read from user settings (config.json)
        ai_config = {
            'provider': 'deepseek',
            'api_key': os.environ.get("DEEPSEEK_API_KEY", ""),
            'base_url': "https://api.deepseek.com/v1/chat/completions"
        }
        
        try:
            import sys
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
                config_path = os.path.join(os.path.dirname(sys.executable), 'config.json')
                if not os.path.exists(config_path):
                    config_path = os.path.join(base_path, 'config.json')
            else:
                config_path = 'config.json'
                
            with open(config_path, 'r') as f:
                config = json.load(f)
                settings = config.get('ai_settings', {})
                
                provider = settings.get('provider', 'deepseek')
                ai_config['provider'] = provider
                
                if provider == 'deepseek':
                    key = settings.get('deepseek_api_key')
                    if key and key.strip() != '':
                        ai_config['api_key'] = key.strip()
                elif provider == 'chatgpt':
                    key = settings.get('chatgpt_api_key')
                    if key and key.strip() != '':
                        ai_config['api_key'] = key.strip()
                        ai_config['base_url'] = "https://api.openai.com/v1/chat/completions"
                elif provider == 'ollama':
                    ai_config['base_url'] = settings.get('ollama_url', 'http://localhost:11434').rstrip('/') + "/api/generate"
                    
        except Exception as e:
            import logging
            logging.debug(f"Could not read AI config: {e}")
            
        return ai_config

    def __init__(self):
        """
        Initialize the Multi-Model AI Analyzer.
        """
        self.ai_config = self._get_ai_config()
        
    def analyze_market(self, symbol, current_price, account_data, technical_data=None):
        """
        Send market data and account margins to the AI and get a trading decision with volume size.
        """
        # Refresh AI config on every analysis to catch UI updates immediately
        self.ai_config = self._get_ai_config()
        provider = self.ai_config['provider']
        api_key = self.ai_config.get('api_key', '')
        base_url = self.ai_config.get('base_url', '')
        
        logging.info(f"[{provider.upper()}] AI Engine evaluating {symbol} at price {current_price} for Auto-Trading.")
        
        balance = account_data.get('balance', 0.0)
        margin_free = account_data.get('margin_free', 0.0)
        
        # If API key is empty and provider is not ollama, refuse to trade (Zero Fake Data)
        if provider != 'ollama' and not api_key:
            logging.warning(f"[{provider.upper()}] API Key missing. AI cannot trade.")
            return {
                "action": "HOLD",
                "volume": 0.0,
                "confidence_percentage": 0,
                "suggested_sl": current_price,
                "suggested_tp": current_price,
                "reasoning": f"Waiting for valid {provider.upper()} API Key to execute live analysis."
            }
            
        prompt = f"""
        You are a highly skilled Forex and Gold (XAUUSD) trading AI for Alkhudari Group.
        
        Current Market Status:
        - Symbol: {symbol}
        - Current Price: {current_price}
        - Technical Indicators: {technical_data or 'None provided'}
        
        Account Status (Risk Management):
        - Total Balance: ${balance}
        - Free Margin: ${margin_free}
        
        Your task:
        1. Analyze the market direction (BUY, SELL, or HOLD).
        2. Calculate the exact volume (Lot size / Ounces) to trade based on the Free Margin. Do not risk more than 5% of the free margin. 
        3. Determine safe Stop Loss and Take Profit levels.
        
        Provide a strict JSON response with your trading decision. Do not include any markdown, backticks, or other text. Only return valid JSON in this format:
        {{
            "action": "BUY" or "SELL" or "HOLD",
            "volume": 0.5,
            "confidence_percentage": 85,
            "suggested_sl": 0.0,
            "suggested_tp": 0.0,
            "reasoning": "Brief explanation"
        }}
        """
        
        try:
            if provider == 'ollama':
                payload = {
                    "model": "llama3", # Default local model
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
                response = requests.post(base_url, json=payload, timeout=30)
                response.raise_for_status()
                ai_reply = response.json().get('response', '{}')
                
            else:
                # DeepSeek or ChatGPT
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                model_name = "deepseek-chat" if provider == 'deepseek' else "gpt-4o"
                
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2, # Low temperature for more analytical/less random responses
                    "response_format": { "type": "json_object" } # Force JSON if supported
                }
                
                response = requests.post(base_url, headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                ai_reply = response.json()['choices'][0]['message']['content']
            
            # Clean up the response just in case the AI added markdown
            ai_reply = ai_reply.strip()
            if ai_reply.startswith('```json'):
                ai_reply = ai_reply[7:]
            if ai_reply.startswith('```'):
                ai_reply = ai_reply[3:]
            if ai_reply.endswith('```'):
                ai_reply = ai_reply[:-3]
                
            # Parse the JSON returned by the AI
            decision = json.loads(ai_reply.strip())
            
            # Validate required fields
            required_keys = ['action', 'volume', 'suggested_sl', 'suggested_tp']
            if not all(k in decision for k in required_keys):
                raise ValueError("AI response missing required keys")
                
            return decision
            
        except Exception as e:
            logging.error(f"[{provider.upper()}] API Error: {e}")
            return {
                "action": "HOLD", 
                "volume": 0.0,
                "confidence_percentage": 0,
                "suggested_sl": current_price,
                "suggested_tp": current_price,
                "reasoning": f"Error connecting to AI: {str(e)}"
            }

if __name__ == "__main__":
    # Test the AI module standalone
    ai = AITradingEngine()
    print("Testing Real AI Integration...")
    mock_account = {"balance": 10000.0, "margin_free": 9800.0}
    decision = ai.analyze_market("XAUUSD", 2350.50, mock_account, {"RSI": 45, "Trend": "Bullish"})
    print(f"AI Decision Format: {json.dumps(decision, indent=2)}")