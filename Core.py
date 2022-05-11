from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify
from functools import wraps
from Forms import *

import UsefulFunctions as Functions
import datetime as DateTime
import smtplib as SMTP
import DISKuse as Disk
import time as Time
import json as Json
import os as OS
import Database
import Security



def InitializeApp():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY = OS.environ.get('SECRET_KEY') or 'dev_key')

    return app



def ThrowNotification(Text : str):
    flash(Text)



app = InitializeApp()
Session = session



# Wrap to define if the user is currently logged in from session
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap



# Log in the user by updating session
def Login(Username):
    User = Database.GetUserData(Username)


    # 0: Username, 1: Name, 2: Avatar, 3: Email, 4: Password, 5: Balance, 6: WalletAddress, 7: PrivateKey 8: Games 9: Stocks
    Session['logged_in'] = True
    Session['Username'] = Username
    Session['Name'] = User[1]
    Session["Avatar"] = User[2]
    Session['Email'] = User[3]
    Session['WalletAddress'] = User[6]
    Session["PrivateKey"] = User[7]
    Session["AccessToken"] = User[8]
    Session["Games"] = User[9]
    Session["Stocks"] = User[10]

    
    if str(User[4]).startswith("-"):
        Session["Balance"] = 0.00
    else: Session["Balance"] = User[5]



@app.route("/")
def index():
    CryptoCurrencyData = Database.GetCryptoData()


    Price = CryptoCurrencyData[0]
    Tokens = CryptoCurrencyData[1]
    Market = CryptoCurrencyData[2]
    Bought = CryptoCurrencyData[3]
    BoughtValue = CryptoCurrencyData[4]
    Sold = CryptoCurrencyData[5]
    SoldValue = CryptoCurrencyData[6]


    return render_template('Index.html',
    Price=Price,
    Tokens=Tokens,
    Market=Market,
    Bought=Bought,
    Sold=Sold,
    BoughtValue=BoughtValue,
    SoldValue=SoldValue,
    Session=Session)



@app.route("/logout")
@is_logged_in
def logout():
    CryptoCurrencyData = Database.GetCryptoData()


    Price = CryptoCurrencyData[0]
    Tokens = CryptoCurrencyData[1]
    Market = CryptoCurrencyData[2]
    Bought = CryptoCurrencyData[3]
    BoughtValue = CryptoCurrencyData[4]
    Sold = CryptoCurrencyData[5]
    SoldValue = CryptoCurrencyData[6]


    return render_template('Index.html',
    Price=Price,
    Tokens=Tokens,
    Market=Market,
    Bought=Bought,
    Sold=Sold,
    BoughtValue=BoughtValue,
    SoldValue=SoldValue,
    Session=Session)



@app.route("/settings", methods=["POST", "GET"])
def settings():
    if request.method == "GET":
        Session["ConfirmationEmailSent"] = False
        return render_template("UserSettings.html", Status="Form", Session=Session)


    if request.method == "POST":
        if not Session["ConfirmationEmailSent"]:
            Username = request.form["Username"]
            Email = request.form["Email"]

            PreviousPassword = request.form["PreviousPassword"]
            NewPassword = request.form["NewPassword"]



            if Username != "" and PreviousPassword != "":
                Status = Database.UserSettings(Session["Username"], PreviousPassword)



            elif Username != "" and PreviousPassword == "":
                Status = Database.UserSettings(Session["Username"], None)


            elif PreviousPassword != "" and Username == "":
                Status = Database.UserSettings(Session["Username"], PreviousPassword)


            elif Username == "" and PreviousPassword == "":
                Status = Database.UserSettings(Session["Username"], None)



            if Status == "WrongPass":
                flash("Previous Password doesnt match...")

                Time.sleep(3)
                flash("")
                return render_template("UserSettings.html", Status="Form", Session=Session)


            if Status == "EmailSent":
                Session["AccountChangingUsername"] = Username,
                Session["AccountChangingEmail"] = Email,
                Session["AccountChangingNewPassword"] = NewPassword


                Sender = "walletcoinofficial@gmail.com"
                Receiver = Session["Email"]
                Session["AccountChangingConfirmCode"] = Functions.CreateRandomKey(5)

                EmailText = """
                    Hello WalletCoin user !!!

                    Someone tried to change your account settings in account '{0}'.
                    If you are this person, your confirmation code is {1} else
                    ignore this email now.
                """.format(Session["Username"], Session["AccountChangingConfirmCode"])


                with SMTP.SMTP("smtp.gmail.com", 587) as Server:
                    Server.starttls()
                    Server.login(Sender, "KonDev17")
                    Server.sendmail(Sender, Receiver, EmailText)


                Session["ConfirmationEmailSent"] = True
                return render_template("UserSettings.html", Status="EmailSent", Session=session)
        
        else:
            if request.form["ConfCode"] != Session["AccountChangingConfirmCode"]:
                flash("Confirmation Code is wrong... try again...")

                Time.sleep(3)
                flash("")
                return render_template("UserSettings.html", Status="EmailSent", Session=session)
        
            else:
                User = Database.GetUserData(Session["Username"])


                # 0: Username, 1: Name, 2: Avatar, 3: Email, 4: Password, 5: Balance, 6: WalletAddress, 7: PrivateKey, 9: AccessToken, 8: Games, 9: Stocks
                NewUser = {"Username": User[0],
                        "Name": User[1],
                        "Avatar": User[2],
                        "Email": User[3],
                        "Password": User[4],
                        "Balance": User[5],
                        "WalletAddress": User[6],
                        "PrivateKey": User[7],
                        "AccessToken": User[8],
                        "Games": User[9],
                        "Stocks": User[10]}
            

                if "AccountChangingUsername" in Session:
                    NewUser["Username"] = Session["AccountChangingUsername"]
                    del Session["AccountChangingUsername"]


                if "AccountChangingEmail" in Session:
                    NewUser["Email"] = Session["AccountChangingEmail"]
                    del Session["AccountChangingEmail"]


                if "AccountChangingNewPassword" in Session:
                    NewUser["Password"] = Session["AccountChangingNewPassword"]
                    del Session["AccountChangingNewPassword"]


