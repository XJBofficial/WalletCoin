import json as JSON



def CompanyHolders():
    with open("database/company/Holders.json", "r") as File:
        Data = JSON.loads(File.read())
        File.close()

        return Data



def Vault():
    with open("database/Price.json", "r") as File:
        Data = JSON.loads(File.read())
        
        
        Cash = Data["Cash"]
        Supply = Data["Supply"]
        Owned = Data["Owned"]

        
        Data.clear()
        File.close()


        return {
            "Cash": Cash,
            "Supply": Supply,
            "Owned": Owned
        }



def GetPrice():
    with open("database/Price.json", "r") as File:
        Data = JSON.loads(File.read())
        Price = Data["Price"]
        
        Data.clear()
        File.close()

        return Price



def SavePrice(Price : float, Cash : float, Supply : float, Owned : float, Chart : dict):
    with open("database/Price.json", "r") as FileRead:
        Price_ = JSON.loads(FileRead.read())


        Price_["Price"] = Price
        Price_["Cash"] = Cash
        Price_["Supply"] = Supply
        Price_["Owned"] = Owned

        
        for Year in Chart:
            if not str(Year) in Price_["Chart"]:
                Price_["Chart"][str(Year)] = {}
            

            for Month in Chart[Year]:
                if not str(Month) in Price_["Chart"][str(Year)]:
                    Price_["Chart"][str(Year)][str(Month)] = {}


                for Day in Chart[Year][Month]:
                    if not str(Day) in Price_["Chart"][str(Year)][str(Month)]:
                        Price_["Chart"][str(Year)][str(Month)][str(Day)] = Chart[Year][Month][Day]
                    else:
                        for C in Chart[Year][Month][Day]:
                            Price_["Chart"][str(Year)][str(Month)][str(Day)].append(C)
        

        with open("database/Price.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Price_, indent=1))
            FileWrite.close()
        

        Price_.clear()
        FileRead.close()



def FindWallet(PrivateKey : str):
    Address = ""


    with open("database/PrivateKeys.json", "r") as File:
        Keys = JSON.loads(File.read())


        if PrivateKey in Keys:
            Address = Keys[PrivateKey]
        

        Keys.clear()
        File.close()
    

    with open("database/Wallets.json", "r") as File:
        Wallets = JSON.loads(File.read())


        if Address in Wallets:
            Wallet = Wallets[Address]
            
            Wallets.clear()
            File.close()

            return Wallet
        else:
            Wallets.clear()
            File.close()

            return {}



def SaveWallets(Wallets : dict, Deleted : list):
    with open("database/Wallets.json", "r") as FileRead:
        Wallets_ = JSON.loads(FileRead.read())


        for W in Deleted:
            del Wallets_[W]
        

        for W in Wallets:
            Wallets_[W] = Wallets[W]
        

        with open("database/Wallets.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Wallets_, indent=1))
            FileWrite.close()
        

        Wallets.clear()
        FileRead.close()



def FindStripeAccount(Address : str):
    with open("database/StripeAccounts.json", "r") as File:
        StripeAccounts = JSON.loads(File.read())


        if Address in StripeAccounts:
            Wallet = StripeAccounts[Address]
            
            StripeAccounts.clear()
            File.close()

            return Wallet
        else:
            StripeAccounts.clear()
            File.close()

            return {}



def SaveStripeAccounts(StripeAccounts : dict):
    with open("database/StripeAccounts.json", "r") as FileRead:
        Accounts_ = JSON.loads(FileRead.read())


        for Wallet in StripeAccounts:
            Accounts_[Wallet] = StripeAccounts[Wallet]
        

        with open("database/StripeAccounts.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Accounts_, indent=1))
            FileWrite.close()
        

        Accounts_.clear()
        FileRead.close()



def FindBankAccounts(Address : str):
    with open("database/BankAccounts.json", "r") as File:
        BankAccounts = JSON.loads(File.read())


        if Address in BankAccounts:
            Wallet = BankAccounts[Address]
            
            BankAccounts.clear()
            File.close()

            return Wallet
        else:
            BankAccounts.clear()
            File.close()

            return {}



def SaveBankAccounts(BankAccounts : dict):
    with open("database/BankAccounts.json", "r") as FileRead:
        Accounts_ = JSON.loads(FileRead.read())


        for Wallet in BankAccounts:
            if not Wallet in Accounts_:
                Accounts_[Wallet] = []

            for Payout in BankAccounts[Wallet]:
                Accounts_[Wallet].append(Payout)
        

        with open("database/BankAccounts.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Accounts_, indent=1))
            FileWrite.close()
        

        Accounts_.clear()
        FileRead.close()



def FindWalletPayment(Address : str, Id : str):
    with open("database/WalletPayments.json", "r") as File:
        Payments = JSON.loads(File.read())


        if Address in Payments:
            Wallet = Payments[Address]
            
            Payments.clear()
            File.close()


            for I in range(0, len(Wallet)):
                if Wallet[I]["Id"] == Id:
                    return Wallet[Id]
            
            return {}
        else:
            Payments.clear()
            File.close()

            return {}



def UpdateWalletPaymentStatus(CachePayments : list, Address : str, Id : str, Status : str):
    with open("database/WalletPayments.json", "r") as File:
        Payments = JSON.loads(File.read())


        if Address in Payments:
            Wallet = Payments[Address]
            
            Payments.clear()
            File.close()


            for I in range(0, len(Wallet)):
                if Wallet[I]["Id"] == Id:
                    Wallet[I]["Status"] = Status
                    return Wallet + CachePayments
            
            return []
        else:
            Payments.clear()
            File.close()

            return []



def FindWalletPayments(Address : str):
    with open("database/WalletPayments.json", "r") as File:
        Payments = JSON.loads(File.read())


        if Address in Payments:
            Wallet = Payments[Address]
            
            Payments.clear()
            File.close()

            return Wallet
        else:
            Payments.clear()
            File.close()

            return {}



def SaveWalletPayments(Payments : dict):
    with open("database/WalletPayments.json", "r") as FileRead:
        Payments_ = JSON.loads(FileRead.read())


        for Wallet in Payments:
            if not Wallet in Payments_:
                Payments_[Wallet] = []

            for Payout in Payments[Wallet]:
                Payments_[Wallet].append(Payout)
        

        with open("database/WalletPayments.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Payments_, indent=1))
            FileWrite.close()
        

        Payments_.clear()
        FileRead.close()



def FindWalletPayout(Address : str, Id : str):
    with open("database/WalletPayouts.json", "r") as File:
        Payouts = JSON.loads(File.read())


        if Address in Payouts:
            Wallet = Payouts[Address]
            
            Payouts.clear()
            File.close()


            for I in range(0, len(Wallet)):
                if Wallet[I]["Id"] == Id:
                    return Wallet[Id]
            
            return {}
        else:
            Payouts.clear()
            File.close()

            return {}



def FindWalletPayouts(Address : str):
    with open("database/WalletPayouts.json", "r") as File:
        Payouts = JSON.loads(File.read())


        if Address in Payouts:
            Wallet = Payouts[Address]
            
            Payouts.clear()
            File.close()

            return Wallet
        else:
            Payouts.clear()
            File.close()

            return {}



def UpdateWalletPayoutStatus(CachePayouts : list, Address : str, Id : str, Status : str):
    with open("database/WalletPayouts.json", "r") as File:
        Payouts = JSON.loads(File.read())


        if Address in Payouts:
            Wallet = Payouts[Address]
            
            Payouts.clear()
            File.close()


            for I in range(0, len(Wallet)):
                if Wallet[I]["Id"] == Id:
                    Wallet[I]["Status"] = Status
                    return Wallet + CachePayouts
            
            return []
        else:
            Payouts.clear()
            File.close()

            return []



def SaveWalletPayouts(Payouts : dict):
    with open("database/WalletPayouts.json", "r") as FileRead:
        Payouts_ = JSON.loads(FileRead.read())


        for Wallet in Payouts:
            if not Wallet in Payouts_:
                Payouts_[Wallet] = []

            for Payout in Payouts[Wallet]:
                Payouts_[Wallet].append(Payout)
        

        with open("database/WalletPayouts.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Payouts_, indent=1))
            FileWrite.close()
        

        Payouts_.clear()
        FileRead.close()



def FindPrivKey(Wallet : str):
    with open("database/PrivateKeys.json", "r") as File:
        PrivateKeys = JSON.loads(File.read())

        
        for Key in PrivateKeys:
            if PrivateKeys[Key] == Wallet:
                PrivateKeys.clear()
                File.close()

                return Key
        

        PrivateKeys.clear()
        File.close()

        return ""



def SavePrivateKeys(PrivateKeys : dict, Deleted : list):
    with open("database/PrivateKeys.json", "r") as FileRead:
        PrivateKeys_ = JSON.loads(FileRead.read())


        for W in Deleted:
            del PrivateKeys_[W]
        

        for W in PrivateKeys:
            PrivateKeys_[W] = PrivateKeys[W]
        

        with open("database/PrivateKeys.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(PrivateKeys_, indent=1))
            FileWrite.close()
        

        PrivateKeys.clear()
        FileRead.close()



def GetBlockchain(Cache : list):
    with open("database/Blockchain.json", "r") as File:
        Blockchain = JSON.loads(File.read())
        Blockchain = Blockchain + Cache

        File.close()
        return Blockchain



def SaveBlockchain(Chain : list):
    with open("database/Blockchain.json", "r") as FileRead:
        Blockchain = JSON.loads(FileRead.read())
        Blockchain = Blockchain + Chain


        with open("database/Blockchain.json", "w") as FileWrite:
            FileWrite.write(JSON.dumps(Blockchain, indent=1))
            FileWrite.close()
        

        FileRead.close()
        Blockchain.clear()



def GetBlockByNumber(Cache : list, Block : int):
    with open("database/Blockchain.json", "r") as File:
        Blockchain = JSON.loads(File.read())
        Blockchain = Blockchain + Cache
        Block_ = []


        for B in Blockchain:
            if B["Block"] == Block:
                Block_.append(B)
        

        for B in Cache:
            if B["Block"] == Block:
                Block_.append(B)

        
        Blockchain.clear()
        File.close()

        return Block_



def GetBlockByWallet(Cache : list, Wallet : str):
    with open("database/Blockchain.json", "r") as File:
        Blockchain = JSON.loads(File.read())
        Blockchain = Blockchain + Cache
        Block_ = []


        for B in Blockchain:
            if B["Sender"] == Wallet:
                Block_.append(B)
        

        for B in Cache:
            if B["Sender"] == Wallet:
                Block_.append(B)

        
        Blockchain.clear()
        File.close()

        return Block_
