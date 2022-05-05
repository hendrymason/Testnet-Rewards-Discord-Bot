import discord # for accessing discord api
import os # for accessing secret environment tokens to hide from public view
import gspread # for gsheets access
#from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd # pandas for simple dataframe usage from gsheets
from replit import db # for basic storage into db within replit


### GSHEETS ###
# converted into a function for per use case basis (only necessary when updating user data in db or adding new user data to db)
def import_gsheets_data():
  # validate api credentials
  gc = gspread.service_account(filename='testnet-rewards-service-key.json')
  
  # access the testnet rewards gsheet
  testnet_rewards_sheet_id = "1L7t5OIwRMlZvxBnTyJBYmgEiJfOOZMB2I_UkYwyMrtc" # found in URL of gsheet
  gsheet_file = gc.open_by_key(testnet_rewards_sheet_id)
  testnet_rewards_sheet = gsheet_file.get_worksheet(0) # pulls first sheet tab in file
  
  # extract gsheets data into a df
  rewards_values = testnet_rewards_sheet.get_all_values()
  testnet_rewards_df = pd.DataFrame(rewards_values[1:],columns=rewards_values[0]) # values index of 0 is the column name
  
  # extract df data into db to keep data stored instead of repulling from gsheets
  for index, row in testnet_rewards_df.iterrows():
    user = row["Discord Usernames"].lower() #*** validate this is the right column name
    user_rewards = row["Reward Amount"]
    if user_rewards != '':
      user_rewards = int(user_rewards) #*** validate this is the right column name
    db[user] = user_rewards

### Test check if db storage is valid and contains users
def check_db_storage():
  for user in db.keys():
    print(user, db[user])

### Test function for locating specific user data
def check_user_rewards(user):
  if user in db.keys():
    print(" -- FOUND USER -- ")
    print(user + ": " + str(db[user]))


### DISCORD BOT SCRIPT ###
# setup discord api client with permission intents
intents = discord.Intents.default()
intents.messages = True # allows message permissions (if not already set in api app)
intents.members = True # allows mentioning of users and access to their user data (if not already set in api app)
client = discord.Client(intents=intents)

# command variable users will use
rewards_cmd = "!testnet-rewards"

# log in console when bot is active within the discord
@client.event
async def on_ready():
  print("*logged in as testnet rewards bot*")

@client.event
async def on_message(message):
  # send only messages to testnet-rewards channel in bronze age testnet category
  if message.channel.id == os.environ['rewards_channel_id']:
    print("checking message...")
    # prevent bot from checking its own sent message
    if message.author == client.user:
      return
    # pull channel object to allow for sending messages
    testnet_rewards_channel = client.get_channel(os.environ['rewards_channel_id'])
    # check for !testnet-rewards command
    if message.content.startswith(rewards_cmd):
      print(f"{message.author.name}#{message.author.discriminator} requested rewards")
      # convert users name into readible format aligned with db storage
      nickname = message.author.name.lower()
      user = f"{nickname}#{message.author.discriminator}" # discord username
      if user in db.keys():
        print(user + " in db testnet rewards")
        user_rewards = db[user]
        # check for user_rewards and send only them if they are not 0
        if user_rewards != 0:
          # create embedded message for display purposes
          embed = discord.Embed(title='Testnet Rewards', colour=discord.Colour.blue())
          message_content = "Rewards: {}".format(user_rewards)
          embed.add_field(name=user, value=message_content, inline=False)
          await testnet_rewards_channel.send(embed=embed)
          # print in console what user requested their rewards
          print(f"{user} was sent their rewards: " + str(user_rewards))
        else:
          # notify user that they were not active/earned 0 rewards
          await testnet_rewards_channel.send(f"{message.author.mention} it doesn't look like you were active last testnet. Try to participate in our upcoming testnet to earn $QUAI!")
          # print in console what user requested their rewards
        print(f"{user} was sent their rewards: " + str(user_rewards))
      # if a user did not participate, notify they have no rewards and encourage them to participate in the next testnet
      else:
        # set user rewards to 0 AND do not store since they did not participate in the testnet - only stored users are participants
        user_rewards = 0
        # create embedded message for display purposes
        embed = discord.Embed(title='Testnet Rewards', colour=discord.Colour.blue())
        message_content = "Rewards: {}".format(user_rewards)
        embed.add_field(name=user, value=message_content, inline=False)
        # send embedded message with rewards and username (for incentive purposes)
        await testnet_rewards_channel.send(embed=embed)
        # notify user 
        await testnet_rewards_channel.send(f"{message.author.mention} it doesn't look like you were active in our last testnet. Try to participate in our upcoming testnet to earn $QUAI!")
        # print in console what user requested their rewards
        print(f"{user} was sent their rewards (They did not participate).")

# Activate the discord bot
client.run(os.environ['TOKEN'])
