from Core import render_template, url_for, redirect, request, jsonify, session
from datetime import datetime as DateTime
from Blockchain import Block, Blockchain
from Forms import RegisterForm
from PIL import Image

import UsefulFunctions as Functions
import DISKuse as Disk
import Core as APP
import os as OS
import json


Session = session



def AddUserData(User : dict, PublicKey : str):
    if User["Username"] in Disk.Users["Users"]:
        APP.ThrowNotification("This user is already exist!")
        return render_template('register.html', form=RegisterForm(request.form), Session=Session)


    else:    
        with open("Users.json", "r") as File:
            try: Data_ = json.loads(File.read())
            except IndexError: pass


            if User["Username"] in Data_["Users"]:
                APP.ThrowNotification("This user is already exist!")
                return render_template('register.html', form=RegisterForm(request.form), Session=Session)


            else:
                Disk.UpdateUserData(User)
#                Data_["Users"][User["Username"]] = User
#                with open("Users.json", "w") as F:
#                    F.write(json.dumps(Data_, indent=1))
#                    F.close()
            
                File.close()


                if PublicKey != None:
                    Disk.UpdatePublicKeys(User=User["Username"], Key=PublicKey)


                APP.Login(User["Username"])
                return redirect(url_for("dashboard"))



def AddWallet(Name : str, Wallet : dict, PublicKey : str):
    with open("Users.json", "r") as File:
        try: Data_ = json.loads(File.read())
        except IndexError: pass



        if Name in Disk.Users["Wallets"]:
            # If this wallet exist in RAM, create a loop until you generate an address that not exist
            WalletAddress = "0x" + Functions.CreateRandomKey(25)
            AddWallet(Name=WalletAddress, Wallet=Wallet, PublicKey=PublicKey)
        

        if Name in Data_["Wallets"]:
            # If this wallet exist in Database, create a loop until you generate an address that not exist
            WalletAddress = "0x" + Functions.CreateRandomKey(25)
            AddWallet(Name=WalletAddress, Wallet=Wallet, PublicKey=PublicKey)


        Disk.UpdateUserData(Wallet)


#        Data_["Wallets"][Name] = Wallet

#        with open("Users.json", "w") as F:
#            F.write(json.dumps(Data_, indent=1))
#            F.close()
        
#        File.close()


#        if PublicKey != None:
#            with open("static/UserData/PublicKeys.json", "r") as FileRead:
#                Data = json.loads(FileRead.read())
#                Data[Name] = PublicKey

#                with open("static/UserData/PublicKeys.json", "w") as FileWrite:
#                    FileWrite.write(json.dumps(Data, indent=1))
#                    FileWrite.close()
                    
#                FileRead.close()



def GetUserData(Username : str):
    if not Username in Disk.Users["Users"]:
        with open("Users.json", "r") as File:
            DataFound = json.loads(File.read())
            Account = {}
            

            for User in DataFound["Users"]:
                if User == Username:
                    Account = DataFound["Users"][User]


            if Account == {}: return []
            else:
                # 0: Username, 1: Name, 2: Avatar, 3: Email, 4: Password, 5: Balance, 6: WalletAddress, 7: PrivateKey, 8: AccessToken, 9: Games 10: Stocks
                return [Account["Username"], Account["Name"], Account["Avatar"], Account["Email"], Account["Password"], Account["Balance"],
                        Account["WalletAddress"], Account["PrivateKey"], Account["AccessToken"], Account["Games"], Account["Stocks"]]

    else:
        Acc = Disk.Users["Users"][Username]
        return [Acc["Username"], Acc["Name"], Acc["Avatar"], Acc["Email"], Acc["Password"], Acc["Balance"],
                Acc["WalletAddress"], Acc["PrivateKey"], Acc["AccessToken"], Acc["Games"], Acc["Stocks"]]



def GetWalletData(Wallet : str):
    if Wallet in Disk.Users["Wallets"]:
        Wallet_ = Disk.Users["Wallets"][Wallet]

        
        # 0: Address, 1: Balance, 2: AccessToken
        return [Wallet, Wallet_["Balance"], Wallet_["AccessToken"]]


    # If doesnt exist in RAM check the Database
    with open("Users.json", "r") as File:
        Wallets = json.loads(File.read())["Wallets"]


        if not Wallet in Wallets:
            return jsonify({"result": {"error": "This wallet doesnt exist!"}})

        return [Wallet, Wallets[Wallet]["Balance"], Wallets[Wallet]["AccessToken"]]



