import time as Time
import json as JSON


TimeStarted = False


Users = {
    "Users": {},
    "Wallets": {}}
Price = {
    "Stats": {},
    "Games": {}
}
Games = {}
PublicKeys = {}
Blockchain = []



def Start(Frames : int):
    print("Time started!!!")


    if Progress() is False:
        TimeStarted = True
    
    Time.sleep(Frames)

    
    if len(Users["Users"]) > 0 or len(Users["Wallets"]) > 0: SaveUserData(Users=Users)
    if len(Price["Stats"]) > 0 or len(Price["Games"]) > 0: SavePriceData(Data=Price)
    if len(Games) > 0: SaveGamesData(Data=Games)
    if len(PublicKeys) > 0: SavePublicKeys(Data=PublicKeys)
    if len(Blockchain) > 0: SaveBlockchainData(Chain=Blockchain)
        
    Start(Frames=100)



def UpdateUserData(User : dict):
    Users["Users"][User["Username"]] = User

    print(Users)



def UpdatePriceData(Path, Price_ : dict):
    if Path == None:
        Price += Price_
    else:
        Price + Path.append(Price_)

    print(Price)



def UpdateGamesData(Game : dict):
    Games[Game["Name"]] = Game

    print(Games)



def UpdatePublicKeys(User : str, Key : str):
    PublicKeys[User] = Key

    print(PublicKeys)



def SaveUserData(Users_ : dict):
    with open("Users.json", "r") as File:
        Data_ = JSON.loads(File.read())


        for User in Users_["Users"]:
            Data_["Users"][User] = Users_["Users"][User]


        for Wallet in Users_["Wallets"]:
            Data_["Wallets"][Wallet] = Users_["Wallets"][Wallet]


        with open("Users.json", "w") as F:
            F.write(JSON.dumps(Data_, indent=1))
            F.close()
    

        File.close()
    
        Users_["Users"].clear()
        Users_["Wallets"].clear()



def SavePriceData(Data : dict):
    with open("Price.json", "r") as FileRead:
        Stats = JSON.loads(FileRead.read())


        if "Stats" in Data:
            for Date in Data["Stats"]:
                for Stat in Data["Stats"][Date]:
                    Stats["Stats"][Date].append(Stats["Stats"][Date][Stat])
        

        if "Games" in Data:
            for Game in Data["Games"]:
                for Date in Data["Games"][Game]:
                    for Stat in Data["Games"][Game][Date]:
                        Stats["Games"][Game][Date].append(Stats["Games"][Game][Date][Stat])
        

        with open("Price.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Stats, indent=1))
            FileWrite.close()


        FileRead.close()


        Price["Stats"].clear()
        Price["Games"].clear()



def SaveGamesData(Data : dict):
    with open("Games.json", "r") as FileRead:
        Games = JSON.loads(FileRead.read())


        for Game in Data:
            Games[Game] = Data[Game]
        
        
        with open("Games.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Games, indent=1))
            FileWrite.close()


        FileRead.close()
        Games.clear()



def SavePublicKeys(Data : dict):
    with open("static/UserData/PublicKeys.json", "r") as FileRead:
        PublicKeys = JSON.loads(FileRead.read())

        
        for Pub in Data:
            PublicKeys[Pub] = Data[Pub]


        with open("static/UserData/PublicKeys.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(PublicKeys, indent=1))
            FileWrite.close()


        FileRead.close()
        PublicKeys.clear()



def SaveBlockchainData(Chain : list):
    with open("Blockchain.json", "r") as FileRead:
        Blocks = JSON.loads(FileRead.read())
        Blocks += Chain


        with open("Blockchain.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Blocks, indent=1))
            FileWrite.close()


        FileRead.close()
        Blockchain.clear()



def Progress():
    return TimeStarted



if __name__ == "__main__":
    Start(Frames=100)
