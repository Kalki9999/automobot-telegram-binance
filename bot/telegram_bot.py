import logging
from functools import wraps

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from bot.binance_client import BinanceClient
from bot.config import load_settings
from bot.state import StateStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("automobot")

SETTINGS = load_settings()
STATE = StateStore()
BINANCE = BinanceClient(
    SETTINGS.binance_api_key,
    SETTINGS.binance_api_secret,
    SETTINGS.binance_testnet,
)


def authorized(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id if user else 0

        # During initial setup, an empty allowlist permits discovery/testing.
        # Before enabling Binance trading, populate TELEGRAM_ALLOWED_USER_IDS.
        if SETTINGS.allowed_user_ids and user_id not in SETTINGS.allowed_user_ids:
            await update.effective_message.reply_text("Access denied.")
            return

        return await handler(update, context)

    return wrapper


@authorized
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_text(
        "🤖 Automobot online.\n"
        f"Your Telegram ID: {user.id if user else 'unknown'}\n\n"
        "Use /status, /balance, /positions, /profit, /pause, /resume or /stop."
    )


@authorized
async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_text(
        f"Your Telegram user ID is: {user.id if user else 'unknown'}"
    )


@authorized
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mode = "LIVE TRADING ENABLED" if SETTINGS.trading_enabled else "SAFE / NO LIVE ORDERS"
    runtime = "RUNNING" if STATE.state.running else "STOPPED"
    paused = "PAUSED" if STATE.state.paused else "ACTIVE"
    binance = "configured" if BINANCE.configured else "not configured"
    await update.effective_message.reply_text(
        "🤖 AUTOMOBOT\n\n"
        f"Runtime: {runtime}\n"
        f"Trading: {mode}\n"
        f"Strategy state: {paused}\n"
        f"Binance: {binance}\n"
        f"Network: {'TESTNET' if SETTINGS.binance_testnet else 'LIVE'}"
    )

@authorized
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not BINANCE.configured:
        await update.effective_message.reply_text(
            "Binance is not connected yet. Add BINANCE_API_KEY and BINANCE_API_SECRET to the runtime environment."
        )
        return

    try:
        balances = BINANCE.non_zero_balances()
    except Exception as exc:
        logger.exception("Balance request failed")
        await update.effective_message.reply_text(f"Binance error: {exc}")
        return

    if not balances:
        await update.effective_message.reply_text("No non-zero balances found.")
        return

    lines = ["💰 BINANCE BALANCE"]
    for item in balances[:25]:
        lines.append(
            f"{item['asset']}: free {item['free']} | locked {item['locked']}"
        )

    if len(balances) > 25:
        lines.append(f"...and {len(balances) - 25} more")
    await update.effective_message.reply_text("\n".join(lines))


@authorized
async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "📊 Spot positions are represented by non-zero asset balances. "
        "Use /balance for the current holdings. Freqtrade position tracking will be added next."
    )


@authorized
async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "📈 P/L tracking is not enabled yet. It will be connected to the Freqtrade trade database."
    )


@authorized
async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    STATE.set_paused(True)
    await update.effective_message.reply_text("⏸ Automobot paused. No new trading actions should be started.")


@authorized
async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not STATE.state.running:
        await update.effective_message.reply_text("Bot is stopped. Use /start to re-enable runtime state.")
        return
    STATE.set_paused(False)
    await update.effective_message.reply_text("▶️ Automobot resumed.")


@authorized
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    STATE.set_running(False)
    STATE.set_paused(True)
    await update.effective_message.reply_text(
        "🛑 Automobot stopped.\n\n"
        "This first version does not submit orders, so no open Binance orders were cancelled."
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled Telegram error", exc_info=context.error)


def main() -> None:
    app = ApplicationBuilder().token(SETTINGS.telegram_token).build()

    handlers = {
        "start": start,
        "status": status,
        "balance": balance,
        "positions": positions,
        "profit": profit,
        "pause": pause,
        "resume": resume,
        "stop": stop,
        "whoami": whoami,
    }

    for command, callback in handlers.items():
        app.add_handler(CommandHandler(command, callback))

    app.add_error_handler(error_handler)
    logger.info("Automobot Telegram backend starting")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