def ChangeAccessToken(Name : str):
    if not Name in Disk.Users["Users"] and not Name in Disk.Users["Wallets"]:    
        with open("Users.json", "r") as File:
            User = json.loads(File.read())


            if Name.startswith("0x"): # This is a wallet
                User["Wallets"][Name]["AccessToken"] = Functions.CreateAccessToken(User["Wallets"][Name]["PrivateKey"])
            else:
                User["Users"][Name]["AccessToken"] = Functions.CreateAccessToken(User["Users"][Name]["PrivateKey"])


            with open("Users.json", "w") as FileWrite:
                FileWrite.write(json.dumps(User, indent=1))
                FileWrite.close()
            
            File.close()
    
    else:
        if Name.startswith("0x"): # This is a wallet
            Disk.Users["Wallets"][Name]["AccessToken"] = Functions.CreateAccessToken(Disk.Users["Wallets"][Name]["PrivateKey"])
        else:
            Disk.Users["Users"][Name]["AccessToken"] = Functions.CreateAccessToken(Disk.Users["Users"][Name]["PrivateKey"])



def LoginWithAccessToken(AccessToken : str):
    Account = {}
    User = ""

    for Username in Disk.Users["Users"]:
        if Disk.Users["Users"][Username]["AccessToken"] == AccessToken:
            Account = Disk.Users["Users"][Username]
            User = Username
            break


    if User != "":
        ChangeAccessToken(Name=User)
        return [Account["Username"], Account["Balance"], Account["WalletAddress"]]

    else:
        # This user may exist in Database
        with open("Users.json", "r") as File:
            Data = json.loads(File.read())


            for Username in Data["Users"]:
                if Data["Users"][Username]["AccessToken"] == AccessToken:
                    Account = Data["Users"][Username]
                    User = Username
                    break
        
        
            if User != "":
                ChangeAccessToken(Name=User)
                return [Account["Username"], Account["Balance"], Account["WalletAddress"]]    
            
            return "User didnt found!"



def LoginWalletWithAccessToken(AccessToken : str):
    WalletDict = {}
    Wallet = ""



    for Address in Disk.Users["Wallets"]:
        if Disk.Users["Wallets"][Address]["AccessToken"] == AccessToken:
            WalletDict = Disk.Users["Wallets"][Address]
            Wallet = Address
            break
    
    
    if Wallet != "":
        ChangeAccessToken(Name=Wallet)
        return [Wallet, WalletDict["Balance"]]
    
    else:
        # This wallet may exist in Database
        with open("Users.json", "r") as File:
            Data = json.loads(File.read())


            for Address in Data["Wallets"]:
                if Data["Wallets"][Address]["AccessToken"] == AccessToken:
                    WalletDict = Data["Wallets"][Address]
                    Wallet = Address
                    break
        
        
            if Wallet != "":
                ChangeAccessToken(Name=Wallet)
                return [Wallet, WalletDict["Balance"]]
            
            return "Wallet didnt found!"



def CreateGame(Name : str, Store : str, Stocks : int):
    # At the beginning, add the data in the file with all the games

    with open("Games.json", "r") as File_:
        Data = json.loads(File_.read())


        if not Name in Data and not Name in Disk.Games:
            NewGame = {"Name": Name,
                                   "Store": Store,
                                   "Stocks": {
                                       "ForSell": 0,
                                       "Owned": Stocks,
                                       "Total": Stocks
                                    },
                                    "Playings": 0,
                                    "Value": float(0.00000000), # 0.00000000 WalletCoins
                                    "Creator": Session["Username"]
                                    }
            
            Disk.UpdateGamesData(NewGame)
            
#            with open("Games.json", "w") as newFile_:
#                Data[Name] = NewGame
#                newFile_.write(json.dumps(Data, indent=1))
#                newFile_.close()
            
