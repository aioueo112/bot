import discord
from discord.ext import commands
import os

# ================== 設定 ==================
TOKEN = os.getenv("TOKEN")  # Renderの環境変数から取得

YOUR_SERVER_ID = 634719150434156546      # 自分のサーバー
RAID_GUILD_ID = 1216303889599565875      # 荒らしの共通鯖
NOTIFY_CHANNEL_ID = 1524739659840618536  # 通知チャンネル

# =========================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ セルフボット起動完了: {bot.user}")
    print(f"自分のサーバー: {bot.get_guild(YOUR_SERVER_ID)}")
    print(f"監視対象: {bot.get_guild(RAID_GUILD_ID)}")

# 荒らし可能性アラート
@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != YOUR_SERVER_ID:
        return

    raid_guild = bot.get_guild(RAID_GUILD_ID)
    if not raid_guild or not raid_guild.get_member(member.id):
        return

    channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="🚨 荒らし可能性アラート",
        description=f"{member.mention} がサーバーに参加しました",
        color=0xff0000
    )
    embed.add_field(name="ユーザー", value=f"{member.name}#{member.discriminator}\n`{member.id}`", inline=False)
    embed.add_field(name="荒らし鯖", value="✅ 所属確認済み", inline=True)
    embed.add_field(name="アカウント作成日", value=discord.utils.format_dt(member.created_at, style='F'), inline=True)
    embed.add_field(name="参加時刻", value=discord.utils.format_dt(member.joined_at, style='F'), inline=True)

    await channel.send("@here", embed=embed)
    print(f"【アラート】 {member} が参加（荒らし鯖所属）")

# !check コマンド
@bot.command()
async def check(ctx):
    if ctx.guild.id != YOUR_SERVER_ID:
        return await ctx.send("このコマンドは自分のサーバーでのみ使用できます。")

    raid_guild = bot.get_guild(RAID_GUILD_ID)
    if not raid_guild:
        return await ctx.send("荒らし監視鯖が見つかりません。")

    overlaps = [m for m in ctx.guild.members if raid_guild.get_member(m.id)]

    if not overlaps:
        embed = discord.Embed(title="✅ チェック結果", description="荒らし鯖との重複メンバーはいません。", color=0x00ff00)
        return await ctx.send(embed=embed)

    embed = discord.Embed(
        title="⚠️ 荒らし鯖との重複メンバー",
        description=f"合計 **{len(overlaps)}人** 見つかりました。",
        color=0xffaa00
    )

    member_list = "\n".join([f"**{m.name}#{m.discriminator}**\n`{m.id}`" for m in overlaps])
    if len(member_list) > 3900:
        member_list = member_list[:3900] + "\n...（続きは省略）"

    embed.description += "\n\n" + member_list
    embed.set_footer(text="早めの対応をおすすめします")
    await ctx.send(embed=embed)

bot.run(TOKEN)
