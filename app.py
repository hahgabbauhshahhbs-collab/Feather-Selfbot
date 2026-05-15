from flask import Flask, render_template, request, jsonify
import discord
from discord.ext import commands
import asyncio
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

bot = None
is_logged_in = False
user_data = {}

def run_bot(token):
    global bot, is_logged_in, user_data
    try:
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix=".", self_bot=True, intents=intents)

        @bot.event
        async def on_ready():
            global is_logged_in, user_data
            is_logged_in = True
            user_data = {
                "username": str(bot.user),
                "avatar": str(bot.user.avatar.url) if bot.user.avatar else None,
            }
            print(f"✅ Feather Selfbot Logged In: {bot.user}")

        # Streaming Command
        @bot.command()
        async def stream(ctx, *, name: str):
            await bot.change_presence(activity=discord.Streaming(
                name=name,
                url="https://www.twitch.tv/feather"
            ))
            await ctx.send("✅ Streaming Status Updated!")

        asyncio.run(bot.start(token))
    except Exception as e:
        print(f"❌ Error: {e}")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/validate_token', methods=['POST'])
def validate_token():
    global is_logged_in

    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({"success": False, "message": "Please enter a valid token"}), 400

    if not is_logged_in:
        thread = threading.Thread(target=run_bot, args=(token,), daemon=True)
        thread.start()
        time.sleep(6)

    return jsonify({
        "success": True,
        "message": "Selfbot Started Successfully",
        "user": user_data
    })


@app.route('/api/logout', methods=['POST'])
def logout():
    global is_logged_in
    is_logged_in = False
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("🚀 Feather Selfbot V1.3 - Ready for Public")
    app.run(host="0.0.0.0", port=port)