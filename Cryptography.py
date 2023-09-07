import random as Random


class Cryptography:
    def __init__(self) -> None:
        self.PublicLogic = "8RyenSiAWUsKJvOFZcV45LE09YuPpXqC61zDMlGt3wrIagfTjQoh2NxdHmbB7k"
        self.PrivateLogic = "2T9gheVfm4P0WGbN3AioCpM8LZj7vuqUsylDKkJRBFc6zaHYwxnQtErSIdX15O"


    # Generate a random key

    def GenerateRandomKey(self, Count : int, RemoveSelected : bool):
        Chars = [
            "A", "B", "C", "D", "E", "F", "G", "H",
            "I", "J", "K", "L", "M", "N", "O", "P",
            "Q", "R", "S", "T", "U", "V", "W", "X",
            "Y", "Z", "a", "b", "c", "d", "e", "f",
            "g", "h", "i", "j", "k", "l", "m", "n",
            "o", "p", "q", "r", "s", "t", "u", "v",
            "w", "x", "y", "z", 0, 1, 2, 3, 4, 5,
            6, 7, 8, 9
        ]

        Text = ""


        if RemoveSelected:
            for I in range(Count):
                if len(Chars) == 1:
                    Text += str(Chars[0])
                    Chars.clear()
                
                elif len(Chars) > 1:
                    Number = Random.randint(0, len(Chars) -1)
                    Text += str(Chars[Number])
                    Chars.remove(Chars[Number])
        else:
            for I in range(Count):
                Number = Random.randint(0, len(Chars) -1)
                Text += str(Chars[Number])
        

        return Text
    

    # Generate a private key from public key

    def GeneratePrivateKey(self, PublicKey : str):
        NewPrivateKey = ""
        PublicKeyDict = {}


        for Char in range(0, len(self.PublicLogic)):
            PublicKeyDict[self.PublicLogic[Char]] = PublicKey[Char]


        for Char in self.PrivateLogic:
            NewPrivateKey += str(PublicKeyDict[Char])


        return NewPrivateKey
    
    
    # Find a private key

    def FindPrivateKey(self, PublicKey : str):
        PrivateKey = self.GeneratePrivateKey(PublicKey=PublicKey)
        return PrivateKey
    

    # Encrypt a text

    def Encrypt(self, PublicKey : str, Text : str):
        EncryptedText = ""


        for T in Text:
            if T == " ":
                EncryptedText += "_"
            else:
                for Pub in range(0, len(self.PublicLogic)):
                    if T == self.PublicLogic[Pub]:
                        EncryptedText += PublicKey[Pub]
        

        return EncryptedText
    

    # Decrypt a text

    def Decrypt(self, PrivateKey : str, Text : str): # Once we find the private key from "FindPrivateKey" method, then we decrypt the text
        DecryptedText = ""


        PrivateKeyDict = {}

        for Pr in range(0, len(self.PrivateLogic)):
            PrivateKeyDict[self.PrivateLogic[Pr]] = PrivateKey[Pr]


        for T in Text:
            if T == "_":
                DecryptedText += " "
            else:
                for KeyValue in PrivateKeyDict:
                    if PrivateKeyDict[KeyValue] == T:
                        DecryptedText += str(KeyValue)
        

        return DecryptedText