#                with open("Users.json", "r") as File:
#                    Users = Json.loads(File.read())
#                    del Users["Users"][Session["Username"]]


#                    with open("Users.json", "w") as File_:
#                        File_.write(Json.dumps(Users, indent=1))
#                        File_.close()

#                    File.close()


                Database.AddUserData(User=NewUser, PublicKey=None)
                return render_template("UserSettings.html", Status="AccountDataChanged", Session=session)



# The Value of Cryptocurrency
@app.route("/priceChart", methods=["GET"])
def priceChart():
    if request.method == "GET":
        RequestArguments = request.args
        Date, Body = {}, {}

        
        if not "Day" in RequestArguments and not "Month" in RequestArguments and not "Year" in RequestArguments:
            Body = {"TimeFrame": "Today", "Day": DateTime.date.today().day, "Month": DateTime.date.today().month, "Year": DateTime.date.today().year}
        else:
            Body = {"TimeFrame": RequestArguments.get("TimeFrame"), "Month": RequestArguments.get("Month") or None, "Year": RequestArguments.get("Year")}

            if "Day" in RequestArguments:
                Body["Day"] = RequestArguments.get("Day")

        Date = Body
        SearchTo = ""


        Chart = Database.GetPriceChart(TimeFrame=Date["TimeFrame"], Date=Date)

        Price = Chart["Price"]
        TimeFrame = Date["TimeFrame"]
        PriceChanged = Chart["Changed"]
        PriceChange = Chart["Change"]
        Volume = Chart["Volume"]
        Bought = Chart["Bought"]
        Sold = Chart["Sold"]


        if TimeFrame == "Today":
            SearchTo = "Hour"
        
        if TimeFrame == "Month" or TimeFrame == "Year":
            SearchTo = "Day"


        return render_template("PriceChart.html",
        Price=Price,
        TimeFrame=TimeFrame,
        SearchTo=SearchTo,
        Changed=PriceChanged,
        PriceChange=Functions.RemoveUselessNums(str(PriceChange), 2),
        Volume=Functions.RemoveUselessNums(str(Volume), 2),
        Bought=Functions.RemoveUselessNums(str(Bought), 8),
        Sold=Functions.RemoveUselessNums(str(Sold), 8),
        Chart=Chart,
        Top3BestInvestions=Chart["BestInvestions"],
        Date=[DateTime.datetime.today().day,
        DateTime.datetime.today().month,
        DateTime.datetime.today().year],
        Session=session)



@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)


    if request.method == 'POST':
        Username = form.username.data
        Name = form.name.data
        Email = form.email.data
        Password = form.password.data
        CryptographyKeys = Security.GenerateKeys()


        User = {"Username": Username,
                "Name": Name,
                "Avatar": "Default.png",
                "Email": Email,
                "Password": Security.Encode(Password, CryptographyKeys[0]),
                "Balance": 3.00000000,
                "WalletAddress": "0x" + Functions.WalletKey(),
                "PrivateKey": CryptographyKeys[1],
                "AccessToken": Functions.CreateAccessToken(CryptographyKeys[1]),
                "Games": {},
                "Stocks": {}}
    
        return Database.AddUserData(User, CryptographyKeys[0])

    return render_template('Register.html', form=form, Session=session)



@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        Username = request.form['username']
        Password = request.form['password']


        # 0: Username, 1: Name, 2: Avatar, 3: Email, 4: Password, 5: Balance, 6: WalletAddress, 7: PrivateKey, 8: AccessToken, 9: Games 10: Stocks
        User = Database.GetUserData(Username=Username)
        accPass = User[4]


        # If the password cannot be found, the user does not exist
        if accPass is None:
            flash("Username didnt found", 'danger')
            return redirect(url_for('login'))
        else:
            PublicKey = ""
            

            if not User[0] in Disk.PublicKeys:
                File = open("static/UserData/PublicKeys.json", "r")
                PublicKey = Json.loads(File.read())[Username]
            else:
                PublicKey = Disk.PublicKeys[User[0]]


            if Security.Encode(Password, PublicKey) == accPass:
                Login(Username)
                Database.ChangeAccessToken(Name=Username)

                return redirect(url_for("dashboard"))
            else:
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))


    return render_template('Login.html', Session=session)



