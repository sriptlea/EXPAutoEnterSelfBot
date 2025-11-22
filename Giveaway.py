import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json

# Configuration
TOKEN = "YOUR_TOKEN_HERE"
SERVER_ID = 1184110194905600132
GIVEAWAY_BOT_ID = 1344240724526235759
EMOJI_ID = 1298856059817168996

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

client = commands.Bot(command_prefix=".", intents=intents, self_bot=True)

# Tracking data
giveaway_stats = {
    "games_entered": 0,
    "won": 0,
    "last_reset": datetime.now()
}

def reset_daily_stats():
    """Reset stats every 24 hours"""
    now = datetime.now()
    if now - giveaway_stats["last_reset"] >= timedelta(hours=24):
        giveaway_stats["games_entered"] = 0
        giveaway_stats["won"] = 0
        giveaway_stats["last_reset"] = now

@client.event
async def on_ready():
    print(f"✅ Selfbot logged in as {client.user}")

@client.command(name="giveawayauto")
async def giveaway_auto(ctx):
    """Enable auto-react to giveaways"""
    guild = client.get_guild(SERVER_ID)
    
    if not guild:
        await ctx.send("❌ Guild not found!")
        return
    
    embed = discord.Embed(
        title="🎁 Giveaway Auto-React Started",
        description=f"Listening for giveaways from bot ID: {GIVEAWAY_BOT_ID}",
        color=discord.Color.green()
    )
    embed.add_field(name="Emoji ID", value=str(EMOJI_ID), inline=False)
    embed.add_field(name="Server", value=guild.name, inline=False)
    embed.set_footer(text="React stats will update in real-time")
    
    await ctx.send(embed=embed)
    print("🎯 Giveaway auto-react enabled!")

@client.event
async def on_message(message):
    """Listen for giveaway messages and auto-react"""
    reset_daily_stats()
    
    if message.guild and message.guild.id == SERVER_ID:
        if message.author.id == GIVEAWAY_BOT_ID and message.embeds:
            # React with custom emoji by ID
            try:
                emoji = discord.PartialEmoji(id=EMOJI_ID)
                await message.add_reaction(emoji)
                giveaway_stats["games_entered"] += 1
                print(f"✅ Reacted to giveaway! Games entered: {giveaway_stats['games_entered']}")
            except Exception as e:
                print(f"❌ Error reacting: {e}")
    
    await client.process_commands(message)

@client.event
async def on_message_edit(before, after):
    """Listen for giveaway end results"""
    reset_daily_stats()
    
    if after.guild and after.guild.id == SERVER_ID:
        if after.author.id == GIVEAWAY_BOT_ID and after.embeds:
            # Check if this is a giveaway end message
            embed = after.embeds[0]
            if "winner" in embed.title.lower() or "won" in embed.description.lower():
                # Check if user is mentioned as winner
                if client.user.mention in embed.description or str(client.user.id) in embed.description:
                    giveaway_stats["won"] += 1
                    print(f"🎉 YOU WON! Total wins: {giveaway_stats['won']}")

@client.command(name="stats")
async def show_stats(ctx):
    """Show current giveaway stats"""
    reset_daily_stats()
    
    embed = discord.Embed(
        title="📊 Giveaway Statistics (24H)",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="Games Entered",
        value=str(giveaway_stats["games_entered"]),
        inline=True
    )
    embed.add_field(
        name="Won",
        value=str(giveaway_stats["won"]),
        inline=True
    )
    
    win_rate = 0
    if giveaway_stats["games_entered"] > 0:
        win_rate = (giveaway_stats["won"] / giveaway_stats["games_entered"]) * 100
    
    embed.add_field(
        name="Win Rate",
        value=f"{win_rate:.1f}%",
        inline=True
    )
    embed.set_footer(text=f"Last reset: {giveaway_stats['last_reset'].strftime('%H:%M:%S')}")
    
    await ctx.send(embed=embed)

@client.command(name="resetstats")
async def reset_stats(ctx):
    """Manually reset stats"""
    giveaway_stats["games_entered"] = 0
    giveaway_stats["won"] = 0
    giveaway_stats["last_reset"] = datetime.now()
    
    await ctx.send("✅ Stats reset!")

if __name__ == "__main__":
    client.run(TOKEN)
