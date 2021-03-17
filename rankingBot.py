import os

from discord.ext import commands

if('IS_HEROKU' not in os.environ):
    from dotenv import load_dotenv

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime

if('IS_HEROKU' not in os.environ):
    load_dotenv()
    DISC_TOKEN = os.getenv('DISCORD_TOKEN')
    DB_TOKEN = os.getenv('DB_TOKEN')
else:
    DISC_TOKEN = os.environ['DISCORD_TOKEN']
    DB_TOKEN = os.environ['DB_TOKEN']

bot = commands.Bot(command_prefix="r-")

dbclient = None

def connectDatabase():
    global dbclient
    try:
        dbclient = MongoClient(DB_TOKEN)
        return True
    except:
        print("Error in connectDatabase: failed to connect to remote database.")
        dbclient = None
        return False
    
    
@bot.command(name='board', help="Creates a new ranking board")
async def new_ranking_board(ctx, board_name=""):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board you are trying to create."
            await ctx.send(response)
            return
    
        col = dbclient.main.create_collection(board_name)

        new_board_data = {
            "guild_name": ctx.guild.name,
            "guild_id": ctx.guild.id,
            "created": datetime.now()
        }
        col.insert_one(new_board_data)
        response = ">>> Ranking board **" + board_name + "** created successfully."
    except pymongo.errors.CollectionInvalid:
        response = ">>> **Error** when creating a new board. Board already exists."
    except:
        response = ">>> **Error** when creating a new board. PLease try again."
    
    await ctx.send(response)

@bot.command(name='close', help="Deletes a given board")
async def delete_ranking_board(ctx, board_name=""):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board you are trying to delete."
            await ctx.send(response)
            return

        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return

        dbclient.main[board_name].drop()
        response = ">>> **Deleted " + board_name + " board**."
    except:
        response = ">>> **Error** when deleting the board. PLease try again."
    
    await ctx.send(response)

@bot.command(name='list', help='Lists all ranking boards')
async def show_all_boards(ctx):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return
    
        all_boards = dbclient.main.list_collection_names()
        response = ">>> **Active Ranking Boards:**"
        for b in all_boards:
            response += "\n\t - " + b
    except:
        response = ">>> **Error** when creating a new board. PLease try again."
    
    await ctx.send(response)
    
@bot.command(name='players', help="Lists all players in a given board")
async def show_all_players_in_board(ctx, board_name=""):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board you are trying to list."
            await ctx.send(response)
            return

        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return
    
        col = dbclient.main[board_name]

        players = col.find({'player_name': {"$exists": True}}, {'player_name':1})

        response = ">>> Player competing in **" + board_name + "**:"
        
        for p in players:
            response += "\n\t - " + p['player_name']

    except:
        response = ">>> **Error**. PLease try again."
    
    await ctx.send(response)

@bot.command(name='add', help="Adds a new player to a given board")
async def new_player(ctx, board_name="", new_player="", starting_score=0):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board."
            await ctx.send(response)
            return

        if(new_player == ""):
            response = ">>> Please include the name of the player you want to add."
            await ctx.send(response)
            return
        
        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return

        col = dbclient.main[board_name]

        if(col.count_documents({"player_name": new_player}) != 0):
            response = ">>> Player already exists in this board."
            await ctx.send(response)
            return

        new_player_data = {
            "player_name": new_player,
            "score": starting_score
        }

        col.insert_one(new_player_data)
        response = ">>> " + new_player + " added to " + board_name + " board."
    
    except:
        response = ">>> **Error**. PLease try again."
    
    await ctx.send(response)

@bot.command(name='rm', help="Removes a player from a given board")
async def remove_player(ctx, board_name="", player=""):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board."
            await ctx.send(response)
            return

        if(player == ""):
            response = ">>> Please include the name of the player you want to remove."
            await ctx.send(response)
            return

        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return

        col = dbclient.main[board_name]

        if(col.count_documents({"player_name": player}) == 0):
            response = ">>> Player doesn't exist in this board."
            await ctx.send(response)
            return

        col.delete_one({'player_name': player})
        response = ">>> " + player + " removed from " + board_name + " board."
    
    except:
        response = ">>> **Error**. PLease try again."
    
    await ctx.send(response)

@bot.command(name='top', help="Shows the current ranking of the given ranking board")
async def show_board_ranking(ctx, board_name=""):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board you are trying to rank."
            await ctx.send(response)
            return

        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return

        col = dbclient.main[board_name]

        players = col.find({'player_name': {"$exists": True}}).sort("score",pymongo.DESCENDING)

        response = ">>> **Ranking " + board_name + ":**"
        
        place = 1

        for p in players:
            response += "\n\t"
            if(place <= 3):
                response += "**" + str(place) + "º**"
            else:
                response += str(place) + "º"
            response += "\t-\t" + str(p['score']) + "\t-\t" + p['player_name']

            if(place == 3):
                response += "\n\t----------------"

            place += 1

    except:
        response = ">>> **Error**. PLease try again."
    
    await ctx.send(response)

@bot.command(name='up', help="Adds points to this player in this ranking board")
async def add_points(ctx, board_name="", player="", points=0):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board."
            await ctx.send(response)
            return

        if(player == ""):
            response = ">>> Please include the name of the player you want to remove."
            await ctx.send(response)
            return

        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return

        col = dbclient.main[board_name]

        if(col.count_documents({"player_name": player}) == 0):
            response = ">>> Player doesn't exist in this board."
            await ctx.send(response)
            return

        col.update_one({"player_name": player}, {'$inc': {'score': points}})
        response = ">>> added **" + str(points) + "** to " + player + " in board " + board_name + "."
        
    except:
        response = ">>> **Error**. PLease try again."
    
    await ctx.send(response)

@bot.command(name='reset', help="Resets the score on a given board")
async def reset_board(ctx, board_name=""):
    try:
        #try to connect to database
        if(dbclient == None):
            if(not connectDatabase()):
                return

        if(board_name == ""):
            response = ">>> Please include the name of the ranking board."
            await ctx.send(response)
            return

        if(board_name not in dbclient.main.list_collection_names()):
            response = ">>> The board " + board_name + " does not exist."
            await ctx.send(response)
            return

        col = dbclient.main[board_name]

        col.update_many({}, {'$set': {'score': 0}})
        response = ">>> **resetted " + board_name + " board**."
        
    except:
        response = ">>> **Error**. PLease try again."
    
    await ctx.send(response)


bot.run(DISC_TOKEN)
