# NE10 Box Score to Recap to Tweet

This python script was created as part of a project for CSC 571 Big Data Programming.

The idea was to take some data, in this case a single game box score, and manipulate it to get a desired output, a full game recap.

In its current form, it is set to just print the recap, and should run without issue on Python 3.6. For security reasons, the Twitter code is commented out, but with the proper keys is able to post directly to the account.

The results for a few games can be seen at [@NE10MBBRecaps](http://twitter.com/ne10mbbrecaps) on Twitter.

As this project was created before the existence of the D2 East Database, it was originally created using direct links to the NE10 website. It also works with ECC box scores, but will need additional work to be compatible with CACC box scores.

## Brief Code Overview

The code can be broken down essentially into two functions - teamtodf() and generateSentences().

teamtodf() takes a box score ([sample](http://www.northeast10.org/sports/mbkb/2017-18/boxscores/20180110_u3ny.xml)) and stores players and statistics in a pandas dataframe that can be easily manipulated.

generateSentences() takes this newly created dataframe and interprets the result, as well as players of interest on both the winning and losing team. Considering the recaps will be posted to Twitter, there is also logic to randomize some of the wording to make multiple recaps sound less robotic and structured. 

Future work on this project will be done to create even more randomization so very few recaps look the same, and in a perfect world would come close to mirroring actual human output. Also, with more work, it is expected that the bot will some day work directly off of the database instead of using links from outside sources.
