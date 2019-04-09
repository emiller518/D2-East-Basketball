from bs4 import BeautifulSoup
import re
from urllib.request import Request, urlopen
import D2East_MySQL as sql
import ssl
import os
import urllib.request


'''
Offline Table:
    raw_html = open('another.htm').read()
    soup = BeautifulSoup(raw_html, 'html.parser')
'''


def schedulesoup(season, conf):
    if conf == 'NE10':
        link = "https://www.northeast10.org/sports/mbkb/" + season + "/schedule"
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        # req = Request(link)
        source = urlopen(req).read()
    elif conf == 'ECC':
        link = "https://www.eccsports.org/sports/mbkb/" + season + "/schedule"
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        # req = Request(link)
        source = urlopen(req).read()
    elif conf == 'CACC':
        link = "https://www.caccathletics.org/sports/mbkb/" + season + "/schedule"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        source = urlopen(link, context=ctx)

    soup = BeautifulSoup(source, 'lxml')
    return soup


def gamesoup(linkseg, season, conf):
    if conf == 'NE10':
        link = "https://www.northeast10.org/sports/mbkb/" + season + "/boxscores/" + linkseg + ".xml"
    elif conf == 'ECC':
        link = "https://www.eccsports.org/sports/mbkb/" + season + "/boxscores/" + linkseg + ".xml"
    elif conf == 'CACC':
        link = "http://www.caccathletics.org/sports/mbkb/" + season + "/boxscores/" + linkseg + ".xml"

    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    source = urlopen(req).read()
    soup = BeautifulSoup(source, 'lxml')
    return soup


def getlinks(soup, season, conf):
    if conf == 'NE10' or conf == 'ECC':
        table = soup.find('table')
    elif conf == 'CACC':
        table = soup.find("div", {"class": "schedule-content clearfix"})

    spans = table.find_all("span", text="Box Score")
    gamelist = []

    for span in spans:
        if "/sports/mbkb/" + season + "/boxscores" in span.parent.get('href'):
            gamelist.insert(0, span.parent.get('href').split("/sports/mbkb/" + season + "/boxscores/")[1].split('.xml')[0])

    return gamelist


def exhibition(soup, linkseg):

    if 'CACC' in soup.find('title').text:
        gameinfo = soup.find("a", href=re.compile(linkseg)).parent.parent.parent.parent
    else:
        gameinfo = soup.find("a", href=re.compile(linkseg)).parent.parent.parent

    ex = gameinfo.find("span", text="#")
    if ex:
        exi = "1"
    else:
        exi = "0"
    return exi


def nonleague(soup, linkseg):

    if 'CACC' in soup.find('title').text:
        gameinfo = soup.find("a", href=re.compile(linkseg)).parent.parent.parent.parent
    else:
        gameinfo = soup.find("a", href=re.compile(linkseg)).parent.parent.parent

    conf = gameinfo.find("span", text="*")
    if conf:
        nonleague = "0"
    else:
        nonleague = "1"
    return nonleague


def postseason(soup, linkseg):

    if 'CACC' in soup.find('title').text:
        gameinfo = soup.find("a", href=re.compile(linkseg)).parent.parent.parent.parent
    else:
        gameinfo = soup.find("a", href=re.compile(linkseg)).parent.parent.parent

    post = gameinfo.find("span", text="%")
    if post:
        p = str(1)
    else:
        p = str(0)
    return p


def gethometeam(soup):
    hometeam = soup.findAll("span", {"class": "team-name"})[1].text.strip()
    return hometeam


def getawayteam(soup):
    awayteam = soup.findAll("span", {"class": "team-name"})[0].text.strip()
    return awayteam


