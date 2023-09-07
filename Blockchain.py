from hashlib import sha256
import datetime as Date
import json as JSON
import Database



class Block:
    def __init__(self, Number : int, Nonce : int, PreviousHash : str, Data : str, Sender : str, Recipient : str, Amount : float, Day : str, Hour : str):
        self.Block = Number
        self.Nonce = Nonce
        self.PreviousHash = PreviousHash
        self.Data = Data
        self.Sender = Sender
        self.Recipient = Recipient
        self.Amount = Amount
        self.Day = Day
        self.Hour = Hour
    

    def CreateHash(self):
        HashedText = str(self.Block) + str(self.Nonce) + self.PreviousHash + self.Data + self.Sender + self.Recipient + str(self.Amount) + self.Day + self.Hour
        SHA256 = sha256()
        SHA256.update(HashedText.encode("utf-8"))
        return SHA256.hexdigest()



class Blockchain:
    def __init__(self):
        self.Nonce = 30
        self.Chain = []
    

    def GenerateBlock(self, Number : int, Nonce : int, PreviousHash : str, Data : str, Sender : str, Recipient : str, Amount : float):
        Day = "%s/%s/%s" % (str(Date.datetime.today().day), str(Date.datetime.today().month), str(Date.datetime.today().year))
        Hour = "%s::%s::%s" % (str(Date.datetime.today().hour), str(Date.datetime.today().minute), str(Date.datetime.today().second))
        Block_ = Block(Number=Number, Nonce=Nonce, PreviousHash=PreviousHash, Data=Data, Sender=Sender, Recipient=Recipient, Amount=Amount, Day=Day, Hour=Hour)
        Bl = {
			"Block": Number,
            "Nonce": Nonce,
			"Hash": Block_.CreateHash(),
			"PrevHash": PreviousHash,
			"Data": Data,
			"Sender": Sender,
            "Recipient": Recipient,
            "Amount": Amount,
			"Day": Day,
			"Hour": Hour
		}

        return Bl


    def GenerateGeneticBlock(self):
        Day = "%s/%s/%s" % (str(Date.datetime.today().day), str(Date.datetime.today().month), str(Date.datetime.today().year))
        Hour = "%s::%s::%s" % (str(Date.datetime.today().hour), str(Date.datetime.today().minute), str(Date.datetime.today().second))
        Block_ = Block(Number=0, Nonce=self.Nonce, PreviousHash="0" * self.Nonce, Data="Genetic Block", Sender="", Recipient="", Amount=0, Day=Day, Hour=Hour)
        Genetic = {
			"Block": 0,
            "Nonce": self.Nonce,
			"Hash": Block_.CreateHash(),
			"PrevHash": "0" * self.Nonce,
			"Data": "Genetic Block",
			"Sender": "",
            "Recipient": "",
            "Amount": 0,
			"Day": Day,
			"Hour": Hour
		}

        return Genetic
    

    def IsValid(self, CacheBlocks : list):
        Blocks = Database.GetBlockchain(Cache=CacheBlocks)


        for B in Blocks:
            Block_ = Block(Number=B["Block"], Nonce=B["Nonce"], PreviousHash=B["PrevHash"], Data=B["Data"], Sender=B["Sender"], Recipient=B["Recipient"], Amount=B["Amount"], Day=B["Day"], Hour=B["Hour"])


            if Block_.CreateHash() != B["Hash"]:
                return False
        

        return True
    

    def FindMyBlocks(self, CacheBlocks : list, Wallet : str):
        return Database.GetBlockByWallet(Cache=CacheBlocks, Wallet=Wallet)
    

    def FindBlockByNumber(self, CacheBlocks : list, Number : int):
        return Database.GetBlockByNumber(Cache=CacheBlocks ,Block=Number)
    

    def GetLastBlocks(self, CacheBlocks : list, Count : int):
        Blocks = []


        if len(CacheBlocks) >= Count:
            for Block_ in range(len(CacheBlocks) -1, len(CacheBlocks) - Count -1, -1):
                Blocks.append(CacheBlocks[Block_])
        else:
            LoadMore = len(CacheBlocks) - Count

            for Block_ in range(len(CacheBlocks) -1, -1, -1):
                Blocks.append(CacheBlocks[Block_])

            with open("database/Blockchain.json", "r") as File:
                Blockchain_ = JSON.loads(File.read())

                if len(Blockchain_) >= LoadMore and LoadMore > 0:
                    for Block_ in range(len(Blockchain_) -1, len(Blockchain_) - LoadMore -1, -1):
                        Blocks.append(Blockchain_[Block_])
                else:
                    for Block_ in range(len(Blockchain_) -1, -1, -1):
                        Blocks.append(Blockchain_[Block_])

                Blockchain_.clear()
                File.close()
        

        return Blocks


    def GetLastBlockNumber(self, CacheBlocks : list):
        Number = -1


        for Block_ in CacheBlocks:
            if Block_["Block"] > Number:
                Number = Block_["Block"]
        


        with open("database/Blockchain.json", "r") as File:
            Blockchain_ = JSON.loads(File.read())

            
            for Block_ in Blockchain_:
                if Block_["Block"] > Number:
                    Number = Block_["Block"]
            

            Blockchain_.clear()
            File.close()
        

        return Number
