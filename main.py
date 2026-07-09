import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN環境変数が設定されていません")
    exit(1)

YOUR_SERVER_ID = 634719150434156546
RAID_GUILD_ID = 1216303889599565875
NOTIFY_CHANNEL_ID = 1524739659840618536

# discord.py-self 対応 Intents
intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True
)

bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 起動成功: {bot.user}")
    print("監視開始")

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != YOUR_SERVER_ID:
        return
    raid = bot.get_guild(RAID_GUILD_ID)
    if not raid or not raid.get_member(member.id):
        return

    ch = bot.get_channel(NOTIFY_CHANNEL_ID)
    if ch:
        e = discord.Embed(title="🚨 荒らしアラート", description=f"{member.mention} が参加", color=0xff0000)
        e.add_field(name="ユーザー", value=f"{member}\n`{member.id}`", inline=False)
        await ch.send("@here", embed=e)

@bot.command()
async def check(ctx):
    if ctx.guild.id != YOUR_SERVER_ID:
        return
    raid = bot.get_guild(RAID_GUILD_ID)
    if not raid:
        return await ctx.send("監視鯖が見つかりません")
    overlaps = [m for m in ctx.guild.members if raid.get_member(m.id)]
    if not overlaps:
        return await ctx.send("✅ 重複なし")
    e = discord.Embed(title="⚠️ 重複メンバー", description=f"{len(overlaps)}人", color=0xffaa00)
    txt = "\n".join([f"{m} (`{m.id}`)" for m in overlaps])
    e.description += "\n\n" + txt[:3900]
    await ctx.send(embed=e)

bot.run(TOKEN)