#            File_.close()



            # Now add the game in my account

            if Session["Username"] in Disk.Users["Users"]:
                MyAccount = Disk.Users["Users"][Session["Username"]]
                NewGame = {"Name": Name,
                                      "Store": Store,
                                      "StockHolder": "True",
                                      "Creator": "True"
                                        }
                MyAccount["Games"][NewGame["Name"]] = NewGame
                MyAccount["Stocks"][NewGame["Name"]] = Stocks


                Session["Games"][NewGame["Name"]] = NewGame
                Session["Stocks"][NewGame["Name"]] = Stocks

            else:
                with open("Users.json", "r") as File:
                    Data = json.loads(File.read())
                    MyAccount = Data["Users"].get(Session["Username"])
                    NewGame = {"Name": Name,
                                          "Store": Store,
                                          "StockHolder": "True",
                                          "Creator": "True"
                                            }
                    
                    MyAccount["Games"][NewGame["Name"]] = NewGame
                    MyAccount["Stocks"][NewGame["Name"]] = Stocks
                    Disk.UpdateUserData(MyAccount)


                    Session["Games"][NewGame["Name"]] = NewGame
                    Session["Stocks"][NewGame["Name"]] = Stocks
                    
                    File.close()
            


            # Finally add your game to stocks market

            Disk.Price["Games"][Name] = {}



def GetGameData(Game : str):
    if Game in Disk.Games:
        return Disk.Games[Game]

    
    File = open("Games.json", "r")
    return json.loads(File.read())[Game]



def GetAllGames():
    File = open("Games.json", "r")
    GamesRead = json.loads(File.read())
    AllGames = {}


    for G in GamesRead:
        AllGames[GamesRead[G["Name"]]] = GamesRead[G]


    for G in Disk.Games:
        AllGames[Disk.Games[G["Name"]]] = Disk.Games[G]


    return AllGames



def BuyStocks(InGame : str, Stocks : int, Bill : float):
    if not InGame in Disk.Games:
        with open("Games.json", "r") as File:
            Data = json.loads(File.read())

            Data[InGame]["Stocks"]["Owned"] += Stocks
            Data[InGame]["Stocks"]["ForSell"] -= Stocks

            Disk.UpdateGamesData(Data[InGame])


#            with open("Games.json", "w") as newFile:
#                newFile.write(json.dumps(Data, indent=1))
#                newFile.close()
        
#            File.close()

    else:
        Disk.Games[InGame]["Stocks"]["Owned"] += Stocks
        Disk.Games[InGame]["Stocks"]["ForSell"] -= Stocks


    if not Session["Username"] in Disk.Users["Users"]:
        with open("Users.json", "r") as File:
            User = json.loads(File.read())
        
            User["Users"][Session["Username"]]["Stocks"][InGame] += Stocks
            Session["Stocks"] = User["Users"][Session["Username"]]["Stocks"]

            Disk.UpdateUserData(User["Users"][Session["Username"]])
            

#            with open("Users.json", "w") as File_:
#                File_.write(json.dumps(User, indent=1))
#                File_.close()
        
#            File.close()
        
    PayGame(InGame, Session["WalletAddress"], Bill)



def SellStocks(InGame : str, Stocks : int):
    if not InGame in Disk.Games:
        with open("Games.json", "r") as File:
            Data = json.loads(File.read())

            Data[InGame]["Stocks"]["ForSell"] += Stocks
            Data[InGame]["Stocks"]["Owned"] -= Stocks

            Disk.UpdateGamesData(Data[InGame])


#            with open("Games.json", "w") as newFile:
#                newFile.write(json.dumps(Data, indent=1))
#                newFile.close()
        
#            File.close()

    else:
        Disk.Games[InGame]["Stocks"]["ForSell"] += Stocks
        Disk.Games[InGame]["Stocks"]["Owned"] -= Stocks


    if not Session["Username"] in Disk.Users["Users"]:
        with open("Users.json", "r") as File:
            User = json.loads(File.read())
        
            User["Users"][Session["Username"]]["Stocks"][InGame] -= Stocks
            Session["Stocks"] = User["Users"][Session["Username"]]["Stocks"]

            Disk.UpdateUserData(User["Users"][Session["Username"]])
            

#            with open("Users.json", "w") as File_:
#                File_.write(json.dumps(User, indent=1))
#                File_.close()
        
#            File.close()


    GamePayYou(InGame, Session["WalletAddress"], float(float(
        Disk.Games[InGame]["Value"] / Disk.Games[InGame]["Owned"] + Disk.Games[InGame]["ForSell"]
    ) * Stocks))



def IssueNewStocks(InGame : str, Amount : int):
    if not InGame in Disk.Games:
        with open("Games.json", "r") as File:
            Data = json.loads(File.read())

            Data[InGame]["Stocks"]["Total"] += Amount
            Data[InGame]["Stocks"]["ForSell"] += Amount

            Disk.UpdateGamesData(Data[InGame])


#            with open("Games.json", "w") as newFile:
#                newFile.write(json.dumps(Data, indent=1))
#                newFile.close()
        
