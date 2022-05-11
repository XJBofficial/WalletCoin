import random as Random



def GenerateKeys():
    PublicKeyGeneratorLogic = """5&9J3fIdyro1]|FknlNtY¥§vz^*pu}[whxa4.?Rim:;"'<DP2)CWj(-gHS7£€bM%LVG¢°_+{\/>,cT8XB~eAsQEqZ=6U0KO`!@#$ """
    PrivateKeyGeneratorLogic = """I5NZVvkKX6Cdi8Yge1OqzHuSU2tPJaw0xh97olQbjFMfWLpDTcEyn3srRm4ABG~`!@#£€$¢¥§%°^&*()-_+={}[]|\/:;"'<>,.? """
    
    PublicKeyCharsUsed = []
    PublicKeyDict = {}
    PublicKey = ""
    PrivateKey = ""


    for Character in PublicKeyGeneratorLogic:
        RandomSelected = PublicKeyGeneratorLogic[Random.randrange(0, len(PublicKeyGeneratorLogic))]
        PublicKeyDict[Character] = RandomSelected


        # Now remove the character used, from "PublicKeyGeneratorLogic".
        NewPublicKeyGeneratorLogic = """"""
        PublicKeyCharsUsed.append(RandomSelected)

        for Char in PublicKeyGeneratorLogic:
            if not Char in PublicKeyCharsUsed:
                NewPublicKeyGeneratorLogic += Char
        

        PublicKeyGeneratorLogic = NewPublicKeyGeneratorLogic
    

    for Character in PublicKeyDict:
        PublicKey += str(PublicKeyDict[Character])


    for Character in PrivateKeyGeneratorLogic:
        PrivateKey += str(PublicKeyDict[Character])
    

    return [PublicKey, PrivateKey]



def Encode(Text : str, PublicKey : str):
    Logic = """5&9J3fIdyro1]|FknlNtY¥§vz^*pu}[whxa4.?Rim:;"'<DP2)CWj(-gHS7£€bM%LVG¢°_+{\/>,cT8XB~eAsQEqZ=6U0KO`!@#$ """
    EncryptedText = ""


    for J in Text:
        for I in range(0, len(Logic)):
            if J == Logic[I]:
                EncryptedText += PublicKey[I]
    
    return EncryptedText



def Decode(Text : str, PublicKey : str, PrivateKey : str):
    PubLogic = """5&9J3fIdyro1]|FknlNtY¥§vz^*pu}[whxa4.?Rim:;"'<DP2)CWj(-gHS7£€bM%LVG¢°_+{\/>,cT8XB~eAsQEqZ=6U0KO`!@#$ """
    PrivLogic = """I5NZVvkKX6Cdi8Yge1OqzHuSU2tPJaw0xh97olQbjFMfWLpDTcEyn3srRm4ABG~`!@#£€$¢¥§%°^&*()-_+={}[]|\/:;"'<>,.? """
    DecryptedText = ""

    PublicKeyDict = {}
    PrivateKeyDict = {}

    KeysMatch = False


    for P in range(0, len(PubLogic)):
        PublicKeyDict[PubLogic[P]] = PublicKey[P]


    for Pr in range(0, len(PrivLogic)):
        PrivateKeyDict[PrivLogic[Pr]] = PrivateKey[Pr]


    # Now check if the keys match

    for J in PublicKeyDict:
        if PublicKeyDict[J] == PrivateKeyDict[J]:
            KeysMatch = True
        else:
            KeysMatch = False


    for T in Text:
        for KeyValue in PrivateKeyDict:
            if PrivateKeyDict[KeyValue] == T:
                DecryptedText += str(KeyValue)


    return DecryptedText
