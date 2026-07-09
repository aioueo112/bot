import discord
from discord.ext import commands

TOKEN = "ここに自分のユーザーTOKEN"  # ← 後で環境変数に変更します

YOUR_SERVER_ID = 634719150434156546
RAID_GUILD_ID = 1216303889599565875
NOTIFY_CHANNEL_ID = 1524739659840618536

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 起動: {bot.user}")

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
        return
    raid_guild = bot.get_guild(RAID_GUILD_ID)
    if not raid_guild:
        return await ctx.send("監視鯖が見つかりません")

    overlaps = [m for m in ctx.guild.members if raid_guild.get_member(m.id)]
    if not overlaps:
        return await ctx.send("✅ 重複メンバーなし")

    embed = discord.Embed(title="⚠️ 荒らし鯖重複メンバー", description=f"**{len(overlaps)}人**", color=0xffaa00)
    text = "\n".join([f"**{m.name}#{m.discriminator}** (`{m.id}`)" for m in overlaps])
    embed.description += "\n\n" + text[:3900]
    await ctx.send(embed=embed)

bot.run(TOKEN)