#            File.close()

        ChangeGameValue(InGame, "NewStocks", Amount)

    else:
        Disk.Games[InGame]["Stocks"]["Total"] += Amount
        Disk.Games[InGame]["Stocks"]["ForSell"] += Amount



def PayGameWithAPI(Name : str, PayerName : str, PayerAccess : str, NewAmount : float):
    SearchTo = "Users"
    User = []


    if PayerName.startswith("0x"):
        SearchTo = "Wallets"
        LoginWalletWithAccessToken(AccessToken=PayerAccess)
    
    else:
        LoginWithAccessToken(AccessToken=PayerAccess)
    

    if len(User) > 0:
        if SearchTo == "Users":
            UpdateWalletData(Wallet=User[2], Amount=NewAmount, Action="Remove")
        
        elif SearchTo == "Wallets":
            UpdateWalletData(Wallet=User[0], Amount=NewAmount, Action="Remove")
    
        ChangeGameValue(Name, "Increased", NewAmount)
        return jsonify({"result": "Game payed!"})
    
    else:
        return jsonify({"result": {"error": "Authentication Failed!"}})



def PayGame(Name : str, Wallet : str, NewAmount : float):
    UpdateWalletData(Wallet, NewAmount, "Remove")
    ChangeGameValue(Name, "Increased", NewAmount)


def GamePayYou(Name : str, Wallet : str, NewAmount : float):
    UpdateWalletData(Wallet, NewAmount, "Add")
    ChangeGameValue(Name, "Decreased", NewAmount)



def ChangeGameValue(Name : str, Action : str, NewAmount : float):
    if not Name in Disk.Games:    
        with open("Games.json", "r") as File:
            Data = json.loads(File.read())
            Disk.UpdateGameData(Data[Name])
            
    
    # Now Change the value
    if Action == "Increased":
        Disk.Games[Name]["Value"] += Functions.RemoveUselessNums(str(NewAmount), 8)

    elif Action == "Decreased":
        Disk.Games[Name]["Value"] -= Functions.RemoveUselessNums(str(NewAmount), 8)


    # Open the price chart and save the new value
