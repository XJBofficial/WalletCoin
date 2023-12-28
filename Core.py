from flask import Flask, request, jsonify
from Blockchain import Blockchain
from Wallet import Wallet, Transaction
from Cryptography import Cryptography

import datetime as DateTime
import stripe as Stripe
import json as JSON
import Database
import os as OS


#StripePUBLIC_KEY = "pk_test_51N5EBzHImWZNuXQo8QWI4wAJzHDqQIYUNYf9g5M14dmFGVKnLEOLukHeqLQYxyL7IsS5hCRhn97fJi467pTtjI8a002EtFkSLD"
#StripeSECRET_KEY = "sk_test_51N5EBzHImWZNuXQojVDpV2LDUIhfDcHnqqC97QDODdbc4LdQjtmtbjHBBZNVIw45VUKUXx9D4a5CuNKJ45rObDy500cHgGYGJa"
StripePUBLIC_KEY = "pk_live_51N5EBzHImWZNuXQolpw4D5mStlDSOkba9NuvDBDuPl3tRcjHEkJQDle01kR3nMEBRkJeJyHm8vvdVuRK4rhvwxUk008xIcdQ9x"
StripeSECRET_KEY = "<< MY_SECRET_KEY >>"
Stripe.api_key = StripePUBLIC_KEY
Stripe.secret_key = StripeSECRET_KEY

CORE = Flask(__name__)
CORE.config.from_mapping(SECRET_KEY = OS.environ.get('SECRET_KEY') or 'dev_key')

WebsiteDomain = "https://walletcoincrypto.com"


# Cache data = = = = = = = = = = = = = = = = = = =

CompanyHolders = dict()
Wallets = dict()
DeletedWallets = []
PrivateKeys = dict()
DeletedPrivateKeys = []
StripeAccounts = dict()
BankAccounts = dict()
Payments = dict()
Payouts = dict()
Blockchain_ = []
PriceChart = dict()
PriceNow : float = Database.GetPrice()

Vault = Database.Vault()


# Fees
Fees_Buy = 4.34 # %
Fees_Sell = 1.5 # %
Fees_Transcate = 0.5 # %


# Api
ApiInvoices = dict()

# End of Cache data = = = = = = = = = = = = = = = =



# B L O C K C H A I N = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/blockchain", methods=["GET"])
def GetBlockchain():
    Chain = Blockchain()

    return jsonify({
        "result": Chain.GetLastBlocks(CacheBlocks=Blockchain_, Count=10)
    }), 200



@CORE.route("/block", methods=["GET"])
def GetBlock():
    Params = request.args
    List = Params.get("list")
    Chain = Blockchain()


    if List == "Wallet":
        Wallet = Params.get("wallet")

        return jsonify({
            "result": Chain.FindMyBlocks(CacheBlocks=Blockchain_, Wallet=Wallet)
        }), 200
    else:
        Number = int(Params.get("number"))

        return jsonify({
            "result": Chain.FindBlockByNumber(CacheBlocks=Blockchain_, Number=Number)
        }), 200



# W A L L E T = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/wallets/create", methods=["POST"])
def WalletsCreate():
    Payload = JSON.loads(request.get_data())
    NewWallet_ = Wallet()
    NewWallet = NewWallet_.CreateWallet(Phrase=Payload["Phrase"])

    Wallets[NewWallet["Address"]] = NewWallet
    PrivateKeys[NewWallet["PrivateKey"]] = NewWallet["Address"]

    return jsonify({
        "result": NewWallet
    }), 200



@CORE.route("/wallets/connect", methods=["POST"])
def WalletsConnect():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]
    Secret = Payload["Secret"]


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            if Wallet_["SecretPhrase"] == Secret:


                return jsonify({
                    "result": {
                        "PublicKey": Wallet_["PublicKey"],
                        "PrivateKey": PrivKey,
                        "SecretPhrase": Wallet_["SecretPhrase"],
                        "API_KEY": Wallet_["API_KEY"],
                        "Address": Wallet_["Address"],
                        "Balance": Wallet_["Balance"]
                    }
                }), 200
            else:
                return jsonify({}), 403
    else:
        if Wallets[PrivateKeys[PrivKey]]["SecretPhrase"] == Secret:
            Wallet_ = Wallets[PrivateKeys[PrivKey]]


            return jsonify({
                    "result": {
                        "PublicKey": Wallet_["PublicKey"],
                        "PrivateKey": PrivKey,
                        "SecretPhrase": Wallet_["SecretPhrase"],
                        "API_KEY": Wallet_["API_KEY"],
                        "Address": Wallet_["Address"],
                        "Balance": Wallet_["Balance"]
                    }
                }), 200
        else:
            return jsonify({}), 403



@CORE.route("/wallets/get", methods=["POST"])
def WalletsGet():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)


        if len(Wallet_) == 0:
            return jsonify({}), 404
        else:
            return jsonify({
                "result": Wallet_
            }), 200
    

    Address = PrivateKeys[PrivKey]
    return jsonify({
        "result": Wallets[Address]
    }), 200