# Transaction System
@app.route("/transaction", methods = ['GET', 'POST'])
@is_logged_in
def transaction():
    Form_ = TransactionForm(request.form)


    if request.method == 'POST':
        Wallet = Form_.wallet.data
        Amount = Form_.amount.data

        if Amount != "":
            if Session["Balance"] < float(Amount):
                flash("This amount isnt available in your wallet!", "danger")

            elif Wallet == Session["WalletAddress"]:
                flash("Invalid transaction.")

            else:
                Database.SendCryptos(Session["Username"], Wallet, float(Amount))

                flash("Money Sent to {0}!".format(Wallet), "success")
                Session["Balance"] = Session["Balance"] - float(Amount)

                Time.sleep(3)
                return redirect(url_for("dashboard"))

            return redirect(url_for('transaction'))


    return render_template('TransferPage.html', Balance=Session["Balance"], form=Form_, page='transaction', Session=session)



#Buy more WalletCoins
@app.route("/buy", methods = ['GET'])
@is_logged_in
def buy():
    if request.method == "GET":
        File = open("Price.json", "r")
        Market = Json.loads(File.read())

        return render_template('Buy.html', Balance=Session["Balance"], Session=Session, Price=Market["Price"], Market=Market["Market"])
    

    if request.method == "POST":
        Data = request.get_json()

        Database.SendCryptos("WalletCoinBANK", Session["WalletAddress"], float(Data["amount"]))
        Database.ChangeCurrencyValue("Increased", Data["amount"], float(Data["amount"])) # amount: cash
        Login(Session["Username"])

        flash("{0} WalletCoins bought!".format(Data["amount"]))

        Time.sleep(3)
        flash("")
        return redirect(url_for("dashboard"))



@app.route("/sell", methods=["POST", "GET"])
def sell():
    return render_template('Sell.html', Balance=Session["Balance"], Session=session)



# Dashboard page
@app.route("/dashboard", methods = ["GET"])
@is_logged_in
def dashboard():
    BalancePrice = Functions.CalculatePrice(float(Session["Balance"]), float(Database.GetPrice()))
    BlockchainChain = Database.GetBlockchain()
    BlocksList = []
    RequestArguments = request.args
    Pages = int(len(BlockchainChain) / 10)
    CurrentPage : int = 0

    
    # Change page using blockchain's Paginator
    if "page" in RequestArguments:
        CurrentPage = int(RequestArguments["page"])

        BlocksCounted = 0


# My failed algorithm for pagination

#        for block in blockchain:
#            if blocksCounted == abs(currentPage * 10 + 10):
#                blocksToRemove = abs(currentPage * 10 + 10)

                # Remove the previous blocks from blocks list
#                for bRemove in blocksList:
#                    if blocksToRemove == 10:
#                        break
#                    else:
#                        blocksList.remove(bRemove)
#                        blocksToRemove = blocksToRemove - 1
            
#            else: # Append some blocks in list until you reach the blocks for this page
#                blocksList.append(block)
#                blocksCounted = blocksCounted + 1


# My successful algorith for pagination

        for Block_ in BlockchainChain:
            if BlocksCounted >= abs(CurrentPage * 10 + 10) and BlocksCounted <= abs(CurrentPage * 10 + 20): # start
                BlocksList.append(Block_)
                BlocksCounted = BlocksCounted + 1

            if BlocksCounted == abs(CurrentPage * 10 + 20): # end
                break
            
            BlocksCounted = BlocksCounted + 1
        
        CurrentPage = CurrentPage
    

    else: # The first page
        BlocksCounted = 0
        for Block_ in BlockchainChain:
            if BlocksCounted == 10:
                break
            else:
                BlocksList.append(Block_)
                BlocksCounted += 1

    
    Previous = CurrentPage - 1
    if Previous < 0:
        Previous = 0
    
    NextPage = CurrentPage + 1
    if NextPage > Pages:
        NextPage = Pages


    return render_template('Blockchain.html',
        Balance=Session["Balance"],
        Price=BalancePrice,
        WalletAddress=Session["WalletAddress"],
        PrivateKey=Session["PrivateKey"],
        AccessToken=Session["AccessToken"],
        BlocksList=BlocksList,
        Pages=Pages,
        Previous=Previous,
        Next=NextPage,
        CurrentPage=CurrentPage,
        Session=Session)



# View block's data ( hash, transactions )
@app.route("/block", methods = ["GET"])
def block():
    args = request.args
    BlockNumber = int(args.get("number"))
    FoundBlock = Database.GetBlock(BlockNumber)
    ThisBlock = Database.GetBlockchainData(BlockNumber)
    return render_template("Block.html",
        Number=BlockNumber,
        Nonce=ThisBlock["Nonce"],
        Hash=ThisBlock["Hash"],
        PreviousHash=ThisBlock["PreviousHash"],
        BlockData=FoundBlock,
        Session=session)



