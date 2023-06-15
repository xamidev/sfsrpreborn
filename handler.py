import sqlite3
import os.path
import threading

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "stocks.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

except sqlite3.Error as error:
    print("Sqlite Error!", error)

"""def getUserBalance(id):
    return cur.execute(f"SELECT balance FROM balances WHERE discordid = '{id}';").fetchall()"""

def getUserBalance(id):
    cur.execute(f"SELECT balance FROM balances WHERE discordid = '{id}';")
    result = cur.fetchone()
    if result:
        return float(result[0])
    else:
        return 0.0

def transferMoney(authorid, recieverid, amount):
    cur.execute(f"UPDATE balances SET balance = '{float(getUserBalance(authorid))-float(amount)}' WHERE discordid = '{authorid}';")
    cur.execute(f"UPDATE balances SET balance = '{float(getUserBalance(recieverid))+float(amount)}' WHERE discordid = '{recieverid}';")
    conn.commit()

def createAgency(authorid, name, ticker, prix):
    cur.execute(f"UPDATE balances SET balance = '{float(getUserBalance(authorid))-float(prix)}' WHERE discordid = '{authorid}';")
    cur.execute(f"INSERT INTO agencies (agencyname, agencyticker, moneyamount, chiefdiscordid) VALUES ('{name}', '{ticker}', '{prix/2}', '{authorid}');")
    cur.execute(f"INSERT INTO stockexchange (ticker, value, availparts) VALUES ('{ticker}', '{prix/2}', '100');")
    conn.commit()

def getBaltop():
    cur.execute(f"SELECT balance, discordid from balances ORDER BY balance DESC")
    #cur.execute(f"SELECT balance FROM balances ORDER BY balance DESC")
    result = cur.fetchall()
    return result

def getAgtop():
    cur.execute(f"SELECT value, ticker from stockexchange ORDER BY value DESC")
    result = cur.fetchall()
    return result

def getAgencyValue(ticker):
    cur.execute(f"SELECT value from stockexchange WHERE ticker = '{ticker}';")
    result = cur.fetchall()
    return result

def getAgencyPastValues(ticker):
    cur.execute(f"SELECT pastvalues from stockexchange WHERE ticker = '{ticker}';")
    result = cur.fetchall()
    return result

def getAgencyParts(ticker):
    cur.execute(f"SELECT value, availparts from stockexchange WHERE ticker = '{ticker}';")
    result = cur.fetchall()
    return result[0]

def getAgencyName(ticker):
    cur.execute(f"SELECT agencyname from agencies WHERE agencyticker = '{ticker}';")
    result = cur.fetchall()
    return result[0]

def refreshPartsBuy(ticker, parts):
    cur.execute(f"UPDATE stockexchange SET availparts = '{int(getAgencyParts(ticker.upper())[1])-parts}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshAgencyValueBuy(ticker, cost):
    cur.execute(f"UPDATE stockexchange SET value = '{round(float(getAgencyValue(ticker.upper())[0][0])+cost*0.05,2)}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

"""def refreshBalanceBuy(id, cost):
    cur.execute(f"UPDATE balances SET balance = '{round(float(getUserBalance(id))-float(cost), 2)}' WHERE discordid = '{id}';")
    conn.commit()"""

def refreshBalanceBuy(id, cost):
    balance = getUserBalance(id)
    if isinstance(cost, (int, float)):
        new_balance = round(balance - cost, 2)
        cur.execute(f"UPDATE balances SET balance = '{new_balance}' WHERE discordid = '{id}';")
        conn.commit()
    else:
        print(f"Error: cost must be a number, not {type(cost)}")

def refreshPortfolioBuy(id, parts, ticker):
    alreadyparts = cur.execute(f"SELECT * from acquisitions WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    result = cur.fetchall()
    alreadyparts = result
    if alreadyparts:
        cur.execute(f"UPDATE acquisitions SET parts = '{int(result[0][2])+int(parts)}' WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    else:
        cur.execute(f"INSERT INTO acquisitions (discordid, ticker, parts) VALUES ('{id}', '{ticker.upper()}', '{parts}')")
    conn.commit()

def getAcquisitions(id):
    cur.execute(f"SELECT * from acquisitions WHERE discordid = '{id}'")
    result = cur.fetchall()
    return result

def getOwners(ticker):
    cur.execute(f"SELECT * from acquisitions WHERE ticker = '{ticker.upper()}' ORDER BY parts DESC;")
    result = cur.fetchall()
    return result

def getUserAccount(id):
    cur.execute(f"SELECT * from balances WHERE discordid = '{id}'")
    result = cur.fetchall()
    return result

def createAccount(id):
    cur.execute(f"INSERT INTO balances (discordid, balance) VALUES ('{id}', '0')")
    conn.commit()

def getAllAgenciesValues():
    cur.execute("SELECT * from stockexchange ORDER BY value DESC")
    result = cur.fetchall()
    return result

def isUserChief(id):
    cur.execute(f"SELECT * from agencies WHERE chiefdiscordid = '{id}';")
    result = cur.fetchall()
    return result

# https://www.chartjs.org/docs/2.9.4/charts/doughnut.html

#séparer tout en classes
#classe errorhandling

def refreshPartsSell(ticker, parts):
    cur.execute(f"UPDATE stockexchange SET availparts = '{int(getAgencyParts(ticker.upper())[1])+parts}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshAgencyValueSell(ticker, cost):
    cur.execute(f"UPDATE stockexchange SET value = '{round(float(getAgencyValue(ticker.upper())[0][0])-cost*0.05,2)}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshBalanceSell(id, cost):
    cur.execute(f"UPDATE balances SET balance = '{round(float(getUserBalance(id))+float(cost), 2)}' WHERE discordid = '{id}';")
    conn.commit()

def refreshPortfolioSell(id, parts, ticker):
    alreadyparts = cur.execute(f"SELECT * from acquisitions WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    result = cur.fetchall()
    cur.execute(f"UPDATE acquisitions SET parts = '{int(result[0][2])-int(parts)}' WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    conn.commit()

def getUserParts(id, ticker):
    cur.execute(f"SELECT parts from acquisitions WHERE discordid = '{id}' AND ticker = '{ticker}';")
    result = cur.fetchall()
    return result

def getAgencyMoney(ticker):
    cur.execute(f"SELECT moneyamount from agencies WHERE agencyticker = '{ticker}'")
    result = cur.fetchall()
    return result

def updateAgencyBalance(ticker, money):
    cur.execute(f"UPDATE agencies SET moneyamount = '{float(money)}' WHERE agencyticker = '{ticker}'")
    conn.commit()

# MECHANICS SECTION

def getAgenciesBalances():
    cur.execute(f"SELECT * from agencies ORDER BY moneyamount DESC")
    result = cur.fetchall()
    return result

def getAgenciesStockExchangeInfo():
    cur.execute(f"SELECT * from stockexchange ORDER BY value DESC")
    result = cur.fetchall()
    return result

def updatePastValues(ticker, pastvalueslist, partvalue):
    cur.execute(f"UPDATE stockexchange SET pastvalues = \"{pastvalueslist}\" WHERE ticker = '{ticker}';")
    cur.execute(f"UPDATE stockexchange SET value = '{partvalue}' WHERE ticker = '{ticker}';")
    conn.commit()