@CORE.route("/wallets/delete", methods=["POST"])
def WalletsDelete():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]
    Secret = Payload["Secret"]


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            if Wallet_["SecretPhrase"] == Secret:
                DeletedWallets.append(Wallet_["Address"])
                DeletedPrivateKeys.append(PrivKey)
                return jsonify({}), 200
            else:
                return jsonify({}), 403
    else:
        if Wallets[PrivateKeys[PrivKey]]["SecretPhrase"] == Secret:
            DeletedWallets.append(Wallet_["Address"])
            DeletedPrivateKeys.append(PrivKey)
            return jsonify({}), 200
        else:
            return jsonify({}), 403



@CORE.route("/wallets/transaction", methods=["POST"])
def WalletsTransaction():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]
    Recipient = Payload["Recipient"]
    Amount = Payload["Amount"]
    SenderAddress = ""


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            # Check sender's balance amount

            AmountWithFees = (Amount * Fees_Transcate) / 100.0
            AmountFees = Amount + AmountWithFees


            if AmountFees > Wallet_["Balance"]:
                return jsonify({
                    "result": "Insufficient wallet balance."
                }), 500


            # Wallet connected, save temponary the credentials in cache memony

            SenderAddress = Wallet_["Address"]
            PrivateKeys[PrivKey] = Wallet_["Address"]
            Wallets[SenderAddress] = Wallet_
    else:
        SenderAddress = PrivateKeys[PrivKey]

    # Check sender's balance amount

    AmountWithFees = (Amount * Fees_Transcate) / 100.0
    AmountFees = Amount + AmountWithFees


    if AmountFees > Wallets[SenderAddress]["Balance"]:
        return jsonify({
            "result": "Insufficient wallet balance."
        }), 402
    

    # Fetch recipient's wallet from database using its receiving address

    if not Recipient in Wallets:
        KeyFound = False
        Key = ""


        for Priv in PrivateKeys:
            if PrivateKeys[Priv] == Recipient:
                KeyFound = True
                Key = Priv
        

        if KeyFound == False:
            Key = Database.FindPrivKey(Recipient)
            KeyFound = True


        if not KeyFound:
            return jsonify({}), 404
        else:
            Wallet_ = Database.FindWallet(PrivateKey=Key)

            if len(Wallet_) > 0:
                PrivateKeys[Key] = Wallet_["Address"]
                Wallets[Wallet_["Address"]] = Wallet_
            else:
                return jsonify({}), 404


    # Transcate the money

    Wallets[Recipient]["Balance"] += Amount
    Wallets[SenderAddress]["Balance"] -= AmountFees
    

    # Developer receive a fee
    
    Payout(Amount=AmountWithFees)

    
    # Validate blockchain and append the new block

    global Blockchain_
    Transaction_ = Transaction(CacheBlocks=Blockchain_, Sender=SenderAddress, Recipient=Recipient, Amount=Amount)
    Blockchain_ = Blockchain_ + Transaction_.GetChain()


    return jsonify({
        "result": {
            "Amount": Wallets[SenderAddress]["Balance"]
        }
    }), 200



@CORE.route("/wallets/buy", methods=["POST"])
def WalletsBuy():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]
    Amount = Payload["Amount"]
    Address = ""


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            # Wallet connected, save temponary the credentials in cache memony

            Address = Wallet_["Address"]
            PrivateKeys[PrivKey] = Address
            Wallets[Address] = Wallet_
    else:
        Address = PrivateKeys[PrivKey]
    

    # Add more WalletCoins on this wallet

    Fee = (Amount * Fees_Buy) / 100.0
    Wallets[Address]["Balance"] += Amount - Fee


    # Developer receive a fee
    
    Payout(Amount=Fee)


    # There are no coins in stock, issue more

    if Vault["Supply"] - Vault["Owned"] < Amount:
        Vault["Supply"] += Amount
    

    # Increase the owned coins by the purchased amount of coins

    Vault["Owned"] += Amount


    # Increase the value of WalletCoin

    ChangePrice()


    return jsonify({
        "result": {
            "Balance": Wallets[Address]["Balance"]
        }
    }), 200



@CORE.route("/wallets/sell", methods=["POST"])
def WalletsSell():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]
    Amount = Payload["Amount"]
    Address = ""


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            # Wallet connected, save the credentials in cache memony temponary 

            if Wallet_["Balance"] < Amount:
                return jsonify({}), 402 # Insufficient Balance
            

            Address = Wallet_["Address"]
            PrivateKeys[PrivKey] = Address
            Wallets[Address] = Wallet_
    else:
        Address = PrivateKeys[PrivKey]

        if Wallets[Address]["Balance"] < Amount:
            return jsonify({}), 402 # Insufficient Balance
    

    Wallets[Address]["Balance"] -= Amount
    
    AmountWithFees = (Amount * Fees_Sell) / 100.0
    Vault["Owned"] -= Amount - AmountWithFees


    # Developer receive a fee
    
    Payout(Amount=AmountWithFees)


    # Decrease the value of WalletCoin

    ChangePrice()


    return jsonify({
        "result": {
            "Balance": Wallets[Address]["Balance"]
        }
    }), 200



