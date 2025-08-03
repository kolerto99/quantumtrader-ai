#!/usr/bin/env python3
"""
Universal AI Trading Terminal
Multi-AI Provider Support with Real-time Data

Developer: @kolerto99
Enhanced version with universal AI provider support and real-time trading simulation
"""

from flask import Flask, render_template_string, request, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import threading
import openai
import os
from typing import Dict, List, Optional
import random

app = Flask(__name__)

# AI Providers Configuration
AI_PROVIDERS = {
    'openai': {
        'name': 'OpenAI GPT',
        'models': ['gpt-4', 'gpt-3.5-turbo'],
        'enabled': True
    },
    'claude': {
        'name': 'Anthropic Claude',
        'models': ['claude-3-sonnet', 'claude-3-haiku'],
        'enabled': False  # Would need API key
    },
    'gemini': {
        'name': 'Google Gemini',
        'models': ['gemini-pro', 'gemini-pro-vision'],
        'enabled': False  # Would need API key
    },
    'local': {
        'name': 'Local LLM',
        'models': ['llama2', 'llama3', 'mistral', 'deepseek-coder', 'deepseek-chat', 'qwen', 'codellama'],
        'enabled': False  # Would need Ollama setup
    }
}

# Portfolio data
portfolio = {
    'cash': 100000.0,
    'positions': {},
    'total_value': 100000.0,
    'trades': []
}

# AI Trading Bot data
ai_bot = {
    'enabled': False,
    'provider': 'openai',
    'model': 'gpt-3.5-turbo',
    'portfolio': {
        'cash': 50000.0,
        'positions': {},
        'total_value': 50000.0,
        'trades': [],
        'performance': []
    },
    'last_analysis': None,
    'thinking_log': [],
    'strategy': 'conservative'
}

SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
market_data_cache = {}
last_update = None

