import discord
from discord import ui, ButtonStyle
import random
import string

# ========================= CONFIG =========================
TOKEN = "MTUxOTc0MDE5MzcxNDczNzIxNA.GQteMS.7XkPmko9q5kUPo00xjiWRcB7irVufTOQ9El8XA"   # ← PUT YOUR TOKEN HERE
PREFIX = "skimunch-"
ALLOWED_CHANNEL_ID = 1519740545277231286
RESET_PASSWORD = "skis"
# =======================================================

keys_db = {}  # In-memory only

class GenerateKeyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Generate Key", style=ButtonStyle.primary, emoji="🔑", custom_id="skimunch:generate_key")
    async def generate_key(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.channel_id != ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("❌ This only works in **#premium-key-gen**.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        
        if user_id in keys_db:
            await interaction.response.send_message(
                f"✅ **Your existing SKIMUNCH key:**\n`{keys_db[user_id]}`\n\nHWID-locked to first device.", 
                ephemeral=True
            )
            return
        
        random_digits = ''.join(random.choices(string.digits, k=11))
        new_key = f"{PREFIX}{random_digits}"
        
        keys_db[user_id] = new_key
        
        await interaction.response.send_message(
            f"✅ **Your SKIMUNCH key has been generated!**\n\n`{new_key}`\n\n"
            f"**Note:** HWID-locked to first device. Contact staff for reset.", 
            ephemeral=True
        )

class SkimunchBot(discord.Client):
    async def on_ready(self):
        print(f"✅ SKIMUNCH Bot is online as {self.user} | Memory Mode")
        self.add_view(GenerateKeyView())

    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.strip()

        # SECRET RESET COMMAND — Private & Clean
        if content.startswith("!rk"):
            parts = content.split()
            if len(parts) > 1 and parts[1] == RESET_PASSWORD:
                keys_db.clear()
                
                # Nice private reset message (only you see it)
                reset_embed = discord.Embed(
                    title="🔄 All keys have been reset!",
                    description="✅ Everyone will get a new key next time they generate one.",
                    color=0x00FF00
                )
                await message.author.send(embed=reset_embed)
                
                try:
                    await message.delete()  # Hide the command
                except:
                    pass
            else:
                try:
                    await message.author.send("❌ Wrong password.")
                    await message.delete()
                except:
                    pass
            return

        # Show key panel (only in allowed channel)
        if message.channel.id != ALLOWED_CHANNEL_ID:
            return

        if content.lower() in ["!key", "!generate", "!skimunch", "!keygen"]:
            embed = discord.Embed(
                title="🔑 SKISMUNCH Premium",
                description="Click the button below to receive your **lifetime license key**.",
                color=0x000000
            )
            embed.add_field(name="• Each account gets one key", value="", inline=False)
            embed.add_field(name="• Your key is HWID locked to the first device", value="", inline=False)
            embed.add_field(name="• Contact staff for support or a HWID reset", value="", inline=False)
            embed.set_footer(text="SKIMUNCH")

            view = GenerateKeyView()
            await message.channel.send(embed=embed, view=view)

intents = discord.Intents.default()
intents.message_content = True
client = SkimunchBot(intents=intents)
client.run(TOKEN)