def gameinfo(gamesoup, schedsoup, linkseg, homeID, awayID, season):

    awayteam = gamesoup.findAll("span", {"class": "team-name"})[0].text.strip()
    hometeam = gamesoup.findAll("span", {"class": "team-name"})[1].text.strip()
    awayscore = gamesoup.findAll("td", {"class": "score total"})[0].text.strip()
    homescore = gamesoup.findAll("td", {"class": "score total"})[1].text.strip()

    seasonID = sql.getseasonid(season)

    if awayscore > homescore:
        winID = awayID
        lossID = homeID
    elif homescore > awayscore:
        winID = homeID
        lossID = awayID
    else:
        winID = ""
        lossID = ""

    gamedate = linkseg.split("_")[0][:4] + "-" + linkseg.split("_")[0][4:6] + "-" + linkseg.split("_")[0][6:]

    if "vs." in gamesoup.findAll("div", {"class": "head"})[0].find("h1").text.strip():
        neutral = 1
    else:
        neutral = 0

    ties = gamesoup.find("th", text="Trends")
    if ties:
        ties = ties.find_next_sibling("td").text.strip().split('Ties: ')[1].split(';')[0]
    else:
        ties = "0"

    leadchanges = gamesoup.find("th", text="Trends")
    if leadchanges:
        leadchanges = leadchanges.find_next_sibling("td").text.strip().split('Lead Changes: ')[1]
    else:
        leadchanges = "0"

    exi = exhibition(schedsoup, linkseg)

    attendance = gamesoup.find("th", text="Attendance: ")
    if attendance:
        attendance = attendance.find_next_sibling("td").text
    else:
        attendance = "0"

    nonlg = nonleague(schedsoup, linkseg)

    gameID = linkseg.split("_")[0] + str(homeID)

    ncaa = "0"

    ne10 = postseason(schedsoup, linkseg)

    gamelist = [gameID, seasonID, homeID, awayID, winID, lossID, homescore, awayscore, gamedate, neutral, exi,
                nonlg, ties, leadchanges, attendance, ne10, ncaa]

    return gamelist


def nonconcheck(home, away):
    homeconf = sql.getteamconf(home)
    awayconf = sql.getteamconf(away)
    if awayconf == homeconf:
        return 0
    else:
        return 1


