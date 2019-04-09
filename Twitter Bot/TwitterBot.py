from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from random import randint
import tweepy


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)


def send_tweet(sentence):
  cfg = {
    "consumer_key"        : "",
    "consumer_secret"     : "",
    "access_token"        : "",
    "access_token_secret" : ""
    }

  api = get_api(cfg)
  status = api.update_status(status=sentence)


def teamtodf(table, link):
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    source = urlopen(req).read()
    soup = BeautifulSoup(source, 'lxml')

    hometable = soup.findAll('table')[table]
    rows = hometable.find_all('tr')
    header = rows[0]

    l = []
    player_list = []
    for tr in rows:
        td = tr.find_all('td')
        try:
            name = tr.find_all('th')
            xs = name[0].find_all('a')
            for zs in xs:
                player_name = zs.text
                player_list.append(player_name)
        except IndexError:
            player_name = ''
        row = [tr.text.strip() for tr in td]
        l.append(row)


    x = header.find_all('th')
    columns = []
    for a in x:
        columns.append(a.text)
    columns.append('STARTER')

    start_names = player_list[0:5]
    reserve_names = player_list[5:]
    starters = l[2:7]
    bench = l[8:-3]
    team = l[-2:]

    to_dataframe = []
    single_row = []


    for i in range(0,5):
        single_row.append(start_names[i])
        for e in starters[i]:
            single_row.append(e)
        single_row.append('Y')
        to_dataframe.append(single_row)
        single_row = []

    i = 0
    for n in bench:
        single_row.append(reserve_names[i])
        for x in n:
            single_row.append(x)
        single_row.append('N')
        to_dataframe.append(single_row)
        single_row = []
        i += 1

    teamstats = pd.DataFrame(to_dataframe, columns=columns)
    teamstats['First'], teamstats['Last'] = teamstats['Player'].str.split(' ', 1).str
    teamstats = teamstats.drop(['Player'], axis=1)
    teamstats['FGM'], teamstats['FGA'] = teamstats['FGM-A'].str.split('-', 1).str
    teamstats = teamstats.drop(['FGM-A'], axis=1)
    teamstats['3PM'], teamstats['3PA'] = teamstats['3PM-A'].str.split('-', 1).str
    teamstats = teamstats.drop(['3PM-A'], axis=1)
    teamstats['FTM'], teamstats['FTA'] = teamstats['FTM-A'].str.split('-', 1).str
    teamstats = teamstats.drop(['FTM-A'], axis=1)

    teamstats = teamstats[['First', 'Last', 'MIN', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'OREB', 'DREB', 'REB',
                           'AST','STL', 'BLK', 'TO', 'PF', 'PTS', 'STARTER']]

    teamstats['MIN'] = pd.to_numeric(teamstats['MIN'], errors='coerce')
    teamstats['FGM'] = pd.to_numeric(teamstats['FGM'], errors='coerce')
    teamstats['FGA'] = pd.to_numeric(teamstats['FGA'], errors='coerce')
    teamstats['3PM'] = pd.to_numeric(teamstats['3PM'], errors='coerce')
    teamstats['3PA'] = pd.to_numeric(teamstats['3PA'], errors='coerce')
    teamstats['FTM'] = pd.to_numeric(teamstats['FTM'], errors='coerce')
    teamstats['FTA'] = pd.to_numeric(teamstats['FTA'], errors='coerce')
    teamstats['OREB'] = pd.to_numeric(teamstats['OREB'], errors='coerce')
    teamstats['DREB'] = pd.to_numeric(teamstats['DREB'], errors='coerce')
    teamstats['REB'] = pd.to_numeric(teamstats['REB'], errors='coerce')
    teamstats['AST'] = pd.to_numeric(teamstats['AST'], errors='coerce')
    teamstats['STL'] = pd.to_numeric(teamstats['STL'], errors='coerce')
    teamstats['BLK'] = pd.to_numeric(teamstats['BLK'], errors='coerce')
    teamstats['TO'] = pd.to_numeric(teamstats['TO'], errors='coerce')
    teamstats['PF'] = pd.to_numeric(teamstats['PF'], errors='coerce')
    teamstats['PTS'] = pd.to_numeric(teamstats['PTS'], errors='coerce')

    return teamstats


