# This is a game about stock prices.

# Imports
from jugaad_data.nse import NSELive # To get data
import time, random
import readline
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
         - "work": A small minigame to earn some money! You can run this command every 10 minutes.
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
    
         Transaction cost(Txn Cost) is 1% of your transaction, which will automatically be deducted.
        
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

def comp_port():
    headers = ["Stock", "Avg Rate", "Shares", "Cost", "Current Rate", "P&L per share", "Txn Cost", "Total P&L"]
    if port_data() != []:
        table = port_data()
        ftable = [] #Final Table
        adds = [] # Things to add up
        inv_amt = []
        cur_amt = []
        for val in table:
            cur_rate = get_rate(val[0])
            profs = cur_rate - float(val[1])
            tax = deduct_tax(float(val[3]), println=False) * -2
            totalprof = float(val[2]) * float(profs) + tax

            val.append(cur_rate)
            val.append(add_color(profs))
            val.append(add_color(tax))
            val.append(add_color(totalprof))

            ftable.append(val)
            adds.append(float(totalprof))
            inv_amt.append(float(val[3]))
            cur_amt.append(float(val[4]) * float(val[2]))
        
        invested = sum(inv_amt)
        current = sum(cur_amt)
        pl = add_color(round(sum(adds), 2))
    else:
        return "You have no shares yet! Buy some!"
    return tabulate(ftable, headers, tablefmt="fancy_grid", numalign="right") + f"\nTotal: ⏣ {pl}\n\nInvested: ⏣ {invested}\nCurrent Amount: ⏣ {current}"
        
def add_color(num):
    if num < 0:
        return Fore.RED + f"{num}" + Fore.RESET
    elif num > 0:
        return Fore.GREEN + f"{num}" + Fore.RESET
    elif num == 0:
        return f"{num}"
    else:
        return ""

def deduct_tax(amt, stock=None, println=True):
    tax = round(amt * 1/100, 2)
    if println and stock != None:
        print(Fore.YELLOW + f"=== A transaction cost of {tax} has been deducted from your account.[{stock}]" + Fore.RESET)
    elif println and stock == None:
        print(Fore.YELLOW + f"=== A transaction cost of {tax} has been deducted from your account." + Fore.RESET)
    return tax

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
        confirm = input("   Stock: {}\n   Shares: {}\n   Rate: {}\n   Price: {}\n   Txn Cost: {}\nDo you want to buy this?(y/n) ".format(stock, int(num), rate, rate*num, deduct_tax(rate*num, println=False)))
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
            amt = deduct_tax(rate*num, stock)
            cash -= amt
            update_cash(cash)
            write_ports(new_list)
            log("{},{},{},{},⏣ {},⏣ {},⏣ {},-".format(get_time(),"Buy", stock, int(num), rate, round(num*rate, 2), round(cash, 2)))
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
        confirm = input("   Stock: {}\n   Shares: {}\n   Rate: {}\n   Price: {}\n   Txn Cost: {}\nDo you want to sell this?(y/n) ".format(stock, int(share_num), rate, rate*share_num, deduct_tax(rate*share_num, println=False)))
        if confirm == "y":
            if share_num < num:
                data[idx]['shares'] -= int(share_num)
                new_list.append(data[idx])
            cash += rate*int(share_num)
            amt = deduct_tax(rate*int(share_num), stock)
            cash -= amt
            write_ports(new_list)
            update_cash(cash)
            log("{},{},{},{},⏣ {},⏣ {},⏣ {},⏣ {}".format(get_time(),"Sell", stock, int(share_num), round(rate, 2), round(share_num*rate, 2), round(cash, 2), add_color(round(float(share_num)*rate - float(share_num)*oldrate, 2))))
            if (rate-oldrate)*share_num > 0:
                pl = "gained" # Profit/Loss
            elif (rate-oldrate)*share_num < 0:
                pl = "lost"
            elif (rate-oldrate)*share_num == 0:
                pl = "lost/gained"
            else:
                pl = ""
            return "Sold {} share(s) of {} stock for ⏣ {}.\nYou {} ⏣ {}\nYour balance is now ⏣ {}.".format(int(share_num), stock, share_num*rate, pl, add_color((rate-oldrate)*share_num), cash)
        else:
            return "Ok, keeping it."
    elif stock not in stocks:
        return "You don't own {} stock.".format(stock)
    elif share_num > num:
        return "You have only {} shares. You can't sell {} shares.".format(int(num), int(share_num))
    elif share_num < 0:
        return "You can't sell {} shares.".format(share_num)
        
def sell_all_shares(cash):
    oldcash = cash
    data_ = get_ports()
    shares_l = []
    stocks_l = []

    for val in data_:
        stocks_l.append(val['stock'])
        shares_l.append(val['shares'])
        data = dict(zip(stocks_l, shares_l))
    
    confirm = input("Are you sure you want to sell EVERYTHING in your portfolio?(y/n) ")
    if confirm == "y":
        for stock, share in data.items():
            rate = get_rate(stock)
            cash += rate*share
            amt = deduct_tax(rate*share, stock)
            cash -= amt
            log("{},{},{},{},⏣ {},⏣ {},⏣ {}, - ".format(get_time(),"Sell", stock, int(share), round(rate, 2), round(share*rate, 2), round(cash, 2)))
            
        update_cash(cash)
        write_ports({})
        return f"Sold:\n- {len(stocks_l)} stocks.\n- {int(sum(shares_l))} shares.\n- Earned ⏣ {cash - oldcash}.\n- Balance is now ⏣ {cash}."
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
        file.write(f"{new_val}")
    return ""