def teamstats(soup, linkseg, homeID, awayID):

    gameID = linkseg.split("_")[0] + str(homeID)

    awaybench = soup.find("th", text="Bench Points")
    if awaybench:
        awaybench = awaybench.find_next_sibling("td").text
    else:
        awaybench = ""

    homebench = soup.find("th", text="Bench Points")
    if homebench:
        homebench = homebench.find_next_sibling("td").find_next_sibling("td").text
    else:
        homebench = ""

    awayptsoffto = soup.find("th", text="Points off Turnovers")
    if awayptsoffto:
        awayptsoffto = awayptsoffto.find_next_sibling("td").text
    else:
        awayptsoffto = ""

    homeptsoffto = soup.find("th", text="Points off Turnovers")
    if homeptsoffto:
        homeptsoffto = homeptsoffto.find_next_sibling("td").find_next_sibling("td").text
    else:
        homeptsoffto = ""

    awaysecondchance = soup.find("th", text="2nd Chance Points")
    if awaysecondchance:
        awaysecondchance = awaysecondchance.find_next_sibling("td").text
    else:
        awaysecondchance = ""

    homesecondchance = soup.find("th", text="2nd Chance Points")
    if homesecondchance:
        homesecondchance = homesecondchance.find_next_sibling("td").find_next_sibling("td").text
    else:
        homesecondchance = ""

    awayptsinpaint = soup.find("th", text="Points in the Paint")
    if awayptsinpaint:
        awayptsinpaint = awayptsinpaint.find_next_sibling("td").text
    else:
        awayptsinpaint = ""

    homeptsinpaint = soup.find("th", text="Points in the Paint")
    if homeptsinpaint:
        homeptsinpaint = homeptsinpaint.find_next_sibling("td").find_next_sibling("td").text
    else:
        homeptsinpaint = ""

    awayfastbreak = soup.find("th", text="Fastbreak Points")
    if awayfastbreak:
        awayfastbreak = awayfastbreak.find_next_sibling("td").text
    else:
        awayfastbreak = ""

    homefastbreak = soup.find("th", text="Fastbreak Points")
    if homefastbreak:
        homefastbreak = homefastbreak.find_next_sibling("td").find_next_sibling("td").text
    else:
        homefastbreak = ""

    awaylargestlead = soup.find("th", text="Largest Lead")
    if awaylargestlead:
        awaylargestlead = awaylargestlead.find_next_sibling("td").text
    else:
        awaylargestlead = ""

    homelargestlead = soup.find("th", text="Largest Lead")
    if homelargestlead:
        homelargestlead = homelargestlead.find_next_sibling("td").find_next_sibling("td").text
    else:
        homelargestlead = ""

    awayLLhalf = soup.find("th", text="Time of Largest Lead")
    if awayLLhalf:
        awayLLhalfText = awayLLhalf.find_next_sibling("td").find_next_sibling("td").text
        if awayLLhalfText == "-":
            awayLLhalf = ""
        elif len(awayLLhalfText.split('-')) == 1:
            awayLLhalf = 'UNK'
        else:
            awayLLhalf = awayLLhalfText.split('-')[0][0]
    else:
        awayLLhalf = ""

    homeLLhalf = soup.find("th", text="Time of Largest Lead")
    if homeLLhalf:
        homeLLhalfText = homeLLhalf.find_next_sibling("td").find_next_sibling("td").text
        if homeLLhalfText == "-":
            homeLLhalf = ""
        elif len(homeLLhalfText.split('-')) == 1:
            homeLLhalf = 'UNK'
        else:
            homeLLhalf = homeLLhalfText.split('-')[0][0]
    else:
        homeLLhalf = ""

    awayLLtime = soup.find("th", text="Time of Largest Lead")
    if awayLLtime:
        if len(awayLLtime.find_next_sibling("td").text.split('-')) == 1:
            awayLLtime = awayLLtime.find_next_sibling("td").text.split('-')[0]
        else:
            awayLLtime = awayLLtime.find_next_sibling("td").text.split('-')[1]
    else:
        awayLLtime = ""

    homeLLtime = soup.find("th", text="Time of Largest Lead")
    if homeLLtime:
        if len(homeLLtime.find_next_sibling("td").text.split('-')) == 1:
            homeLLtime = homeLLtime.find_next_sibling("td").text.split('-')[0]
        else:
            homeLLtime = homeLLtime.find_next_sibling("td").text.split('-')[1]
    else:
        homeLLtime = ""

    homestats = [gameID, homeID, homeptsoffto, homesecondchance, homeptsinpaint, homefastbreak, homebench,
                 homelargestlead, homeLLhalf, homeLLtime]
    awaystats = [gameID, awayID, awayptsoffto, awaysecondchance, awayptsinpaint, awayfastbreak, awaybench,
                 awaylargestlead, awayLLhalf, awayLLtime]

    teamstats = [homestats, awaystats]

    return teamstats


def playerstats(soup, homeID=0, awayID=0):

    allplayers = []

    for i in getlists(soup,homeID,awayID, "home"):
        allplayers.append(i)

    for i in getlists(soup,homeID,awayID, "away"):
        allplayers.append(i)

    return allplayers


