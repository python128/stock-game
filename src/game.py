# This is a game about stock prices.

# Imports
from jugaad_data.nse import NSELive # To get data
from colorama import Fore, init
from bs4 import BeautifulSoup as bs # To parse data
import csv # Some help with csv formats
import pandas as pd # Some more help with csv
from tabulate import tabulate # To tabulate data(portfolio & logs)
from datetime import datetime as dt # For log msgs
import sys # To exit

init(autoreset=True)
##########################################
###  Time - Log Messages - Bank Loans  ###
##########################################
# Function to get time for portfolio
def get_time():
    return str(dt.now().strftime("%d/%m/%Y %H:%M:%S"))
    
# Logs actions
def log(msg):
    with open("log.txt", "a") as logfile:
        logfile.write("{}\n".format(msg))
    return ""
    
# Reads the log file
def read_log():
    with open("log.txt", "r") as logfile:
        reader = csv.reader(logfile)
        data = []
        for row in reader:
            data.append(row)
        return data[1:][::-1] # [::-1] reverses the order
        
# Basic loan to start with
def loan():
    cash = get_cash()
    ports = get_ports()
    logs = read_log()
    if cash == 0 and ports == [] and logs == []:
        msg = "You don't have any money to start with. The bank will provide you with ⏣ 5000 to start. \n\
As an added bonus, you don't need to pay this ⏣ 5000 back to us!"
        update_cash(5000)
        return msg
        
    elif cash > 0 and ports == []:
        return "You have some cash! Invest them in promising stocks to earn some money.⏣ "
        
    else:
        return "You don't require a loan right now!"
        
def help_msg():
    msg = """
        This is a Help Message.
        ~ Commands:
         - "fs <stock>": Find rate of specified stock.
         - "bal": Gives your balance.
         - "port": Shows your portfolio.
         - "buy <stock> <num of shares>": Buys <num of shares> <stock> from the stock market.
         - "sell <stock> <num of shares>": Sells <num of shares> from <stock> to the market.
         - "loan": Gets you your first loan of ⏣ 5000 with no interest and no back pay.
         - "log": Shows your logs, i.e. what all you bought/sold, at which time, at which rate, etc.
         - "comp <stock>": Compares your stock with the real time market. Shows your losses or gains.
         - "help": Shows this help message.
         - "exit": Exits the game cleanly; ^C also works.
         - "quit": Same as 'exit'
        
         Run "loan" to start.
        
        ~ Aim:
         This is basically a project which helps people to buy and sell shares, without investing their actual money.
         So, this has no risks. However, if you win, you get nothing, but, if you lose, you lose nothing!
         Essentially, this is like a simulation, with all actual prices. 
         You have to go to https://google.com/finance to check fluctuations, good stocks, etc. 
         My code only gives the rate as of now.
        
         One can easily edit the files to show their portfolios as more, and make their cash extremely high.
         I know this, and if you want you can do this. However, the game is meant for practice, not fooling.
         If you do so, it's basically your loss.
    """
    return msg
    
def comp(stock):
    data = get_ports()
    stocks = []
    for val in data:
        if val['stock'] == stock.upper(): 
            oldrate = val['rate']
            shares = val['shares']
        stocks.append(val['stock'])
    
    # table = []
    # headers = ["Old Rate", "Current Rate", "Profit/Loss"] 
    if stock.upper() in stocks:
        newrate = get_rate(stock)
        # table.append(oldrate); table.append(newrate); table.append(str(float(newrate)-float(oldrate)))
        # final = dict(zip(headers, table))
        # return tabulate(final, headers="keys", tablefmt="fancy_grid")
        return "--- {} ---\nOld Rate: {}\nCurrent Rate: {}\nProfit/Loss: {}".format(stock.upper(), oldrate, newrate, newrate-oldrate)
    
###########################################
### Info from Internet(Google Finanace) ###
###########################################
# Function to get data of stock
def get_data(stock):
    n = NSELive()
    q = n.stock_quote(stock.upper())
    data = q['priceInfo']['lastPrice']
    return "{} => {}".format(stock, data)
        
# Function to return only the rate
def get_rate(stock):
    n = NSELive()
    q = n.stock_quote(stock.upper())
    data = q['priceInfo']['lastPrice']
    return data
        
###########################################
###        Buying/Selling shares        ###
###########################################
# Function to buy shares
def buy_shares(cash, stock, num):
    try: stock = stock.strip().upper()
    except ValueError: return "Please provide proper data."
    if not get_data(stock):
        return "That stock is not present."
    rate = get_rate(stock)
    
    stocks = []
    new_list = []
    data = get_ports()
    for val in data:
        if val['stock'] == stock: idx = data.index(val)
        if val['stock'] != stock: new_list.append(val)
        stocks.append(val['stock'])

    try: num = float(int(num))
    except ValueError: return "Please provide a valid number"
    if num <= 0: return "You can't buy {} shares!".format(num)

    if cash - rate*num > 0:
        confirm = input(">> Are you sure you want to buy {} shares of {} for ⏣ {}[⏣ {} per share]?(y/n) ".format(int(num), stock, rate*num, rate))
        if confirm == "y":
            if stock in stocks:
                data[idx]['shares'] += num
                data[idx]['rate'] = (data[idx]['rate'] + rate) / 2
                data[idx]['amt'] += data[idx]['rate'] * data[idx]['shares']
                new_list.append(data[idx])
            elif stock not in stocks:
                new_dict = {"stock":stock, "rate":rate, "shares":int(num), "amt":rate*num}
                new_list.append(new_dict)
            cash -= rate*num
            update_cash(cash)
            write_ports(new_list)
            log("{},{},{},{},{},{}".format(get_time(),"Buy", stock, int(num), rate, num*rate))
            return ">> Bought {} shares of {} stock for ⏣ {} \nYou have ⏣ {} remaining.".format(int(num), stock, rate*num, cash)
        else:
            return ">> Alright, not buying it"
    else:
        return ">> You need more money to buy {} shares of {} stock.".format(int(num), stock)
        