# Gets the cash
def get_cash():
    with open("cash.txt", "r") as file:
        try: return round(float(file.read()), 2)
        except ValueError: update_cash(0.0)

# Updates the cash
def update_work():
    with open("work.txt", "w") as file:
        newtime = str(dt.now().strftime("%d/%m/%Y %H:%M:%S"))
        file.write(f"{newtime}")
    return ""

# Gets the cash
def get_work():
    with open("work.txt", "r") as file:
        try: return file.read()
        except: update_work(); return file.read()

def work(cash):
    with open("text.txt", "r") as file:
        text = file.read().strip().split("\n")
    
    print("\033[4mWork\033[0m: Type the following sentences and hit return!")
    t = 3
    while t > 0:
        print(t, end=""); time.sleep(1); print("\r", end="\r")
        t -= 1
    
    correct = 0
    fails = 0
    for i in range(3):
        choice = random.choice(text)
        print(choice)
        inp = input(Fore.YELLOW + f"{i+1}>> " + Fore.RESET)
        if inp == choice:
            print(Fore.GREEN + "Nice! You typed perfectly!\n" + Fore.RESET)
            correct += 1
        else:
            print(Fore.RED + "Oh no! You made an error!\n" + Fore.RESET)
            fails += 1
    
    earned = correct*100 + fails*25
    cash += earned
    update_cash(cash)
    update_work()
    
    if correct == 3: praise = "Great! 3/3!"
    elif correct == 2: praise = "Good job! 2/3!"
    elif correct == 1: praise = "Not bad... 1/3"
    elif correct == 0: praise = "Uh.. You didn't do any one correctly. :(\nBetter luck next time!\nHint: Pay attention to capital letters and punctuation."
    else: praise = ""
    return f"{praise}\nSuccesses: {correct} (* ⏣ 100)\nFails: {fails} (* ⏣ 25)\nMoney earned: ⏣ {earned}\nBalance: ⏣ {cash}"

###########################################
###            Actual Game              ###
###########################################
def game():
    cash = get_cash()
    work_time = get_work()
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
        return comp_port()
        
    elif "buy" in cmd:
        try: 
            li = list(cmd.split(" "))
            return buy_shares(cash, li[1], li[2])
        except IndexError: return "Please provide 2 arguments: buy <stock> <num. of shares>"

    elif ["sell", "--all"] == list(cmd.split(" ")):
        return sell_all_shares(cash)

    elif "sell" == list(cmd.split(" "))[0]:
        try: 
            li = list(cmd.split(" "))
            return sell_shares(cash, li[1], li[2])
        except IndexError: return "Please provide 2 arguments: sell <stock> <num. of shares>"
        
    elif "log" == cmd.strip():
        headers = ["Date/Time", "Action", "Stock", "Shares", "Rate", "Price", "Balance", "P&L"]
        if read_log() != []:
            table = read_log()
        else:
            return "There is nothing in your logs! Do some activity, and you can see your logs."
        return tabulate(table, headers, tablefmt="fancy_grid", numalign="right")

    elif "log --all" in cmd:
        headers = ["Date/Time", "Action", "Stock", "Shares", "Rate", "Price", "Balance", "P&L"]
        table = []
        if read_log() != []:
            if len(read_log(full=True)) > 30:
                confirm = input("Are you sure? This will take up a lot of space, and time.(y/n) ")
                if confirm == "y": table = read_log(full=True)
                else: return "\033[F"
            else:
                table = read_log(full=True)
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
        print("\033[2K\r" + Fore.MAGENTA + "Bye! Don't forget to see your stocks soon!")
        sys.exit(0)

    elif "work" in cmd:
        wait_time = dt.strptime(work_time, "%d/%m/%Y %H:%M:%S") + datetime.timedelta(minutes=1)
        if wait_time <= dt.now():
            return work(cash)
        else:
            min = str(wait_time-dt.now()).split('.')[0].split(':')[1].lstrip("0")
            sec = str(wait_time-dt.now()).split('.')[0].split(':')[2].lstrip("0")
            if min != "": min_var = " minutes "
            else: min_var = ""
            return f"You need to wait for {min}{min_var}{sec} seconds more to work again..."

    else:
        return "\033[F"

    
if __name__ == "__main__":
    print(Fore.MAGENTA + "Welcome to stock-game! Type `help` for help")
    if calc_se(): print(Fore.GREEN + "Stock market is OPEN.")
    else: print(Fore.RED + "Stock market is CLOSED.")
    while True:
        try:
            print(game())
        except KeyboardInterrupt:
            print("\033[2K\r" + Fore.MAGENTA + "Bye! Don't forget to see your stocks soon!")
            sys.exit(0)