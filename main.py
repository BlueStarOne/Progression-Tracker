# Progression Tracker: Main Flow
# Blue - 24/06/2025
# Last update on 01/07/2025

# IMPORTS ---------------------------------

import discord
from discord import app_commands, ui
from discord.ext import commands
import json
import database as db
import status_rotation
from datetime import datetime, timezone
import os

# VARIABLES -------------------------------

bot_token = "YOUR BOT TOKEN"
slash_commands_allowed_users = [] # User ID
slash_commands_blacklist = [] # User ID
automod_channel_id = # Channel ID

# FUNCTIONS -------------------------------

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
  
def slash_command():
  filename = "variables.json"
  with open(filename, "r", encoding="utf-8") as file:
    var = json.load(file)
  var["slash_commands_amount"] += 1
  with open(filename, "w", encoding="utf-8") as file:
    json.dump(var, file, indent=2)

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id in slash_commands_allowed_users

# DISCORDPY -------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", activity=discord.Game("Beach Buggy Racing 2"), intents=intents)
update_config("overdrive_status", False)

@bot.event
async def on_ready():
  db.log(f"Logged in as {bot.user} (ID: {bot.user.id})")
  
  bot.loop.create_task(status_rotation.rotate_status(bot))
 
# PREFIX COMMANDS -------------------------

@bot.command()
async def sync(ctx):
  if ctx.author.id in slash_commands_allowed_users:
    try:
      synced = await bot.tree.sync()
      await ctx.send(f"Synced {len(synced)} command(s)")
      db.log(f"{ctx.author.id} synced {len(synced)} command(s)")
    except Exception as e:
      await ctx.send(f"Failed to sync commands: {e}")
      db.log(f"Failed to sync commands: {e}")

# /PROGRESSION ----------------------------

class ProgressionModal3(discord.ui.Modal, title="Progression 3/3"):
    powerups = ui.TextInput(label="Powerups Unlocked", placeholder="e.g. 34",  required=False)
    common_upgrades = ui.TextInput(label="Common Powerups Upgrades", placeholder="e.g. 178", required=False)
    rare_upgrades = ui.TextInput(label="Rare Powerups Upgrades", placeholder="e.g. 142", required=False)
    epic_upgrades = ui.TextInput(label="Epic Powerups Upgrades", placeholder="e.g. 102", required=False)
    

    async def on_submit(self, interaction: discord.Interaction):
        try:
            powerups = int(self.powerups.value) if self.powerups.value else 0
            common_upgrades = int(self.common_upgrades.value) if self.common_upgrades.value else 0
            rare_upgrades = int(self.rare_upgrades.value) if self.rare_upgrades.value else 0
            epic_upgrades = int(self.epic_upgrades.value) if self.epic_upgrades.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if powerups > read_var("powerups") or powerups < 0:
            await interaction.response.send_message("Error: This amount of powerups doesn't exist. Please retry.", ephemeral=True)
            return

        if common_upgrades > read_var("common_upgrades") or common_upgrades < 0:
            await interaction.response.send_message("Error: This amount of common powerups upgrades is invalid. Please retry.", ephemeral=True)
            return

        if rare_upgrades > read_var("rare_upgrades") or rare_upgrades < 0:
            await interaction.response.send_message("Error: Invalid amount of rare powerups upgrades. Please retry.", ephemeral=True)
            return
          
        if epic_upgrades > read_var("epic_upgrades") or epic_upgrades < 0:
            await interaction.response.send_message("Error: Invalid amount of epic powerups upgrades. Please retry.", ephemeral=True)
            return

        # Store user data
        update_data = {}
        if self.powerups.value:
            update_data["powerups"] = int(self.powerups.value)
        
        if self.common_upgrades.value:
            update_data["common_upgrades"] = int(self.common_upgrades.value)
        
        if self.rare_upgrades.value:
            update_data["rare_upgrades"] = int(self.rare_upgrades.value)
            
        if self.epic_upgrades.value:
            update_data["epic_upgrades"] = int(self.epic_upgrades.value)
            
        # Now insert or update only the provided fields
        db.insert_or_update_user(interaction.user.id, update_data)
        
        # Last calculations + storage
        db.insert_or_update_user(interaction.user.id, {"total_progression":db.fetch_value_by_column(interaction.user.id,"discord_id","new_progression"),"new_progression":0})
        
        # exp%
        level_exp = db.fetch_value_by_column(interaction.user.id,"discord_id","level_exp")
        exp = db.fetch_value_by_column(interaction.user.id,"discord_id","exp")
        total_exp = level_exp + exp
        exp_progression=(total_exp*100)/read_var("level20")
        
        # cars%
        total_cars = db.fetch_value_by_column(interaction.user.id, "discord_id", "cars")
        cars_progression=(total_cars*100)/read_var("cars")
        
        # cars_skins
        total_cars_skins = db.fetch_value_by_column(interaction.user.id, "discord_id", "cars_skins")
        cars_skins_progression=(total_cars_skins*100)/read_var("cars_skins")
        
        # drivers%
        total_drivers = db.fetch_value_by_column(interaction.user.id, "discord_id", "drivers")
        drivers_progression=(total_drivers*100)/read_var("drivers")
        
        # drivers_skins
        total_drivers_skins = db.fetch_value_by_column(interaction.user.id, "discord_id", "drivers_skins")
        drivers_skins_progression=(total_drivers_skins*100)/read_var("drivers_skins")
        
        # tracks
        tracks = db.fetch_value_by_column(interaction.user.id, "discord_id", "tracks")
        tracks_progression = (tracks*100)/read_var("tracks")
        
        # powerups
        powerups_progression = (int(self.powerups.value)*100)/read_var("powerups")
        
        # common_upgrades
        common_upgrades_progression = (int(self.common_upgrades.value)*100)/read_var("common_upgrades")
        
        # rare_upgrades
        rare_upgrades_progression = (int(self.rare_upgrades.value)*100)/read_var("rare_upgrades")
        
        # epic_upgrades
        epic_upgrades_progression = (int(self.epic_upgrades.value)*100)/read_var("epic_upgrades")
        
        # total progression
        total_progression=(exp_progression+cars_progression+cars_skins_progression+drivers_progression+drivers_skins_progression+tracks_progression+powerups_progression+common_upgrades_progression+rare_upgrades_progression+epic_upgrades_progression)/10
        
        # update database
        db.insert_or_update_user(interaction.user.id, {"exp_progression":exp_progression, "cars_progression":cars_progression,"cars_skins_progression":cars_skins_progression,"drivers_progression":drivers_progression,"drivers_skins_progression":drivers_skins_progression,"tracks_progression":tracks_progression,"powerups_progression":powerups_progression,"common_progression":common_upgrades_progression,"rare_progression":rare_upgrades_progression,"epic_progression":epic_upgrades_progression,"new_progression":total_progression})
        
        
        embed=discord.Embed(
          title="BBR2 Account Progression",
          description=("You finished answering our questions!\n"
          "Here are your sats:\n\n"
          f"BBR2 Username : {db.fetch_value_by_column(interaction.user.id, 'discord_id', 'bbr2_username')}\n"
          f"New Total Progression : {round(total_progression,1)}%\n"
          f"Old Total Progression : {round(db.fetch_value_by_column(interaction.user.id, 'discord_id', 'total_progression'),1)}%\n"
          f"EXP : {round(exp_progression,1)}%\n"
          f"Cars : {round(cars_progression,1)}%\n"
          f"Cars Gold Skins : {round(cars_skins_progression,1)}%\n"
          f"Drivers : {round(drivers_progression,1)}%\n"
          f"Drivers Outfits : {round(drivers_skins_progression,1)}%\n"
          f"Powerups Unlocked : {round(powerups_progression,1)}%\n"
          f"Common Powerups Upgrades : {round(common_upgrades_progression,1)}%\n"
          f"Rare Powerups Upgrades : {round(rare_upgrades_progression,1)}%\n"
          f"Epic Powerups Upgrades : {round(epic_upgrades_progression,1)}%\n"
          f"Tracks Unlocked : {round(tracks_progression,1)}%\n\n"
          "Enjoy!!!"),
          color=0x134fd3)
        slash_command()
        await interaction.response.edit_message(embed=embed, view=None)