#    with open("Price.json", "r") as ChartFile:
#        ChartData = json.loads(ChartFile.read())
    
    NewDate = {"Changed": Action, "Day": DateTime.today().day, "Hour": DateTime.today().hour, "Month": DateTime.today().month, "Year": DateTime.today().year, "Value": Data[Name]["Value"], "Bought": 0.0, "Sold": 0.0}
                

    if "%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year ) in Disk.Price["Games"][Name]:
        TodayStatsStructure = Disk.Price["Games"][Name]["%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year )]


        if Action == "Increased":
            NewDate["Bought"] = NewAmount
            NewDate["Sold"] = 0.0
            
        elif Action == "Decreased":
            NewDate["Sold"] = NewAmount
            NewDate["Bought"] = 0.0


        TodayStatsStructure.append(NewDate)
        
    else:
        if Action == "Increased":
            NewDate["Bought"] = NewAmount
            NewDate["Sold"] = 0.0
            
        elif Action == "Decreased":
            NewDate["Sold"] = NewAmount
            NewDate["Bought"] = 0.0
            

        Disk.Price["Games"][Name]["%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year )] = [NewDate]



def UserSettings(Username : str, PreviousPass : str):
    if PreviousPass != None:
        PreviousUser = GetUserData(Username)
        
        if PreviousUser[3] != PreviousPass:
            return "WrongPass"


    return "EmailSent"



def GameSettings(PreviousGame : str, Name : str, Description : str, Image_):
    if not Name in Disk.Games:
        with open("Games.json", "r") as FileRead:
            PreviousGameData = json.loads(FileRead.read())[PreviousGame]


        if len(Name) > 0:
            PreviousGameData["Name"] = Name

        if len(Description) > 0:
            PreviousGameData["Description"] = Description


        if Image_ != None:
            if Image_["UploadImage"].filename.endswith(".png") or Image_["UploadImage"].filename.endswith("jpg") or Image_["UploadImage"].filename.endswith("svg"):
                SaveImage(Image_, "UserData/GameIcon/" + PreviousGameData["Image"], (50, 50))
        

        Disk.Games[Name] = PreviousGameData
        
        FileRead.close()



def UpdateWalletData(Wallet : str, Amount : float, Action : str):
    WalletAddress = ""


    for User in Disk.Users["Users"]:
        if Disk.Users["Users"][User]["WalletAddress"] == Wallet:
            WalletAddress = Wallet
            Balance = Disk.Users["Users"][User]["Balance"]


            if Action == "Add":
                Balance += Functions.RemoveUselessNums(str(Amount), 8)
            
            if Action == "Remove":
                Balance -= Functions.RemoveUselessNums(str(Amount), 8)
            

            Disk.Users["Users"][User]["Balance"] = Balance


    if WalletAddress != Wallet:
        with open("Users.json", "r") as File:
            Data = json.loads(File.read())

            for User in Data["Users"]:
                if Data["Users"][User]["WalletAddress"] == Wallet:
                    Balance = Data["Users"][User]["Balance"]


                    if Action == "Add":
                        Balance += Functions.RemoveUselessNums(str(Amount), 8)
                    
                    if Action == "Remove":
                        Balance -= Functions.RemoveUselessNums(str(Amount), 8)
                    

                    Data["Users"][User]["Balance"] = Balance
                    Session["Balance"] = Balance


                    Disk.UpdateUserData(Data["Users"][User])



def GetPriceChart(TimeFrame : str, Date : dict):
    with open("Price.json", "r") as File:
        Data = json.loads(File.read())
        File.close()

        Stats = []
        Bought, Sold = 0.00, 0.00
        Volume = 0.0
        Change = 0.0
        Changed = ""


        if TimeFrame == "Today":
            StatsToday : list = []
            for Date_ in Data["Stats"]:
                if Date_ == "%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"]):
                    Date__ = Data["Stats"]["%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"])]
                
                    for Stat in Date__:
                        Bought += Stat["CoinsBought"]
                        Sold += Stat["CoinsSold"]
                        Volume += Stat["Volume"]

                        StatsToday.append(Stat)


            for Date_ in Disk.Price["Stats"]:
                if Date_ == "%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"]):
                    Date__ = Disk.Price["Stats"]["%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"])]
                
                    for Stat in Date__:
                        Bought += Stat["CoinsBought"]
                        Sold += Stat["CoinsSold"]
                        Volume += Stat["Volume"]

                        StatsToday.append(Stat)


            Stats = StatsToday

        
        
        if TimeFrame == "Week":
            pass



        if TimeFrame == "Month":
            MonthlyStats : list = []
            for Date_ in Data["Stats"]:
                if Date_.endswith("/%s/%s" % (Date["Month"], Date["Year"])):
                    Date__ = Data["Stats"][Date_]
                    
                    for Stat in Date__:
                        Bought += Stat["CoinsBought"]
                        Sold += Stat["CoinsSold"]
                        Volume += Stat["Volume"]

                        MonthlyStats.append(Stat)


            for Date_ in Disk.Price["Stats"]:
                if Date_.endswith("/%s/%s" % (Date["Month"], Date["Year"])):
                    Date__ = Disk.Price["Stats"][Date_]
                    
                    for Stat in Date__:
                        Bought += Stat["CoinsBought"]
                        Sold += Stat["CoinsSold"]
                        Volume += Stat["Volume"]

                        MonthlyStats.append(Stat)

            Stats = MonthlyStats



        if TimeFrame == "Year":
            AnnualStats : list = []
            for Date_ in Data["Stats"]:
                if Date_.endswith(Date["Year"]):
                    Date__ = Data["Stats"][Date_]
                
                    for Stat in Date__:
                        Bought += Stat["CoinsBought"]
                        Sold += Stat["CoinsSold"]
                        Volume += Stat["Volume"]

                        AnnualStats.append(Stat)


            for Date_ in Disk.Price["Stats"]:
                if Date_.endswith(Date["Year"]):
                    Date__ = Disk.Price["Stats"][Date_]
                
                    for Stat in Date__:
                        Bought += Stat["CoinsBought"]
                        Sold += Stat["CoinsSold"]
                        Volume += Stat["Volume"]

                        AnnualStats.append(Stat)

            Stats = AnnualStats



        # Now return the change of Crypto
        
        if len(Stats) > 0:
            PercentChange = ((float(Stats[int(len(Stats)) - 1]["Value"]) - Stats[0]["Value"]) / abs(Stats[0]["Value"])) * 100.00
            Change = PercentChange


            if Stats[int(len(Stats)) - 1]["Value"] > Stats[0]["Value"]:
                Changed = "Increased"


            if Stats[int(len(Stats)) - 1]["Value"] < Stats[0]["Value"]:
                Changed = "Decreased"


            if Stats[int(len(Stats)) - 1]["Value"] == Stats[0]["Value"]:
                Change = 0.00
                Changed = "Increased"



        return {"Price": Data["Price"], "Change": float(Change), "Changed": Changed,
                "Volume": Volume, "Bought": Bought, "Sold": Sold,
                "Stats": Stats, "BestInvestions": []}



