# This is a game about stock prices.

# Imports
from jugaad_data.nse import NSELive # To get data
from colorama import Fore, init
from bs4 import BeautifulSoup as bs # To parse data
import csv # Some help with csv formats
import pandas as pd # Some more help with csv
from tabulate import tabulate # To tabulate data(portfolio & logs)
from datetime import datetime as dt # For log msgs
import datetime
import sys # To exit

init(autoreset=True)
##########################################
###  Time - Log Messages - Bank Loans  ###
##########################################
# Function to get time for portfolio
def get_time():
    return str(dt.now().strftime("%d/%m/%Y %H:%M:%S"))
    
def calc_se():
    day = str(dt.today().strftime("%A"))
    x = dt.now().time()
    time = datetime.timedelta(hours=x.hour, minutes=x.minute)
    start = datetime.timedelta(hours=9, minutes=15)
    end = datetime.timedelta(hours=15, minutes=30)
        
    if day == "Saturday" or day == "Sunday":
        return False
    else:
        if start < time < end:
            return True
        else:
            return False
    
# Logs actions
def log(msg):
    with open("log.txt", "a") as logfile:
        logfile.write("{}\n".format(msg))
    return ""
    
# Reads the log file
def read_log(full=False):
    with open("log.txt", "r") as logfile:
        reader = csv.reader(logfile)
        data = []
        for row in reader:
            data.append(row)
        if full:
            return data[1:][::-1]
        else:
            return data[1:][::-1][:10] # [::-1] reverses the order
        
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
        return "You have some cash! Invest them in promising stocks to earn some money ⏣ ."
        
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
         - "sell --all": Sells all of your shares.
         - "loan": Gets you your first loan of ⏣ 5000 with no interest and no back pay.
         - "log": Shows your logs(only 10 newest), i.e. what all you bought/sold, at which time, at which rate, etc.
         - "log --all": Shows all of your logs. Might take some time, and lots of space in your terminal.
         - "comp <stock>": Compares your stock with the real time market. Shows your losses or gains.
         - "comp --port": Compares your entire portfolio with current rates.
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
    
    if stock.upper() in stocks:
        newrate = get_rate(stock)
        return "--- {} ---\nOld Rate: {}\nCurrent Rate: {}\nProfit/Loss: ⏣ {}\nNum. of Shares: {}\nTotal profit/loss: ⏣ {}".format(Fore.MAGENTA + stock.upper() + Fore.RESET, oldrate, newrate, add_color(newrate-oldrate), shares, add_color(newrate*shares-oldrate*shares))
    else:
        return f"You don't own {stock.upper()} stock."
        
def add_color(num):
    if num < 0:
        return Fore.RED + f"{num}" + Fore.RESET
    elif num > 0:
        return Fore.GREEN + f"{num}" + Fore.RESET
    elif num == 0:
        return f"{num}"
    else:
        return ""
        
def add_coin(num):
    return f"⏣ {num}"
        
###########################################
### Info from Internet(Google Finanace) ###
###########################################
# Function to get data of stock
def get_data(stock):
    try:
        n = NSELive()
        q = n.stock_quote(stock.upper())
        data = q['priceInfo']['lastPrice']
        return "{} => ⏣ {}".format(stock, data)
    except:
        return False
        
# Function to return only the rate
def get_rate(stock):
    try:
        n = NSELive()
        q = n.stock_quote(stock.upper())
        data = q['priceInfo']['lastPrice']
        return float(data)
    except:
        return 0
        
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
            log("{},{},{},{},⏣ {},⏣ {},⏣ {},-".format(get_time(),"Buy", stock, int(num), rate, num*rate, cash))
            return ">> Bought {} shares of {} stock for ⏣ {} \nYou have ⏣ {} remaining.".format(int(num), stock, rate*num, cash)
        else:
            return ">> Alright, not buying it"
    else:
        return ">> You need (⏣ {}) more money to buy {} shares of {} stock.".format(num*rate-cash, int(num), stock)
        
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
        if val['stock'] == stock: 
            idx = data.index(val)
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
            log("{},{},{},{},⏣ {},⏣ {},⏣ {},⏣ {}".format(get_time(),"Sell", stock, int(share_num), rate, share_num*rate, cash, add_color(float(share_num)*rate - float(share_num)*oldrate)))
            if (rate-oldrate)*share_num > 0:
                pl = "gained" # Profit/Loss
            elif (rate-oldrate)*share_num < 0:
                pl = "lost"
            elif (rate-oldrate)*share_num == 0:
                pl = "lost/gained"
            else:
                pl = ""
            return "Sold {} share(s) of {} stock for ⏣ {}.\nYou {} ⏣ {}\nYour balance is now ⏣ {cash}.".format(int(share_num), stock, share_num*rate, pl, add_color((rate-oldrate)*share_num))
        else:
            return "Ok, keeping it."
    elif stock not in stocks:
        return "You don't own {} stock.".format(stock)
    elif share_num > num:
        return "You have only {} shares. You can't sell {} shares.".format(int(num), int(share_num))
    elif share_num < 0:
        return "You can't sell {} shares.".format(share_num)
        
