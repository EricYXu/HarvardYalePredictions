Youtube Link to Demo: https://youtu.be/CjpDRYZStRo

This is the sportsbook for the biggest football game of the year, Harvard vs. Yale. This is meant to be a way for students and trusted adults to place bets on the game. Our application 
provides features such as real-time betting lines, user balance tracking, and historical game statistics and utilizes Flask, Socket.IO, SQLite, and Bootstrap for a seamless and interactive 
user experience.

TLDR How to use our website:
- type flask run in the terminal under the right directory
- open the link
- loaded to front page
- If you have an account, login. Else, register as a new user.
- Once you are logged in, you will see a dashboard, that allows you to practice bet on certain things
- Either choose to play around, or go to the stats page
- On the stats page, you will be prompted to input years into our website, and follow instructions to do that
- click on the ESPN link
- Make a betting decision based on what you see from previous games
- Look at the betting lines on all bets page.
- Place bet on the live betting page, and if you want to bet more than the amount in the account right now, you can input more money. You can also select what you want to bet on, as there are 3 options, Over/Under, Moneyline, and Spread
- Place bet, and then see the bet on all bets. If other people have bet when you are utilizing the website, it will show up and you can see
- Log out after betting, or place more than one bet

In order to run the code, you will need to download the libraries in the requirements.txt file, using pip, as well as have Python, PIP, and SQLite downloaded. You can install these using 
pip install __. Now that you are all situated to run the code, clone the repository from github into your codespace. Now, simply type flask run into the terminal and there will be a link that 
pops up. After that, you will be able to see a home page pop up, with options of registering, or logging in. Also on the home page, you will see a button to register. Click that, and register so
you can log in. You will also see that the number of users using our sportsbook increased by 1. Now, log into the page, and you will be greeted with new buttons. 

If you are simply here to explore the website, your dashboard will show you how much money you have, your usernames, and some fun questions to ponder about. These are simply fun questions, not 
anything to bet on. This is for you as the user to enjoy. Now, moving on, you can also go to the stats page, and look at stats from previous years. Type in a year from 2010-2024, and an ESPN 
button will pop up and guide you to the game stats. 

Lastly, you have the option to place a bet, which is done on the place bets page. This will allow you to bet as much money as you want to, though we restrict each account to 1000 dollars to 
promote healthy betting, and not spending so much money. The user has the option to enter as much money to bet given the current betting lines. The user also has a drop down menu to select what 
type of line they want to bet. The bet will then be posted on the view bets tab, which can be viewed by clicking on it. This page has the current moneylines for each type of bet, as well as your
bet and everyone else's bet, and is updated live. This allows you to see if the community agrees with your bet.