def ChangeCurrencyValue(Action : str, Cash : float, Value : float):
    if "Stats" in Disk.Price:
        if "%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year ) in Disk.Price["Stats"]:
            DateStats = Disk.Price["Stats"]["%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year )]


            if Action == "Increased":
                Disk.Price["Economy"] += Cash
                Disk.Price["Tokens"] += Value
                Disk.Price["Market"] -= Value
            
            elif Action == "Decreased":
                Disk.Price["Economy"] -= Cash
                Disk.Price["Tokens"] -= Value
                Disk.Price["Market"] += Value

            
            NewEconomy = Functions.RemoveUselessNums(str(DateStats["Economy"] / float(DateStats["Tokens"] + DateStats["Market"])), 2)
            DateStats["Price"] = NewEconomy


            NewValue = {"Day": DateTime.today().day,
                                "Month": DateTime.today().month,
                                "Year": DateTime.today().year,
                                "Hour": DateTime.today().hour,
                                "Value": NewEconomy,
                                "CoinsBought": 0.0,
                                "CoinsSold": 0.0,
                                "Volume": 0.0}

            
            if Action == "Increased":
                NewValue["CoinsBought"] += Functions.RemoveUselessNums(str(Value), 8)
                NewValue["Volume"] += Functions.RemoveUselessNums(str(Cash), 2)
                
            elif Action == "Decreased":
                NewValue["CoinsSold"] += Functions.RemoveUselessNums(str(Value), 8)


            DateStats.append(NewValue)

        else:
            if Action == "Increased":
                Disk.Price["Economy"] += Cash
                Disk.Price["Tokens"] += Value
                Disk.Price["Market"] -= Value
            
            elif Action == "Decreased":
                Disk.Price["Economy"] -= Cash
                Disk.Price["Tokens"] -= Value
                Disk.Price["Market"] += Value

            
            NewEconomy = Functions.RemoveUselessNums(str(DateStats["Economy"] / float(DateStats["Tokens"] + DateStats["Market"])), 2)
            DateStats["Price"] = NewEconomy


            NewValue = {"Day": DateTime.today().day,
                                "Month": DateTime.today().month,
                                "Year": DateTime.today().year,
                                "Hour": DateTime.today().hour,
                                "Value": NewEconomy,
                                "CoinsBought": 0.0,
                                "CoinsSold": 0.0,
                                "Volume": 0.0}

            
            if Action == "Increased":
                NewValue["CoinsBought"] += Functions.RemoveUselessNums(str(Value), 8)
                NewValue["Volume"] += Functions.RemoveUselessNums(str(Cash), 2)
                
            elif Action == "Decreased":
                NewValue["CoinsSold"] += Functions.RemoveUselessNums(str(Value), 8)
            

            Disk.Price["Stats"]["%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year )] = [NewValue]


    else:
        File = open("Price.json", "r")
        Data = json.loads(File.read())



        if Action == "Increased":
            Data["Economy"] += Cash
            Data["Tokens"] += Value
            Data["Market"] -= Value
        
        elif Action == "Decreased":
            Data["Economy"] -= Cash
            Data["Tokens"] -= Value
            Data["Market"] += Value

        
        NewEconomy = Functions.RemoveUselessNums(str(Data["Economy"] / float(Data["Tokens"] + Data["Market"])), 2)
        Data["Price"] = NewEconomy


        NewValue = {"Day": DateTime.today().day,
                            "Month": DateTime.today().month,
                            "Year": DateTime.today().year,
                            "Hour": DateTime.today().hour,
                            "Value": NewEconomy,
                            "CoinsBought": 0.0,
                            "CoinsSold": 0.0,
                            "Volume": 0.0}

        
        if Action == "Increased":
            NewValue["CoinsBought"] += Functions.RemoveUselessNums(str(Value), 8)
            NewValue["Volume"] += Functions.RemoveUselessNums(str(Cash), 2)
            
        elif Action == "Decreased":
            NewValue["CoinsSold"] += Functions.RemoveUselessNums(str(Value), 8)



        Chart = {"Price": Data["Price"],
            "Market": Data["Market"],
            "Tokens": Data["Tokens"],
            "Economy": Data["Economy"],
            "Stats": {
                "%s/%s/%s" % ( DateTime.today().day, DateTime.today().month, DateTime.today().year ): [
                    NewValue
                ]
            }}
        
        Disk.UpdatePriceData(Path=None, Price_=Chart)



def GetStockPriceChart(Game: str, TimeFrame : str, Date : dict):
    with open("Price.json", "r") as File:
        Data = json.loads(File.read())
        File.close()

        Stats = []
        Bought, Sold = 0.00, 0.00
        Volume = 0.0
        Change = 0
        Changed = ""


        if TimeFrame == "Today":
            StatsToday : list = []

            if "%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"]) in Disk.Price["Games"][Game]:
                for Date_ in Disk.Price["Games"][Game]["%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"])]:
                    StatsToday.append(Date_)
            
            else:
                if "%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"]) in Data["Games"][Game]:
                    for Date_ in Data["Games"][Game]["%s/%s/%s" % (Date["Day"], Date["Month"], Date["Year"])]:
                        StatsToday.append(Date_)

            Stats = StatsToday
        
        
        if TimeFrame == "Week":
            pass


        if TimeFrame == "Month":
            MonthlyStats : list = []
            for Date_ in Data["Games"][Game]:
                if "/%s/%s" % (Date["Month"], Date["Year"]) in Date_:
                    for Month in Data["Games"][Game][Date_]:
                        MonthlyStats.append(Month)


            for Date_ in Disk.Price["Games"][Game]:
                if "/%s/%s" % (Date["Month"], Date["Year"]) in Date_:
                    for Month in Disk.Price["Games"][Game][Date_]:
                        MonthlyStats.append(Month)


                

            Stats = MonthlyStats


        if TimeFrame == "Year":
            AnnualStats : list = []
            for Date_ in Data["Games"][Game]:
                if Date_.endswith(Date["Year"]):
                    for Year in Data["Games"][Game][Date_]:
                        AnnualStats.append(Year)


            for Date_ in Disk.Price["Games"][Game]:
                if Date_.endswith(Date["Year"]):
                    for Year in Data["Games"][Game][Date_]:
                        AnnualStats.append(Year)

            Stats = AnnualStats
        


        # Return the volume, the change, the stocks bought and the stocks sold in the game

        for Stat in Stats:
            Bought += Functions.RemoveUselessNums(str(Stat["Bought"]), 8)
            Sold += Functions.RemoveUselessNums(str(Stat["Sold"]), 8)

        if int(len(Stats)) > 0:
            Change = Stats[0]["Value"] - Stats[int(len(Stats)) - 1]["Value"]
        
        Volume = Bought


        return {"Change": Change, "Changed": Changed, "Volume": Volume, "Bought": Bought, "Sold": Sold, "Stats": Stats}