# Create a new game
@app.route("/createGame", methods=["POST", "GET"])
def createGame():
    Page = CreateGameForm(request.form)


    if request.method == "POST":
        AllGames = Database.GetAllGames()


        if Page.gameName.data != "" and Page.stocksAmount.data != "":
            if Page.gameName.data in AllGames:
                flash("This game already exist!")
                return render_template("CreateGame.html", form=Page)
            

            Database.CreateGame(Page.gameName.data, Page.promotion.data, int(Page.stocksAmount.data))
            flash("Game Created !!!")

        else:
            flash("Please fill in the spaces !!!")


    return render_template("CreateGame.html", form=Page, Session=session)



# My Games Dashboard
@app.route("/myGamesDashboard", methods=["GET"])
def myGamesDashboard():
    RequestArguments = request.args


    if "Game" in RequestArguments:
        DashboardAction = "Game"
        Game = {}


        if not RequestArguments.get("Game") in Disk.Games:
            Game = Database.GetGameData(RequestArguments.get("Game"))
        else:
            Game = Disk.Games[RequestArguments.get("Game")]


        # Load the game
        MyGames = Session["Games"]
        GamesStockHolder = {}
    

        for Game_ in MyGames:
            for GameData in MyGames[Game_]:
                if GameData == "StockHolder":
                    if MyGames[Game_][GameData] == "True":
                        GamesStockHolder[Game_] = Game_


        return PrepareMyGame(MyGames_=MyGames, Game=Game, Action=DashboardAction, Null=False, RequestArguments=request.args)
            
    else:
        MyGames = Session["Games"]

        GamesCounted = 0
        for Game_ in MyGames:
            if GamesCounted < 1:
                Game = Database.GetGameData(Game_)
                GamesCounted += 1
            break


        if int(len(MyGames)) > 0: 
            DashboardAction = "Idle"
            GamesStockHolder = {}
        

            for Game_ in MyGames:
                for GameData in MyGames[Game_]:
                    if GameData == "StockHolder":
                        if MyGames[Game_][GameData] == "True":
                            GamesStockHolder[Game_] = Game_



            return render_template("MyGamesDashboard.html",
                Action="Idle",
                MyGames=Session["Games"],
                GamesStockHolder=GamesStockHolder,
                Date=[
                DateTime.datetime.today().day,
                DateTime.datetime.today().month,
                DateTime.datetime.today().year],
                Session=session)
        else:
            return PrepareMyGame({}, {}, "NoGames", True, request.args)



@app.route("/games/explore/<string:type>", methods=["GET"])
def exploreGame(type):
    if request.method == "GET":
        Type = type



        # First of all, load my investings data - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        MyGames = Session["Games"]

        GamesCounted = 0
        for Game_ in MyGames:
            if GamesCounted < 1:
                Game = Database.GetGameData(Game_)
                GamesCounted += 1
            break


        if int(len(MyGames)) > 0: 
            DashboardAction = "Idle"
            GamesStockHolder = {}
        

            for Game_ in MyGames:
                for GameData in MyGames[Game_]:
                    if GameData == "StockHolder":
                        if MyGames[Game_][GameData] == "True":
                            GamesStockHolder[Game_] = Game_



        # Now load the games - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if Type == "MostValued":
            Games = Database.GetAllGames()
            MostValuedGamesDict = {
                "Section1": {},
                "Section2": {},
                "Section3": {},
                "Section4": {}
            }
            MostValuedGames = []
            MostValuedGamesNames = []
            CurrentSection = 4


            while len(MostValuedGames) < 16:
                MostValuedGame = 0


                for Game in Games:
                    GameAlreadyAdded = False


                    if Game in MostValuedGamesNames:
                        GameAlreadyAdded = True
                        continue

                    
                    if not GameAlreadyAdded:
                        if Games[Game]["Value"] > MostValuedGame:
                            MostValuedGame = Games[Game]["Value"]
                

                for  Game in Games:
                    if Games[Game]["Value"] == MostValuedGame and not Game in MostValuedGamesNames:
                        GameDict = {"Name": Game, "IconPath": "Default.jpg", "Value": Games[Game]["Value"]}
                        MostValuedGames.append(GameDict)
            

            for Game in range(0, len(MostValuedGames) - 1):
                if len(MostValuedGamesDict["Section" + str(CurrentSection)]) < 4:
                    MostValuedGamesDict["Section" + CurrentSection][MostValuedGames[Game]["Name"]] = MostValuedGames[Game]
                else:
                    CurrentSection -= 1
                    MostValuedGamesDict["Section" + CurrentSection][MostValuedGames[Game]["Name"]] = MostValuedGames[Game]
            

            return render_template("MyGamesDashboard.html",
                Action="Explore",
                Results=MostValuedGamesDict,
                MyGames=Session["Games"],
                GamesStockHolder=GamesStockHolder,
                Date=[
                DateTime.datetime.today().day,
                DateTime.datetime.today().month,
                DateTime.datetime.today().year],
                Session=session)
        


        if Type == "Trend":
            pass



@app.route("/gameCreator", methods=["GET"])
def gameCreator():
    if request.method == "GET":
        User : list
        

        if request.args.get("Creator") in Disk.Users["Users"]:
            User = Disk.Users["Users"][request.args.get("Creator")]
        else:
            User = Database.GetUserData(request.args.get("Creator"))
        
        
        Games = User[7]
        GamesFound : list = []


        GamesCounted = 0
        for Game in Games:
            if GamesCounted == 3:
                break
            
            GamesFound.append(Game)
            GamesCounted += 1

        return render_template("MyGamesDashboard.html", Action="GameCreatorPage", CreatorName=User[0], Games=GamesFound, Session=session)



