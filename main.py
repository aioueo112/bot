import os
import discord
from discord import app_commands
import requests

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TARGET_GUILD_ID = int(os.getenv("TARGET_GUILD_ID", "0"))

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user.name}")

@bot.event
async def on_member_join(member: discord.Member):
    if not WEBHOOK_URL or not TARGET_GUILD_ID:
        return

    target_guild = bot.get_guild(TARGET_GUILD_ID)
    if target_guild is None:
        return

    if target_guild.get_member(member.id) is not None:
        payload = {
            "content": f"🔔 **共通サーバーのメンバーが参加しました！**\n"
                       f"ユーザー名: {member.mention} ({member.name})\n"
                       f"参加したサーバー: {member.guild.name}"
        }
        requests.post(WEBHOOK_URL, json=payload)

@bot.tree.command(name="check", description="このサーバー内で、特定の共通サーバーにも所属している人を一覧表示します")
async def check_common_members(interaction: discord.Interaction):
    current_guild = interaction.guild
    target_guild = bot.get_guild(TARGET_GUILD_ID)

    if target_guild is None:
        await interaction.response.send_message("共通サーバーの情報が取得できませんでした。", ephemeral=True)
        return

    common_members = []
    for member in current_guild.members:
        if member.bot:
            continue
        if target_guild.get_member(member.id) is not None:
            # メンション - `ID(数字)` (ユーザー名) の形式に変更
            common_members.append(f"{member.mention} - `{member.id}` ({member.name})")

    embed = discord.Embed(
        title="🔍 共通サーバー所属メンバー一覧",
        color=discord.Color.blue()
    )
    embed.add_field(name="対象サーバー", value=target_guild.name, inline=False)

    if common_members:
        members_list = "\n".join(common_members)
        if len(members_list) > 1024:
            members_list = members_list[:1010] + "\n...他"
        embed.add_field(name=f"該当者 ({len(common_members)}人)", value=members_list, inline=False)
    else:
        embed.add_field(name="該当者", value="該当するメンバーはいません。", inline=False)

    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    if not TOKEN:
        print("エラー: DISCORD_BOT_TOKEN が環境変数に設定されていません。")
    else:
        bot.run(TOKEN)
