automobot-telegram-binance
Private Telegram-controlled Binance automation foundation designed to evolve into a Freqtrade-powered trading system.
Current stage
Telegram bot control layer
/start, /status, /balance, /positions, /profit, /pause, /resume, /stop
/whoami helper for obtaining the Telegram user ID
Binance REST account reader
Binance testnet support
Persistent runtime pause/stop state
Docker/Railway-friendly deployment
No order execution yet
Safety
This repository intentionally starts with live trading disabled.
Never commit:
Telegram bot tokens
Binance API keys or secrets
.env files
For Binance, use an API key with read/trade permissions only. Never grant withdrawal permissions.
Before live trading:
Run the bot in a safe environment.
Verify Telegram access control.
Verify Binance testnet connectivity.
Integrate Freqtrade and dry-run.
Add risk limits.
Only then consider live spot trading.
Local run
Create a virtual environment, install dependencies, set environment variables from .env.example, then run:
python -m bot.telegram_bot
Railway
Deploy the repository as a Docker service and configure the environment variables in Railway. Do not store secrets in GitHub.
Telegram commands
/start /status /balance /positions /profit /pause /resume /stop /whoami