@app.route("/searchGame", methods=["POST"])
def searchGame():
    if request.method == "POST":
        SearchGame = request.form["game"]
        Games = Database.GetAllGames()
        FoundGames = []

        MyGames = Session["Games"]
        GamesStockHolder = {}


        for Game in Games:
            if Game.startswith(SearchGame):
                FoundGames.append(Game)
        

        for Game_ in MyGames:
            for GameData in MyGames[Game_]:
                if GameData == "StockHolder":
                    if MyGames[Game_][GameData] == "True":
                        GamesStockHolder[Game_] = Game_
        

        return render_template("myGamesDashboard.html",
        Action="Search",
        Searched=SearchGame,
        FoundGames=FoundGames,
        MyGames=Session["Games"],
        GamesStockHolder=GamesStockHolder,
        Date=[DateTime.datetime.day,
        DateTime.datetime.month,
        DateTime.datetime.year],
        Session=session)



@app.route("/gameSettings", methods=["POST", "GET"])
def gameSettings():
    if request.method == "GET":
        RequestArguments = request.args

        return render_template("myGamesDashboard.html",
        Action="Settings",
        Game=RequestArguments.get("Game"),
        MyGames=Session["Games"],
        Date=[DateTime.datetime.day,
        DateTime.datetime.month,
        DateTime.datetime.year],
        Session=session)
    

    if request.method == "POST":
        RequestArguments = request.args

        NewName = request.form["GameName"]
        NewDescription = request.form["GameDescription"]


        if not "UploadImage" in request.files:
            Database.GameSettings(PreviousGame=RequestArguments.get("Game"), Name=NewName, Description=NewDescription, Image_=None)
        else:
            Database.GameSettings(PreviousGame=RequestArguments.get("Game"), Name=NewName, Description=NewDescription, Image_=request.files["UploadImage"])
        
        flash("Game data changed !!!")

        
        Time.sleep(3)
        return redirect(url_for(f"myGamesDashboard"))



def PrepareMyGame(MyGames_ : dict, Game : dict, Action : str, Null : bool, RequestArguments):
    if not Null:
        MyGames = MyGames_
        GamesStockHolder = {}
        Stats = {}
        SearchTo = ""
        StockValue = Game["Value"] / Game["Stocks"]["Total"]
        StocksOwned = Game["Stocks"]["Owned"]
        StockValueWLLC = Functions.CalculateStockPrice(int(StocksOwned), float(Game["Value"]))
        StockValueEUR = Functions.CalculatePrice(StockValueWLLC, Database.GetPrice())
        Date, Body = {}, {}


        if not "Day" in RequestArguments and not "Month" in RequestArguments and not "Year" in RequestArguments:
            Body = {"TimeFrame": "Today", "Day": DateTime.date.today().day, "Month": DateTime.date.today().month, "Year": DateTime.date.today().year}
            SearchTo = "Hour"
    
        else:
            Body = {"TimeFrame": RequestArguments.get("TimeFrame"), "Month": RequestArguments.get("Month") or None, "Year": RequestArguments.get("Year")}

            if "Day" in RequestArguments: Body["Day"] = RequestArguments.get("Day")
            if RequestArguments.get("TimeFrame") == "Today": SearchTo = "Hour"
            if RequestArguments.get("TimeFrame") == "Month" or RequestArguments.get("TimeFrame") == "Year": SearchTo = "Day"

        Date = Body



        if "Game" in RequestArguments:
            Stats = Database.GetStockPriceChart(RequestArguments.get("Game"), Body["TimeFrame"], Date)
        else:
            GamesCounted = 0
            for Game_ in MyGames:
                if GamesCounted < 1:
                    Stats = Database.GetStockPriceChart(Game_, Body["TimeFrame"], Date)
                    GamesCounted += 1
                break



        for Game_ in MyGames:
            for GameData in MyGames[Game_]:
                if GameData == "StockHolder":
                    if MyGames[Game_][GameData] == "True":
                        GamesStockHolder[Game_] = Game_


        return render_template("MyGamesDashboard.html",
        Action=Action, Game=RequestArguments.get("Game"),
        SearchTo=SearchTo,
        GameCreator=Game["Creator"],
        Playings = Game["Playings"],
        StockValue=Functions.RemoveUselessNums(str(StockValue), 8),
        StockEUR=Functions.RemoveUselessNums(str(StockValueEUR), 2),
        MyGames=MyGames_,
        GamesStockHolder=GamesStockHolder,
        Volume=Stats["Volume"],
        Bought=Functions.RemoveUselessNums(str(Stats["Bought"]), 8),
        Sold=Functions.RemoveUselessNums(str(Stats["Sold"]), 8),
        Change=Functions.RemoveUselessNums(str(Stats["Change"]), 2),
        Changed=Stats["Changed"],
        Chart=Stats["Stats"],
        Date=[DateTime.datetime.today().day,
        DateTime.datetime.today().month,
        DateTime.datetime.today().year],
        Session=session)
    
    else:
        return render_template("MyGamesDashboard.html",
        Action="Idle",
        Game="",
        SearchTo="",
        GameCreator="",
        Playings=0,
        StockValue=0.0,
        StockEUR=0.00,
        MyGames=[],
        GamesStockHolder=[],
        Volume=0.0,
        Bought=0.0, Sold=0.0,
        Change=0.0,
        Changed="",
        Chart=[], Date=[
        DateTime.datetime.today().day,
        DateTime.datetime.today().month,
        DateTime.datetime.today().year],
        Session=session)



