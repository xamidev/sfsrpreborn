import sqlite3
import os.path

#                                                    ___________________
#___________________________________________________|   DB CONNECTION   |______________________________________________________________________________________
#                                                   |___________________|

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "stocks.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

except sqlite3.Error as error:
    print("Sqlite Error!", error)

#                                                    ___________________
#___________________________________________________|   MAIN DB CALLS   |______________________________________________________________________________________
#                                                   |___________________|

def getUserBalance(id):
    """
    Renvoie le solde d'un utilisateur.

    :param id: (int) id de l'utilisateur
    :param return: (float) solde de l'utilisateur
    """
    #assert type(id) is int, "L'id utilisateur n'est pas de type int"

    cur.execute(f"SELECT balance FROM balances WHERE discordid = '{id}';")
    result = cur.fetchone()
    if result:
        return float(result[0])
    else:
        return 0.0

def transferMoney(authorid, recieverid, amount):
    """
    Transfère l'argent de authorid vers recieverid avec le montant amount.

    :param authorid: (str) id de l'auteur de la transaction
    :param recieverid: (str) id du receveur de la transaction
    :param amount: (float) montant transféré
    """
    #assert type(authorid) is str, "L'ID de l'auteur de la transaction n'est pas de type str"
    #assert type(recieverid) is str, "L'ID du receveur de la transaction doit être de type str"
    #assert type(amount) is float, "Le montant (amont) doit être de type float"
    
    cur.execute(f"UPDATE balances SET balance = '{float(getUserBalance(authorid))-float(amount)}' WHERE discordid = '{authorid}';")
    cur.execute(f"UPDATE balances SET balance = '{float(getUserBalance(recieverid))+float(amount)}' WHERE discordid = '{recieverid}';")
    conn.commit()

def createAgency(authorid, name, ticker, prix):
    """
    Crée une agence spatiale ayant un nom, ticker, et le prix de la création, avec l'authorid.

    :param authorid: (int) id du créateur d'agence
    :param name: (str) nom de l'agence
    :param ticker: (str) ticker de l'agence
    :param prix: (int) prix de la création de l'agence
    """
    assert type(authorid) is int, "L'ID de l'auteur de la transaction n'est pas de type int"
    assert type(name) is str, "Le nom d'agence n'est pas de type str"
    assert type(ticker) is str, "L'ticker d'agence n'est pas de type str"
    assert type(prix) is int, "Le prix de création d'agence n'est pas de type int"

    cur.execute(f"UPDATE balances SET balance = '{float(getUserBalance(authorid))-float(prix)}' WHERE discordid = '{authorid}';")
    cur.execute(f"INSERT INTO agencies (agencyname, agencyticker, moneyamount, chiefdiscordid) VALUES ('{name}', '{ticker}', '{prix/2}', '{authorid}');")
    cur.execute(f"INSERT INTO stockexchange (ticker, value, availparts) VALUES ('{ticker}', '{prix/2}', '100');")
    conn.commit()

def getBaltop():
    """
    Renvoie le classement décroissant de la fortune des joueurs.
    
    :param return: (dict) clé: discord id, valeur: balance 
    """
    
    cur.execute(f"SELECT balance, discordid from balances ORDER BY balance DESC")
    result = cur.fetchall()
    return result

def getAgtop():
    """
    Renvoie le classement des valeurs des parts d'agences.

    :param return: (dict) clé: ticker, valeur: value
    """

    cur.execute(f"SELECT value, ticker from stockexchange ORDER BY value DESC")
    result = cur.fetchall()
    return result

def getAgencyValue(ticker):
    """
    Renvoie la valeur de la part d'une agence.

    :param ticker: (str) ticker de l'agence
    :param return: (float) valeur de l'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"

    cur.execute(f"SELECT value from stockexchange WHERE ticker = '{ticker}';")
    result = cur.fetchall()
    return result

def getAgencyPastValues(ticker):
    """
    Renvoie les dernières valeurs des parts d'une agence, sur une semaine.

    :param ticker: (str) ticker de l'agence
    :param return: (str) liste des valeurs de l'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"

    cur.execute(f"SELECT pastvalues from stockexchange WHERE ticker = '{ticker}';")
    result = cur.fetchall()
    return result

def getAgencyParts(ticker):
    """
    Renvoie le nombre de parts disponibles d'une agence.

    :param ticker: (str) ticker de l'agence
    :param return: (int) nombre de parts disponibles de l'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    
    cur.execute(f"SELECT value, availparts from stockexchange WHERE ticker = '{ticker}';")
    result = cur.fetchall()
    return result[0]

def getAgencyName(ticker):
    """
    Renvoie le nom d'une agence via son ticker.
    
    :param ticker: (str) forme abrégée de l'agence
    :param return: (str) nom complet de l'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    
    cur.execute(f"SELECT agencyname from agencies WHERE agencyticker = '{ticker}';")
    result = cur.fetchall()
    return result[0]

