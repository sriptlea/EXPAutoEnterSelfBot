import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio


TOKEN = "YOURTOKEN"  # REPLACE WITH ur own token
SERVER_ID = 1184110194905600132
GIVEAWAY_BOT_ID = 1344240724526235759
EMOJI_ID = "1298856059817168996"

client = commands.Bot(command_prefix=".", self_bot=True)


giveaway_stats = {
    "messages_reacted": 0,
    "games_entered": 0,
    "won": 0,
    "last_reset": datetime.now()
}

# auto react is default enabled i would recommend not to use cmds since u would get limited
auto_react_enabled = True

def reset_daily_stats():
    """Reset stats every 24 hours"""
    now = datetime.now()
    if now - giveaway_stats["last_reset"] >= timedelta(hours=24):
        giveaway_stats["messages_reacted"] = 0
        giveaway_stats["games_entered"] = 0
        giveaway_stats["won"] = 0
        giveaway_stats["last_reset"] = now
        print("📊 Daily stats reset!")

@client.event
async def on_ready():
    print(f"✅ Selfbot logged in as {client.user}")
    print(f"User ID: {client.user.id}")
    print(f"🎁 Giveaway Auto-React is **ENABLED** by default")
    try:
        guild = client.get_guild(SERVER_ID)
        if guild:
            print(f"✅ Connected to server: {guild.name}")
            print(f"🎯 Monitoring bot ID: {GIVEAWAY_BOT_ID}")
            # Subscribe to channels for better message delivery
            for channel in guild.text_channels:
                try:
                    await channel.history(limit=1).flatten()
                except:
                    pass
        else:
            print(f"❌ Server {SERVER_ID} not found!")
    except Exception as e:
        print(f"Error checking guild: {e}")

@client.command(name="giveawayauto")
async def giveawayauto_cmd(ctx):
    """Start auto-reacting to giveaways"""
    global auto_react_enabled
    guild = client.get_guild(SERVER_ID)
    if not guild:
        await ctx.send("❌ Guild not found!")
        return
    
    auto_react_enabled = True
    await ctx.send(f"🎁 Giveaway Auto-React **ENABLED**\n✅ Listening for bot: {GIVEAWAY_BOT_ID}\n📍 Server: {guild.name}")
    print("🎯 Giveaway auto-react ENABLED!")

@client.command(name="giveawaystop")
async def giveawaystop_cmd(ctx):
    """Stop auto-reacting to giveaways"""
    global auto_react_enabled
    auto_react_enabled = False
    await ctx.send("⏸️ Giveaway Auto-React **DISABLED**")
    print("⏸️ Giveaway auto-react DISABLED!")

@client.command(name="stats")
async def stats_cmd(ctx):
    """Show giveaway stats"""
    win_rate = 0
    if giveaway_stats["games_entered"] > 0:
        win_rate = (giveaway_stats["won"] / giveaway_stats["games_entered"]) * 100
    
    status = "✅ ENABLED" if auto_react_enabled else "⏸️ DISABLED"
    
    stats_msg = f"📊 **Giveaway Statistics (24H)**\n"
    stats_msg += f"Status: {status}\n"
    stats_msg += f"Messages Reacted: {giveaway_stats['messages_reacted']}\n"
    stats_msg += f"Games Entered: {giveaway_stats['games_entered']}\n"
    stats_msg += f"Won: {giveaway_stats['won']}\n"
    stats_msg += f"Win Rate: {win_rate:.1f}%\n"
    stats_msg += f"Last reset: {giveaway_stats['last_reset'].strftime('%Y-%m-%d %H:%M:%S')}"
    
    await ctx.send(stats_msg)

@client.event
async def on_message(message):
    """Listen for giveaway messages and react with the first emoji on the post"""
    reset_daily_stats()
    

    await client.process_commands(message)
    
    if message.author == client.user:
        return
    
    if auto_react_enabled and message.guild and message.guild.id == SERVER_ID:
        if message.author.id == GIVEAWAY_BOT_ID and message.embeds:
            # Wait a moment for bot to add its own reactions
            await asyncio.sleep(1)
            
            # Fetch the message again to get updated reactions
            try:
                msg = await message.channel.fetch_message(message.id)
                
                if msg.reactions:
                    # React with the FIRST emoji only
                    first_reaction = msg.reactions[0]
                    try:
                        await msg.add_reaction(first_reaction.emoji)
                        giveaway_stats["messages_reacted"] += 1
                        giveaway_stats["games_entered"] += 1
                        print(f"🎁 Reacted with {first_reaction.emoji}! Games entered: {giveaway_stats['games_entered']}")
                    except Exception as e:
                        print(f"⚠️ Could not add {first_reaction.emoji}: {e}")
                else:
                    # No reactions = don't count, don't react
                    print(f"⏭️ No reactions found on giveaway, skipping...")
                    
            except Exception as e:
                print(f"❌ Error processing message: {type(e).__name__} - {e}")

@client.event
async def on_message_edit(before, after):
    """Listen for giveaway end results"""
    reset_daily_stats()
    
    if after.guild and after.guild.id == SERVER_ID:
        if after.author.id == GIVEAWAY_BOT_ID and after.embeds:
            # Check if this is a giveaway end message
            embed = after.embeds[0]
            embed_text = (embed.title or "") + " " + (embed.description or "")
            
            # Check for winner announcement
            if any(word in embed_text.lower() for word in ["winner", "won", "congratulations", "🎉"]):
                # Check if user won
                username = client.user.name.lower()
                user_id = str(client.user.id)
                user_mention = client.user.mention
                
                if username in embed_text.lower() or user_id in embed_text or user_mention in embed_text:
                    giveaway_stats["won"] += 1
                    print(f"🎉🎉🎉 YOU WON! Total wins: {giveaway_stats['won']} 🎉🎉🎉")

@client.event
async def on_error(event, *args, **kwargs):
    """Handle errors gracefully"""
    print(f"❌ Error in {event}: {args}")

if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("⚠️ Make sure you've replaced the TOKEN with a valid one!")