def getlists(soup, homeID, awayID, type):
    if type == "home": table = 2
    else: table = 1

    table = (soup.find_all('table')[table])
    rows = table.find_all('tr')

    data = []

    rebi = 0
    orebi = 0
    drebi = 0
    pfi = 0
    toi = 0

    for row in rows[1:]:
        cols = row.find_all(['th', 'td'])
        cols = [ele.text.strip().replace("  \t                        ", "") for ele in cols]
        cols[0] = cols[0].replace('\n', '')

        if cols[0] == 'TOTALS':
            total = cols

        if (len(cols) >= 14) & (cols[0] != 'TOTALS'):

            namenum = cols[0].split(' - ')
            del cols[0]

            cols.insert(0, namenum[0])
            cols.insert(1, namenum[1])

            if cols[0] == 'TM':
                cols[0] = '100'

            for i in range(len(cols)):
                if cols[i] == '':
                    cols[i] = '0'

            if cols[3] != '':
                if '-' in cols[3]:
                    fg = cols[3].split('-')
                    del cols[3]
                    cols.insert(3, fg[0])
                    cols.insert(4, fg[1])
                else:
                    cols.insert(3, '0')

            if cols[5] != '':
                if '-' in cols[5]:
                    threes = cols[5].split('-')
                    del cols[5]
                    cols.insert(5, threes[0])
                    cols.insert(6, threes[1])
                else:
                    cols.insert(5, '0')

            if cols[7] != '':
                if '-' in cols[7]:
                    ft = cols[7].split('-')
                    del cols[7]
                    cols.insert(7, ft[0])
                    cols.insert(8, ft[1])
                else:
                    cols.insert(7, '0')

            if cols[0] != '100':
                orebi = orebi + int(cols[9])
                drebi = drebi + int(cols[10])
                rebi = rebi + int(cols[11])
                toi = toi + int(cols[15])
                pfi = pfi + int(cols[16])

            if cols[0] == "00" or cols[0] == "0":
                cols[0] = cols[0]
            else:
                cols[0] = cols[0].lstrip("0")


            if "," in cols[1]:
                if ", " in cols[1]:
                    namesplit = cols[1].split(", ")
                    cols[1] = namesplit[1] + " " + namesplit[0]
                else:
                    namesplit = cols[1].split(",")
                    cols[1] = namesplit[1] + " " + namesplit[0]

            cols[1] = cols[1].lower().title()

            data.append([ele for ele in cols if ele])

    totaloreb = total[5]
    totaldreb = total[6]
    totalreb = total[7]
    totalto = total[11]
    totalpf = total[12]

    for i in range(0, len(data)):
        if i <= 4:
            data[i].append(1)
        else:
            data[i].append(0)

    if data[-1][0] != '100':
        data.append(['100', 'Team', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 0])
    if (int(totaloreb) - int(orebi)) != 0:
        data[-1][9] = (int(totaloreb) - int(orebi))
    if (int(totaldreb) - int(drebi)) != 0:
        data[-1][10] = (int(totaldreb) - int(drebi))
    if (int(totalreb) - int(rebi)) != 0:
        data[-1][11] = (int(totalreb) - int(rebi))
    if (int(totalto) - int(toi)) != 0:
        data[-1][15] = (int(totalto) - int(toi))
    if (int(totalpf) - int(pfi)) != 0:
        data[-1][16] = (int(totalpf) - int(pfi))

    for i in range(0, len(data)):
        if type == "home":
            data[i].append(homeID)
        else:
            data[i].append(awayID)

    return data