# Buy some stocks
@app.route("/buyStocks", methods=["POST", "GET"])
def buyStocks():
    form = BuyStocksForm(request.form)

    if request.method == "GET":
        RequestArguments = request.args
        MyGames = Session["Games"]
        Game = {}

        
        if RequestArguments.get("Game") in Disk.Games:
            Game = Disk.Games[RequestArguments.get("Game")]
        else:
            Game = Database.GetGameData(RequestArguments.get("Game"))


        return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="BuyStocks", Null=False, RequestArguments=RequestArguments)


    if request.method == "POST":
        RequestArguments = request.args
        MyGames = Session["Games"]
        Game = {}


        if RequestArguments.get("Game") in Disk.Games:
            Game = Disk.Games[RequestArguments.get("Game")]
        else:
            Game = Database.GetGameData(RequestArguments.get("Game"))


        GameValue = Game["Value"]
        StocksAmount = Game["Stocks"]["Total"]
        AmountToPay = Functions.CalculateStockPrice(StocksAmount, GameValue) * int(form.amount.data)


        if Game["Stocks"]["ForSell"] <= int(form.amount.data):
            flash("This amount isnt available for purchace.")
            return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="BuyStocks", Null=False, RequestArguments=RequestArguments)
        
        elif Session["Balance"] <= AmountToPay:
            flash("This amount isnt available in your wallet.")
            return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="BuyStocks", Null=False, RequestArguments=RequestArguments)
        
        else:
            Database.BuyStocks(RequestArguments.get("Game"), int(form.amount.data), float(AmountToPay))
            flash("Stocks Bought !!!")

            Login(Session["username"])
            return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="BuyStocks", Null=False, RequestArguments=RequestArguments)



# Sell stocks
@app.route("/sellStocks", methods=["POST", "GET"])
def sellStocks():
    form = SellStocksForm(request.form)

    if request.method == "GET":
        RequestArguments = request.args
        MyGames = Session["Games"]
        Game = {}


        if RequestArguments.get("Game") in Disk.Games:
            Game = Disk.Games[RequestArguments.get("Game")]
        else:
            Game = Database.GetGameData(RequestArguments.get("Game"))


        return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="SellStocks", Null=False, RequestArguments=RequestArguments)
    
    
    if request.method == "POST":
        RequestArguments = request.args
        MyGames = Session["Games"]
        MyStocks = Session["Stocks"]
        Game = {}


        if RequestArguments.get("Game") in Disk.Games:
            Game = Disk.Games[RequestArguments.get("Game")]
        else:
            Game = Database.GetGameData(RequestArguments.get("Game"))


        if MyStocks[RequestArguments.get("Game")] < int(form.amount.data):            
            flash("This amount isnt available in your stocks wallet")
            return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="SellStocks", Null=False, RequestArguments=RequestArguments)
        
        else:
            Session["Stocks"] = MyStocks
            Database.SellStocks(RequestArguments.get("Game"), int(form.amount.data))


            if not Session["Username"] in Disk.Users["Users"]:
                NewUser = {"Username": Session["Username"],
                        "Name": Session["Name"],
                        "Avatar": Session["Avatar"],
                        "Email": Session["Email"],
                        "Password": Session["Password"],
                        "Balance": Session["Balance"],
                        "WalletAddress": Session["WalletAddress"],
                        "PrivateKey": Session["PrivateKey"],
                        "AccessToken": Session["AccessToken"],
                        "Games": Session["Games"],
                        "Stocks": Session["Stocks"]}
                
            Disk.Users["Users"][Session["username"]]["Stocks"] = Session["Stocks"]

            flash("{0} Stocks Sold !!!".format(str(form.amount.data)))
            return PrepareMyGame(MyGames_=MyGames, Game=Game, Action="SellStocks", Null=False, RequestArguments=RequestArguments)



@app.route("/issueStocks", methods=["POST", "GET"])
def issueStocks():
    if request.method == "GET":
        RequestArguments = request.args
        MyGame = Session["Games"]
        Game = {}


        if RequestArguments.get("Game") in Disk.Games:
            Game = Disk.Games[RequestArguments.get("Game")]
        else:
            Game = Database.GetGameData(RequestArguments.get("Game"))


        return PrepareMyGame(MyGames_=MyGame, Game=Game, Action="IssueStocks", Null=False, RequestArguments=RequestArguments)
    
    
    if request.method == "POST":
        RequestArguments = request.args
        MyGame = Session["Games"]
        Game = {}


        if RequestArguments.get("Game") in Disk.Games:
            Game = Disk.Games[RequestArguments.get("Game")]
        else:
            Game = Database.GetGameData(RequestArguments.get("Game"))


        Database.IssueNewStocks(InGame=RequestArguments.get("Game"), Amount=int(request.form["amount"]))


        flash("{0} new Stocks released !!!".format(str(request.form["amount"])))
        return PrepareMyGame(MyGames_=MyGame, Game=Game, Action="IssueStocks", Null=False, RequestArguments=RequestArguments)



