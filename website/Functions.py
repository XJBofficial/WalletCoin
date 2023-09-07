def IsNumber(Text):
    for T in Text:
        if not str(T) in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
            return False
    
    return True



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

    Result.replace("e", "")
    return float(Result)
