from hashlib import sha256
import datetime as DateTime
import DISKuse as Disk
import Database



def updatehash(*args):
    hashing_text = ""; h = sha256()

    # Loop through each argument and hash
    for arg in args:
        hashing_text += str(arg)

    h.update(hashing_text.encode('utf-8'))
    return h.hexdigest()



class Block():
    def __init__(self, Number = 0, PreviousHash = "0" * 64, Data = None, Nonce = 0):
        self.Data = Data
        self.Number = Number
        self.PreviousHash = PreviousHash
        self.Nonce = Nonce


    def hash(self):
        return updatehash(self.Number, self.PreviousHash, self.Data, self.Nonce)


    def __str__(self):
        return str("Block#: %s\nHash: %s\nPrevious: %s\nData: %s\nNonce: %s\n" % (
            self.Number, self.hash(), self.PreviousHash, self.Data, self.Nonce)
        )



class Blockchain():
    difficulty = 3


    def __init__(self):
        self.chain = []
    

    def mine(self, Block_, MyBlockNumber):
        Number : int


        if MyBlockNumber == None:
            BiggestBlock = 0

            for Bl in Database.GetBlockchain():
                if Bl["Number"] > BiggestBlock:
                    BiggestBlock = Bl["Number"]
            
            Number = BiggestBlock
        else:
            Number = MyBlockNumber + 1
        


        NewBlock = {
            "Number": Number,
            "PreviousHash": Block_.PreviousHash,
            "Hash": Block_.hash(),
            "Data": Block_.Data,
            "Nonce": Block_.Nonce
            }
        
        Disk.Blockchain.append(NewBlock)


    def isValid(self):
        for i in range(1, len(self.chain)):
            _previous = self.chain[i].PreviousHash
            _current = self.chain[i-1].hash()

            if _previous != _current or _current[:self.difficulty] != "0" * self.difficulty:
                return False

        return True
