
import D2EastWebScrape as scrape
import D2East_MySQL as sql


# this function will look at all links on https://www.northeast10.org/sports/mbkb/2018-19/schedule
def insertnewgame(conf,season):

    schedsoup = scrape.schedulesoup(season, conf)

    for link in scrape.getlinks(schedsoup, season, conf):

        print(link)
        # if the link is in the link table, skip. if not, run logic to add required data
        if not sql.linkindb(link):

            gamesoup = scrape.gamesoup(link, season, conf)

            # set team name variables for better code readability
            homeTeamName = scrape.gethometeam(gamesoup)
            awayTeamName = scrape.getawayteam(gamesoup)

            # first search for the home team. does it exist? if not, insert into table
            if sql.teamindb(homeTeamName) == False:
                sql.insertteam(homeTeamName)
                print(homeTeamName + " added to the Team table.")

            # now that it exists, we have the ID
            homeTeamID = sql.getteamid(homeTeamName)

            # do the same for the away team
            if sql.teamindb(awayTeamName) == False:
                sql.insertteam(awayTeamName)
                print(awayTeamName + " added to the Team table.")
            awayTeamID = sql.getteamid(awayTeamName)

            # get all the items needed to create the record in game table, return as a list, then insert
            gameinfo = scrape.gameinfo(gamesoup, schedsoup, link, homeTeamID, awayTeamID, season)
            sql.insertgame(gameinfo)

            gameID = gameinfo[0]

            print('Successfully created game ' + gameID + '. 1 record added to the Game table.')

            # scrape all the player stats from the game, return as a list of lists
            playerstats = scrape.playerstats(gamesoup, homeTeamID, awayTeamID)

            # loop through the list for each record. does it exist? if not you will need the name and number to add it
            for i in playerstats:

                playerNumber = i[0]
                playerName = i[1]
                playerTeam = i[-1]

                if sql.playernameindb(playerTeam, playerName) is not None:
                    playerID = sql.playernameindb(playerTeam, playerName)
                    sql.insertminplayeryear(playerID, playerTeam, season, playerNumber)
                elif sql.playernumindb(playerTeam, playerNumber, season) is not None:
                    playerID = sql.playernumindb(playerTeam, playerNumber, season)
                    sql.insertminplayeryear(playerID, playerTeam, season, playerNumber)
                else:
                    sql.insertplayer(playerName, playerNumber, playerTeam, season)
                    print("Successfully added player " + playerName + " to the Player table.")
                    playerID = sql.getplayerid(playerTeam, playerNumber, season)

                del i[0]
                del i[0]
                del i[-1]

                i.insert(0, playerID)
                i.insert(0, gameID)

                sql.insertplayerstats(i)

                print("Successfully added " + playerName + "'s stats from game " + gameID + " to the PlayerStats table.")

            # Lastly do the team stats
            teamstats = scrape.teamstats(gamesoup, link, homeTeamID, awayTeamID)
            for i in teamstats:
                sql.insertteamstats(i)
            print("Successfully added team stats from game " + gameID + " to the TeamStats table.")

            # Finally add the link to the link table (Where is the gameID?)
            sql.insertlink(gameID, link, conf)

            # sql.committodb()

            print("Upload complete. Game " + gameID + " added to the database.")

        else:
            pass


def insertpbp(conf,season):
    schedsoup = scrape.schedulesoup(season, conf)
    for link in scrape.getlinks(schedsoup, season, conf):
        print(link)
        if sql.pbpindb(link) == 0:
            sql.markpbpcomplete(link)
            gamesoup = scrape.gamesoup(link, season, conf)
            gameid = sql.getgameidfromlink(link)
            scrape.parsepbp(gamesoup, gameid, season)
        else:
            pass


insertpbp('NE10', '2018-19')
insertpbp('CACC', '2018-19')
insertpbp('ECC', '2018-19')

insertnewgame('NE10', '2018-19')
insertnewgame('CACC', '2018-19')
insertnewgame('ECC', '2018-19')