def refreshPartsBuy(ticker, parts):
    """
    Rafraîchit le nombre de parts disponibles lors de l'achat/vente de parts d'une agence.

    :param ticker: (str) ticker de l'agence
    :param parts: (int) nouveau nombre de parts disponibles
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    assert type(parts) is int, "Le nombre de parts n'est pas de type int"

    cur.execute(f"UPDATE stockexchange SET availparts = '{int(getAgencyParts(ticker.upper())[1])-parts}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshAgencyValueBuy(ticker, cost):
    """
    Rafraîchit la valeur des parts d'une agence.

    :param ticker: (str) ticker de l'agence
    :param cost: (float) nouvelle valeur d'une part d'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    assert type(cost) is float, "Le coût n'est pas de type float"

    cur.execute(f"UPDATE stockexchange SET value = '{round(float(getAgencyValue(ticker.upper())[0][0])+cost*0.05,2)}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshBalanceBuy(id, cost):
    """
    Rafraîchit le solde d'un utilisateur lors d'un achat.

    :param id: (int) id de l'utilisateur
    :param cost: (float) coût de l'opération d'achat
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"
    assert type(cost) is float, "Le coût de l'opération d'achat n'est pas de type cost"
    
    balance = getUserBalance(id)
    if isinstance(cost, (int, float)):
        new_balance = round(balance - cost, 2)
        cur.execute(f"UPDATE balances SET balance = '{new_balance}' WHERE discordid = '{id}';")
        conn.commit()
    else:
        print(f"Error: cost must be a number, not {type(cost)}")

def refreshPortfolioBuy(id, parts, ticker):
    """
    Rafraîchit le portfolio du user (id), affiche le nombre de parts (parts) qu'il possède dans une agence donnée (ticker)
    """
    assert type(id) is int, "L'ID n'est pas de type int"
    assert type(parts) is int, "Le nombre de parts n'est pas de type int"
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    
    alreadyparts = cur.execute(f"SELECT * from acquisitions WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    result = cur.fetchall()
    alreadyparts = result
    if alreadyparts:
        cur.execute(f"UPDATE acquisitions SET parts = '{int(result[0][2])+int(parts)}' WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    else:
        cur.execute(f"INSERT INTO acquisitions (discordid, ticker, parts) VALUES ('{id}', '{ticker.upper()}', '{parts}')")
    conn.commit()

def getAcquisitions(id):
    """
    Renvoie les acquisitions d'un utilisateur.

    :param id: (int) id de l'utilisateur
    :param return: (dict) acquisitions de l'utilisateur
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"
    
    cur.execute(f"SELECT * from acquisitions WHERE discordid = '{id}'")
    result = cur.fetchall()
    return result

def getOwners(ticker):
    """
    Renvoie les actionnaires d'une agence par ordre décroissant.

    :param ticker: (str) ticker de l'agence
    :param return: (dict) actionnaires de l'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"

    cur.execute(f"SELECT * from acquisitions WHERE ticker = '{ticker.upper()}' ORDER BY parts DESC;")
    result = cur.fetchall()
    return result

def getUserAccount(id):
    """
    Renvoie le solde d'un utilisateur.

    :param id: (str) id de l'utilisateur
    :param return: (dict) solde de l'utilisateur
    """
    assert type(id) is str, "L'id de l'utilisateur n'est pas de type str"

    cur.execute(f"SELECT * from balances WHERE discordid = '{id}'")
    result = cur.fetchall()
    return result

def createAccount(id):
    """
    Crée un compte bancaire pour un utilisateur.

    :param id: (int) id de l'utilisateur
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"
    
    cur.execute(f"INSERT INTO balances (discordid, balance) VALUES ('{id}', '0')")
    conn.commit()

def getAllAgenciesValues():
    """
    Renvoie les valeurs des parts de toutes les agences par ordre décroissant.

    :param return: (dict) valeurs des parts
    """
    
    cur.execute("SELECT * from stockexchange ORDER BY value DESC")
    result = cur.fetchall()
    return result

def isUserChief(id):
    """
    Renvoie les agences dont l'utilisateur est le créateur.

    :param id: (int) id de l'utilisateur
    :param return: (dict) agences dont l'utilisateur est le créateur
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"

    cur.execute(f"SELECT * from agencies WHERE chiefdiscordid = '{id}';")
    result = cur.fetchall()
    return result

def refreshPartsSell(ticker, parts):
    """
    Rafraîchit les parts disponibles d'une agence lors d'une opération de vente par un utilisateur.

    :param ticker: (str) ticker de l'agence
    :param parts: (int) nombre de parts vendues
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    assert type(parts) is int, "Le nombre de parts vendues n'est pas de type int"
    
    cur.execute(f"UPDATE stockexchange SET availparts = '{int(getAgencyParts(ticker.upper())[1])+parts}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshAgencyValueSell(ticker, cost):
    """
    Rafraîchit la valeur des parts d'une agence lors d'une opération de vente par un utilisateur.

    :param ticker: (str) ticker de l'agence
    :param cost: (float) coût de l'opération de vente
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    assert type(cost) is float, "Le coût n'est pas de type float"

    cur.execute(f"UPDATE stockexchange SET value = '{round(float(getAgencyValue(ticker.upper())[0][0])-cost*0.05,2)}' WHERE ticker = '{ticker.upper()}';")
    conn.commit()

def refreshBalanceSell(id, cost):
    """
    Rafraîchit le solde d'un utilisateur lors d'une opération de vente.

    :param id: (int) id de l'utilisateur
    :param cost: (float) coût de l'opération de vente
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"
    assert type(cost) is float, "Le coût de l'opération n'est pas de type float"

    cur.execute(f"UPDATE balances SET balance = '{round(float(getUserBalance(id))+float(cost), 2)}' WHERE discordid = '{id}';")
    conn.commit()

def refreshPortfolioSell(id, parts, ticker):
    """
    Rafraîchit le portfolio d'un utilisateur lors d'une opération de vente.

    :param id: (int) id de l'utilisateur
    :param parts: (int) nombre de parts de l'utilisateur
    :param ticker: (str) ticker de l'agence
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"
    assert type(parts) is int, "Le nombre de parts n'est pas de type int"
    assert type(ticker) is str, "Le ticker de l'agence n'est pas de type str"
    
    alreadyparts = cur.execute(f"SELECT * from acquisitions WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    result = cur.fetchall()
    cur.execute(f"UPDATE acquisitions SET parts = '{int(result[0][2])-int(parts)}' WHERE discordid = '{id}' AND ticker = '{ticker.upper()}';")
    conn.commit()

def getUserParts(id, ticker):
    """
    Renvoie le nombre de parts d'une agence possédées par un utilisateur.

    :param id: (int) id de l'utilisateur
    :param ticker: (str) ticker de l'agence
    :param return: (int) nombre de parts
    """
    assert type(id) is int, "L'id de l'utilisateur n'est pas de type int"
    assert type(ticker) is str, "Le ticker de l'agence n'est pas de type str"
    
    cur.execute(f"SELECT parts from acquisitions WHERE discordid = '{id}' AND ticker = '{ticker}';")
    result = cur.fetchall()
    return result

def getAgencyMoney(ticker):
    """
    Renvoie le montant de la fortune d'une agence via le compte agence.
    
    :param ticker: (str) ticker de l'agence
    :param return: (float) montant de l'argent de l'agence
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"

    cur.execute(f"SELECT moneyamount from agencies WHERE agencyticker = '{ticker}'")
    result = cur.fetchall()
    return result

def updateAgencyBalance(ticker, money):
    """
    Met à jour la fortune d'une agence.

    :param ticker: (str) abréviation de l'agence en 3 ou 4 lettres
    :param money: (float) nouvelle valeur de la fortune de l'agence
    """
    assert type(ticker) is str, "Le type du ticker n'est pas str"
    assert type(money) is float, "Le type de l'argent n'est pas float"

    cur.execute(f"UPDATE agencies SET moneyamount = '{float(money)}' WHERE agencyticker = '{ticker}'")
    conn.commit()

#                                                    ___________________
#___________________________________________________| MECHANICS SECTION |______________________________________________________________________________________
#                                                   |___________________|

def getAgenciesBalances():
    """
    Renvoie le classement des agences les plus riches par ordre décroissant
    
    :param return: (dict) clé: ticker, valeur: richesse de l'agence
    """
    cur.execute(f"SELECT * from agencies ORDER BY moneyamount DESC")
    result = cur.fetchall()
    return result

def getAgenciesStockExchangeInfo():
    """
    Renvoie les caractéristiques boursières des agences par ordre décroissant de valeur.

    :param return: (list) caractéristiques boursières
    """

    cur.execute(f"SELECT * from stockexchange ORDER BY value DESC")
    result = cur.fetchall()
    return result

def updatePastValues(ticker, pastvalueslist, partvalue):
    """
    Rafraîchit les valeurs passées des parts d'une agence.

    :param ticker: (str) ticker de l'agence
    :param pastvalueslist: (str) liste des valeurs précédentes des parts de l'agence
    :param partvalue: (float) valeur unitaire des parts à rajouter à la liste
    """
    assert type(ticker) is str, "Le ticker n'est pas de type str"
    assert type(pastvalueslist) is str, "La liste des valeurs des parts n'est pas de type list"
    assert type(partvalue) is float, "La valeur unitaire des parts n'est pas de type float"

    cur.execute(f"UPDATE stockexchange SET pastvalues = \"{pastvalueslist}\" WHERE ticker = '{ticker}';")
    cur.execute(f"UPDATE stockexchange SET value = '{partvalue}' WHERE ticker = '{ticker}';")
    conn.commit()