def sell_all_shares(cash):
    data = get_ports()
    total_l = []
    shares_l = []
    oldcash = cash

    for val in data:
        total_l.append(val['amt'])
        shares_l.append(val['shares'])
        
    total = sum(total_l)
    shares = sum(shares_l)
    cash += total    
    
    confirm = input("Are you sure you want to sell EVERYTHING in your portfolio?(y/n) ")
    if confirm == "y":
        update_cash(cash)
        write_ports({})
        log(f"{get_time()},Sell,Everything,{shares},-,{total},{cash},-")
        return f"Sold {shares} shares, for a total of {total}.\nYour balance is now ⏣ {cash}."
    else:
        return "Ok!"
        
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

    elif "port" == list(cmd.split(" "))[0]:
        headers = ["Stock", "Avg Rate", "Shares", "Cost"]
        if port_data() != []:
            table = port_data()
        else:
            return "You have no shares yet! Buy some!"
        return tabulate(table, headers, tablefmt="fancy_grid", numalign="right")

    elif "comp --port" in cmd:
        headers = ["Stock", "Avg Rate", "Shares", "Cost", "Current Rate", "Profit/Loss(per share)", "Total Profit/Loss"]
        if port_data() != []:
            table = port_data()
            ftable = []
            adds = []
            for val in table:
                val.append(get_rate(val[0]))
                profs = float(val[4]) - float(val[1])
                val.append(add_color(profs))
                totalprof = float(val[2]) * float(profs)
                val.append(add_color(totalprof))
                ftable.append(val)
                adds.append(float(totalprof))
            pl = add_color(round(sum(adds), 2))
        else:
            return "You have no shares yet! Buy some!"
        return tabulate(ftable, headers, tablefmt="fancy_grid", numalign="right") + f"\nTotal: {pl}"

    elif "buy" in cmd:
        try: 
            li = list(cmd.split(" "))
            return buy_shares(cash, li[1], li[2])
        except IndexError: return "Please provide 2 arguments: buy <stock> <num. of shares>"

    elif "sell" == cmd.strip():
        try: 
            li = list(cmd.split(" "))
            return sell_shares(cash, li[1], li[2])
        except IndexError: return "Please provide 2 arguments: sell <stock> <num. of shares>"
        
    elif "sell --all" in cmd:
        return sell_all_shares(cash)

    elif "log" == cmd.strip():
        headers = ["Date/Time", "Action", "Stock", "Shares", "Rate", "Price", "Balance", "Profit/Loss"]
        if read_log() != []:
            table = read_log()
        else:
            return "There is nothing in your logs! Do some activity, and you can see your logs."
        return tabulate(table, headers, tablefmt="fancy_grid", numalign="right")

    elif "log --all" in cmd:
        headers = ["Date/Time", "Action", "Stock", "Shares", "Rate", "Price", "Balance", "Profit/Loss"]
        if read_log() != []:
            if len(read_log(full=True)) > 30:
                confirm = input("Are you sure? This will take up a lot of space, and time?(y/n) ")
                if confirm == "y": table = read_log(full=True)
                else: return "\033[F"
        else:
            return "There is nothing in your logs! Do some activity, and you can see your logs."
        return tabulate(table, headers, tablefmt="fancy_grid", numalign="right")

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
        print("\033[F\r" + Fore.MAGENTA + "Bye! Don't forget to see your stocks soon!")
        sys.exit(0)

    else:
        return "\033[F"
    
    
if __name__ == "__main__":
    print(Fore.MAGENTA + "Welcome to stock-game! Type `help` for help")
    if calc_se():
        print(Fore.GREEN + "Stock market is OPEN.")
    else:
        print(Fore.RED + "Stock market is CLOSED.")
    while True:
        try:
            print(game())
        except KeyboardInterrupt:
            print("\r" + Fore.MAGENTA + "Bye! Don't forget to see your stocks soon!")
            sys.exit(0)