def generateSentences(link, homedf, awaydf):

    ne10teams = ['American Intl', 'Bentley', 'Assumption', 'Stonehill', 'Merrimack', 'Franklin Pierce',
                 'Saint Rose', 'Saint Anselm', 'Le Moyne']
    homedf['FanSc'] = homedf['PTS'] + (2 * homedf['STL']) + (2 * homedf['BLK']) + (1.2 * homedf['REB']) + (
            1.5 * homedf['AST']) - (homedf['TO'])
    awaydf['FanSc'] = awaydf['PTS'] + (2 * awaydf['STL']) + (2 * awaydf['BLK']) + (1.2 * awaydf['REB']) + (
            1.5 * awaydf['AST']) - (awaydf['TO'])

    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    source = urlopen(req).read()
    soup = BeautifulSoup(source, 'lxml')

    # Get team names and scores
    awayteam = soup.find("label", {"class": "label visitor"}).getText()
    hometeam = soup.find("label", {"class": "label home"}).getText()
    homescore = soup.find("div", {"class": "team-score home"}).getText()
    awayscore = soup.find("div", {"class": "team-score visitor"}).getText()

    if hometeam == 'American Int\'l':
        hometeam = 'American Intl'
    if awayteam == 'American Int\'l':
        awayteam = 'American Intl'

    if hometeam not in ne10teams:
        hometeamNonCon = True
    if awayteam not in ne10teams:
        awayteamNonCon = True

    # ### THIS IS HOW TO GET the second value
    '''
    point_sort = homedf.sort_values(by="PTS",ascending=False)
    point_sort = point_sort.reset_index()
    print(point_sort)
    idx = len(point_sort) - 2
    print(str(point_sort["First"][idx]) + str(point_sort["Last"][idx]) + ' scored ' + str(point_sort["PTS"][idx]))
    '''

    # Randomize words in first sentence
    random = randint(0, 7)
    sentence1adj2 = ', '
    if random == 0:
        sentence1adj = ' tops '
    elif random == 1:
        sentence1adj = ' surpasses '
    elif random == 2:
        sentence1adj = ' knocks off '
    elif random == 3:
        sentence1adj = ' topples '
    elif random == 4:
        sentence1adj = ' gets by '
    elif random == 5:
        sentence1adj = ' dispatches '
    elif random == 6:
        sentence1adj = ' gets past '
    else:
        sentence1adj = ' defeats '

    # Write first sentence, define data frames based on winning teams
    if homescore > awayscore:
        sentence1 = (hometeam + sentence1adj + awayteam + sentence1adj2 + homescore + ' - ' + awayscore + '. ')
        windf = homedf
        lossdf = awaydf
        winteam = hometeam
        loseteam = awayteam
    else:
        sentence1 = (awayteam + sentence1adj + hometeam + sentence1adj2 + awayscore + ' - ' + homescore + '. ')
        windf = awaydf
        lossdf = homedf
        winteam = awayteam
        loseteam = hometeam

    # Get the index of the leading scorer
    ptsidx = windf['PTS'].idxmax()

    highScoreName = (windf['First'][ptsidx] + ' ' + windf['Last'][ptsidx])
    highScorePoints = str(windf['PTS'][ptsidx]) + ' points'

    # Randomize description in the second sentence
    s2rand = randint(0, 8)
    if s2rand == 0:
        sentence2adj = highScoreName + ' led ' + winteam
    if s2rand == 1:
        sentence2adj = highScoreName + ' led the ' + winteam + ' attack'
    if s2rand == 2:
        sentence2adj = highScoreName + ' led the charge for ' + winteam
    if s2rand == 3:
        sentence2adj = highScoreName + ' led the ' + winteam + ' offense'
    if s2rand == 4:
        sentence2adj = highScoreName + ' led the way for ' + winteam
    if s2rand == 5:
        sentence2adj = winteam + '\'s ' + highScoreName + ' led the team'
    if s2rand == 6:
        sentence2adj = winteam + '\'s ' + highScoreName + ' led the way'
    if s2rand == 7:
        sentence2adj = winteam + '\'s ' + highScoreName + ' led the charge'
    if s2rand == 8:
        sentence2adj = winteam + '\'s ' + highScoreName + ' led the attack'

    # Write the second sentence. The high scorer either leads his team or all players in scoring. Write accordingly.
    if windf['PTS'].max() > lossdf['PTS'].max():
        gameHigh = True
        teamHigh = False
    else:
        teamHigh = True
        gameHigh = False

    random = randint(0, 3)
    if random == 0:
        if gameHigh:
            pointsHigh = ' with a game high '
        elif teamHigh:
            pointsHigh = ' with a game high '
        else:
            pointsHigh = ' with '
    if random == 1:
        if gameHigh:
            pointsHigh = ' with a game high '
        else:
            pointsHigh = ' with '
    if random == 2:
        if gameHigh:
            pointsHigh = ' with a game high '
        else:
            pointsHigh = ' with '
    if random == 3:
        pointsHigh = ' with '

    # The second sentence is written here
    sentence2 = sentence2adj + pointsHigh + highScorePoints

    # If the player shot well from the field, add it to sentence 2
    if (windf['FGM'][ptsidx] / windf['FGA'][ptsidx])*100 > 60:
        random = randint(0,1)
        if random == 0:
            highshotpct = (int((windf['FGM'][ptsidx] / windf['FGA'][ptsidx])*100))
            sentence2 = sentence2 + ' on ' + str(highshotpct) + '% shooting'
        if random == 1:
            sentence2 = sentence2 + ' on ' + str(windf['FGM'][ptsidx]) + ' of ' + str(windf['FGA'][ptsidx]) + ' shooting'

    # If the high scorer had more than 5 points or rebounds, set a flag
    if (windf['AST'][ptsidx]) >= 5:
        highscoreast = True
    else:
        highscoreast = False
    if (windf['REB'][ptsidx]) >= 5:
        highscorereb = True
    else:
        highscorereb = False

    # Modify the sentence to include assist / rebound sentence if either of the flags are true
    if highscoreast and highscorereb:
        sentence2 = sentence2 + ' along with ' + str(windf['REB'][ptsidx]) + ' rebounds and ' + str(windf['AST'][ptsidx]) + ' assists'
    elif highscoreast:
        sentence2 = sentence2 + ' along with ' + str(windf['AST'][ptsidx]) + ' assists'
    elif highscorereb:
        sentence2 = sentence2 + ' along with ' + str(windf['REB'][ptsidx]) + ' rebounds'

    # End the sentence with a period
    sentence2 = sentence2 + '. '

    # For the next sentence, look at the teams highest rebounder
    rebidx = windf['REB'].idxmax()

    # If the leading rebounder was also the leading scorer, we already talked about them
    # If not, include a sentence about them
    # ##### POSSIBLY ADD A SENTENCE ABOUT THE HIGH ASSIST PLAYER AND RANDOMIZE THEM ###### #
    # ##### OR LOOK AT WHICH NUMBER WAS HIGHER, POINTS OR ASSISTS ###### #
    if rebidx == ptsidx:
        sentence3 = ''
    else:
        sentence3 = (windf['First'][rebidx] + ' ' + windf['Last'][rebidx])
        if windf['PTS'][rebidx] >= 8:
            sentence3 = sentence3 + ' scored ' + str(windf['PTS'][rebidx]) + ' points and grabbed ' + \
                        str(windf['REB'][rebidx]) + ' boards'
            if windf['STARTER'][rebidx] == 'N':
                sentence3 = sentence3 + ' off the bench'
            sentence3 = sentence3 + '. '
        else:
            sentence3 = sentence3 + ' pulled in ' + str(windf['REB'][rebidx]) + ' rebounds'
            if windf['STARTER'][rebidx] == 'N':
                sentence3 = sentence3 + ' off the bench'
            sentence3 = sentence3 + '. '

    sentence4 = 'For ' + loseteam + ', '

    lptsidx = lossdf['PTS'].idxmax()

    sentence4 = sentence4 + (lossdf['First'][lptsidx] + ' ' + lossdf['Last'][lptsidx] + ' posted ' +
                 str(lossdf['PTS'][lptsidx]) + ' points')

    if (lossdf['AST'][lptsidx]) >= 5:
        highscoreast = True
    else:
        highscoreast = False
    if (lossdf['REB'][lptsidx]) >= 5:
        highscorereb = True
    else:
        highscorereb = False

    if highscoreast and highscorereb:
        sentence4 = sentence4 + ', ' + str(lossdf['REB'][lptsidx]) + ' rebounds and ' + str(lossdf['AST'][lptsidx]) + ' assists'
    elif highscoreast:
        sentence4 = sentence4 + ' and ' + str(lossdf['AST'][lptsidx]) + ' assists'
    elif highscorereb:
        sentence4 = sentence4 + ' and ' + str(lossdf['REB'][lptsidx]) + ' rebounds'

    sentence4 = sentence4 + ' in the losing effort.'

    returnsentence = sentence1 + sentence2 + sentence3 + sentence4

    if len(sentence1 + sentence2 + sentence3 + sentence4) < 281:
        returnsentence = sentence1 + sentence2 + sentence3 + sentence4
    elif len(sentence1 + sentence2 + sentence3) < 281:
        returnsentence = sentence1 + sentence2 + sentence3

    return returnsentence

home=2
away=1


linklist = ['https://www.northeast10.org/sports/mbkb/2018-19/boxscores/20181117_ia4b.xml',
            'https://www.eccsports.org/sports/mbkb/2018-19/boxscores/20190224_jj1v.xml',
            'http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180120_7b34.xml',
            'http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180110_i4cg.xml',
            'http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180110_u3ny.xml',
            'http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180110_i4cg.xml',
            'http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180112_vehd.xml',
            'http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180127_rxww.xml']

for i in linklist:
    home1 = teamtodf(home,i)
    away1 = teamtodf(away,i)
    recap = generateSentences(i,home1,away1)
    print(recap)

    # if len(recap) < 281:
        # send_tweet(recap)