# S T R I P E A C C O U N T S = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/stripeAccount/create", methods=["POST"])
def CreateStripeAccount():
    Payload = JSON.loads(request.get_data())
    Wallet = Payload["Wallet"]
    StripeAccounts[Wallet] = Payload
    
    
    return jsonify({
        "result": StripeAccounts[Wallet]
    }), 200



@CORE.route("/stripeAccount/<string:Wallet>", methods=["GET"])
def GetStripeAccount(Wallet):
    if Wallet in StripeAccounts:
        return jsonify({
            "result": StripeAccounts[Wallet]
        }), 200
    

    Account = Database.FindStripeAccount(Address=Wallet)


    if len(Account) > 0:
        return jsonify({
            "result": Account
        }), 200
    
    
    return jsonify({}), 404



# B A N K A C C O U N T S = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/bankAccount/create", methods=["POST"])
def CreateBankAccount():
    Payload = JSON.loads(request.get_data())
    Wallet = Payload["Wallet"]


    if not Wallet in BankAccounts:
        BankAccounts[Wallet] = []
    

    Account = dict()

    for P in Payload:
        Account[P] = Payload[P]

    BankAccounts[Wallet].append(Account)

    return jsonify({
        "result": BankAccounts[Wallet]
    }), 200



@CORE.route("/bankAccounts/<string:Wallet>", methods=["GET"])
def GetBankAccounts(Wallet):
    WalletBank = []


    if Wallet in BankAccounts:
        WalletBank = BankAccounts[Wallet]
    

    Accounts = Database.FindBankAccounts(Address=Wallet)


    if len(Accounts) > 0:
        WalletBank += Accounts


        return jsonify({
            "result": WalletBank
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



# P A Y M E N T S = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/payments/create", methods=["POST"])
def CreatePayment():
    Payload = JSON.loads(request.get_data())
    Crypto = Cryptography()
    Id = Crypto.GenerateRandomKey(Count=10, RemoveSelected=False) # Payload["Id"]
    Wallet = Payload["Wallet"]


    if not Wallet in Payments:
        Payments[Wallet] = []
    

    NewPayment = {
        "Id": Id,
        "Wallet": Wallet,
        "Amount": Payload["Amount"],
        "Status": "Authorizing",
        "Date": {
            "Year": DateTime.datetime.today().year,
            "Month": DateTime.datetime.today().minute,
            "Day": DateTime.datetime.today().day,
            "Hour": DateTime.datetime.today().hour,
            "Minute": DateTime.datetime.today().minute,
            "Second": DateTime.datetime.today().second
        }
    }
    Payments[Wallet].append(NewPayment)


    return jsonify({
        "result": NewPayment
    }), 200



@CORE.route("/payments/<string:Wallet>", methods=["GET"])
def GetPayments(Wallet):
    WalletPayments = []


    if Wallet in Payments:
        WalletPayments = Payments[Wallet]
    

    Payments_ = Database.FindWalletPayments(Address=Wallet)


    if len(Payments_) > 0:
        WalletPayments = Payments_ + WalletPayments


        return jsonify({
            "result": WalletPayments
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



@CORE.route("/payments/<string:Wallet>/<string:Id>", methods=["GET"])
def WalletGetPayments(Wallet, Id):
    if Wallet in Payments:
        for I in range(0, len(Payments[Wallet])):
            if Payments[Wallet][I]["Id"] == Id:
                return jsonify({
                    "result": Payments[Wallet][I]
                }), 200
    

    Payment = Database.FindWalletPayment(Address=Wallet, Id=Id)


    if len(Payment) > 0:
        return jsonify({
            "result": Payment
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



@CORE.route("/payments/<string:Wallet>/<string:Id>/status", methods=["POST"])
def WalletUpdatePaymentStatus(Wallet, Id):
    Payload = JSON.loads(request.get_data())


    if Wallet in Payments:
        for I in range(0, len(Payments[Wallet])):
            if Payments[Wallet][I]["Id"] == Id:
                Payments[Wallet][I]["Status"] = Payload["Status"]

                return jsonify({}), 200
    

    Payments_ = Database.UpdateWalletPaymentStatus(CachePayments=Payments, Address=Wallet, Id=Id, Status=Payload["Status"])
    Payments[Wallet] = Payments_

    return jsonify({}), 200



@CORE.route("/payments/<string:Wallet>/last", methods=["GET"])
def GetLastPayment(Wallet):
    if Wallet in Payments:
        return jsonify({
            "result": Payments[Wallet][len(Payments[Wallet]) -1]
        }), 200
    

    Payments_ = Database.FindWalletPayments(Address=Wallet)


    if len(Payments_) > 0:
        return jsonify({
            "result": Payments_[len(Payments_) -1]
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



# P A Y O U T S = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/payouts/create", methods=["POST"])
def CreatePayout():
    Payload = JSON.loads(request.get_data())
    Crypto = Cryptography()
    Id = Crypto.GenerateRandomKey(Count=10, RemoveSelected=False) # Payload["Id"]
    Wallet = Payload["Wallet"]


    if not Wallet in Payouts:
        Payouts[Wallet] = []
    

    Payout = {
        "Id": Id,
        "Wallet": Wallet,
        "WLLC": Payload["WLLC"],
        "Amount": Payload["Amount"],
        "Destination": Payload["Destination"],
        "Status": "Pending",
        "Date": {
            "Year": DateTime.datetime.today().year,
            "Month": DateTime.datetime.today().minute,
            "Day": DateTime.datetime.today().day,
            "Hour": DateTime.datetime.today().hour,
            "Minute": DateTime.datetime.today().minute,
            "Second": DateTime.datetime.today().second
        }
    }
    Payouts[Wallet].append(Payout)


    return jsonify({
        "result": Payout
    }), 200



@CORE.route("/payouts/<string:Wallet>", methods=["GET"])
def GetPayouts(Wallet):
    WalletPayouts = []


    if Wallet in Payouts:
        WalletPayouts = Payouts[Wallet]
    

    Payouts_ = Database.FindWalletPayouts(Address=Wallet)


    if len(Payouts_) > 0:
        WalletPayouts = Payouts_ + WalletPayouts


        return jsonify({
            "result": WalletPayouts
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



@CORE.route("/payouts/<string:Wallet>/<string:Id>", methods=["GET"])
def GetPayout(Wallet, Id):
    if Wallet in Payouts:
        for I in range(0, len(Payouts[Wallet])):
            if Payouts[Wallet][I]["Id"] == Id:
                return jsonify({
                    "result": Payouts[Wallet][I]
                }), 200
    

    Payout = Database.FindWalletPayout(Address=Wallet, Id=Id)


    if len(Payout) > 0:
        return jsonify({
            "result": Payout
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



@CORE.route("/payouts/<string:Wallet>/<string:Id>/status", methods=["POST"])
def WalletUpdatePayoutStatus(Wallet, Id):
    Payload = JSON.loads(request.get_data())


    if Wallet in Payouts:
        for I in range(0, len(Payouts[Wallet])):
            if Payouts[Wallet][I]["Id"] == Id:
                Payouts[Wallet][I]["Status"] = Payload["Status"]

                return jsonify({}), 200
    

    Payouts_ = Database.UpdateWalletPayoutStatus(CachePayouts=Payouts[Wallet], Address=Wallet, Id=Id, Status=Payload["Status"])
    Payouts[Wallet] = Payouts_

    return jsonify({}), 200



@CORE.route("/payouts/<string:Wallet>/last", methods=["GET"])
def GetLastPayout(Wallet):
    if Wallet in Payouts:
        return jsonify({
            "result": Payouts[Wallet][len(Payouts[Wallet]) -1]
        }), 200
    

    Payouts_ = Database.FindWalletPayouts(Address=Wallet)


    if len(Payouts_) > 0:
        return jsonify({
            "result": Payouts_[len(Payouts_) -1]
        }), 200
    
    
    return jsonify({
        "result": []
    }), 200



# A P I K E Y S = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/wallets/validateApiKey", methods=["POST"])
def ValidateApiKey():
    Payload = JSON.loads(request.get_data())
    Wallet = Payload["Wallet"]
    ApiKey = Payload["Key"]


    # Find private key

    PrivKey = ""

    if not Wallet in Wallets:
        Key = Database.FindPrivKey(Wallet=Wallet)

        
        if Key != "":
            PrivKey = Key
        else:
            return jsonify({
                "result": {
                    "message": "Private key not found.",
                    "statusCode": 404
                }
            }), 404
    else:
        PrivKey = Wallets[Wallet]["PrivateKey"]


    # Fetch my wallet from database using my private key

    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({
                "result": {
                    "message": "Wallet not found.",
                    "statusCode": 404
                }
            }), 404
        else:
            if Wallet_["API_KEY"] == ApiKey:
                return jsonify({}), 200
            else:
                return jsonify({
                    "result": {
                        "message": "Invalid API key.",
                        "statusCode": 403
                    }
                }), 403
    else:
        if Wallets[PrivateKeys[PrivKey]]["API_KEY"] == ApiKey:
            return jsonify({}), 200
        else:
            return jsonify({
                "result": {
                    "message": "Invalid API key.",
                    "statusCode": 403
                }
            }), 403



# A C C E P T P A Y M E N T S = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/wallets/invoices/create", methods=["POST"])
def InvoicesCreate():
    Payload = JSON.loads(request.get_data())
    PrivKey = Payload["PrivKey"]
    Description = Payload["Description"]
    Amount = Payload["Amount"]
    SuccessUrl = Payload["Urls"]["Success"]
    FailedUrl = Payload["Urls"]["Failed"]
    CancelUrl = Payload["Urls"]["Cancel"]


    # Fetch my wallet from database using my private key

    Address = ""


    if not PrivKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PrivKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            Address = Wallet_["Address"]
    else:
        Address = PrivateKeys[PrivKey]
    

    # Create the new invoice

    Crypto = Cryptography()
    InvoiceId = Crypto.GenerateRandomKey(Count=20, RemoveSelected=False)
    Invoice = {
        "Id": InvoiceId,
        "Description": Description,
        "Amount": Amount,
        "Urls": {
            "Success": SuccessUrl,
            "Failed": FailedUrl,
            "Cancel": CancelUrl
        }
    }

    if not Address in ApiInvoices:
        ApiInvoices[Address] = {}
    
    ApiInvoices[Address][InvoiceId] = Invoice

    return jsonify({
        "result": {
            "invoice": InvoiceId,
            "payment_url": WebsiteDomain + "/payments?invoice=%s&seller=%s" % (InvoiceId, Address)
        }
    }), 200



@CORE.route("/wallets/invoices/execute", methods=["POST"])
def InvoicesExecute():
    Payload = JSON.loads(request.get_data())
    SellerAddress = Payload["Seller"]
    PayerPrivateKey = Payload["PayerPrivateKey"]
    PayerSecretPhrase = Payload["PayerSecretPhrase"]
    InvoiceId = Payload["InvoiceId"]


    # Fetch seller wallet from database using seller private key

    SellerKeyFound = False
    SellerPrivateKey = ""


    for Priv in PrivateKeys:
        if PrivateKeys[Priv] == SellerAddress:
            SellerPrivateKey = Priv
            SellerKeyFound = True
    

    if SellerKeyFound == False:
        Key = Database.FindPrivKey(Wallet=SellerAddress)

        if Key == "":
            return jsonify({}), 404
        else:
            SellerPrivateKey = Key


    Address = ""


    if not SellerPrivateKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=SellerPrivateKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            Address = Wallet_["Address"]
            PrivateKeys[SellerPrivateKey] = Address
            Wallets[PrivateKeys[SellerPrivateKey]] = Wallet_
    else:
        Address = PrivateKeys[SellerPrivateKey]
    

    # Fetch payer wallet

    PayerAddress = ""


    if not PayerPrivateKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PayerPrivateKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            if Wallet_["SecretPhrase"] == PayerSecretPhrase:
                PayerAddress = Wallet_["Address"]
            else:
                return jsonify({}), 403
    else:
        if Wallets[PrivateKeys[PayerPrivateKey]]["SecretPhrase"] == PayerSecretPhrase:
            PayerAddress = Wallets[PrivateKeys[PayerPrivateKey]]["Address"]
        else:
            return jsonify({}), 403
    

    # Find invoice information & payer wallet

    Invoice = ApiInvoices[Address][InvoiceId]
    PayAmount = Invoice["Amount"]

    AmountWithFees = (PayAmount * Fees_Transcate) / 100.0
    AmountFees = PayAmount + AmountWithFees


    if not PayerPrivateKey in PrivateKeys:
        Wallet_ = Database.FindWallet(PrivateKey=PayerPrivateKey)

        
        if len(Wallet_) == 0: # Not Found
            return jsonify({}), 404
        else:
            # Wallet connected, save the credentials in cache memony temponary 

            if Wallet_["Balance"] < AmountFees:
                return jsonify({}), 402 # Insufficient Balance
            
            
            PayerAddress = Wallet_["Address"]
            PrivateKeys[PayerPrivateKey] = PayerAddress
            Wallets[PrivateKeys[PayerPrivateKey]] = Wallet_
    

    # Transcate the money

    Wallets[Address]["Balance"] += PayAmount
    Wallets[PayerAddress]["Balance"] -= AmountFees


    global Earnings

    
    # Receive a fee
    
    Payout(Amount=AmountWithFees)

    
    # Validate blockchain and append the new block

    global Blockchain_
    Transaction_ = Transaction(CacheBlocks=Blockchain_, Sender=PayerAddress, Recipient=Address, Amount=PayAmount)
    Blockchain_ = Blockchain_ + Transaction_.GetChain()


    # Remove the completed invoice


    print(ApiInvoices)
    print(Address)
    print(PayerAddress)


    #del ApiInvoices[Address][InvoiceId]

    #if len(ApiInvoices[Address]) == 0:
    #    del ApiInvoices[Address]
    

    return jsonify({}), 200



@CORE.route("/wallets/invoices/get", methods=["POST"])
def InvoicesGet():
    Payload = JSON.loads(request.get_data())
    Seller = Payload["Seller"]
    InvoiceId = Payload["Invoice"]


    if Seller in ApiInvoices:
        if InvoiceId in ApiInvoices[Seller]:
            return jsonify({
                "result": ApiInvoices[Seller][InvoiceId]
            }), 200
    

    return jsonify({}), 404



# P R I C E = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def ChangePrice():
    Year = DateTime.datetime.today().year
    Month = DateTime.datetime.today().month
    Day = DateTime.datetime.today().day
    Cash = Stripe.Balance.retrieve(
        api_key=StripeSECRET_KEY,
        stripe_account="acct_1N5EBzHImWZNuXQo"
    )
    Cash = Cash["available"][0]["amount"] + Cash["pending"][0]["amount"]
    Cash_ = str(Cash)[0:len(str(Cash))-2]
    Cents = str(Cash)[:len(str(Cash))-3:-1]
    Cents = Cents[::-1]
    Cash = float("%s.%s" % (Cash_, Cents))


    # Prepare the stats wall for the first price change of the day!

    ChartLoaded = False


    global PriceChart

    if Year in PriceChart:
        if Month in PriceChart[Year]:
            if Day in PriceChart[Year][Month]:
                ChartLoaded = True
    

    if not ChartLoaded:
        with open("database/Price.json", "r") as File:
            Chart_ = JSON.loads(File.read())
            Chart = []


            if str(Year) in Chart_:
                if str(Month) in Chart_[str(Year)]:
                    if str(Day) in Chart_[str(Year)][str(Month)]:
                        for P in Chart_[str(Year)][str(Month)][str(Day)]:
                            Chart.append(P["Price"])
            
            Chart_.clear()
            File.close()


            if not Year in PriceChart:
                PriceChart[Year] = {}
            

            if not Month in PriceChart[Year]:
                PriceChart[Year][Month] = {}
            

            if not Day in PriceChart[Year][Month]:
                PriceChart[Year][Month][Day] = []


            PriceChart[Year][Month][Day] = Chart
    

    # = = = = = = = = = = = = = = = = = = = = = = = = = =

    NewChange = {
        "Price": 0,
        "Date": {
            "Hour": DateTime.datetime.today().hour,
            "Minute": DateTime.datetime.today().minute,
            "Second": DateTime.datetime.today().second
        }
    }


    Vault["Cash"] = Cash
    NewChange["Price"] = Vault["Cash"] / Vault["Supply"]
    
    
    PriceChart[Year][Month][Day].append(NewChange)
    
    global PriceNow
    PriceNow = NewChange["Price"]



@CORE.route("/price", methods=["GET"])
def GetPrice():
    return jsonify({
        "result": PriceNow
    }), 200



@CORE.route("/getCryptoData", methods=["GET"])
def GetCryptoData():
    Stats = GetStats(Queries=request.args, List="hours")


    return jsonify({
        "result": {
            "Price": PriceNow,
            "MarketCap": Vault["Cash"],
            "Supply": Vault["Supply"],
            "Bought": Vault["Owned"]
        }
    }), 200



@CORE.route("/price/<string:List>", methods=["GET"])
def GetPriceChart(List):
    return jsonify({
        "result": GetStats(Queries=request.args, List=List)
    }), 200



def GetStats(Queries, List : str):
    if List == "years":

        # Get total stats = = = = = = = = = = = =
    
        with open("database/Price.json", "r") as File:
            Stats = JSON.loads(File.read())
            Stats = Stats["Chart"]
            Total = []


            for Year in Stats:
                for Month in Stats[Year]:
                    for Day in Stats[Year][Month]:
                        Price_ = 0

                        
                        for S in Stats[Year][Month][Day]:
                            Price_ = S["Price"]
                        

                        # Search in temporary memory for this day

                        if int(Year) in PriceChart:
                            if int(Month) in PriceChart[int(Year)]:
                                if int(Day) in PriceChart[int(Year)][int(Month)]:
                                    for S in Stats[int(Year)][int(Month)][int(Day)]:
                                        Price_ = S["Price"]


                        Total.append({
                            "Tag": "%s/%s/%s" % (str(Year), str(Month), str(Day)),
                            "Value": Price_
                        })
            

            File.close()
            Stats.clear()


            FirstYear = 0
            LastYear = 0


            if len(Total) != 0:
                FirstYear = Total[0]["Value"]
                LastYear = Total[len(Total) -1]["Value"]


            ChangePercent = 0

            if FirstYear > 0 or LastYear > 0:
                ChangePercent = round((LastYear - FirstYear) / abs(FirstYear) * 100.0, 2)


            Changed = ""


            if LastYear >= FirstYear:
                Changed = "Increase"
            else:
                Changed = "Decrease"


            return {
                "Time": "Total",
                "Price": PriceNow,
                "Changed": Changed,
                "ChangePercent": ChangePercent,
                "Owned": Vault["Owned"],
                "ForSell": Vault["Supply"] - Vault["Owned"],
                "MarketCap": Vault["Cash"],
                "Stats": Total
            }


    elif List == "months":
        # Get the annual stats = = = = = = = = = = = =

        if "year" in Queries:
            Year = Queries.get("year")


            with open("database/Price.json", "r") as File:
                Stats = JSON.loads(File.read())
                Stats = Stats["Chart"]
                Annual = []


                if Year in Stats:
                    for Month in Stats[Year]:
                        for Day in Stats[Year][Month]:
                            Price_ = 0

                            
                            for S in Stats[Year][Month][Day]:
                                Price_ = S["Price"]
                            

                            # Search in temporary memory for this day

                            if int(Year) in PriceChart:
                                if int(Month) in PriceChart[int(Year)]:
                                    if int(Day) in PriceChart[int(Year)][int(Month)]:
                                        for S in Stats[int(Year)][int(Month)][int(Day)]:
                                            Price_ = S["Price"]


                            Annual.append({
                                "Tag": "%s/%s" % (str(Month), str(Day)),
                                "Value": Price_
                            })


                File.close()
                Stats.clear()


                FirstMonth = 0
                LastMonth = 0


                if len(Annual) != 0:
                    FirstMonth = Annual[0]["Value"]
                    LastMonth = Annual[len(Annual) -1]["Value"]


                ChangePercent = 0

                if FirstMonth > 0 or LastMonth > 0:
                    ChangePercent = round((LastMonth - FirstMonth) / abs(FirstMonth) * 100.0, 2)
                

                Changed = ""


                if LastMonth >= FirstMonth:
                    Changed = "Increase"
                else:
                    Changed = "Decrease"


                return {
                    "Time": "Year",
                    "Price": PriceNow,
                    "Changed": Changed,
                    "ChangePercent": ChangePercent,
                    "Owned": Vault["Owned"],
                    "ForSell": Vault["Supply"] - Vault["Owned"],
                    "MarketCap": Vault["Cash"],
                    "Stats": Annual
                }
        
        return {
            "message": "Invalid data passed.",
            "status_code": 400
        }


    elif List == "days":
        # Get the stats of a month = = = = = = = = = = =

        if "month" in Queries and "year" in Queries:
            Year = Queries.get("year")
            Month = Queries.get("month")


            with open("database/Price.json", "r") as File:
                Stats = JSON.loads(File.read())
                Stats = Stats["Chart"]
                Daily = []
                

                if Year in Stats:
                    if Month in Stats[Year]:
                        for Day in Stats[Year][Month]:
                            for S in Stats[Year][Month][Day]:

                                Daily.append({
                                    "Tag": "%s/%s/%s::" % (str(Year), str(Month), str(Day)) + "%s:%s:%s" % (str(S["Date"]["Hour"]), str(S["Date"]["Minute"]), str(S["Date"]["Second"])),
                                    "Value": S["Price"]
                                })
                            

                            # Search in temporary memory for this day

                            if int(Year) in PriceChart:
                                if int(Month) in PriceChart[int(Year)]:
                                    if int(Day) in PriceChart[int(Year)][int(Month)]:
                                        for S in Stats[int(Year)][int(Month)][int(Day)]:

                                            Daily.append({
                                                "Tag": "%s/%s/%s::" % (str(Year), str(Month), str(Day)) + "%s:%s:%s" % (str(S["Date"]["Hour"]), str(S["Date"]["Minute"]), str(S["Date"]["Second"])),
                                                "Value": S["Price"]
                                            })
                

                File.close()
                Stats.clear()


                FirstDay = 0
                LastDay = 0


                if len(Daily) != 0:
                    FirstYear = Daily[0]["Value"]
                    LastYear = Daily[len(Daily) -1]["Value"]


                ChangePercent = 0

                if FirstDay > 0 or LastDay > 0:
                    ChangePercent = round((LastDay - FirstDay) / abs(FirstDay) * 100.0, 2)
                
                
                Changed = ""


                if LastDay >= FirstDay:
                    Changed = "Increase"
                else:
                    Changed = "Decrease"


                return {
                    "Time": "Months",
                    "Price": PriceNow,
                    "Changed": Changed,
                    "ChangePercent": ChangePercent,
                    "Owned": Vault["Owned"],
                    "ForSell": Vault["Supply"] - Vault["Owned"],
                    "MarketCap": Vault["Cash"],
                    "Stats": Daily
                }
        
        return {
            "message": "Invalid data passed.",
            "status_code": 400
        }
    else:
        # Get the stats of a day = = = = = = = = = = = =

        if "day" in Queries and "month" in Queries and "year" in Queries:
            Year = Queries.get("year")
            Month = Queries.get("month")
            Day = Queries.get("day")


            with open("database/Price.json", "r") as File:
                Stats = JSON.loads(File.read())
                Stats = Stats["Chart"]
                Hours = []


                if Year in Stats:
                    if Month in Stats[Year]:
                        if Day in Stats[Year][Month]:
                            for S in Stats[Year][Month][Day]:
                                Hours.append({
                                    "Tag": "%s:%s:%s" % (str(S["Date"]["Hour"]), str(S["Date"]["Minute"]), str(S["Date"]["Second"])),
                                    "Value": S["Price"]
                                })
                

                # Now get the new stats from cache
                if int(Year) in PriceChart:
                    if int(Month) in PriceChart[int(Year)]:
                        if int(Day) in PriceChart[int(Year)][int(Month)]:
                            for S in PriceChart[int(Year)][int(Month)][int(Day)]:
                                Hours.append({
                                    "Tag": "%s:%s:%s" % (str(S["Date"]["Hour"]), str(S["Date"]["Minute"]), str(S["Date"]["Second"])),
                                    "Value": S["Price"]
                                })
                

                File.close()
                Stats.clear()

                
                FirstHour = 0
                LastHour = 0


                if len(Hours) != 0:
                    FirstYear = Hours[0]["Value"]
                    LastYear = Hours[len(Hours) -1]["Value"]


                ChangePercent = 0

                if FirstHour > 0 or LastHour > 0:
                    ChangePercent = round((LastHour - FirstHour) / abs(FirstHour) * 100.0, 2)


                Changed = ""


                if LastHour >= FirstHour:
                    Changed = "Increase"
                else:
                    Changed = "Decrease"


                return {
                    "Time": "Day",
                    "Price": PriceNow,
                    "Changed": Changed,
                    "ChangePercent": ChangePercent,
                    "Owned": Vault["Owned"],
                    "ForSell": Vault["Supply"] - Vault["Owned"],
                    "MarketCap": Vault["Cash"],
                    "Stats": Hours
                }
        
        return {
            "message": "Invalid data passed.",
            "status_code": 400
        }



# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def Payout(Amount : float):
    for Holder in CompanyHolders:
        # Payout in crypto

        if not Holder["Wallet"] in Wallets:
            KeyFound = False
            Key = ""


            for Priv in PrivateKeys:
                if PrivateKeys[Priv] == Holder["Wallet"]:
                    KeyFound = True
                    Key = Priv
            

            if KeyFound == False:
                Key = Database.FindPrivKey(Holder["Wallet"])
                KeyFound = True


            Wallet_ = Database.FindWallet(PrivateKey=Key)

            if len(Wallet_) > 0:
                PrivateKeys[Key] = Wallet_["Address"]
                Wallets[Wallet_["Address"]] = Wallet_


        # Transfer the money

        Wallets[Holder["Wallet"]]["Balance"] += Amount / len(CompanyHolders)



# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@CORE.route("/save", methods=["POST"])
def CacheSave():
    # Payout the sellers

    Cash = Stripe.Balance.retrieve(
        api_key=StripeSECRET_KEY,
        stripe_account="acct_1N5EBzHImWZNuXQo"
    )
    Cash = Cash["available"][0]["amount"]


    for Wallet in Payouts:
        for Pay in range(0, len(Payouts[Wallet])):
            if Payouts[Wallet][Pay]["Status"] == "Pending":
                Destination = Payouts[Wallet][Pay]["Destination"]
                Amount = int(Payouts[Wallet][Pay]["Amount"] * 100)


                if Cash >= Amount:
                    # Transfer the funds

                    Stripe.Transfer.create(
                        api_key=StripeSECRET_KEY,
                        amount=Amount,
                        currency="eur",
                        destination=Destination
                    )


                    # Payout

                    Stripe.Payout.create(
                        api_key=StripeSECRET_KEY,
                        amount=Amount,
                        currency="eur",
                        stripe_account=Destination
                    )

                    Cash -= Amount


    with open("database/WalletPayouts.json", "r") as FileRead:
        Payouts_ = JSON.loads(FileRead.read())


        for Wallet in Payouts_:
            for Pay in range(0, len(Payouts_[Wallet])):
                if Payouts_[Wallet][Pay]["Status"] == "Pending":
                    Destination = Payouts_[Wallet][Pay]["Destination"]
                    Amount = int(Payouts_[Wallet][Pay]["Amount"] * 100)


                    if Cash >= Amount:
                        # Transfer the funds

                        Stripe.Transfer.create(
                            api_key=StripeSECRET_KEY,
                            amount=Amount,
                            currency="eur",
                            destination=Destination
                        )


                        # Payout

                        Stripe.Payout.create(
                            api_key=StripeSECRET_KEY,
                            amount=Amount,
                            currency="eur",
                            method="instant",
                            stripe_account=Destination
                        )

                        Payouts_[Wallet][Pay]["Status"] = "Completed"
                        Cash -= Amount


    Database.SavePrice(Price=PriceNow, Cash=Vault["Cash"], Supply=Vault["Supply"], Owned=Vault["Supply"], Chart=PriceChart)
    Database.SaveWallets(Wallets=Wallets, Deleted=DeletedWallets)
    Database.SavePrivateKeys(PrivateKeys=PrivateKeys, Deleted=DeletedPrivateKeys)
    Database.SaveStripeAccounts(StripeAccounts=StripeAccounts)
    Database.SaveBankAccounts(BankAccounts=BankAccounts)
    Database.SaveWalletPayments(Payments=Payments)
    Database.SaveWalletPayouts(Payouts=Payouts)


    global Blockchain_
    Database.SaveBlockchain(Chain=Blockchain_)


    PriceChart.clear()
    Wallets.clear()
    PrivateKeys.clear()
    StripeAccounts.clear()
    BankAccounts.clear()
    Payments.clear()
    Payouts.clear()
    Blockchain_ = []


    global CompanyHolders
    CompanyHolders = Database.CompanyHolders()


    if "close" in request.args: # Used to stop the program in order to upload a new update without losing any temporary data
        quit()


    return jsonify({}), 200



if __name__ == '__main__':
    CompanyHolders = Database.CompanyHolders()
    CORE.secret_key = 'secret123'
    CORE.run(port=3048, debug=True)
