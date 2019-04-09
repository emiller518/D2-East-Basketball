This program was created as a tool to automate tedious scouting report generation during my time as a graduate assistant with Saint Rose's basketball team. It leverages the Python docx module and the D2 East database to calculate and insert statistics and return them in a docx format for the team to print and utilize before games.

This folder contains a few specific files of note. 

## Scouting.py

This file requires a connection to the database (D2East_MySQL.py from the database folder) and access to Synergy Sports Technology.  

The generate report function requires the team name, season, a player number, made paint attempts, and total paint attempts (both taken from Synergy). The script will then calculate certain stats, as well as pull stats from the database for each player, and insert them into a specified location on the scouting report.

```python
scoutteam = 'MER'
season = "2018-19"
playerstats = [[0,145,255],
               [1,21,54],
               [13,19,35],
               [23,24,37],
               [15,65,90],
               [4,10,15],
               [5,49,90],
               [14,3,3],
               [31,12,20]]
teampaint = [348, 599]

generatereport(scoutteam, season, playerstats, teampaint)
```
Descriptions for each player are not currently implemented ("This is a description" is just a placeholder), but there is work being done to add descriptions to the database. Eventually no user input will be needed outside of the stats.

## Template Files

Since a report will have a different number of players each time, the template files determine the locations of the text based on the number of players on a given report.

## Icon Logos and Player Portraits

These icons and player portraits are required for each generated report and were included based on the Merrimack example from above.

## Merrimack--scout.docx

Since the database is not hooked up, this file provides the generated report from the function call above.

In the future, the goal is to create this utility as a web app so coaches can use it without the need for Python.
