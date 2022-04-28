import discord
import os
import gspread
#from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from replit import db

## GSHEETS ##
# validate api credentials
gc = gspread.service_account(filename='testnet-rewards-service-key.json')

# access the testnet rewards gsheet
testnet_rewards_sheet_id = "" # found in URL of gsheet
gsheet_file = gc.open_by_key(testnet_rewards_sheet_id)
testnet_rewards_sheet = gsheet_file.get_worksheet(0) # pulls first sheet tab in file

# extract gsheets data into a df
rewards_values = testnet_rewards_sheet.get_all_values()
testnet_rewards_df = pd.DataFrame(rewards_values[1:],columns=rewards_values[0]) # values index of 0 is the column name # *** validate there is a column header in gsheets

# extract df data into db to keep data stored instead of repulling from gsheets
testnet_rewards = {}
for row in testnet_rewards_df.iterrows():
  user = row['Discord Name'].lower() #*** validate this is the right column name
  user_rewards = row['Rewards'] #*** validate this is the right column name
  testnet_rewards[user] = user_rewards
  #db[user] = user_rewards
  
# check if dictionary storage is valid before storing in db
# for user, rewards in testnet_rewards.items():
#   print(user, rewards)

# check if db storage is valid
for user in db.keys():
  print(user, db[user])

## DISCORD ##
# setup discord api client
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# command variable users will use
rewards_cmd = "!testnet-rewards"
# testnet rewards channel id
channel_id = "" #*** pull channel id from discord once created (ensure bot has access)

# quai server id (also referred to as a guild)
# quai_guild_id = 887783279053406238

@client.event
async def on_ready():
  print("*logged in as testnet rewards bot*")

@client.event
async def on_message(message):
  print(message)
  if message.channel.id == channel_id:
    print("checking message...")
    if message.author == client.user: # don't check if the message is from the bot
      return
    testnet_rewards_channel = client.get_channel(channel_id)
    if message.content.startswith(rewards_cmd):
      print(f"({message.author.name}#{message.author.discriminator}) requested rewards")
      nickname = message.author.name.lower()
      user = f"{nickname}#{message.author.discriminator}"
      if user in testnet_rewards.keys():
        user_rewards = testnet_rewards[user]
        embed = discord.Embed(title='Testnet Rewards', colour=discord.Colour.blue())
        message_content = "Rewards: {}".format(user_rewards)
        embed.add_field(name=user, value=message_content, inline=False)
        await testnet_rewards_channel.send(embed=embed)
        if user_rewards == 0:
          await testnet_rewards_channel.send(f"{message.author.mention} it doesn't look like you were active last testnet. Try to participate in our upcoming testnet to earn $QUAI!")
        print(f"{user} was sent their rewards")
      else:
        db[user] = 0
        embed = discord.Embed(title='Testnet Rewards', colour=discord.Colour.blue())
        message_content = "Rewards: {}".format(user_rewards)
        embed.add_field(name=user, value=message_content, inline=False)
        await testnet_rewards_channel.send(embed=embed)
        await testnet_rewards_channel.send(f"{message.author.mention} it doesn't look like you were active last testnet. Try to participate in our upcoming testnet to earn $QUAI!")
        print(f"{user} was sent their rewards")

client.run(os.environ['TOKEN'])