class AITradingEngine:
    def __init__(self):
        self.openai_client = openai.OpenAI() if os.getenv('OPENAI_API_KEY') else None
        
    def analyze_market(self, provider: str, model: str, market_data: Dict) -> Dict:
        """Universal market analysis using specified AI provider"""
        
        if provider == 'openai' and self.openai_client:
            return self._analyze_with_openai(model, market_data)
        elif provider == 'claude':
            return self._analyze_with_claude(model, market_data)
        elif provider == 'gemini':
            return self._analyze_with_gemini(model, market_data)
        elif provider == 'local':
            return self._analyze_with_local(model, market_data)
        else:
            return self._simulate_analysis(market_data)
    
    def _analyze_with_openai(self, model: str, market_data: Dict) -> Dict:
        """OpenAI GPT analysis"""
        try:
            # Prepare market data summary
            market_summary = self._prepare_market_summary(market_data)
            
            prompt = f"""
            You are a professional AI trading assistant analyzing real-time market data.
            
            Current Market Data:
            {market_summary}
            
            Current AI Portfolio:
            - Cash: ${ai_bot['portfolio']['cash']:,.2f}
            - Positions: {ai_bot['portfolio']['positions']}
            - Total Value: ${ai_bot['portfolio']['total_value']:,.2f}
            
            Strategy: {ai_bot['strategy']}
            
            Analyze the market and provide:
            1. Market sentiment (bullish/bearish/neutral)
            2. Top 3 opportunities with reasoning
            3. Risk assessment
            4. Specific trading recommendation (BUY/SELL/HOLD with symbol and quantity)
            5. Your thinking process
            
            Respond in JSON format:
            {{
                "sentiment": "bullish/bearish/neutral",
                "opportunities": ["reason1", "reason2", "reason3"],
                "risk_level": "low/medium/high",
                "recommendation": {{
                    "action": "BUY/SELL/HOLD",
                    "symbol": "SYMBOL",
                    "quantity": number,
                    "reasoning": "detailed explanation"
                }},
                "thinking": "step by step analysis process",
                "confidence": 0.85
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            analysis['provider'] = 'OpenAI'
            analysis['model'] = model
            analysis['timestamp'] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            return self._simulate_analysis(market_data)
    
    def _analyze_with_claude(self, model: str, market_data: Dict) -> Dict:
        """Claude analysis (placeholder - would need Anthropic API)"""
        return self._simulate_analysis(market_data, provider="Claude", model=model)
    
    def _analyze_with_gemini(self, model: str, market_data: Dict) -> Dict:
        """Gemini analysis (placeholder - would need Google API)"""
        return self._simulate_analysis(market_data, provider="Gemini", model=model)
    
    def _analyze_with_local(self, model: str, market_data: Dict) -> Dict:
        """Local LLM analysis (placeholder - would need Ollama)"""
        return self._simulate_analysis(market_data, provider="Local LLM", model=model)
    
    def _simulate_analysis(self, market_data: Dict, provider: str = "Simulator", model: str = "demo") -> Dict:
        """Simulate AI analysis for demo purposes"""
        
        # Calculate market trends
        prices = [stock['price'] for stock in market_data.values() if stock]
        changes = [stock['change_pct'] for stock in market_data.values() if stock]
        avg_change = np.mean(changes) if changes else 0
        
        # Determine sentiment
        if avg_change > 1:
            sentiment = "bullish"
        elif avg_change < -1:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        # Find best/worst performers
        sorted_stocks = sorted(
            [(k, v) for k, v in market_data.items() if v],
            key=lambda x: x[1]['change_pct'],
            reverse=True
        )
        
        best_performer = sorted_stocks[0] if sorted_stocks else None
        worst_performer = sorted_stocks[-1] if sorted_stocks else None
        
        # Generate recommendation
        if sentiment == "bullish" and best_performer:
            action = "BUY"
            symbol = best_performer[0]
            reasoning = f"{symbol} showing strong momentum with {best_performer[1]['change_pct']:.2f}% gain"
        elif sentiment == "bearish" and symbol in ai_bot['portfolio']['positions']:
            action = "SELL"
            symbol = list(ai_bot['portfolio']['positions'].keys())[0]
            reasoning = f"Market downturn detected, reducing exposure in {symbol}"
        else:
            action = "HOLD"
            symbol = "CASH"
            reasoning = "Market conditions suggest waiting for better opportunities"
        
        # Calculate quantity based on available cash and risk
        if action == "BUY" and symbol in market_data:
            max_investment = ai_bot['portfolio']['cash'] * 0.2  # Max 20% per trade
            quantity = int(max_investment / market_data[symbol]['price'])
        elif action == "SELL" and symbol in ai_bot['portfolio']['positions']:
            quantity = ai_bot['portfolio']['positions'][symbol] // 2  # Sell half
        else:
            quantity = 0
        
        return {
            "sentiment": sentiment,
            "opportunities": [
                f"Market showing {sentiment} sentiment with {avg_change:.2f}% average change",
                f"Best performer: {best_performer[0]} (+{best_performer[1]['change_pct']:.2f}%)" if best_performer else "No clear winners",
                f"Volatility creating trading opportunities" if abs(avg_change) > 1 else "Low volatility market"
            ],
            "risk_level": "high" if abs(avg_change) > 2 else "medium" if abs(avg_change) > 1 else "low",
            "recommendation": {
                "action": action,
                "symbol": symbol,
                "quantity": quantity,
                "reasoning": reasoning
            },
            "thinking": f"""
            Step 1: Analyzed {len(market_data)} stocks with average change of {avg_change:.2f}%
            Step 2: Market sentiment determined as {sentiment} based on price movements
            Step 3: Identified {best_performer[0] if best_performer else 'no'} as top performer
            Step 4: Risk assessment shows {sentiment} conditions
            Step 5: Recommendation: {action} {symbol} based on current market dynamics
            """,
            "confidence": 0.75 + random.random() * 0.2,
            "provider": provider,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
    
    def _prepare_market_summary(self, market_data: Dict) -> str:
        """Prepare market data summary for AI analysis"""
        summary = []
        for symbol, data in market_data.items():
            if data:
                summary.append(f"{symbol}: ${data['price']} ({data['change']:+.2f}, {data['change_pct']:+.2f}%) Vol: {data['volume']:,} RSI: {data['rsi']}")
        return "\n".join(summary)

# Initialize AI engine
ai_engine = AITradingEngine()

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="30d")
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        # RSI calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'volume': int(hist['Volume'].iloc[-1]),
            'rsi': round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else 50
        }
    except:
        return None

def update_market_data():
    """Background task to update market data"""
    global market_data_cache, last_update
    
    while True:
        try:
            new_data = {}
            for symbol in SYMBOLS:
                new_data[symbol] = get_stock_data(symbol)
            
            market_data_cache = new_data
            last_update = datetime.now()
            
            # Trigger AI analysis if bot is enabled
            if ai_bot['enabled']:
                run_ai_analysis()
            
        except Exception as e:
            print(f"Market data update error: {e}")
        
        time.sleep(30)  # Update every 30 seconds

def run_ai_analysis():
    """Run AI analysis and potentially execute trades"""
    try:
        analysis = ai_engine.analyze_market(
            ai_bot['provider'],
            ai_bot['model'],
            market_data_cache
        )
        
        ai_bot['last_analysis'] = analysis
        ai_bot['thinking_log'].append({
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis
        })
        
        # Keep only last 10 analyses
        if len(ai_bot['thinking_log']) > 10:
            ai_bot['thinking_log'] = ai_bot['thinking_log'][-10:]
        
        # Execute trade if recommendation is actionable
        if analysis['recommendation']['action'] in ['BUY', 'SELL'] and analysis['confidence'] > 0.7:
            execute_ai_trade(analysis['recommendation'])
            
    except Exception as e:
        print(f"AI analysis error: {e}")

def execute_ai_trade(recommendation):
    """Execute AI recommended trade"""
    try:
        symbol = recommendation['symbol']
        action = recommendation['action']
        quantity = recommendation['quantity']
        
        if symbol in market_data_cache and market_data_cache[symbol] and quantity > 0:
            price = market_data_cache[symbol]['price']
            total_cost = quantity * price
            
            if action == 'BUY' and ai_bot['portfolio']['cash'] >= total_cost:
                ai_bot['portfolio']['cash'] -= total_cost
                ai_bot['portfolio']['positions'][symbol] = ai_bot['portfolio']['positions'].get(symbol, 0) + quantity
                
                trade = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': price,
                    'total': total_cost,
                    'reasoning': recommendation['reasoning'],
                    'ai_decision': True
                }
                ai_bot['portfolio']['trades'].append(trade)
                
            elif action == 'SELL' and ai_bot['portfolio']['positions'].get(symbol, 0) >= quantity:
                ai_bot['portfolio']['cash'] += total_cost
                ai_bot['portfolio']['positions'][symbol] -= quantity
                
                if ai_bot['portfolio']['positions'][symbol] == 0:
                    del ai_bot['portfolio']['positions'][symbol]
                
                trade = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': price,
                    'total': total_cost,
                    'reasoning': recommendation['reasoning'],
                    'ai_decision': True
                }
                ai_bot['portfolio']['trades'].append(trade)
        
        # Update portfolio value
        ai_bot['portfolio']['total_value'] = calculate_ai_portfolio_value()
        
    except Exception as e:
        print(f"AI trade execution error: {e}")

def calculate_portfolio_value():
    total = portfolio['cash']
    for symbol, quantity in portfolio['positions'].items():
        if quantity > 0 and symbol in market_data_cache and market_data_cache[symbol]:
            total += market_data_cache[symbol]['price'] * quantity
    return total

def calculate_ai_portfolio_value():
    total = ai_bot['portfolio']['cash']
    for symbol, quantity in ai_bot['portfolio']['positions'].items():
        if quantity > 0 and symbol in market_data_cache and market_data_cache[symbol]:
            total += market_data_cache[symbol]['price'] * quantity
    return total

# Start background market data updates
market_thread = threading.Thread(target=update_market_data, daemon=True)
market_thread.start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Trading Terminal</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(ellipse at center, #0a0a0a 0%, #000000 100%);
            color: #ffffff;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Animated background particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .particle {
            position: absolute;
            width: 2px;
            height: 2px;
            background: #00d4ff;
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.3; }
            50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
        }

        .header {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 0, 128, 0.1) 100%);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0, 212, 255, 0.3);
            padding: 20px 40px;
            position: relative;
            z-index: 10;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .header h1 {
            background: linear-gradient(135deg, #00d4ff 0%, #00ff88 50%, #ff0080 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-align: center;
        }

        .header .subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            margin-top: 8px;
            text-align: center;
            font-weight: 300;
            letter-spacing: 1px;
        }

        .main-container {
            display: grid;
            grid-template-columns: 300px 1fr 350px 350px;
            height: calc(100vh - 120px);
            gap: 15px;
            padding: 15px;
            position: relative;
            z-index: 10;
        }

        .glass-panel {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        .glass-panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        }

        .section-title {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 16px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            padding-bottom: 8px;
        }

        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 40px;
            height: 2px;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
        }

        .ai-controls {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
        }

        .ai-status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .ai-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff0080;
            animation: pulse 2s ease-in-out infinite;
        }

        .ai-indicator.active {
            background: #00ff88;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 5px currentColor; }
            50% { opacity: 0.5; box-shadow: 0 0 20px currentColor; }
        }

        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            margin: 5px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            color: #000;
            border: 1px solid rgba(0, 255, 136, 0.5);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
        }

        .ai-thinking {
            background: rgba(255, 0, 128, 0.05);
            border: 1px solid rgba(255, 0, 128, 0.2);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            max-height: 200px;
            overflow-y: auto;
        }

        .thinking-item {
            margin-bottom: 10px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            font-size: 12px;
            line-height: 1.4;
        }

        .thinking-timestamp {
            color: rgba(255, 255, 255, 0.5);
            font-size: 10px;
        }

        .market-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stock-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 15px;
            transition: all 0.4s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .stock-card:hover {
            background: rgba(0, 212, 255, 0.05);
            border-color: rgba(0, 212, 255, 0.4);
            transform: translateY(-2px);
        }

        .stock-symbol {
            font-size: 16px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 5px;
        }

        .stock-price {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 5px;
            color: #ffffff;
        }

        .stock-change {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .positive { color: #00ff88; }
        .negative { color: #ff0080; }

        .portfolio-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 14px;
        }

        .position-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
        }

        .position-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .position-symbol {
            color: #00d4ff;
            font-weight: 600;
        }

        .position-details {
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
            display: flex;
            justify-content: space-between;
        }

        .trade-item {
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 12px;
        }

        .trade-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            font-weight: 600;
        }

        .ai-badge {
            background: linear-gradient(135deg, #ff0080, #00d4ff);
            color: #fff;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
        }

        .status-bar {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
            position: relative;
            z-index: 10;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 5px;
            font-size: 12px;
            font-weight: 500;
        }

        .form-group select,
        .form-group input {
            width: 100%;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 13px;
        }

        ::-webkit-scrollbar {
            width: 4px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(0, 212, 255, 0.5);
            border-radius: 2px;
        }

        @media (max-width: 1600px) {
            .main-container {
                grid-template-columns: 1fr;
                grid-template-rows: auto auto auto auto;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <!-- Animated particles background -->
    <div class="particles" id="particles"></div>

    <div class="header">
        <h1>AI Trading Terminal</h1>
        <div class="subtitle">Universal Multi-AI Trading Platform | Real-time Market Analysis</div>
    </div>

    <div class="main-container">
        <!-- Human Portfolio -->
        <div class="glass-panel">
            <h3 class="section-title">Human Portfolio</h3>
            <div id="human-portfolio">
                <div class="portfolio-item">
                    <span>Total Value:</span>
                    <span id="human-total">$100,000</span>
                </div>
                <div class="portfolio-item">
                    <span>Cash:</span>
                    <span id="human-cash">$100,000</span>
                </div>
                <div class="portfolio-item">
                    <span>P&L:</span>
                    <span id="human-pnl">$0</span>
                </div>
            </div>

            <h4 style="color: #00ff88; margin: 15px 0 10px 0; font-size: 14px;">Positions</h4>
            <div id="human-positions">
                <div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">
                    No positions
                </div>
            </div>

            <h4 style="color: #ff0080; margin: 15px 0 10px 0; font-size: 14px;">Manual Trading</h4>
            <div class="form-group">
                <label>Symbol</label>
                <select id="trade-symbol">
                    <option value="">Select</option>
                    <option value="AAPL">AAPL</option>
                    <option value="GOOGL">GOOGL</option>
                    <option value="MSFT">MSFT</option>
                    <option value="AMZN">AMZN</option>
                    <option value="TSLA">TSLA</option>
                    <option value="NVDA">NVDA</option>
                    <option value="META">META</option>
                    <option value="NFLX">NFLX</option>
                </select>
            </div>
            <div class="form-group">
                <label>Quantity</label>
                <input type="number" id="trade-quantity" min="1" value="1">
            </div>
            <div class="form-group">
                <label>Price</label>
                <input type="number" id="trade-price" step="0.01" readonly>
            </div>
            <button class="btn btn-primary" onclick="executeTrade('BUY')" style="width: 48%;">BUY</button>
            <button class="btn btn-secondary" onclick="executeTrade('SELL')" style="width: 48%;">SELL</button>
        </div>

        <!-- Market Data -->
        <div class="glass-panel">
            <h3 class="section-title">Live Market Data</h3>
            <div class="market-grid" id="market-data">
                <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.5);">
                    Loading market data...
                </div>
            </div>
        </div>

        <!-- AI Bot Portfolio -->
        <div class="glass-panel">
            <h3 class="section-title">AI Bot Portfolio</h3>
            
            <div class="ai-controls">
                <div class="ai-status">
                    <div class="ai-indicator" id="ai-indicator"></div>
                    <span id="ai-status-text">AI Bot: Disabled</span>
                </div>
                
                <div class="form-group">
                    <label>AI Provider</label>
                    <select id="ai-provider">
                        <option value="openai">OpenAI GPT</option>
                        <option value="claude">Anthropic Claude</option>
                        <option value="gemini">Google Gemini</option>
                        <option value="local">Local LLM</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Strategy</label>
                    <select id="ai-strategy">
                        <option value="conservative">Conservative</option>
                        <option value="aggressive">Aggressive</option>
                        <option value="balanced">Balanced</option>
                    </select>
                </div>
                
                <button class="btn btn-primary" onclick="toggleAI()" id="ai-toggle">Start AI Bot</button>
                <button class="btn btn-secondary" onclick="runAnalysis()">Manual Analysis</button>
            </div>

            <div id="ai-portfolio-stats">
                <div class="portfolio-item">
                    <span>Total Value:</span>
                    <span id="ai-total">$50,000</span>
                </div>
                <div class="portfolio-item">
                    <span>Cash:</span>
                    <span id="ai-cash">$50,000</span>
                </div>
                <div class="portfolio-item">
                    <span>P&L:</span>
                    <span id="ai-pnl">$0</span>
                </div>
            </div>

            <h4 style="color: #00ff88; margin: 15px 0 10px 0; font-size: 14px;">AI Positions</h4>
            <div id="ai-positions">
                <div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">
                    No positions
                </div>
            </div>
        </div>

        <!-- AI Analysis -->
        <div class="glass-panel">
            <h3 class="section-title">AI Analysis</h3>
            
            <div id="current-analysis">
                <div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">
                    No analysis yet
                </div>
            </div>

            <h4 style="color: #ff0080; margin: 15px 0 10px 0; font-size: 14px;">AI Thinking Log</h4>
            <div class="ai-thinking" id="ai-thinking">
                <div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">
                    AI thinking will appear here
                </div>
            </div>

            <h4 style="color: #00d4ff; margin: 15px 0 10px 0; font-size: 14px;">Trade History</h4>
            <div style="max-height: 200px; overflow-y: auto;" id="ai-trades">
                <div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">
                    No AI trades yet
                </div>
            </div>
        </div>
    </div>

    <div class="status-bar">
        <div>Market Status: <span style="color: #00ff88;">OPEN</span></div>
        <div>Last Update: <span id="last-update">--:--:--</span></div>
        <div>AI Provider: <span id="current-provider">OpenAI</span></div>
        <div>Connection: <span style="color: #00ff88;">LIVE</span></div>
    </div>

    <script>
        let aiEnabled = false;
        let marketData = {};

        // Create animated particles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 30;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 6 + 's';
                particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
                
                const colors = ['#00d4ff', '#ff0080', '#00ff88'];
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];
                
                particlesContainer.appendChild(particle);
            }
        }

        async function loadMarketData() {
            try {
                const response = await fetch('/api/market-data');
                const data = await response.json();
                marketData = data;
                renderMarketData(data);
                updateLastUpdate();
            } catch (error) {
                console.error('Error loading market data:', error);
            }
        }

        function renderMarketData(data) {
            const container = document.getElementById('market-data');
            container.innerHTML = '';

            Object.values(data).forEach(stock => {
                if (!stock) return;
                
                const card = document.createElement('div');
                card.className = 'stock-card';
                card.onclick = () => selectStock(stock.symbol);
                
                const changeClass = stock.change >= 0 ? 'positive' : 'negative';
                const changeSign = stock.change >= 0 ? '+' : '';
                
                card.innerHTML = `
                    <div class="stock-symbol">${stock.symbol}</div>
                    <div class="stock-price">$${stock.price}</div>
                    <div class="stock-change ${changeClass}">
                        ${changeSign}${stock.change} (${changeSign}${stock.change_pct}%)
                    </div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.6);">
                        Vol: ${(stock.volume / 1000000).toFixed(1)}M | RSI: ${stock.rsi}
                    </div>
                `;
                
                container.appendChild(card);
            });
        }

        function selectStock(symbol) {
            document.getElementById('trade-symbol').value = symbol;
            document.getElementById('trade-price').value = marketData[symbol]?.price || '';
        }

        async function toggleAI() {
            const provider = document.getElementById('ai-provider').value;
            const strategy = document.getElementById('ai-strategy').value;
            
            try {
                const response = await fetch('/api/ai/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider, strategy })
                });
                
                const result = await response.json();
                aiEnabled = result.enabled;
                
                updateAIStatus();
                
            } catch (error) {
                console.error('Error toggling AI:', error);
            }
        }

        function updateAIStatus() {
            const indicator = document.getElementById('ai-indicator');
            const statusText = document.getElementById('ai-status-text');
            const toggleBtn = document.getElementById('ai-toggle');
            
            if (aiEnabled) {
                indicator.classList.add('active');
                statusText.textContent = 'AI Bot: Active';
                toggleBtn.textContent = 'Stop AI Bot';
                toggleBtn.className = 'btn btn-secondary';
            } else {
                indicator.classList.remove('active');
                statusText.textContent = 'AI Bot: Disabled';
                toggleBtn.textContent = 'Start AI Bot';
                toggleBtn.className = 'btn btn-primary';
            }
        }

        async function runAnalysis() {
            try {
                const response = await fetch('/api/ai/analyze', { method: 'POST' });
                const analysis = await response.json();
                displayAnalysis(analysis);
            } catch (error) {
                console.error('Error running analysis:', error);
            }
        }

        function displayAnalysis(analysis) {
            const container = document.getElementById('current-analysis');
            
            if (!analysis) {
                container.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px;">No analysis available</div>';
                return;
            }
            
            const sentimentColor = analysis.sentiment === 'bullish' ? '#00ff88' : 
                                  analysis.sentiment === 'bearish' ? '#ff0080' : '#00d4ff';
            
            container.innerHTML = `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: ${sentimentColor}; font-weight: 600;">${analysis.sentiment.toUpperCase()}</span>
                        <span style="color: #00d4ff;">${(analysis.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-bottom: 10px;">
                        ${analysis.provider} ${analysis.model}
                    </div>
                </div>
                
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="color: #00ff88; font-size: 12px; font-weight: 600; margin-bottom: 5px;">RECOMMENDATION</div>
                    <div style="font-size: 13px; margin-bottom: 5px;">
                        <span style="color: ${analysis.recommendation.action === 'BUY' ? '#00ff88' : '#ff0080'}; font-weight: 600;">
                            ${analysis.recommendation.action}
                        </span>
                        ${analysis.recommendation.symbol} 
                        ${analysis.recommendation.quantity > 0 ? `(${analysis.recommendation.quantity} shares)` : ''}
                    </div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.6);">
                        ${analysis.recommendation.reasoning}
                    </div>
                </div>
                
                <div style="font-size: 11px; color: rgba(255,255,255,0.5);">
                    Risk: ${analysis.risk_level} | ${new Date(analysis.timestamp).toLocaleTimeString()}
                </div>
            `;
        }

        async function loadPortfolios() {
            try {
                const [humanResponse, aiResponse] = await Promise.all([
                    fetch('/api/portfolio'),
                    fetch('/api/ai/portfolio')
                ]);
                
                const humanData = await humanResponse.json();
                const aiData = await aiResponse.json();
                
                updatePortfolioDisplay('human', humanData);
                updatePortfolioDisplay('ai', aiData);
                
            } catch (error) {
                console.error('Error loading portfolios:', error);
            }
        }

        function updatePortfolioDisplay(type, data) {
            const prefix = type === 'human' ? 'human' : 'ai';
            
            document.getElementById(`${prefix}-total`).textContent = `$${data.total_value.toLocaleString()}`;
            document.getElementById(`${prefix}-cash`).textContent = `$${data.cash.toLocaleString()}`;
            
            const pnl = data.total_value - (type === 'human' ? 100000 : 50000);
            const pnlElement = document.getElementById(`${prefix}-pnl`);
            pnlElement.textContent = `$${pnl.toLocaleString()}`;
            pnlElement.className = pnl >= 0 ? 'positive' : 'negative';
            
            // Update positions
            const positionsContainer = document.getElementById(`${prefix}-positions`);
            if (Object.keys(data.positions).length === 0) {
                positionsContainer.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">No positions</div>';
            } else {
                positionsContainer.innerHTML = '';
                Object.entries(data.positions).forEach(([symbol, quantity]) => {
                    if (quantity > 0) {
                        const currentPrice = marketData[symbol]?.price || 0;
                        const currentValue = quantity * currentPrice;
                        
                        const positionDiv = document.createElement('div');
                        positionDiv.className = 'position-item';
                        positionDiv.innerHTML = `
                            <div class="position-header">
                                <span class="position-symbol">${symbol}</span>
                                <span style="color: #00ff88;">$${currentValue.toFixed(2)}</span>
                            </div>
                            <div class="position-details">
                                <span>${quantity} shares</span>
                                <span>@ $${currentPrice}</span>
                            </div>
                        `;
                        positionsContainer.appendChild(positionDiv);
                    }
                });
            }
        }

        async function loadAIData() {
            try {
                const [analysisResponse, thinkingResponse, tradesResponse] = await Promise.all([
                    fetch('/api/ai/analysis'),
                    fetch('/api/ai/thinking'),
                    fetch('/api/ai/trades')
                ]);
                
                const analysis = await analysisResponse.json();
                const thinking = await thinkingResponse.json();
                const trades = await tradesResponse.json();
                
                displayAnalysis(analysis);
                displayThinking(thinking);
                displayAITrades(trades);
                
            } catch (error) {
                console.error('Error loading AI data:', error);
            }
        }

        function displayThinking(thinkingLog) {
            const container = document.getElementById('ai-thinking');
            
            if (!thinkingLog || thinkingLog.length === 0) {
                container.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">AI thinking will appear here</div>';
                return;
            }
            
            container.innerHTML = '';
            thinkingLog.slice(-5).reverse().forEach(entry => {
                const thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'thinking-item';
                thinkingDiv.innerHTML = `
                    <div class="thinking-timestamp">${new Date(entry.timestamp).toLocaleTimeString()}</div>
                    <div style="margin-top: 5px; white-space: pre-line;">${entry.analysis.thinking}</div>
                `;
                container.appendChild(thinkingDiv);
            });
        }

        function displayAITrades(trades) {
            const container = document.getElementById('ai-trades');
            
            if (!trades || trades.length === 0) {
                container.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; font-style: italic; font-size: 12px;">No AI trades yet</div>';
                return;
            }
            
            container.innerHTML = '';
            trades.slice(-10).reverse().forEach(trade => {
                const tradeDiv = document.createElement('div');
                tradeDiv.className = 'trade-item';
                
                const actionClass = trade.action === 'BUY' ? 'positive' : 'negative';
                
                tradeDiv.innerHTML = `
                    <div class="trade-header">
                        <span class="${actionClass}">${trade.action} ${trade.symbol}</span>
                        <span class="ai-badge">AI</span>
                    </div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.6); margin-bottom: 3px;">
                        ${trade.quantity} @ $${trade.price} = $${trade.total.toFixed(2)}
                    </div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.5);">
                        ${trade.reasoning}
                    </div>
                `;
                
                container.appendChild(tradeDiv);
            });
        }

        async function executeTrade(action) {
            const symbol = document.getElementById('trade-symbol').value;
            const quantity = parseInt(document.getElementById('trade-quantity').value);
            const price = parseFloat(document.getElementById('trade-price').value);

            if (!symbol || !quantity || !price) {
                alert('Please fill all fields');
                return;
            }

            try {
                const response = await fetch('/api/trade', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, action, quantity, price })
                });

                const result = await response.json();
                
                if (result.success) {
                    loadPortfolios();
                } else {
                    alert(result.message);
                }
            } catch (error) {
                alert('Trade execution failed');
            }
        }

        function updateLastUpdate() {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }

        document.getElementById('trade-symbol').addEventListener('change', function() {
            const symbol = this.value;
            if (symbol && marketData[symbol]) {
                document.getElementById('trade-price').value = marketData[symbol].price;
            }
        });

        document.getElementById('ai-provider').addEventListener('change', function() {
            document.getElementById('current-provider').textContent = this.options[this.selectedIndex].text;
        });

        // Initialize
        createParticles();
        loadMarketData();
        loadPortfolios();
        loadAIData();

        // Auto-refresh
        setInterval(() => {
            loadMarketData();
            loadPortfolios();
            loadAIData();
        }, 30000);
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/market-data')
def market_data():
    return jsonify(market_data_cache)

@app.route('/api/portfolio')
def get_portfolio():
    portfolio['total_value'] = calculate_portfolio_value()
    return jsonify(portfolio)

@app.route('/api/ai/portfolio')
def get_ai_portfolio():
    return jsonify(ai_bot['portfolio'])

@app.route('/api/ai/analysis')
def get_ai_analysis():
    return jsonify(ai_bot['last_analysis'])

@app.route('/api/ai/thinking')
def get_ai_thinking():
    return jsonify(ai_bot['thinking_log'])

@app.route('/api/ai/trades')
def get_ai_trades():
    return jsonify(ai_bot['portfolio']['trades'])

@app.route('/api/ai/toggle', methods=['POST'])
def toggle_ai():
    data = request.json
    ai_bot['enabled'] = not ai_bot['enabled']
    ai_bot['provider'] = data.get('provider', 'openai')
    ai_bot['strategy'] = data.get('strategy', 'conservative')
    
    return jsonify({
        'enabled': ai_bot['enabled'],
        'provider': ai_bot['provider'],
        'strategy': ai_bot['strategy']
    })

@app.route('/api/ai/analyze', methods=['POST'])
def manual_ai_analysis():
    if market_data_cache:
        run_ai_analysis()
    return jsonify(ai_bot['last_analysis'])

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json
    symbol = data.get('symbol')
    action = data.get('action')
    quantity = int(data.get('quantity', 0))
    price = float(data.get('price', 0))
    
    total_cost = quantity * price
    
    if action == 'BUY':
        if portfolio['cash'] >= total_cost:
            portfolio['cash'] -= total_cost
            portfolio['positions'][symbol] = portfolio['positions'].get(symbol, 0) + quantity
            
            trade = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'total': total_cost
            }
            portfolio['trades'].append(trade)
            return jsonify({'success': True, 'message': f'Bought {quantity} shares of {symbol}'})
        else:
            return jsonify({'success': False, 'message': 'Insufficient funds'})
    
    elif action == 'SELL':
        current_position = portfolio['positions'].get(symbol, 0)
        if current_position >= quantity:
            portfolio['cash'] += total_cost
            portfolio['positions'][symbol] -= quantity
            
            trade = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'total': total_cost
            }
            portfolio['trades'].append(trade)
            return jsonify({'success': True, 'message': f'Sold {quantity} shares of {symbol}'})
        else:
            return jsonify({'success': False, 'message': 'Insufficient shares'})
    
    return jsonify({'success': False, 'message': 'Invalid action'})

if __name__ == '__main__':
    print("🚀 Starting Universal AI Trading Terminal...")
    print("🤖 Multi-AI Provider Support...")
    print("📊 Real-time Market Analysis...")
    print("💎 Live Trading Simulation...")
    print("🌐 Server starting on http://0.0.0.0:7000")
    app.run(host='0.0.0.0', port=7000, debug=False)

