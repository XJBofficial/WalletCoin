import requests



def priceChart(TimeFrame : str, Day : str, Month : str, Year : str):
    result = requests.get("http://127.0.0.1:5000/api/price/chart/?TimeFrame=%s&Day=%sMonth=%s&Year=%s" % (TimeFrame, Day, Month, Year))
    print(result.text)


def connectAccount(AccessToken):
    result = requests.get("http://127.0.0.1:5000/api/auth/?AccessToken=" + AccessToken)
    print(result.text)


def walletCreate(Password):
    result = requests.post("http://127.0.0.1:5000/api/wallet/create/?Pass=" + Password)
    print(result.text)


def walletConnect(AccessToken):
    result = requests.get("http://127.0.0.1:5000/api/wallet/connect/?AccessToken=" + AccessToken)
    print(result.text)


def transcate(Access, Wallet, Amount):
    result = requests.post("http://127.0.0.1:5000/api/transaction/?AccessToken=%s&WalletAddress=%s&Amount=%s" % (Access, Wallet, Amount))
    print(result.text)


def payGame(game, purchaser, amount):
    result = requests.post("http://127.0.0.1:5000/api/payToPlay?game=%s&purchaser=%s&amount=%s" % (game, purchaser, amount))
    print(result.text)



while True:
    action = input("Action: ")


    if action == "priceChart":
        TimeFrame = input("TimeFrame: ")
        Day = input("Day: ")
        Month = input("Month: ")
        Year = input("Year: ")

        priceChart(TimeFrame=TimeFrame, Day=Day, Month=Month, Year=Year)


    if action == "auth":
        AccessToken = input("Access Token: ")

        connectAccount(AccessToken=AccessToken)
    

    if action == "walletCreate":
        Pass = input("Password: ")

        walletCreate(Password=Pass)
    

    if action == "walletConnect":
        AccessToken = input("AccessToken: ")

        walletConnect(AccessToken=AccessToken)


    if action == "transaction":
        AccessToken = input("AccessToken: ")
        Wallet = input("Wallet: ")
        Amount = input("Amount: ")

        transcate(Access=AccessToken, Wallet=Wallet, Amount=Amount)
    

    if action == "payGame":
        game = input("Game: ")
        purchaser = input("Purchaser: ")
        amount = float(input("Amount: "))

        payGame(game, purchaser, amount)