def GetPrice():
    if "Price" in Disk.Price:
        return Disk.Price["Price"]
    
    else:
        File = open("Price.json", "r")
        Data = json.loads(File.read())
        File.close()

        return Data["Price"]



def GetCryptoData():
    File = open("Price.json", "r")
    Data = json.loads(File.read())


    Tokens = Data["Tokens"]
    Market = Data["Market"]
    Bought = 0.0
    BoughtValue = 0.00
    Sold = 0.0
    SoldValue = 0.00


    for Date_ in Data["Stats"]:
        if Date_ == "%s/%s/%s" % (DateTime.today().day, DateTime.today().month, DateTime.today().year):
            Date__ = Data["Stats"]["%s/%s/%s" % (DateTime.today().day, DateTime.today().month, DateTime.today().year)]
            

            for Stat in Date__:
                Bought += Stat["CoinsBought"]
                Sold += Stat["CoinsSold"]


    if "%s/%s/%s" % (DateTime.today().day, DateTime.today().month, DateTime.today().year) in Disk.Price["Stats"]:
        DataPlus = Disk.Price["Stats"]["%s/%s/%s" % (DateTime.today().day, DateTime.today().month, DateTime.today().year)]


        Tokens += Disk.Price["Tokens"]
        Market += Disk.Price["Market"]
        

        for Stat in DataPlus:
            Bought += Stat["CoinsBought"]
            Sold += Stat["CoinsSold"]


    if Bought > 0.0:
        BoughtValue = Functions.CalculatePrice(Bought, Data["Price"])
    
    if Sold > 0.0:
        SoldValue = Functions.CalculatePrice(Sold, Data["Price"])


    return [Data["Price"], Tokens, Market, Bought, BoughtValue, Sold, SoldValue]



