"""
swiftnode/bot/discord_bot.py
===========================
Discord bot integration for SwiftNode.
"""
import discord
from discord.ext import commands
import asyncio
from rich.console import Console
from swiftnode.config import load_config
from swiftnode.core.agent import SwiftNodeCore

console = Console()

class SwiftNodeDiscordBot(discord.Client):
    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent

    async def on_ready(self):
        console.print(f"[bold green]✅ Discord Bot Logged in as {self.user} (ID: {self.user.id})[/]")
        console.print("[dim]Listening for messages...[/dim]")

    async def on_message(self, message):
        # Prevent replying to itself
        if message.author.id == self.user.id:
            return

        # Basic text handling for now - assuming channel DM or ping
        if self.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            user_text = message.content.replace(f'<@{self.user.id}>', '').strip()
            
            if not user_text:
                return
                
            async with message.channel.typing():
                try:
                    # Very simple synchronous call blocking logic - in real world use executor
                    response_text = await asyncio.to_thread(self.agent.process_query, user_text)
                    
                    # Discord has a 2000 char cap per message
                    chunks = [response_text[i:i+1950] for i in range(0, len(response_text), 1950)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                except Exception as e:
                    console.print(f"[bold red]Discord Bot Error:[/] {e}")
                    await message.channel.send("⚠️ Agent encountered an error processing your request.")


def run_discord_bot():
    config = load_config()
    token = config.get("discord_token")

    if not token:
        console.print("[bold red]❌ Discord token not found in config.[/]")
        console.print("[dim]Run `swiftnode config` to set up Discord.[/dim]")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    
    agent = SwiftNodeCore(config)
    client = SwiftNodeDiscordBot(agent=agent, intents=intents)
    try:
        client.run(token, log_handler=None) # Use our rich console instead
    except discord.LoginFailure:
        console.print("[bold red]❌ Invalid Discord token.[/]")
    except Exception as e:
        console.print(f"[bold red]❌ Discord Error:[/] {e}")

if __name__ == "__main__":
    run_discord_bot()
