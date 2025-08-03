# 🚀 QuantumTrader AI - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ **Repository Contents Verified:**
- `src/ai_trading_terminal.py` - Main application file
- `requirements.txt` - Python dependencies
- `README.md` - Complete documentation
- `LICENSE` - MIT license
- `screenshots/` - PNG screenshots for documentation
- `DEPLOYMENT.md` - This deployment guide

## 🖥️ Server Deployment Instructions

### 1️⃣ **Clone Repository**
```bash
# Clone from GitHub
git clone https://github.com/kolerto99/quantumtrader-ai.git
cd quantumtrader-ai
```

### 2️⃣ **Install Dependencies**
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Or using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ **Set Environment Variables**
```bash
# Required: OpenAI API Key
export OPENAI_API_KEY="your_openai_api_key_here"

# Optional: Additional AI providers
export ANTHROPIC_API_KEY="your_claude_api_key"
export GOOGLE_API_KEY="your_gemini_api_key"
```

### 4️⃣ **Run Application**
```bash
# Start the application
python3 src/ai_trading_terminal.py

# Application will be available at:
# http://localhost:7000
```

### 5️⃣ **Production Deployment (Optional)**
```bash
# For production, use a WSGI server like Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:7000 src.ai_trading_terminal:app
```

## 🔧 Configuration Options

### **AI Provider Setup**

**OpenAI (Required for full functionality):**
```bash
export OPENAI_API_KEY="sk-..."
```

**Anthropic Claude:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Google Gemini:**
```bash
export GOOGLE_API_KEY="AIza..."
```

**Local LLM (Ollama):**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download models
ollama pull llama2
ollama pull deepseek-coder
ollama pull mistral
```

## 🌐 Network Configuration

### **Firewall Settings**
```bash
# Allow port 7000 (or your chosen port)
sudo ufw allow 7000
```

### **Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:7000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Considerations

### **Environment Variables**
- Store API keys in environment variables, never in code
- Use `.env` files for local development
- Use secure secret management in production

### **Network Security**
- Run behind a reverse proxy (Nginx/Apache)
- Use HTTPS in production
- Implement rate limiting if needed

## 📊 Monitoring & Logs

### **Application Logs**
```bash
# View application logs
tail -f /var/log/quantumtrader-ai.log

# Or redirect output
python3 src/ai_trading_terminal.py > app.log 2>&1 &
```

### **System Resources**
- Monitor CPU usage (AI analysis can be intensive)
- Monitor memory usage (market data caching)
- Monitor network usage (real-time data fetching)

## 🔄 Updates & Maintenance

### **Update Application**
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
# (Use your process manager or restart manually)
```

### **Backup Configuration**
```bash
# Backup environment variables
env | grep -E "(OPENAI|ANTHROPIC|GOOGLE)_API_KEY" > api_keys_backup.env
```

## 🐛 Troubleshooting

### **Common Issues**

**Port Already in Use:**
```bash
# Find process using port 7000
lsof -i :7000

# Kill process if needed
kill -9 <PID>
```

**Missing Dependencies:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**API Key Issues:**
```bash
# Verify environment variables
echo $OPENAI_API_KEY

# Test API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**Market Data Issues:**
```bash
# Test Yahoo Finance connection
python3 -c "import yfinance as yf; print(yf.download('AAPL', period='1d'))"
```

## 📈 Performance Optimization

### **Production Settings**
- Use multiple worker processes with Gunicorn
- Enable caching for market data
- Use Redis for session storage if needed
- Implement connection pooling

### **Resource Limits**
```bash
# Set memory limits
ulimit -m 2048000  # 2GB memory limit

# Set CPU limits
cpulimit -l 50 python3 src/ai_trading_terminal.py
```

## 🎯 Success Verification

### **Health Check**
```bash
# Test application endpoint
curl http://localhost:7000

# Should return HTML content with "AI Trading Terminal"
```

### **Feature Testing**
1. ✅ Main interface loads
2. ✅ Market data updates (check timestamps)
3. ✅ AI analysis works (if API keys configured)
4. ✅ Trading simulation functions
5. ✅ Portfolio tracking updates

## 📞 Support

If you encounter issues during deployment:
- Check [GitHub Issues](https://github.com/kolerto99/quantumtrader-ai/issues)
- Contact [@kolerto99](https://github.com/kolerto99)
- Follow [@Iuvnriki](https://x.com/Iuvnriki) for updates

---

**🚀 Your QuantumTrader AI is ready for deployment!**