# Function to sell shares
def sell_shares(cash, stock, num):
    stock = stock.upper().strip()
    try: share_num = float(int(num))
    except ValueError: return "Please provide a valid number."
    data = get_ports()
    rate = get_rate(stock)
    stocks = []
    new_list = []

    for val in data:
        if val['stock'] == stock: idx = data.index(val)
        if val['stock'] != stock: new_list.append(val)
        stocks.append(val['stock'])
    
    try: num = data[idx]['shares']
    except UnboundLocalError: num = 0
    try: oldrate = data[idx]['rate']
    except UnboundLocalError: oldrate = 0

    if stock in stocks and share_num <= num and share_num > 0:
        confirm = input(">> Are you sure you want to sell {} share(s) of {} stock for ⏣ {}[⏣ {} per share]?(y/n) ".format(int(share_num), stock, rate*share_num, rate))
        if confirm == "y":
            if share_num < num:
                data[idx]['shares'] -= int(share_num)
                new_list.append(data[idx])
            cash += rate*int(share_num)
            write_ports(new_list)
            update_cash(cash)
            log("{},{},{},{},{},{}".format(get_time(),"Sell", stock, int(share_num), rate, share_num*rate))
            return "Sold {} share(s) of {} stock for ⏣ {}.\nYou gained ⏣ {}".format(int(share_num), stock, share_num*rate, (rate-oldrate)*share_num)
        else:
            return "Ok, keeping it."
    elif stock not in stocks:
        return "You don't own {} stock.".format(stock)
    elif share_num > num:
        return "You have only {} shares. You can't sell {} shares.".format(int(num), int(share_num))
    elif share_num < 0:
        return "You can't sell {} shares.".format(share_num)
        
##########################################
###      Functions with portfolio      ###
##########################################
# Function to get the portfolio data
def port_data():
    with open("port.csv", "r") as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            data.append(row)
        return data[1:]
        
# Function to get the portfolio data in a dictionary format to work with.
def get_ports():
    return pd.read_csv("port.csv").to_dict(orient="records")

# Rewrites the portfolio file(for updating when selling shares)
def write_ports(item):
    fields = ['stock', 'rate', 'shares', "amt"]
    with open('port.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames = fields)
        writer.writeheader()
        writer.writerows(item)
    return ""

###########################################
###        Functions with Cash          ###
###########################################
# Updates the cash
def update_cash(new_val):
    with open("cash.txt", "w") as file:
        file.write(str(new_val))
    return ""

# Gets the cash
def get_cash():
    with open("cash.txt", "r") as file:
        try: return round(float(file.read()), 2)
        except ValueError: update_cash(0.0)
        
###########################################
###            Actual Game              ###
###########################################
def game():
    cash = get_cash()
    cmd = input("~>> " + Fore.CYAN)
    print(Fore.WHITE, end="\r")
    if "fs" in cmd:
        stock = cmd.replace("fs", "").strip()
        if get_data(stock):
            return get_data(stock)
        else:
            return "That stock is not present."
    elif "bal" in cmd:
        return "⏣ " + str(cash)
    elif "port" in cmd:
        headers = ["Stock", "Avg Rate", "Shares", "cost"]
        if port_data() != []:
            table = port_data()
        else:
            return "You have no shares yet! Buy some!"
        return tabulate(table, headers, tablefmt="fancy_grid")
    elif "buy" in cmd:
        try: 
            li = list(cmd.split(" "))
            return buy_shares(cash, li[1], li[2])
        except IndexError: return "Please provide 2 arguments: buy <stock> <num. of shares>"
    elif "sell" in cmd:
        try: 
            li = list(cmd.split(" "))
            return sell_shares(cash, li[1], li[2])
        except IndexError: return "Please provide 2 arguments: sell <stock> <num. of shares>"
    elif "log" in cmd:
        headers = ["Date/Time", "Action", "Stock", "Shares", "Rate", "Price"]
        if read_log() != []:
            table = read_log()
        else:
            return "There is nothing in your logs! Do some activity, and you can see your logs."
        return tabulate(table, headers, tablefmt="fancy_grid")
    elif "loan" in cmd:
        return loan()
    elif "help" in cmd:
        return help_msg()
    elif "comp" in cmd:
        try:
            li = list(cmd.split(" "))
            return comp(li[1])
        except IndexError: return "Please provide 1 argument: comp <stock>"
    elif "exit" in cmd or "quit" in cmd:
        print("\x1b[6D" + Fore.MAGENTA + "Bye! Don't forget to see your stocks soon!")
        sys.exit(0)
    else:
        return ""
    
    
if __name__ == "__main__":
    print(Fore.MAGENTA + "Welcome to stock-game! Type `help` for help")
    while True:
        try:
            print(game())
        except KeyboardInterrupt:
            print("\x1b[6D" + Fore.MAGENTA + "Bye! Don't forget to see your stocks soon!")
            sys.exit(0)