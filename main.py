import os
import random
import datetime
import threading
import http.server
import socketserver
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

PORT = int(os.environ.get("PORT", 10000))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"Serving health check on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_played = {}
last_result = {} # ユーザーごとの前回のルーレット結果を記憶する辞書

# 使える文字のプール（重複ありで選べる文字）
CHARACTER_POOL = ["鬼", "田", "敬", "一", "郎"]
TARGET_WORD = "鬼田敬一郎"
VERIFY_ROLE_ID = 1568118976779915356

class RouletteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ルーレットを回す 🎲", style=discord.ButtonStyle.primary, custom_id="spin_roulette_button")
    async def spin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        today = datetime.date.today()

        if user_id in last_played and last_played[user_id] == today:
            await interaction.response.send_message(
                f"{interaction.user.mention} さん、本日のルーレットは既に引いています！また明日挑戦してください。",
                ephemeral=True
            )
            return

        # 同じ文字が重複することも含めて、5文字をランダムに生成する
        while True:
            result_word = "".join(random.choices(CHARACTER_POOL, k=5))
            # 前回と同じ結果でなければループを抜ける（ただし、まだ前回の記録がない、または大当りの場合はそのまま通す）
            if user_id not in last_result or result_word != last_result[user_id] or result_word == TARGET_WORD:
                break

        # 今回の結果を保存
        last_played[user_id] = today
        last_result[user_id] = result_word

        if result_word == TARGET_WORD:
            await interaction.response.send_message(
                f"🎉 **大当たり！** 🎉\n"
                f"結果: **{result_word}**\n"
                f"おめでとうございます！「{TARGET_WORD}」が完成しました！🎁 景品獲得です！",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"🎲 **ルーレット結果** 🎲\n"
                f"結果: **{result_word}**\n"
                f"残念！「{TARGET_WORD}」にはなりませんでした。また明日挑戦してね！",
                ephemeral=True
            )

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="認証する", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("このコマンドはサーバー内で実行してください。", ephemeral=True)
            return

        role = guild.get_role(VERIFY_ROLE_ID)
        if not role:
            await interaction.response.send_message("エラー: 指定された認証ロールが見つかりませんでした。管理者にお問い合わせください。", ephemeral=True)
            return

        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("認証が完了しました！ロールが付与されました。", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("エラー: ボットにロールを付与する権限（またはロール管理の階層不足）があります。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"エラーが発生しました: {e}", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(RouletteView())
    bot.add_view(VerifyView())
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

@bot.tree.command(name="oni", description="鬼田敬一郎ルーレットのパネルを設置します")
async def oni(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎰 鬼田敬一郎ルーレット 🎰",
        description="下の「ルーレットを回す 🎲」ボタンを押してルーレットを回そう！\n見事「鬼田敬一郎」が揃ったら景品ゲット！\n*(※挑戦は1日1回までです)*",
        color=discord.Color.gold()
    )
    view = RouletteView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="verify", description="認証パネルを設置します（管理者向け）")
@app_commands.checks.has_permissions(administrator=True)
async def verify(interaction: discord.Interaction):
    embed = discord.Embed(
        title="サーバー認証",
        description="下の「認証する」ボタンを押して、サーバーの利用規約に同意し、参加を完了しましょう！",
        color=discord.Color.blue()
    )
    view = VerifyView()
    await interaction.response.send_message(embed=embed, view=view)

@verify.error
async def verify_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("このコマンドを実行する権限がありません（管理者限定）。", ephemeral=True)

bot.run(TOKEN)
