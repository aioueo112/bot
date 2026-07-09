import discord
from discord.ext import commands
import os

# ================== 設定 ==================
# TOKENは絶対にここに直接書かない！
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ エラー: TOKEN環境変数が設定されていません！")
    exit(1)

YOUR_SERVER_ID = 634719150434156546
RAID_GUILD_ID = 1216303889599565875
NOTIFY_CHANNEL_ID = 1524739659840618536

# =========================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ セルフボット起動完了: {bot.user}")
    print("トークン: 正常に読み込み済み")

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != YOUR_SERVER_ID:
        return

    raid_guild = bot.get_guild(RAID_GUILD_ID)
    if not raid_guild or not raid_guild.get_member(member.id):
        return

    channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="🚨 荒らし可能性アラート", description=f"{member.mention} が参加", color=0xff0000)
        embed.add_field(name="ユーザー", value=f"{member.name}#{member.discriminator}\n`{member.id}`", inline=False)
        embed.add_field(name="荒らし鯖", value="所属確認済み", inline=True)
        await channel.send("@here", embed=embed)

@bot.command()
async def check(ctx):
    if ctx.guild.id != YOUR_SERVER_ID:
        return await ctx.send("自分のサーバーでのみ使用できます。")
    
    raid_guild = bot.get_guild(RAID_GUILD_ID)
    if not raid_guild:
        return await ctx.send("監視鯖が見つかりません。")

    overlaps = [m for m in ctx.guild.members if raid_guild.get_member(m.id)]
    
    if not overlaps:
        return await ctx.send("✅ 重複メンバーなし")
    
    embed = discord.Embed(title="⚠️ 荒らし鯖重複メンバー", description=f"**{len(overlaps)}人**", color=0xffaa00)
    text = "\n".join([f"**{m.name}#{m.discriminator}** (`{m.id}`)" for m in overlaps])
    embed.description += "\n\n" + (text if len(text) < 3900 else text[:3900] + "\n...省略")
    await ctx.send(embed=embed)

bot.run(TOKEN)
