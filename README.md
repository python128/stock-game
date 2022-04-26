# `stock-game`
A simple simulation of a stock market without investing real money.

<details> <summary> Gif of the game </summary>

![Video for game](./stock_game2.gif)

</details>
  
## Installation
- Clone the github repo(`git clone https://github.com/python128/stock-game.git`)
- In your terminal, run: 
  ```sh
  pip install -r requirements.txt
  OR 
  pip3 install -r requirements.txt
  ```
- This will install all the required dependancies.
Now you are ready to start!

<details> <summary> More Data </summary>
  
  #### Modules Used
  - BeautifulSoup4
  - colorama
  - jugaad_data
  - pandas
  - tabulate
</details>

## The Game
This game is fairy straightforward.

> FYI, this works with only NSE of India due to `Jugaad_data`.
> I use it since it is obviously faster. (2.3s[before] vs 0.01s[after])

Run `python game.py` OR `python3 game.py` in the `src/` folder.
A prompt as such will appear.
```
~>> 
```
You can now type in some commands.

Here are the commands.
```
- "fs <stock>": Find rate of specified stock.
- "bal": Gives your balance.
- "port": Shows your portfolio.
- "buy <stock> <num of shares>": Buys <num of shares> <stock> from the stock market.
- "sell <stock> <num of shares>": Sells <num of shares> from <stock> to the market.
- "loan": Gets you your first loan of ⏣ 5000 with no interest and no back pay.
- "log": Shows your logs, i.e. what all you bought/sold, at which time, at which rate, etc.
- "comp <stock>": Compares your stock with the real time market. Shows your losses or gains.
- "help": Shows this help message.
- "exit": Exits the game cleanly; ^C(ctrl+c) also works.
- "quit": Same as 'exit'
```
  
You can get more info by typing `help`.
To exit, type either `exit` or `quit`. You can also press <kbd>Ctrl+C</kbd>

  
Data is collected from [jugaad_data](https://github.com/jugaad-py/jugaad-data).