def rosterscrape(abbr, season, link):
    teamID = sql.getteamidfromabvr(abbr)
    seasonID = sql.getseasonid(season)

    if len(str(seasonID)) == 1:
        seasonlabel = str(0) + str(seasonID)
    else:
        seasonlabel = str(seasonID)

    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    source = urlopen(req).read()
    soup = BeautifulSoup(source, 'lxml')

    fulltable = soup.find_all("div", {"class": "sidearm-roster-player-container"})

    for player in fulltable:

        hometown = player.find("span", {"class": "sidearm-roster-player-hometown"}).text
        town = hometown.split(", ")[0]
        state = hometown.split(", ")[1]
        state = state.replace('.', '')

        if state == 'Conn':
            state = 'CT'
        if state == 'Calif':
            state = 'CA'
        if state == 'Mass':
            state = 'MA'
        if state == 'Fla':
            state = 'FL'
        if state == 'Ontario':
            state = 'Canada'
        if state == 'Ind':
            state = 'IN'
        if state == 'Mich':
            state = 'MI'
        if state == 'Ohio':
            state = 'OH'
        if state == 'WVa':
            state = 'WV'
        if state == 'Maine':
            state = 'ME'
        if state == 'Ill':
            state = 'IL'

        if len(state) > 2:
            foreign = str(1)
        else:
            foreign = str(0)
            state = state.upper()

        if player.find("span", {"class": "sidearm-roster-player-highschool"}) is not None:
            highschool = player.find("span", {"class": "sidearm-roster-player-highschool"}).text
        elif player.find("span", {"class": "sidearm-roster-player-previous-school"}) is not None:
            highschool = player.find("span", {"class": "sidearm-roster-player-previous-school"}).text
        else:
            highschool = ''

        clss = player.find("span", {"class": "sidearm-roster-player-academic-year"}).text
        newdiv = player.find("div", {"class": "sidearm-roster-player-position"})
        # position = newdiv.find("span", {"class": 'hide-on-medium'}).text.strip()
        position = newdiv.find("span", {"class": 'text-bold'}).text.strip()

        #for str2011
        test = newdiv.find("span", {"class": 'text-bold'})
        textx = test.find("span", {"class": 'hide-on-medium'})
        if textx is not None:
            position = textx.text.strip()

        if newdiv.find("span", {"class": "sidearm-roster-player-height"}):
            height = newdiv.find("span", {"class": "sidearm-roster-player-height"}).text
        else:
            height = ''

        number = player.find("span", {"class": "sidearm-roster-player-jersey-number"}).text

        if 'fr' in clss.lower():
            classID = str(1)
        elif 'so' in clss.lower():
            classID = str(2)
        elif 'jr' in clss.lower():
            classID = str(3)
        elif 'sr' in clss.lower():
            classID = str(4)
        elif 'gr' in clss.lower():
            classID = str(5)
        else:
            classID = str(0)

        name = player.find_all("a")[1].text.title()

        if name == 'Terrence  Rountree Jr.':
            name = 'Terrence Rountree'

        if name == 'Full Bio':
            name = player.find_all("a")[0].text.title()

        if ' ' in name:
            name = name.replace("  ", " ")

        finalheight = height.replace("\"", "")

        playerexists = (sql.playeronteamindb(teamID, name))
        playeryearexists = (sql.playeryearindb(teamID, name, seasonID))

        if playerexists:
            playerid = sql.getplayernameid(teamID, name)
            sql.updateplayer(playerid, town, state, foreign, highschool)
            if playeryearexists:
                sql.updateplayeryear(playerid, seasonID, classID, finalheight, position)
            else:
                sql.insertplayeryear(playerid, teamID, seasonID, classID, number, finalheight, position)
        else:
            playerlist = [name, town, state, foreign, highschool]
            playeryearlist = [teamID, seasonID, classID, number, finalheight, position]
            sql.insertplayerfull(playerlist, playeryearlist)

        imglink = player.find("img", {"class": "lazy"})

        playerid = sql.getplayernameid(teamID, name)

        try:
            imglabel = str(abbr) + str(seasonlabel) + str(playerid) + '.jpg'
            imglink = (os.path.dirname(link)) + imglink['data-original'].replace('?width=80', '')
            imglink = imglink.replace(' ', '%20')
            urllib.request.urlretrieve(imglink, imglabel)
        except TypeError:
            pass

        print(name + ' - ' + town + ' - ' + state + ' - ' + foreign + ' - ' + highschool + ' - ' + clss + ' - ' +
              classID + ' - ' + number + ' - ' + finalheight + ' - ' + position)


def parsepbp(soup, gameID, season):

    firsthalf = soup.find_all("table", attrs={'role':'presentation'})[0]
    secondhalf = soup.find_all("table", attrs={'role':'presentation'})[1]

    fhplays = firsthalf.find_all('tr')
    shplays = secondhalf.find_all('tr')

    homeTeamName = gethometeam(soup)
    awayTeamName = getawayteam(soup)

    playsinhalf(fhplays, homeTeamName, awayTeamName, '1', gameID, season)
    playsinhalf(shplays, homeTeamName, awayTeamName, '2', gameID, season)


