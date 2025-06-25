# Progression Tracker: Main Flow
# Blue - 24/06/2025
# Last update on 24/06/2025

# Imports
import discord
from discord import app_commands
from discord.ext import commands
import json
import sqlite3
import database as db
import status_rotation

#--------------------------------------------

# Functions
def update_config(key, value, filename="variables.json"):
  with open(filename, "r", encoding="utf-8") as file:
    var = json.load(file)
  var[key] = value
  with open(filename, "w", encoding="utf-8") as file:
    json.dump(var, file, indent=2)

def read_var(key, filename="variables.json"):
  with open(filename,"r", encoding="utf-8") as file:
    var = json.load(file)
  return var[key]

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == YOURDISCORDID

#--------------------------------------------

# Discordpy
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user} (ID: {bot.user.id})")
  await bot.change_presence(
        activity=discord.Game(name="Beach Buggy Racing 2"))
  update_config("overdrive_status", False)
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(f"Failed to sync commands: {e}")
  
  bot.loop.create_task(status_rotation.rotate_status(bot))
#--------------------------------------------

# Progression
class progression_embed_one(discord.ui.View):
  @discord.ui.button(label="Ready?", style=discord.ButtonStyle.primary)
  async def ready(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message("Hi!")


@bot.tree.command(name="progression",description="Calculate your BBR2 progression")
async def progression(interaction: discord.Interaction):
  embed = discord.Embed(
    title="BBR2 Account Progression",
    description=(
    f"Calculate your total progression in Beach Buggy Racing 2\n"
    f"Answer the following question using the STATS section of the game.\n"
    f"## Please use your real informations, as they are used in leaderboards\n"
    f"First time trying? Use /help first!\n"
    f"Actually, accuracy cannot reach 100%\n"
    f"Matching BBR2 V{read_var('version')}"),
    color=0x134fd3
  )
  button = progression_embed_one()
  await interaction.response.send_message(embed=embed, view=button)

#--------------------------------------------

# Delete Data

class delete_data_button(discord.ui.View):
  @discord.ui.button(label="YES", style=discord.ButtonStyle.danger)
  async def ready(self, interaction: discord.Interaction, button: discord.ui.Button):
    user_id = str(interaction.user.id)
    db.delete_user(user_id)
    embed = discord.Embed(
      title="Delete Data",
      description=("Your data were successfully deleted from the database"),
      color=0xff0000
  )
    await interaction.response.edit_message(embed=embed, view=None)


@bot.tree.command(name="delete-data", description="Delete your user data from the database")
async def deletedata(interaction: discord.Interaction):
  embed = discord.Embed(
    title="Delete Data",
    description=("# You're about to delete your data from the bot database\n# Are you really sure you want to do this?"),
    color=discord.Color.red()
  )
  button=delete_data_button()
  await interaction.response.send_message(embed=embed, view=button, ephemeral=True)

#--------------------------------------------

# Fun

@bot.tree.command(name="fun", description="get fun stats")
async def fun(interaction: discord.Interaction):
  embed = discord.Embed(
    title="Fun Stats",
    description=(f"Amount of users in database : 3)\n"
f"Amount of slash commands executed : {read_var('slash_commands_amount')}"
f"Amount of EXP earned by users : "
f"Total time driven : "
f"Total distance driven :  kms"
f"Average progression : %"
f"Average level : "
f"Average speed :  kms/h"),
    color=0x134fd3
  )
  await interaction.response.send_message(embed=embed)

#--------------------------------------------
# Status Changer (Owner only)
@bot.tree.command(name="status-changer", description="Changes the bot status")
@app_commands.choices(activity=[
    app_commands.Choice(name="Playing", value="Playing"),
    app_commands.Choice(name="Streaming", value="Streaming"),
    app_commands.Choice(name="Listening", value="Listening"),
    app_commands.Choice(name="Watching", value="Watching"),
    app_commands.Choice(name="Reset", value="Reset")
])
@app_commands.describe(
    activity="Activity type",
    text="Status text"
)
@app_commands.check(is_owner)
async def owner_command(interaction: discord.Interaction, activity: str, text: str):
    if activity == "Playing":
        await bot.change_presence(activity=discord.Game(name=text))

    elif activity == "Streaming":
        await bot.change_presence(activity=discord.Streaming(name=text, url="https://discord.gg/vectorunit"))

    elif activity == "Listening":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))

    elif activity == "Watching":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    
    if activity != "Reset":
      update_config("overdrive_status", True)
    else:
      await bot.change_presence(activity=discord.Game(name="Beach Buggy Racing 2"))
      update_config("overdrive_status", False)
    
    await interaction.response.send_message("Status set ✅", ephemeral=True)

@owner_command.error
async def owner_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)


#--------------------------------------------
# Bot token
bot.run('YOURTOKEN')