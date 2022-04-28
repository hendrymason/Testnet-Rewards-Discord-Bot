# Testnet-Rewards-Discord-Bot
This bot enables members of the quai network discord to access their aggregated testnet rewards data through a discord command

The Bot runs with dependencies in the replit browser compiler. Replit allows the following to work smoothly:
  - Only one pull needed from gsheets on initialization of the bot script, after which the data is stored in the replit db
  - the replit db allows for easy key-value pair access to easily available, persistant storage
  - replit has a "always on" feature that allows the script to run continuously via replit servers

Main Script:
- Gsheets Data Extraction into replit db
- Discord Bot retrieving and sending users testnet reward data