@app.route("/About")
def about():
    return render_template("About.html", Session=session)


@app.route("/FAQ")
def FAQ():
    return render_template("FAQ.html", Session=session)


@app.route("/RESTfulApi")
def restFulApi():
    return render_template("RestApi.html", Session=session)


@app.route("/helpCenter")
def helpCenter():
    return render_template("HelpCenter.html", Session=session)


@app.route("/reportProblem", methods=["POST"])
def reportProblem():
    if request.method == "POST":
        Email = request.form["email"]
        Text = request.form["message"]


        Sender = "netsgamedev@gmail.com"
        Admin = "walletcoinofficial2021@gmail.com"
        Message = """
            Hey WalletCoin Admin,

            Someone reported a problem in WalletCoin. The sender is {0}.
            Message:
            
            {1}
        """.format(Email, Text)


        with SMTP.SMTP("smtp.gmail.com", 587) as Server:
            Server.starttls()
            Server.login(Sender, "gamedev.com")
            Server.sendmail(Sender, Admin, Message)
        

        flash("Message was sent!")

        Time.sleep(3)
        flash("")


        return redirect(url_for("dashboard"))



# # # # Create the restful api # # # #


@app.route("/api/price/", methods=["GET"])
def Price():
    if request.method == "GET":
        Price = Database.GetPrice()
        return jsonify({"result": "%s EUR" % Price})



@app.route("/api/price/change/", methods=["POST"])
def PriceChange():
    if request.method == "POST":
        RequestArguments = request.args


        if "bought" in RequestArguments:
            Database.ChangeCurrencyValue("Increased", float(RequestArguments.get("amount")) * Database.GetPrice(), RequestArguments.get("amount"))
        
        if "sold" in RequestArguments:
            Database.ChangeCurrencyValue("Decreased", float(RequestArguments.get("amount")) * Database.GetPrice(), RequestArguments.get("amount"))



@app.route("/api/price/chart/", methods=["GET"])
def PriceChart():
    if request.method == "GET":
        RequestArguments = request.args
        Date = {}


        if not "TimeFrame" in RequestArguments:
            return jsonify({"result": {"error": "TimeFrame argument is missing!"}})
        
        TimeFrame = RequestArguments.get("TimeFrame")

        
        if not "Day" in RequestArguments and not "Month" in RequestArguments and not "Year" in RequestArguments:
            Date = {"TimeFrame": "Today", "Day": DateTime.date.today().day, "Month": DateTime.date.today().month, \
                "Year": DateTime.date.today().year}
        else:
            Date = {"TimeFrame": RequestArguments.get("TimeFrame"), "Month": RequestArguments.get("Month") or None, \
                "Year": RequestArguments.get("Year")}

            if "Day" in RequestArguments:
                Date["Day"] = RequestArguments.get("Day")


        return jsonify({"result": Database.GetPriceChart(
                TimeFrame=TimeFrame, Date=Date)
                }
            )



@app.route("/api/auth/", methods=["GET"])
def ApiAuth():
    if request.method == "GET":
        RequestArguments = request.args


        if not "AccessToken" in RequestArguments:
            return jsonify({"result": {"error": "AccessToken argument doesnt exist!"}})

        AccessToken = RequestArguments.get("AccessToken")


        Account = Database.LoginWithAccessToken(AccessToken=AccessToken)


        if Account == "User didnt found!":
            return jsonify({"result": {"error": "This account doesnt exist"}})
        else:
            return jsonify({"result": {"Username": Account[0], "Balance": Account[1], "WalletAddress": Account[2]}})



@app.route("/api/wallet/create/", methods=["POST"])
def CreateWallet():
    if request.method == "POST":
        RequestArguments = request.args
        Keys = Security.GenerateKeys()


        if not "Pass" in RequestArguments:
            return jsonify({"result": {"error": "Please define a password"}})
        
        Password = RequestArguments.get("Pass")
        Wallet = "0x" + Functions.CreateRandomKey(30)


        NewWallet = {
            "Balance": 0.0,
            "Password": Password,
            "PrivateKey": Keys[1],
            "AccessToken": Functions.CreateAccessToken(Keys[1])
        }

        Database.AddWallet(Name=Wallet, Wallet=NewWallet, PublicKey=Keys[0])
        return jsonify({"result": NewWallet})



@app.route("/api/wallet/connect/", methods=["GET"])
def ConnectWallet():
    if request.method == "GET":
        RequestArguments = request.args


        if not "AccessToken" in RequestArguments:
            return jsonify({"result": {"error": "AccessToken argument doesnt exist!"}})

        AccessToken = RequestArguments.get("AccessToken")


        Wallet = Database.LoginWalletWithAccessToken(AccessToken=AccessToken)


        if Wallet == "Wallet didnt found!":
            return jsonify({"result": {"error": "This account doesnt exist"}})
        else:
            return jsonify({"result": {"Address": Wallet[0], "Balance": Wallet[1]}})