def playsinhalf(halfplays, home, away, half, gameID, season):
    playnum = 1

    for i in halfplays[0:-1]:

        if 'home' in i['class']:
            team = 'H'
        else:
            team = 'A'

        teamID = sql.getteamidfromgame(gameID, team)

        time = i.find("td", {"class": "time"}).text
        text = i.find("span", {"class": "text"}).text.strip().replace('\n', ' ')
        if i.find("span", {"class": "v-score"}):
            awayscore = i.find("span", {"class": "v-score"}).text
        else:
            awayscore = str(0)
        if i.find("span", {"class": "h-score"}):
            homescore = i.find("span", {"class": "h-score"}).text
        else:
            homescore = str(0)
        splittext = text.replace(' ', ',').split(',')

        name = []
        playtype = []

        seconds = str((int(time.split(':')[0]) * 60) + int(time.split(':')[1]))

        for x in splittext:
            if x.isupper():
                if (x != 'III') and (x != 'II'):
                    name = [x] + name
            else:
                playtype.append(x)

        name = " ".join(name)

        if name == 'TEAM' or ('TIMEOUT' in name):
            sqlname = ['%TEAM%', '%TEAM%']
        elif name == '':
            sqlname = ['UNKNOWN', 'PLAYER']
        else:
            first = '%' + name.split(' ')[0] + '%'
            last = '%' + name.split(' ')[1] + '%'
            sqlname = [first, last]

        playtype = " ".join(playtype)

        if '30SEC' in name or '20SEC' in name:
            playID = '1'
        elif 'TIMEOUT TEAM' in name:
            playID = '2'
        elif ('MEDIA TIMEOUT' in name) or ('TIMEOUT MEDIA' in name):
            playID = '3'
        elif '{' in playtype:
            playID = '0'
        elif 'missed layup' in playtype:
            playID = '4'
        elif 'missed jump shot' in playtype:
            playID = '5'
        elif 'missed tip-in' in playtype:
            playID = '6'
        elif 'missed dunk' in playtype:
            playID = '7'
        elif 'made layup' in playtype:
            playID = '8'
        elif 'made jump shot' in playtype:
            playID = '9'
        elif 'made tip-in' in playtype:
            playID = '10'
        elif 'made dunk' in playtype:
            playID = '11'
        elif 'missed 3-pt. jump shot' in playtype:
            playID = '12'
        elif 'made 3-pt. jump shot' in playtype:
            playID = '13'
        elif 'made free throw' in playtype:
            playID = '14'
        elif 'missed free throw' in playtype:
            playID = '15'
        elif 'offensive rebound' in playtype:
            playID = '16'
        elif 'defensive rebound' in playtype:
            playID = '17'
        elif 'Assist' in playtype:
            playID = '18'
        elif 'Steal' in playtype:
            playID = '19'
        elif 'Block' in playtype:
            playID = '20'
        elif 'Turnover' in playtype:
            playID = '21'
        elif 'Foul' in playtype:
            playID = '22'
        elif 'goes to the bench' in playtype:
            playID = '23'
        elif 'enters the game' in playtype:
            playID = '24'
        elif 'deadball rebound' in playtype:
            playID = '25'
        else:
            playID = '0'

        playerID = sql.getplayeridpbp(teamID, sqlname, season)

        if playerID is None:
            playerID = '0'
        else:
            name = ''

        insertlist = [gameID, half, playnum, time, seconds, playerID, playID, homescore, awayscore, team, name]

        sql.insertpbp(insertlist)

        print(str(gameID) + ' ' + half + ' ' + str(playnum) + ' ' + time + ' ' + seconds + '(' + str(playerID) + ') ' +
              playID + ' ' + awayscore + ' ' + homescore + ' ' + team + ' ' + name)

        playnum = playnum + 1
