from riotwatcher import LolWatcher
import discord
import asyncio
from datetime import datetime



#riot api key (expiers every day)
riotkey = ''
#discord api bot key
discordkey = ''
#discord channel to post to
discordchannel = 
#set region to NA
region = 'na1'
#number of games tested
gamesTested = 10
#define watcher as the key we use to interact with lol data
watcher = LolWatcher(riotkey)
#define discord client
client = discord.Client()
#test for demations every x seconds(600 for 10 minuets)
seconds = 300



        #####
        #set fuctions
        #####



#fuction for finding rank info and accout id based on summoner name
def findInfo(summonerName):
    player = watcher.summoner.by_name(region,summonerName)
    stats = watcher.league.by_summoner(region, player['id'])

    #find what number is ranked solo
    queueType = stats[0]['queueType']

    if queueType == "RANKED_SOLO_5x5":
        rankedSolo = 0
    else:
        rankedSolo = 1

    #pick the info to find
    tier = stats[rankedSolo]['tier']
    rank = stats[rankedSolo]['rank']
    LP = stats[rankedSolo]['leaguePoints']

    #print info
    print(summonerName)
    if tier == "MASTER" or tier == "GRANDMASTER" or tier == "CHALLENGER":
        print(tier)
        print(LP)
    else:
        print(tier)
        print(rank)
        print(LP)

    #return user id
    return [summonerName, player['accountId'], tier, rank, LP]

#test every x amount of time if players ranks have changed
async def testplayers():
    while True:
        await asyncio.sleep(seconds)
        for x in range(numberOfPlayers):
            testPlayerChange = findInfo(playerNames[x])
            if listOfPlayers[x][2] == testPlayerChange[2] and listOfPlayers[x][3] == testPlayerChange[3]:
                print('same rank')
                print()
            else:
                print('different rank')

                cRankValue = getRankValue(testPlayerChange)
                pRankValue = getRankValue(listOfPlayers[x])

                #test if rank is up or down
                if cRankValue > pRankValue:

                    lossKDA = findPlayerKDA(listOfPlayers[x][1])

                    #make variables readable
                    lossKDAstr = str(str(lossKDA[1][0]) + '/' + str(lossKDA[1][1]) + '/' + str(lossKDA[1][2]))

                    if testPlayerChange[2] == 'MASTER' or testPlayerChange[2] == 'GRANDMASTER' or testPlayerChange[2] == 'CHALLENGER':
                        Rank = str(testPlayerChange[2])
                    else:
                        Rank = str(str(testPlayerChange[2]) + ' ' + str(testPlayerChange[3]))

                    #variables used to print
                    pUser = listOfPlayers[x][0]
                    pRank = Rank
                    pLossStreak = lossKDA[0]
                    pLossKDA = lossKDAstr

                    #send discord message passing the data
                    client.loop.create_task(printData(pUser, pRank, pLossStreak, pLossKDA))
                else:
                    print('updated player')
                    print()
                #update 'listOfPlayers'
                listOfPlayers[x] = testPlayerChange

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time)
        print()

#find the loss streak of a player and thier kda during the streak
def findPlayerKDA(userID):
    print()
    playerHistory = watcher.match.matchlist_by_account(region, userID, 420, None, None, None, gamesTested)

    #put all match history data into 'historyInfo'
    historyInfo = []
    for x in range(gamesTested):
        historyInfo.append(watcher.match.by_id(region, playerHistory['matches'][x]['gameId']))

    #get user number in each game
    userNumber = []
    for x in range (gamesTested):
        for y in range(10):
            if (historyInfo[x]['participantIdentities'][y]['player']['currentAccountId']) == userID:
                userNumber.append(y)
                break

    #find the loss streak the player is on
    lossStreak = 0
    for x in range(gamesTested):
        if historyInfo[x]['participants'][userNumber[x]]['stats']['win'] == False:
            lossStreak = lossStreak + 1
        else:
            break

    #find the kda during loss streak
    KDAaverage = []
    if lossStreak != 0:
        for x in range(lossStreak):
            kills = historyInfo[x]['participants'][userNumber[x]]['stats']['kills']
            deaths = historyInfo[x]['participants'][userNumber[x]]['stats']['deaths']
            assists = historyInfo[x]['participants'][userNumber[x]]['stats']['assists']

            KDA = []

            KDA.append(kills)
            KDA.append(deaths)
            KDA.append(assists)

            KDAaverage.append(KDA)

        #average and round kda
        KDAaverage = [sum(x) / len(x) for x in zip(*KDAaverage)]
        KDAaverage = [round(xg, 1) for xg in KDAaverage]

        return lossStreak, KDAaverage
    else:
        return 0, [0,0,0]

#get rankValue from 'listOfPlayers' format
def getRankValue(playerRankInfo):
    ranks = ['CHALLENGER', 'GRANDMASTER', 'MASTER', 'DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'IRON']
    rating = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    divitions = ['I', 'II', 'III', 'IV']
    divitionValue = [1, 2, 3, 4]
    rankValue = 0
    for x in range(len(ranks)):
        if playerRankInfo[2] == ranks[x]:
            rankValue = rankValue + rating[x]
    for x in range(len(divitions)):
        if playerRankInfo[3] == divitions[x]:
            rankValue = rankValue + divitionValue[x]
    return rankValue

#send data to discord
@client.event
async def printData(User, Rank, LossStreak, LossKDA):
    channel = client.get_channel(discordchannel)
    print('User:' + str(User))
    print('Rank:' + str(Rank))
    print('Loss Streak:' + str(LossStreak))
    print('KDA:' + str(LossKDA))
    print()
    await channel.send('looks good :tada: {} :tada:\nWelcome to {}\nLossStreak: {}\nRecent KDA: {}'.format(User, Rank, LossStreak, LossKDA))

#ready check
@client.event
async def on_ready():
    print('we logged in'.format(client))
    print()

#testing fuction
@client.event
async def on_message(message):
    if message.content.startswith('#hi'):
        print("HI!!!!")  
        await message.channel.send('HI!')



        #####
        #Run Start up code
        #####



#read "Player.txt"
f = open('Players.txt','r')

playerNames = []
numberOfPlayers = 0
for line in f:

    line = line.strip("\n")
    line = line.strip()
    if line != 'Players:' and line != '':
        numberOfPlayers = numberOfPlayers +1
        playerNames.append(line)
    
print()
print('testing ' + str(numberOfPlayers) + ' players')
print(playerNames)
print()

f.close()

#store each player rank in variable 'listOfPlayers'
listOfPlayers = []
for x in range(numberOfPlayers):
    listOfPlayers.append(findInfo(playerNames[x]))
    print()



        #####
        #run the bot
        #####



client.loop.create_task(testplayers())
client.run(discordkey)
