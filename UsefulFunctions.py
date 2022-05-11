from hashlib import sha256 as SHA256
import random as Random



def CalculatePrice(amount, price):
    Price : float

    if float(price) < 0.7 or float(price) == 0.7:
        Price = ( float(price) * float(amount) ) % 100.0
    
    elif float(price) > 0.7:
        Price = float(price) * float(amount)
    
    return Price



def CalculateStockPrice(Amount : int, GameValue : float):
    # Amount = The amount of stocks game owning
    return GameValue / float(Amount)



def WalletKey():
    return CreateRandomKey(35)



def CreateRandomKey(charsCount: int):
    key : str = ""

    charactersUpper = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    characters = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    for char in charactersUpper:
        characters.append(char)
        characters.append(char.lower())
    
    for i in range(charsCount):
        key = key + str(characters[ Random.randrange(0, len(characters)) ])

    return key



def CreateAccessToken(PrivateKey : str):
    CharactersUpper = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    Characters = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    AccessToken = ""


    for Char in CharactersUpper:
        Characters.append(Char)
        Characters.append(Char.lower())
    

    for Char in range(0, 20 + 1):
        if PrivateKey[Char] in Characters:
            AccessToken += str(Characters[ Random.randrange(0, len(Characters) - 1) ])
        else:
            AccessToken += "0"
    

    return AccessToken



def Hash(text : str):
    return SHA256(text.encode("UTF-8")).hexdigest()



def RemoveUselessNums(Text : str, Count : int):
    Result : str = ""
    DotFound : bool = False
    NumbersCounted : int = 0
    

    for Char in Text:
        Result += str(Char)
        
        if Char == ".":
            DotFound = True

        if DotFound and Char != ".":
            NumbersCounted += 1

        if NumbersCounted == Count:
            break

    return float(Result)
