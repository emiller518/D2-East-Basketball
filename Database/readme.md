This folder contains a few scripts that were used in order to create the back end database for all Division 2 East statistics which has been the basis for other utilities and analysis.

The creation of the database has been split into the three python files seen above:


*D2East_MySQL.py, which handles reading from and writing to the database using mysql.connector
*D2EastWebScrape.py, which scrapes box scores from the ECC, CACC, and NE10 websites using urllib.request and BeautifulSoup 4
*Main.py, which combines the logic from both files to run the following two functions, looping through all available box scores given for the season:

**insertnewgame(): Checks to see if a game exists in the database, and if not adds all information from the box score, and adds all players or teams not currently in the database.

**insertpbp(): Adds all play by play data for a given game (will not work unless the insertnewgame function has been run first).

The SQL file to display a majority of the statistics included in the database has also been included.
