from Cryptography import Cryptography
from Blockchain import Blockchain
import datetime as Date


class Wallet:
    def CreateWallet(self, Phrase : str):
        Crypto = Cryptography()
        NewWallet = {
            "Address": Crypto.GenerateRandomKey(Count=25, RemoveSelected=False),
            "Balance": 0.0,
            "PublicKey": Crypto.GenerateRandomKey(Count=len(Crypto.PublicLogic), RemoveSelected=True),
            "PrivateKey": "",
            "SecretPhrase": Phrase,
            "API_KEY": Crypto.GenerateRandomKey(Count=64, RemoveSelected=False)
        }

        NewWallet["PrivateKey"] = Crypto.GeneratePrivateKey(PublicKey=NewWallet["PublicKey"])
        return NewWallet



class Transaction:
    def __init__(self, CacheBlocks : list, Sender : str, Recipient : str, Amount : float):
        self.Chain = Blockchain()


        if self.Chain.IsValid(CacheBlocks=CacheBlocks):
            MyBlocks = self.Chain.FindMyBlocks(CacheBlocks=CacheBlocks, Wallet=Sender)
            MyBlockNumber : int


            if len(MyBlocks) == 0:
                MyBlockNumber = self.Chain.GetLastBlockNumber(CacheBlocks=CacheBlocks) + 1
            else:
                MyBlockNumber = MyBlocks[0]["Block"]
        

            # Check for existing blocks. If there are not any block, generate the new one and after add your own block

            if MyBlockNumber == 0:
                self.Chain.Chain.append(self.Chain.GenerateGeneticBlock())
                MyBlockNumber = 1
            

            # Append the new block

            if len(MyBlocks) > 0:
                self.Chain.Chain.append(
                    self.Chain.GenerateBlock(
                        Number=MyBlockNumber,
                        Nonce=MyBlocks[0]["Nonce"],
                        PreviousHash=MyBlocks[len(MyBlocks) -1]["Hash"],
                        Data="Transaction %s WLLC" % str(Amount),
                        Sender=Sender,
                        Recipient=Recipient,
                        Amount=Amount
                    )
                )
            else:
                # Get the last blocks, so you can find the previous hash

                LastBlocks = self.Chain.GetLastBlocks(CacheBlocks=CacheBlocks + self.Chain.Chain, Count=1)
                PreviousHash : str


                if len(LastBlocks) > 1:
                    PreviousHash = self.Chain.Chain[len(self.Chain.Chain) -1]["Hash"]
                elif len(LastBlocks) == 1:
                    PreviousHash = LastBlocks[0]["Hash"]
                
                
                self.Chain.Chain.append(
                    self.Chain.GenerateBlock(
                        Number=MyBlockNumber,
                        Nonce=self.Chain.Nonce,
                        PreviousHash=PreviousHash,
                        Data="Transaction %s WLLC" % str(Amount),
                        Sender=Sender,
                        Recipient=Recipient,
                        Amount=Amount
                    )
                )
    

    def GetChain(self):
        return self.Chain.Chain