def SendCryptos(Sender : str, Recipient : str, Amount : float):
    if Sender != "WalletCoinBANK":
        UpdateWalletData(Wallet=Session["WalletAddress"], Amount=float(Amount), Action="Remove")


    UpdateWalletData(Wallet=Recipient, Amount=float(Amount), Action="Add")


    Data = "%s -->> %s -->> %s" % (Sender, Recipient, Amount)
    NewBlock(Data=Data)



def apiTransaction(AccessToken : str, Wallet : str, Amount : float):
    User = LoginWithAccessToken(AccessToken=AccessToken)
    if User != {}:
        if float(Amount) > float(User[1]) or float(Amount) == 0: # User[1] = Balance
            return jsonify({"result": {"error": "This amount isnt available in your Wallet!"}})
        

        UpdateWalletData(Wallet=User[2], Amount=float(Amount), Action="Remove")
        UpdateWalletData(Wallet=Wallet, Amount=float(Amount), Action="Add")


        Data = "%s -->> %s -->> %s" % (User[0], Wallet, Amount) # User[0] = Username
        NewBlock(Data=Data)

        return jsonify({"result": "Transaction succeed! {0} -->> {1} -->> {2}".format(User[0], Wallet, Amount)})
    
    return jsonify({"result": {"error": "Login Failed"}})



def GetBlockchainData(Number : int):
    BlockResult = {}

    
    for Block in Disk.Blockchain:
        Number_ = Block["Number"]
        if Number_ == Number:
            BlockResult = Block
            break

    if len(BlockResult) > 0:
        return BlockResult


    # If this block didnt found, check the Database
    with open("Blockchain.json", "r") as File:
        Data = json.loads(File.read())

        for Block in Data:
            Number_ = Block["Number"]
            if Number_ == Number:
                BlockResult = Block
                break
        
        return BlockResult



def GetBlockchain():
    with open("Blockchain.json", "r") as File:
        Data = json.loads(File.read())
        File.close()

        BlockchainChain = []


        for BL in Data:
            BlockchainChain.append(BL)
        
        for BL in Disk.Blockchain:
            BlockchainChain.append(BL)
        

        return BlockchainChain



def GetBlock(Number : int):
    BlocksResult = []
    BlocksNonce = []

    
    for Block_ in Disk.Blockchain:
        if int(Block_["Number"]) == Number:
            BlocksResult.append(Block_)
            BlocksNonce.append(Block_["Nonce"])


    
    with open("Blockchain.json", "r") as File:
        Data = json.loads(File.read())

        for Block_ in Data:
            if int(Block_["Number"]) == Number:
                if not int(Block_["Nonce"]) in BlocksNonce:
                    BlocksResult.append(Block_)

        
        File.close()

        BlocksResult.clear()
        BlocksNonce.clear()

        return BlocksResult



def NewBlock(Data : str):
    Blockchain_ = GetBlockchain()
    

    if len(Blockchain_) == 0:
        Blockchain().mine(Block_=Block(Number=0, PreviousHash="0" * 64, Data=None, Nonce=0), MyBlockNumber=0)

    else:
        MyBlock = None
        Number = 0


        for Block_ in Blockchain_:
            if Block_["Data"].startswith(Session["Username"] or Session["WalletAddress"]):
                MyBlock = Block_["Number"]
                break


        if MyBlock != None:
            Number = MyBlock
        else:
            Number = 0

        
        Blockchain().mine(Block_=Block(Number=Number,
            PreviousHash=Blockchain_[len(Blockchain_) -1]["Hash"],
            Data=Data,
            Nonce=Blockchain_[len(Blockchain_) - 1]["Nonce"]
            ), MyBlockNumber=MyBlock)



def get_blockchain():
    Blockchain_ = Blockchain()
    
    for Bl in GetBlockchain():
        Blockchain_.chain.append(Block(int(Bl["Number"]), Bl['PreviousHash'], Bl['Data'], int(Bl['Nonce'])))

    return Blockchain_



def SaveImage(Picture, Name : str, Size : tuple):
    ImagePath = OS.path.join("static", Name)

    Icon = Image.open(Picture)
    Icon.thumbnail(Size)
    Icon.save(ImagePath)

    return Name