@app.route("/api/transaction/", methods=["POST"])
def ApiTransaction():
    if request.method == "POST":
        RequestArguments = request.args


        if not "WalletAddress" in RequestArguments:
            return jsonify({"result": {"error": "WalletAddress doesnt exist!"}})
        
        WalletAddress = RequestArguments.get("WalletAddress")


        if not "AccessToken" in RequestArguments:
            return jsonify({"result": {"error": "AccessToken argument doesnt exist!"}})

        AccessToken = RequestArguments.get("AccessToken")


        if not "Amount" in RequestArguments:
            return jsonify({"result": {"error": "amount doesnt exist!"}})
        
        Amount = RequestArguments.get("Amount")


        return Database.apiTransaction(AccessToken=AccessToken, Wallet=WalletAddress, Amount=Amount)



@app.route("/api/withdraw", methods=["POST"])
def Withdraw():
    if request.method == "POST":
        RequestArguments = request.args


        if "Secret" in RequestArguments:
            if RequestArguments.get("Secret") == "WLLC_TRANS_2811":
                From, To = "", ""
                Amount = 0.0


                if "From" in RequestArguments:
                    From = RequestArguments.get("From")
                

                if "To" in RequestArguments:
                    To = RequestArguments.get("To")
                

                if "Amount" in RequestArguments:
                    Amount = RequestArguments.get("Amount")


                Database.UpdateWalletData(Wallet=From, Amount=Amount, Action="Remove")
                Database.UpdateWalletData(Wallet=To, Amount=Amount, Action="Add")



@app.route("/api/newPlayer/", methods=["POST"])
def NewPlayer():
    if request.method == "POST":
        RequestArguments = request.args
        

        if not "game" in RequestArguments:
            return jsonify({"result": {"error": "'game' argument doesnt exist in request body!"}})
        
        GameName = RequestArguments.get("game")
        

        if not "playerUname" in RequestArguments:
            return jsonify({"result": {"error": "player's username doesnt exist in the request body!"}})

        PlayerUsername = RequestArguments.get("playerUname")


        if GameName in Disk.Games:
            Disk.Games[GameName]["Playings"] += 1

        else:
            Game = Database.GetGameData(GameName)
            Game["Playings"] += 1

            Disk.UpdateGameData(Game)

        
        return jsonify({"result": "New playing added to game: {0}".format(GameName)})



@app.route("/api/donateGame/", methods=["POST"])
def DonateGame():
    if request.method == "POST":
        RequestArgs = request.args

        GameName : str
        Donater : str
        Amount : float


        if not "game" in RequestArgs:
            return jsonify({"result": {"error": "'game' argument doesnt exist!"}})
        else: GameName = RequestArgs.get("game")


        if not "donator" and not "donater" in RequestArgs:
            return jsonify({"result": {"error": "donator's username doesnt exist! Remember, you can use 'donator' or 'donater' in the request arguments!"}})
        else:
            if "donater" in RequestArgs:
                Donater = RequestArgs.get("donater")
            elif "donator" in RequestArgs:
                Donater = RequestArgs.get("donator")
        
        
        if not "amount" in RequestArgs:
            return jsonify({"result": {"error": "please define an amount that sender will donate!"}})
        else: Amount = RequestArgs.get("amount")

        
        Account = Database.LoginWithApiKey(Donater)
        if Account[6] == None: # api key
            return jsonify({"result": {"error": "This api key did not found!"}})
        
        if Account[6] == Donater:
            if float(Account[4]) < float(Amount): # balance
                return jsonify({"result": {"error": "This amount isnt available in your wallet!"}})
            
            else:
                Database.PayGame(GameName, Donater, float(Amount))
        
        return jsonify({"result": "Someone Donated your game!"})



@app.route("/api/payToPlay", methods=["POST"])
def PayGame():
    if request.method == "POST":
        RequestArgs = request.args

        GameName : str
        Purchacer : str
        Amount : float


        if not "game" in RequestArgs:
            return jsonify({"result": {"error": "'game' argument doesnt exist!"}})
        else: GameName = RequestArgs.get("game")


        if not "purchaser" in RequestArgs:
            return jsonify({"result": {"error": "please define the purchaser of the game!"}})
        else: Purchacer = RequestArgs.get("purchaser")
        

        if not "amount" in RequestArgs:
            return jsonify({"result": {"error": "please define an amount that sender will pay!"}})
        else: Amount = RequestArgs.get("amount")


        Account = Database.LoginWithApiKey(Purchacer)
        if Account[6] == None: # api key
            return jsonify({"result": {"error": "This api key not found!"}})
        
        if Account[6] == Purchacer:
            if float(Account[4]) < float(Amount): # balance
                return jsonify({"result": {"error": "This amount isnt available in your wallet!"}})
            
            else:
                Database.PayGame(GameName, Purchacer, float(Amount))

        return jsonify({"result": "Someone Payed your game!"})



if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug = True)
