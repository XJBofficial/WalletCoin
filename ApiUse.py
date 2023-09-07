import requests


API = "http://127.0.0.1:3049"



def Price():
    Result = requests.get(url=API + "/api/price")
    print(Result.json())



def PriceChartMonths(Year : int):
    Result = requests.get(url=API + "/api/price/chart?list=months&year=" + str(Year))
    print(Result.json())



def PriceChartDays(Year : int, Month : int):
    Result = requests.get(url=API + "/api/price/chart?list=days&year=%s&month=%s" % (str(Year), str(Month)))
    print(Result.json())



def PriceChartHours(Year : int, Month : int, Day : int):
    Result = requests.get(url=API + "/api/price/chart?list=hours&year=%s&month=%s&day=%s" % (str(Year), str(Month), str(Day)))
    print(Result.json())



def WalletConnect(PrivateKey : str, SecretPhrase : str, Wallet : str, APIkey : str):
    Body = {
        "private_key": PrivateKey,
        "secret_phrase": SecretPhrase,
        "wallet": Wallet,
        "api_key": APIkey
    }
    Result = requests.post(API + "/api/wallet/auth", data=Body)
    print(Result.json())



def Transcate(PrivateKey : str, Recipient : str, Amount : float, Wallet : str, APIkey : str):
    Body = {
        "private_key": PrivateKey,
        "recipient": Recipient,
        "amount": Amount,
        "wallet": Wallet,
        "api_key": APIkey
    }
    Result = requests.post(url=API + "/api/wallet/transaction", data=Body)
    print(Result.json())



def Withdraw(PrivateKey : str, WithdrawTo : str, Amount : float, Wallet : str, APIkey : str):
    Body = {
        "private_key": PrivateKey,
        "withdraw_to": WithdrawTo,
        "amount": Amount,
        "wallet": Wallet,
        "api_key": APIkey
    }
    Result = requests.post(url=API + "/api/wallet/withdraw", data=Body)
    print(Result.json())



def Deposit(PrivateKey : str, DepositTo : str, Amount : float, Wallet : str, APIkey : str):
    Body = {
        "private_key": PrivateKey,
        "deposit_to": DepositTo,
        "amount": Amount,
        "wallet": Wallet,
        "api_key": APIkey
    }
    Result = requests.post(url=API + "/api/wallet/deposit", data=Body)
    print(Result.json())



def Payment(PrivateKey : str, Description : str, Amount : float, Urls : dict, Wallet : str, APIkey : str):
    Body = {
        "private_key": PrivateKey,
        "description": Description,
        "amount": Amount,
        "success_url": Urls["success"],
        "failed_url": Urls["failed"],
        "cancel_url": Urls["cancel"],
        "wallet": Wallet,
        "api_key": APIkey
    }
    Result = requests.post(url=API + "/api/webPayments", data=Body)
    print(Result.json())



while True:
    Action = input("Action: ")


    if Action == "price":
        Price()


    if Action == "priceChart":
        List = input("List: ")


        if not List in ["hours", "days", "months"]:
            print("Invalid argument.")
        else:
            if List == "hours":
                Day = int(input("Day: "))
                Month = int(input("Month: "))
                Year = int(input("Year: "))

                PriceChartHours(Year=Year, Month=Month, Day=Day)
            
            elif List == "days":
                Month = int(input("Month: "))
                Year = int(input("Year: "))

                PriceChartDays(Year=Year, Month=Month)
            
            else:
                Year = int(input("Year: "))
                PriceChartMonths(Year=Year)


    if Action == "walletConnect":
        Wallet = input("Wallet: ")
        ApiKey = input("API_KEY: ")
        PrivateKey = input("PrivateKey: ")
        SecretPhrase = input("SecretPhrase: ")

        WalletConnect(PrivateKey=PrivateKey, SecretPhrase=SecretPhrase, Wallet=Wallet, APIkey=ApiKey)


    if Action == "transaction":
        Wallet = input("Wallet: ")
        ApiKey = input("API_KEY: ")
        PrivateKey = input("PrivateKey: ")
        Recipient = input("Recipient: ")
        Amount = float(input("Amount: "))

        Transcate(PrivateKey=PrivateKey, Recipient=Recipient, Amount=Amount, Wallet=Wallet, APIkey=ApiKey)
    

    if Action == "withdraw":
        Wallet = input("Wallet: ")
        ApiKey = input("API_KEY: ")
        PrivateKey = input("PrivateKey: ")
        WithdrawTo = input("Withdraw To: ")
        Amount = float(input("Amount: "))

        Withdraw(PrivateKey=PrivateKey, WithdrawTo=WithdrawTo, Amount=Amount, Wallet=Wallet, APIkey=ApiKey)
    

    if Action == "deposit":
        Wallet = input("Wallet: ")
        ApiKey = input("API_KEY: ")
        PrivateKey = input("PrivateKey: ")
        DepositTo = input("Deposit To: ")
        Amount = float(input("Amount: "))

        Deposit(PrivateKey=PrivateKey, DepositTo=DepositTo, Amount=Amount, Wallet=Wallet, APIkey=ApiKey)


    if Action == "payment":
        Wallet = input("Wallet: ")
        ApiKey = input("API_KEY: ")
        PrivateKey = input("PrivateKey: ")
        Description = input("Description: ")
        Amount = float(input("Amount: "))
        SuccessUrl = input("Success url: ")
        FailedUrl = input("Failed url: ")
        CancelUrl = input("Cancel url: ")

        Urls = {
            "success": SuccessUrl,
            "failed": FailedUrl,
            "cancel": CancelUrl
        }

        Payment(PrivateKey=PrivateKey, Description=Description, Amount=Amount, Urls=Urls, Wallet=Wallet, APIkey=ApiKey)