class progression_embed_three(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    @discord.ui.button(label="Finish!", style=discord.ButtonStyle.primary)
    async def ready(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't use this button.", ephemeral=True)
            return
        await interaction.response.send_modal(ProgressionModal3())


class ProgressionModal2(discord.ui.Modal, title="Progression 2/3"):
    drivers = ui.TextInput(label="Drivers Owned", placeholder="e.g. 8",  required=False)
    drivers_skins = ui.TextInput(label="Drivers Skins Owned", placeholder="e.g. 16", required=False)
    tracks = ui.TextInput(label="Tracks Unlocked", placeholder="e.g. 25", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            drivers = int(self.drivers.value) if self.drivers.value else 0
            drivers_skins = int(self.drivers_skins.value) if self.drivers_skins.value else 0
            tracks = int(self.tracks.value) if self.tracks.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if drivers > read_var("drivers") or drivers < 0:
            await interaction.response.send_message("Error: This amount of drivers doesn't exist. Please retry.", ephemeral=True)
            return

        if drivers_skins > read_var("drivers_skins") or drivers_skins < 0:
            await interaction.response.send_message("Error: This amount of drivers outfits is invalid. Please retry.", ephemeral=True)
            return

        if tracks > read_var("tracks") or tracks < 0:
            await interaction.response.send_message("Error: Invalid amount of tracks. Please retry.", ephemeral=True)
            return

        # Automoderation
        if drivers_skins == read_var("drivers_skins"):
            embed = discord.Embed(
                title="Suspicious User Found",
                description=(
                    f"A user has assumed owning Cassette Bot - User information review needed\n"
                    f"User: <@{interaction.user.id}> ({interaction.user.id})\n"
                    f"BBR2 Username: {db.fetch_column_by_value("discord_id", interaction.discord.id, "bbr2_username")}\n"
                    f"Server: {interaction.guild.name}\n"
                    f"Channel: <#{interaction.channel.id}>\n"
                    f"Date: <t:{int(interaction.created_at.timestamp())}:d> <t:{int(interaction.created_at.timestamp())}:T>"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="Remember these informations can be incorrect as filled by the users themselves")

            channel = bot.get_channel(automod_channel_id)
            if channel:
                await channel.send(embed=embed)
            else:
                now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
                db.log(f"Message couldn't be sent to automod channel on {now} UTC")

        # Store user data
        update_data = {}
        if self.drivers.value:
            update_data["drivers"] = int(self.drivers.value)
        
        if self.drivers_skins.value:
            update_data["drivers_skins"] = int(self.drivers_skins.value)
        
        if self.tracks.value:
            update_data["tracks"] = int(self.tracks.value)
        # Now insert or update only the provided fields
        db.insert_or_update_user(interaction.user.id, update_data)

        
        embed=discord.Embed(
          title="BBR2 Account Progression",
          description=("Almost there!\n\nFinish the last row of questions now!"),
          color=0x134fd3
        )
        await interaction.response.edit_message(embed=embed, view=progression_embed_three(interaction.user.id))


class progression_embed_two(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def ready(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't use this button.", ephemeral=True)
            return
        await interaction.response.send_modal(ProgressionModal2())


class ProgressionModal1(discord.ui.Modal, title="Progression 1/3"):
    bbr2_username = ui.TextInput(label="BBR2 Username", placeholder="e.g. VectorMatt", min_length=3, max_length=15, required=True)
    level = ui.TextInput(label="Current Level", placeholder="e.g. 16", required=False)
    exp = ui.TextInput(label="Current Amount of EXP", placeholder="e.g. 160542", required=False)
    cars = ui.TextInput(label="Cars Owned", placeholder="e.g. 45", required=False)
    cars_skins = ui.TextInput(label="Cars Gold Skins Owned", placeholder="e.g. 34", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(self.level.value) if self.level.value else 0
            exp = int(self.exp.value) if self.exp.value else 0
            cars = int(self.cars.value) if self.cars.value else 0
            cars_skins = int(self.cars_skins.value) if self.cars_skins.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if level > read_var("level") or level < 0:
            await interaction.response.send_message("Error: This level doesn't exist. Please retry.", ephemeral=True)
            return

        if exp > read_var(f"level{level + 1}") - read_var(f"level{level}") or exp < 0:
            await interaction.response.send_message("Error: This EXP amount is invalid. Please retry.", ephemeral=True)
            return

        if cars > read_var("cars") or cars < 0:
            await interaction.response.send_message("Error: Invalid number of cars. Please retry.", ephemeral=True)
            return

        if cars_skins > read_var("cars_skins") or cars_skins < 0:
            await interaction.response.send_message("Error: Invalid number of gold skins. Please retry.", ephemeral=True)
            return

        # Automoderation
        if cars == read_var("cars"):
            embed = discord.Embed(
                title="Suspicious User Found",
                description=(
                    f"A user has assumed being level 20 - User information review needed\n"
                    f"User: <@{interaction.user.id}> ({interaction.user.id})\n"
                    f"BBR2 Username: {self.bbr2_username.value}\n"
                    f"Server: {interaction.guild.name}\n"
                    f"Channel: <#{interaction.channel.id}>\n"
                    f"Date: <t:{int(interaction.created_at.timestamp())}:d> <t:{int(interaction.created_at.timestamp())}:T>"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="Remember these informations can be incorrect as filled by the users themselves")

            channel = bot.get_channel(automod_channel_id)
            if channel:
                await channel.send(embed=embed)
            else:
                now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
                db.log(f"Message couldn't be sent to automod channel on {now} UTC")

        # Store user data
        update_data = {"bbr2_username": self.bbr2_username.value}  # required field
        
        if self.level.value:
            update_data["level"] = int(self.level.value)
            update_data["level_exp"] = read_var(f"level{int(self.level.value)}")
        
        if self.exp.value:
            update_data["exp"] = int(self.exp.value)
        
        if self.cars.value:
            update_data["cars"] = int(self.cars.value)
        
        if self.cars_skins.value:
            update_data["cars_skins"] = int(self.cars_skins.value)
        
        # Now insert or update only the provided fields
        db.insert_or_update_user(interaction.user.id, update_data)

        
        embed=discord.Embed(
          title="BBR2 Account Progression",
          description=("Your data is being stored in the database!\n\nClick below to continue!"),
          color=0x134fd3
        )
        await interaction.response.edit_message(embed=embed, view=progression_embed_two(interaction.user.id))


class progression_embed_one(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    @discord.ui.button(label="Ready?", style=discord.ButtonStyle.primary)
    async def ready(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't use this button.", ephemeral=True)
            return
        await interaction.response.send_modal(ProgressionModal1())


@bot.tree.command(name="progression", description="Calculate your BBR2 progression")
async def progression(interaction: discord.Interaction):
  if interaction.user.id in slash_commands_blacklist:
    await interaction.response.send_message("Due to previous bad behavior, you are not allowed to use this bot anymore", ephemeral=True)
    return
  if read_var("maintenance"):
    await interaction.response.send_message("The database/bot is under maintenance. This command is disabled until the end of the maintenance", ephemeral=True)
  else:
    embed = discord.Embed(
        title="BBR2 Account Progression",
        description=(
            f"Calculate your total progression in Beach Buggy Racing 2\n"
            f"Answer the following question using the STATS section of the game.\n"
            f"## Please use your real informations, as they are used in leaderboards\n"
            f"First time trying? Use /help first!\n"
            f"Actually, accuracy cannot reach 100%\n"
            f"Matching BBR2 V{read_var('version')}"
        ),
        color=0x134fd3
    )
    await interaction.response.send_message(embed=embed, view=progression_embed_one(interaction.user.id))

# /SEARCH-USER ----------------------------

@bot.tree.command(name="search-user", description="Search a user's stats")
@app_commands.describe(
    user="Discord user",
    bbr2="BBR2 username"
)
async def search_user(interaction: discord.Interaction, user: discord.User = None, bbr2: str = None):
    if interaction.user.id in slash_commands_blacklist:
    await interaction.response.send_message("Due to previous bad behavior, you are not allowed to use this bot anymore", ephemeral=True)
    return
    if user is None and bbr2 is None:
        await interaction.response.send_message("Please answer at least one of the fields", ephemeral=True)
        return

    if user is not None:
        if db.check_if_exists("discord_id", user.id):
            embed = discord.Embed(
                title=f"{user.mention} stats | {db.fetch_value_by_column(user.id, 'discord_id', 'bbr2_username')}",
                description=(
                    f"Progression : {round(db.fetch_value_by_column(user.id, 'discord_id', 'new_progression'),1)}%\n\n"
                    f"Level : {db.fetch_value_by_column(user.id, 'discord_id', 'level')}/{read_var('level')}\n"
                    f"Current EXP : {db.fetch_value_by_column(user.id, 'discord_id', 'exp')}\n\n"
                    f"Cars : {db.fetch_value_by_column(user.id, 'discord_id', 'cars')}/{read_var('cars')}\n"
                    f"Cars Gold Skins : {db.fetch_value_by_column(user.id, 'discord_id', 'cars_skins')}/{read_var('cars_skins')}\n"
                    f"Drivers : {db.fetch_value_by_column(user.id, 'discord_id', 'drivers')}/{read_var('drivers')}\n"
                    f"Drivers Outfits : {db.fetch_value_by_column(user.id, 'discord_id', 'drivers_skins')}/{read_var('drivers_skins')}\n\n"
                    f"Powerups : {db.fetch_value_by_column(user.id, 'discord_id', 'powerups')}/{read_var('powerups')}\n"
                    f"- Common Upgrades : {db.fetch_value_by_column(user.id, 'discord_id', 'common_upgrades')}/{read_var('common_upgrades')}\n"
                    f"- Rare Upgrades : {db.fetch_value_by_column(user.id, 'discord_id', 'rare_upgrades')}/{read_var('rare_upgrades')}\n"
                    f"- Epic Upgrades : {db.fetch_value_by_column(user.id, 'discord_id', 'epic_upgrades')}/{read_var('epic_upgrades')}\n\n"
                    f"Tracks : {db.fetch_value_by_column(user.id, 'discord_id', 'tracks')}/{read_var('tracks')}\n\n"
                    f"Races Played : {db.fetch_value_by_column(user.id, 'discord_id', 'races_total')}\n"
                    f"Races Won : {db.fetch_value_by_column(user.id, 'discord_id', 'races_win')}\n"
                    f"Races Win Percentage : {round(db.fetch_value_by_column(user.id, 'discord_id', 'races_win_percentage'),1)}%\n\n"
                    f"Tournaments Played : {db.fetch_value_by_column(user.id, 'discord_id', 'tournaments_total')}\n"
                    f"Tournaments Won : {db.fetch_value_by_column(user.id, 'discord_id', 'tournaments_win')}\n"
                    f"Tournaments Win Percentage : {round(db.fetch_value_by_column(user.id, 'discord_id', 'tournaments_win_percentage'),1)}%\n\n"
                    f"Total Time Driven : {db.fetch_value_by_column(user.id, 'discord_id', 'total_time_driven')} hours\n"
                    f"Total Distance Driven : {db.fetch_value_by_column(user.id, 'discord_id', 'total_distance_driven')} kilometers\n"
                    f"Average Speed : {round(db.fetch_value_by_column(user.id, 'discord_id', 'average_speed'),1)} kms/h"
                ),
                color=0x134fd3
            )
            raw_timestamp = db.fetch_value_by_column(user.id, 'discord_id', 'row_updated')
            formatted_timestamp = datetime.fromisoformat(raw_timestamp).strftime("%B %d, %Y at %H:%M UTC")
            embed.set_footer(text=f"User last updated on {formatted_timestamp}")
            slash_command()
            await interaction.response.send_message(embed=embed)
            return
        else:
          await interaction.response.send_message("This user did not used the /progression command yet", ephemeral=True)

    elif bbr2 is not None:
        if db.check_if_exists("bbr2_username", bbr2):
            embed = discord.Embed(
                title=f"<@{db.fetch_value_by_column(bbr2, 'bbr2_username', 'discord_id')}> stats | {bbr2}",
                description=(
                    f"Progression : {round(db.fetch_value_by_column(bbr2, 'bbr2_username', 'new_progression'),1)}%\n\n"
                    f"Level : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'level')}/{read_var('level')}\n"
                    f"Current EXP : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'exp')}\n\n"
                    f"Cars : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'cars')}/{read_var('cars')}\n"
                    f"Cars Gold Skins : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'cars_skins')}/{read_var('cars_skins')}\n"
                    f"Drivers : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'drivers')}/{read_var('drivers')}\n"
                    f"Drivers Outfits : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'drivers_skins')}/{read_var('drivers_skins')}\n\n"
                    f"Powerups : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'powerups')}/{read_var('powerups')}\n"
                    f"- Common Upgrades : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'common_upgrades')}/{read_var('common_upgrades')}\n"
                    f"- Rare Upgrades : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'rare_upgrades')}/{read_var('rare_upgrades')}\n"
                    f"- Epic Upgrades : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'epic_upgrades')}/{read_var('epic_upgrades')}\n\n"
                    f"Tracks : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'tracks')}/{read_var('tracks')}\n\n"
                    f"Races Played : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'races_total')}\n"
                    f"Races Won : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'races_win')}\n"
                    f"Races Win Percentage : {round(db.fetch_value_by_column(bbr2, 'bbr2_username', 'races_win_percentage'),1)}%\n\n"
                    f"Tournaments Played : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'tournaments_total')}\n"
                    f"Tournaments Won : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'tournaments_win')}\n"
                    f"Tournaments Win Percentage : {round(db.fetch_value_by_column(bbr2, 'bbr2_username', 'tournaments_win_percentage'),1)}%\n\n"
                    f"Total Time Driven : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'total_time_driven')} hours\n"
                    f"Total Distance Driven : {db.fetch_value_by_column(bbr2, 'bbr2_username', 'total_distance_driven')} kilometers\n"
                    f"Average Speed : {round(db.fetch_value_by_column(bbr2, 'bbr2_username', 'average_speed'),1)} kms/h"
                ),
                color=0x134fd3
            )
            raw_timestamp = db.fetch_value_by_column(bbr2, 'bbr2_username', 'row_updated')
            formatted_timestamp = datetime.fromisoformat(raw_timestamp).strftime("%B %d, %Y at %H:%M UTC")
            embed.set_footer(text=f"User last updated on {formatted_timestamp}")
            slash_command()
            await interaction.response.send_message(embed=embed)
            return
        else:
          await interaction.response.send_message("This BBR2 username is not referenced in the database. Make you sure you entered it correctly", ephemeral=True)
          return

# /CALCULATE ------------------------------
class ModalRacesWin(discord.ui.Modal, title="Races win %"):
    total_races = ui.TextInput(label="Total Races Played", placeholder="e.g. 57", required=True)
    total_races_win = ui.TextInput(label="Total Races Win", placeholder="e.g. 16", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            total_races = int(self.total_races.value) if self.total_races.value else 0
            total_races_win = int(self.total_races_win.value) if self.total_races_win.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if total_races < 0 or total_races_win < 0:
            await interaction.response.send_message("Error: Value cannot be less than 0.", ephemeral=True)
            return
        if total_races_win > total_races:
          await interaction.response.send_message("Error: Races win can't be higher than races")


        # Store user data
        races_win_percentage = (total_races_win*100/total_races)

        db.insert_or_update_user(interaction.user.id, {"races_total": total_races, "races_win": total_races_win, "races_win_percentage": races_win_percentage})

        
        embed=discord.Embed(
          title="Races Win Percentage",
          description=(f"Races win percentage : {round(races_win_percentage,3)}%\n\n"
          f"Races played : {total_races}\n"
          f"Races win : {total_races_win}"
          ),
          color=0x134fd3
        )
        slash_command()
        await interaction.response.send_message(embed=embed)

class ModalTournamentsWin(discord.ui.Modal, title="Tournaments win %"):
    total_tournaments = ui.TextInput(label="Total Tournaments Played", placeholder="e.g. 57", required=True)
    total_tournaments_win = ui.TextInput(label="Total Tournaments Win", placeholder="e.g. 16", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            total_tournaments = int(self.total_tournaments.value) if self.total_tournaments.value else 0
            total_tournaments_win = int(self.total_tournaments_win.value) if self.total_tournaments_win.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if total_tournaments < 0 or total_tournaments_win < 0:
            await interaction.response.send_message("Error: Value cannot be less than 0.", ephemeral=True)
            return
        if total_tournaments_win > total_tournaments:
          await interaction.response.send_message("Error: Tournaments win can't be higher than tournaments")


        # Store user data
        tournaments_win_percentage = (total_tournaments_win*100/total_tournaments)

        db.insert_or_update_user(interaction.user.id, {"tournaments_total": total_tournaments, "tournaments_win": total_tournaments_win, "tournaments_win_percentage": tournaments_win_percentage})

        
        embed=discord.Embed(
          title="Tournaments Win Percentage",
          description=(f"Tournaments win percentage : {round(tournaments_win_percentage,3)}%\n\n"
          f"Tournamentss played : {total_tournaments}\n"
          f"Tournaments win : {total_tournaments_win}"
          ),
          color=0x134fd3
        )
        slash_command()
        await interaction.response.send_message(embed=embed)

class ModalAverageSpeed(discord.ui.Modal, title="Average Speed"):
    total_time = ui.TextInput(label="Total Time Driven (in hours)", placeholder="e.g. 57", required=True)
    total_distance = ui.TextInput(label="Total Distance Driven (in kms)", placeholder="e.g. 160", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            total_time = int(self.total_time.value) if self.total_time.value else 0
            total_distance = int(self.total_distance.value) if self.total_distance.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if total_distance < 0 or total_time < 0:
            await interaction.response.send_message("Error: Value cannot be less than 0.", ephemeral=True)
            return

        # Store user data
        average_speed = total_distance/total_time

        db.insert_or_update_user(interaction.user.id, {"total_time_driven": total_time, "total_distance_driven": total_distance, "average_speed": average_speed})

        
        embed=discord.Embed(
          title="Average Speed",
          description=(f"Average Speed : {round(average_speed,3)} km/h\n\n"
          f"Time driven: {total_time} hours\n"
          f"Distance driven : {total_distance} kilometers"
          ),
          color=0x134fd3
        )
        slash_command()
        await interaction.response.send_message(embed=embed)

class ModalLevelUp(discord.ui.Modal, title="Level Up"):
    level = ui.TextInput(label="Your Level", placeholder="e.g. 16", required=True)
    exp = ui.TextInput(label="Your Current EXP", placeholder="e.g. 1601985", required=True)
    exp_a_day = ui.TextInput(label="Average EXP Earned in One Day", placeholder="e.g. 2400", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(self.level.value) if self.level.value else 0
            exp = int(self.exp.value) if self.exp.value else 0
            exp_a_day = int(self.exp_a_day.value) if self.exp.value else 0
        except ValueError:
            await interaction.response.send_message("Please make sure all number fields contain only numbers.", ephemeral=True)
            return

        # Validation
        if level < 0 or exp < 0 or exp_a_day < 0:
            await interaction.response.send_message("Error: Value cannot be less than 0.", ephemeral=True)
            return
        if level > read_var("level"):
          await interaction.response.send_message("Error: This level dont exist", ephemeral=True)
        if exp > read_var(f"level{level + 1}") - read_var(f"level{level}"):
            await interaction.response.send_message("Error: This EXP amount is invalid", ephemeral=True)
            return

        exp_needed_next_level=read_var(f"level{level+1}")-(exp+read_var(f"level{level}"))
        time_next_level=exp_needed_next_level/exp_a_day
        
        exp_needed_max_level=read_var(f"level{read_var("level")}")-(exp+read_var(f"level{level}"))
        time_max_level=exp_needed_max_level/exp_a_day

        
        embed=discord.Embed(
          title="Time to Level Up",
          description=(f"You will need about:\n"
          f"- {round(time_next_level,1)} day(s) to reach level {level+1}\n"
          f"- {round(time_max_level,1)} day(s) to reach level {read_var('level')}\n\n"
          f"EXP left for level {level+1} : {exp_needed_next_level}\n"
          f"EXP left for level {read_var("level")} : {exp_needed_max_level}\n"
          f"EXP earned in one day : {exp_a_day}"
          
          ),
          color=0x134fd3
        )
        slash_command()
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="calculate", description="Calculate some stuff")
@app_commands.choices(stuff=[
  app_commands.Choice(name="Races win %", value="Races win %"),
  app_commands.Choice(name="Tournaments win %", value="Tournaments win %"),
  app_commands.Choice(name="Average speed", value="Average speed"),
  app_commands.Choice(name="Level up", value="Level up")
  ])
@app_commands.describe(stuff="What do you want to calculate")
async def calculate(interaction: discord.Interaction, stuff: str):
  if interaction.user.id in slash_commands_blacklist:
    await interaction.response.send_message("Due to previous bad behavior, you are not allowed to use this bot anymore", ephemeral=True)
    return
  if stuff == "Races win %":
    await interaction.response.send_modal(ModalRacesWin())
  elif stuff == "Tournaments win %":
    await interaction.response.send_modal(ModalTournamentsWin())
  elif stuff == "Average speed":
    await interaction.response.send_modal(ModalAverageSpeed())
  elif stuff == "Level up":
    await interaction.response.send_modal(ModalLevelUp())

# /LEADERBOARD ----------------------------

@bot.tree.command(name="leaderboard", description="View leaderboards")
@app_commands.choices(lb_type=[
    app_commands.Choice(name="Progression", value="Progression"),
    app_commands.Choice(name="EXP", value="EXP"),
    app_commands.Choice(name="Races win %", value="Races win %"),
    app_commands.Choice(name="Tournaments win %", value="Tournaments win %"),
    app_commands.Choice(name="Average speed", value="Average Speed"),
    app_commands.Choice(name="Most time played", value="Most time played"),
    app_commands.Choice(name="Most races played", value="Most races played"),
    app_commands.Choice(name="Most tournaments played", value="Most tournaments played")
])
@app_commands.describe(
    lb_type="Leaderboard type"
)
async def leaderboard(interaction: discord.Interaction, lb_type: str):
  medals = ["🥇", "🥈", "🥉"]
  length_lb_max = 10
  if interaction.user.id in slash_commands_blacklist:
    await interaction.response.send_message("Due to previous bad behavior, you are not allowed to use this bot anymore", ephemeral=True)
    return
  
  if lb_type == "Progression" :
    leaderboard_data = db.fetch_leaderboard("new_progression", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Progression** : {round(value,3)} %\n\n"
        )

    embed = discord.Embed(
        title="🏆 Progression Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    await interaction.response.send_message(embed=embed)
  
  elif lb_type == "EXP" :
    # Fetch leaderboard sorted by level and then exp
    leaderboard_data = db.fetch_leaderboard_by_columns(["level", "exp"], limit=length_lb_max)
    
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return
    
    leaderboard_text = ""
    
    for index, (discord_id, level, exp) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"
    
        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")
    
        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Level** : {level} **| EXP** : {exp}\n\n"
        )
    
    embed = discord.Embed(
        title="🏆 Level & EXP Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)


  elif lb_type == "Races win %" :
    leaderboard_data = db.fetch_leaderboard("races_win_percentage", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Races win** : {round(value,3)} %\n\n"
        )

    embed = discord.Embed(
        title="🏆 Races Win Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)

  elif lb_type == "Tournaments win %" :
    leaderboard_data = db.fetch_leaderboard("tournaments_win_percentage", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Tournaments win** : {round(value,3)} %\n\n"
        )

    embed = discord.Embed(
        title="🏆 Tournaments win Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)

  elif lb_type == "Average speed" :
    leaderboard_data = db.fetch_leaderboard("average_speed", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Average speed** : {round(value,3)} km/h\n\n"
        )

    embed = discord.Embed(
        title="🏆 Average Speed Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)

  elif lb_type == "Most time played" :
    leaderboard_data = db.fetch_leaderboard("total_time_driven", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Time played** : {value} hours\n\n"
        )

    embed = discord.Embed(
        title="🏆 Time Played Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)

  elif lb_type == "Most races played" :
    leaderboard_data = db.fetch_leaderboard("races_total", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Races played** : {value}\n\n"
        )

    embed = discord.Embed(
        title="🏆 Most Races Played Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)

  elif lb_type == "Most tournaments played" :
    leaderboard_data = db.fetch_leaderboard("tournaments_total", limit=length_lb_max)  # or your column name
    if not leaderboard_data:
        await interaction.response.send_message("No data available.", ephemeral=True)
        return

    leaderboard_text = ""

    for index, (discord_id, value) in enumerate(leaderboard_data):
        # Medal or number
        prefix = medals[index] if index < len(medals) else f"{index+1}️⃣"

        # Fetch BBR2 username
        bbr2_username = db.fetch_value_by_column(discord_id, "discord_id", "bbr2_username")

        leaderboard_text += (
            f"{prefix} **— <@{discord_id}> | {bbr2_username}**\n"
            f"**Tournaments played** : {value}\n\n"
        )

    embed = discord.Embed(
        title="🏆 Most Tournaments Played Leaderboard",
        description=leaderboard_text,
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)



# /DELETE-DATA ----------------------------

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
    slash_command()
    await interaction.response.edit_message(embed=embed, view=None)
    db.log(f"{interaction.user.id} requested a data deletion")


@bot.tree.command(name="delete-data", description="Delete your user data from the database")
async def deletedata(interaction: discord.Interaction):
  embed = discord.Embed(
    title="Delete Data",
    description=("# You're about to delete your data from the bot database\n# Are you really sure you want to do this?"),
    color=discord.Color.red()
  )
  button=delete_data_button()
  await interaction.response.send_message(embed=embed, view=button, ephemeral=True)

# /FUN ------------------------------------

@bot.tree.command(name="fun", description="Get fun stats")
async def fun(interaction: discord.Interaction):
    if interaction.user.id in slash_commands_blacklist:
      await interaction.response.send_message("Due to previous bad behavior, you are not allowed to use this bot anymore", ephemeral=True)
      return
    # total exp = level_exp + exp
    level_exp_list, count = db.fetch_column_values("level_exp")
    exp_list, _ = db.fetch_column_values("exp")
    total_exp = sum(level_exp_list) + sum(exp_list)

    # total time driven
    time_list, _ = db.fetch_column_values("total_time_driven")
    total_time = sum(time_list)

    # total distance driven
    distance_list, _ = db.fetch_column_values("total_distance_driven")
    total_distance = sum(distance_list)

    # average progression
    progression_list, _ = db.fetch_column_values("new_progression")
    average_progression = sum(progression_list) / count if count else 0

    # average level
    level_list, _ = db.fetch_column_values("level")
    average_level = sum(level_list) / count if count else 0

    # average speed
    speed_list, _ = db.fetch_column_values("average_speed")
    average_speed = sum(speed_list) / count if count else 0

    # time now
    now = datetime.now(timezone.utc)
    formatted_time = now.strftime("%d/%m/%Y %H:%M")

    # create embed
    embed = discord.Embed(
        title="Fun Stats",
        description=(
            f"Users in database: {count}\n"
            f"Slash commands executed: {read_var('slash_commands_amount')+1}\n"
            f"Total EXP earned: {total_exp:,}\n"
            f"Total time driven: {total_time} hours\n"
            f"Total distance driven: {total_distance} km\n"
            f"Average progression: {average_progression:.2f}%\n"
            f"Average level: {average_level:.2f}\n"
            f"Average speed: {average_speed:.2f} km/h\n\n"
            f"Last updated on {formatted_time} UTC"
        ),
        color=0x134fd3
    )
    slash_command()
    await interaction.response.send_message(embed=embed)

# /HELP -----------------------------------

# Sample help pages
help_pages = [
    discord.Embed(title="General",
    description=(f"- Please use your REAL account informations. Using fake informations may mess up with the database and fake all the values of the leaderboards\n- - If you want to calculate progress with fake informations, please do not refer a Beach Buggy Racing 2 username\n- - When calculating progress, if you input a BBR2 username, all previous data associated to your discord account will be overwritten (e.g. BBR2 username, progressions stats, etc). This is the normal behavior, you shouldn't worry about it\n- <@1006897949822959696> keeps the rights to edit/delete any entries suspected to be fake\n- If you have any question, doubt or want to report a suspicious entrie, feel free to ping/DM <@1006897949822959696>\n- Bad use of the bot may result in a ban of using its features\n- Every data that you enter in the bot can be accessed by any discord user using this bot. If you don't to share something, leave the field blank\n- Changed Discord account? Want to erase your data from the bot? DM <@1006897949822959696> or <@575252669443211264> (if on VU server)\n- Based on BBR2 V{read_var('version')}"),
    color=0x134fd3),
    discord.Embed(title="Help",
    description="Available commands:\n- /help : Get help with the bot\n- /fun : See fun stats from database\n- /progression : Calculate you BBR2 progression\n- /search-user-stats : Check an user's stats using his Discord/BBR2 username\n- /leaderboard : Show leaderboard",
    color=0x134fd3),
    discord.Embed(title="Informations",
    description=f"Currently on {read_var('servers_joined')}\nLatency : {bot.latency * 1000} ms\nCurrently storing {read_var('users_in_database')} users informations\nCreated by <@1006897949822959696>\nProfile picture & banner by <@637366800128016384> ",
    color=0x134fd3),
    discord.Embed(title="Roadmap",
    description="Soon™\n- Log user data so they can access their old progress results without needing to redo all the process\n- User data update\n- Find progression data by BBR2/Discord username\n- Total Progression/WinLoss Ratio/Average Speed leaderboards\n\nCertainly never\n- Access BBR2 account data by referencing username (Can't do unless Matt provides a working API for this) ",
    color=0x134fd3),
]

class HelpView(discord.ui.View):
    def __init__(self, user_id: int, page=0):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.page = page
        self.total_pages = len(help_pages)
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()

        self.prev_button = discord.ui.Button(label="≪ Previous", style=discord.ButtonStyle.primary, disabled=(self.page == 0))
        self.prev_button.callback = self.prev_button_callback
        self.add_item(self.prev_button)

        page_button = discord.ui.Button(label=f"{self.page + 1}/{self.total_pages}", style=discord.ButtonStyle.secondary, disabled=True)
        self.add_item(page_button)

        self.next_button = discord.ui.Button(label="Next ≫", style=discord.ButtonStyle.primary, disabled=(self.page == self.total_pages - 1))
        self.next_button.callback = self.next_button_callback
        self.add_item(self.next_button)

    async def prev_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this help menu.", ephemeral=True)
            return

        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=help_pages[self.page], view=self)

    async def next_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't interact with this help menu.", ephemeral=True)
            return

        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=help_pages[self.page], view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


@bot.tree.command(name="help", description="Get help with the bot")
async def help_command(interaction: discord.Interaction):
    slash_command()
    view = HelpView(interaction.user.id)
    await interaction.response.send_message(embed=help_pages[0], view=view)
    view.message = await interaction.original_response()

# /DATABASE-MANAGEMENT --------------------
# (Owner only)

@bot.tree.command(name="database-management", description="Admin Only")
@app_commands.choices(delete_row=[
    app_commands.Choice(name="Yes", value="yes"),
    app_commands.Choice(name="No", value="no")
])
@app_commands.describe(
    discord_id="ID of the user to modify",
    column="Ask Blue for columns list",
    value="New value",
    delete_row="Delete user's row?"
)
async def database_management(
    interaction: discord.Interaction,
    discord_id: str,
    column: str = None,
    value: str = None,
    delete_row: str = "no"
):
    if interaction.user.id not in slash_commands_allowed_users:
        await interaction.response.send_message("You are not allowed to run this command", ephemeral=True)
        return

    delete_flag = True if delete_row == "yes" else False

    result = db.admin_database_management(discord_id, column, value, delete_flag)
    if result is True:
        await interaction.response.send_message("Action done successfully", ephemeral=True)
        db.log(f"Action executed on row by {interaction.user.id}\nRow : {discord_id}\nColumn : {column}\nValue : {value}\nDelete row : {delete_flag}")
    elif result == "Invalid column":
        await interaction.response.send_message("Invalid column", ephemeral=True)
    else:
        await interaction.response.send_message("Action couldn't be completed. Check logs", ephemeral=True)


# /STATUS-CHANGER -------------------------
# (Owner only)

@bot.tree.command(name="status-changer", description="Changes the bot status")
@app_commands.choices(activity=[
    app_commands.Choice(name="Playing", value="Playing"),
    app_commands.Choice(name="Streaming", value="Streaming"),
    app_commands.Choice(name="Listening", value="Listening"),
    app_commands.Choice(name="Watching", value="Watching"),
    app_commands.Choice(name="Maintenance", value="Maintenance"),
    app_commands.Choice(name="Reset", value="Reset")
])
@app_commands.describe(
    activity="Activity type",
    text="Status text"
)
@app_commands.check(is_owner)
async def owner_command(interaction: discord.Interaction, activity: str, text: str = None):
    if activity == "Playing":
        await bot.change_presence(activity=discord.Game(name=text))

    elif activity == "Streaming":
        await bot.change_presence(activity=discord.Streaming(name=text, url="https://discord.gg/vectorunit"))

    elif activity == "Listening":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))

    elif activity == "Watching":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
        
    elif activity == "Maintenance":
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="under maintenance"))
      update_config("maintenance", True)
    
    if activity != "Reset":
      update_config("overdrive_status", True)
    else:
      await bot.change_presence(activity=discord.Game(name="Beach Buggy Racing 2"))
      update_config("overdrive_status", False)
      update_config("maintenance", False)
    
    await interaction.response.send_message("Status set ✅", ephemeral=True)
    db.log(f"Status changed by {interaction.user.id}\nNew status : {activity} {text}")

@owner_command.error
async def owner_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

# /EXPORT-DATABASE ------------------------

@bot.tree.command(name="export-database", description="Admin Only")
async def export_database(interaction: discord.Interaction):
    if interaction.user.id in slash_commands_allowed_users :
      csv_path = "users_export.csv"
      success = db.export_database_to_csv(csv_path)
  
      if success and os.path.exists(csv_path):
          file = discord.File(csv_path)
          await interaction.response.send_message("Here is the exported database:", file=file, ephemeral=True)
          db.log(f"Database successfully exported by {interaction.user.id}")
          os.remove(csv_path)  # Clean up after sending
      else:
          await interaction.response.send_message("Failed to export the database.", ephemeral=True)
          db.log("Failed to export database")
    else: 
      await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
      return


# RUN BOT ---------------------------------

bot.run(bot_token)