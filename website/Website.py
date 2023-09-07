from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from functools import wraps

import requests as Requests
import datetime as DateTime
import json as Json
import Functions
import os as OS


WEB = Flask(__name__)
WEB.config.from_mapping(SECRET_KEY = OS.environ.get('SECRET_KEY') or 'dev_key')

Session_ = session

CORE = "http://127.0.0.1:3048"



# Wrap to define if user has connected a wallet

def connected_wallet(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "Address" in Session_:
            return f(*args, **kwargs)
        else:
            return redirect("/wallet/connect")
    return wrap



# Some functions = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


def GetPrice():
    Res = Requests.request(url=CORE + "/price", method="GET")


    if Res.status_code == 200:
        return Res.json()["result"]
    
    return None



def GetCryptoData():
    Day = str(DateTime.datetime.today().day)
    Month = str(DateTime.datetime.today().month)
    Year = str(DateTime.datetime.today().year)
    Res = Requests.request(url=CORE + "/getCryptoData?year=%s&month=%s&day=%s" % (Year, Month, Day), method="GET")


    if Res.status_code == 200:
        return Res.json()["result"]
    
    return None



def GetPriceChart(List : str, Date : dict):
    RequestUrl = CORE + "/price/" + List


    if List == "months":
        RequestUrl += "?year=%s" % str(Date["year"])


    elif List == "days":
        RequestUrl += "?year=%s&month=%s" % (str(Date["year"]), str(Date["month"]))
    

    elif List == "hours":
        RequestUrl += "?year=%s&month=%s&day=%s" % (str(Date["year"]), str(Date["month"]), str(Date["day"]))


    Res = Requests.request(url=RequestUrl, method="GET")


    if Res.status_code == 200:
        return Res.json()["result"]
    
    return None



# Main Code = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@WEB.route("/")
def Index():
    CryptoCurrencyData = GetCryptoData()


    Price = CryptoCurrencyData["Price"]
    Volume = CryptoCurrencyData["Volume"]
    Supply = CryptoCurrencyData["Supply"]
    Bought = CryptoCurrencyData["Bought"]


    return render_template(
        'Index.html',
        Price=Price,
        Volume=Volume,
        Supply=Supply,
        Bought=Bought,
        Session=Session_
    )



@WEB.route("/logout")
@connected_wallet
def Logout():
    Session_.clear()
    return redirect("/")



# The Value chart of Cryptocurrency

@WEB.route("/price", methods=["GET"])
def PriceChart():
    if request.method == "GET":
        RequestArguments = request.args
        List = RequestArguments.get("time")
        Date = {}

        
        if not "day" in RequestArguments and not "month" in RequestArguments and not "year" in RequestArguments:
            List = "hours"
            Date = {
                "day": DateTime.datetime.today().day,
                "month": DateTime.datetime.today().month,
                "year": DateTime.datetime.today().year
            }
        else:
            for Arg in RequestArguments:
                Date[Arg] = RequestArguments.get(Arg)


        Chart = GetPriceChart(List=str(List), Date=Date)
        
        
        Price = Chart["Price"]
        PriceChanged = Chart["Changed"]
        PriceChange = Chart["ChangePercent"]
        Owned = Chart["Owned"]
        ForSell = Chart["ForSell"]
        Volume = Chart["Volume"]
        MarketCap = Chart["MarketCap"]


        return render_template(
            "PriceChart.html",
            Price=Price,
            Changed=PriceChanged,
            PriceChange=Functions.RemoveUselessNums(str(PriceChange), 2),
            Owned=Functions.RemoveUselessNums(str(Owned), 8),
            ForSell=Functions.RemoveUselessNums(str(ForSell), 8),
            Volume=Functions.RemoveUselessNums(str(Volume), 3),
            MarketCap=Functions.RemoveUselessNums(str(MarketCap), 3),
            Chart=Chart["Stats"],
            Date=[
                DateTime.datetime.today().day,
                DateTime.datetime.today().month,
                DateTime.datetime.today().year
            ],
            Session=Session_
        )



@WEB.route("/wallet/create", methods=["POST", "GET"])
def WalletCreate():
    if request.method == "POST":
        Form = request.form
        Payload = {
            "Phrase": Form["Phrase"]
        }
        Payload = Json.dumps(Payload)
        Res = Requests.request(url=CORE + "/wallets/create", method="POST", data=Payload)


        if Res.status_code == 200:
            Wallet = Res.json()["result"]

            return render_template(
                "WalletCreate.html",
                Session=Session_,
                Status="Success",
                Priv=Wallet["PrivateKey"],
                Phrase=Wallet["SecretPhrase"]
            )
        
        return render_template("WalletCreate.html", Session=Session_, Status="Error")
    

    if request.method == "GET":
        return render_template("WalletCreate.html", Session=Session_)



@WEB.route("/wallet/connect", methods = ["POST", "GET"])
def WalletConnect():
    Form = request.form


    if request.method == "POST":
        Payload = {
            "PrivKey": Form["PrivateKey"],
            "Secret": Form["Phrase"]
        }
        Payload = Json.dumps(Payload)
        Res = Requests.request(url=CORE + "/wallets/connect", method="POST", data=Payload)


        if Res.status_code == 200:
            Wallet = Res.json()["result"]

            Session_["PublicKey"] = Wallet["PublicKey"]
            Session_["PrivateKey"] = Wallet["PrivateKey"]
            Session_["SecretPhrase"] = Wallet["SecretPhrase"]
            Session_["Address"] = Wallet["Address"]
            Session_["Balance"] = float(Wallet["Balance"])
            Session_["API_KEY"] = Wallet["API_KEY"]


            return redirect("/blockchain")
        
        return render_template("WalletConnect.html", Session=Session_, Status="Error")
    

    if request.method == "GET":
        return render_template("WalletConnect.html", Session=Session_)



@WEB.route("/wallet/settings", methods=["GET"])
@connected_wallet
def WalletSettings():
    return render_template(
        "WalletSettings.html",
        Session=Session_,
        PublicKey=Session_["PublicKey"],
        PrivateKey=Session_["PrivateKey"],
        SecretPhrase=Session_["SecretPhrase"]
    )



@WEB.route("/wallet/delete", methods = ["POST", "GET"])
@connected_wallet
def WalletDelete():
    Form = request.form


    if request.method == "POST":
        if Session_["Balance"] > 0:
            return render_template(
                "WalletSettings.html",
                Session=Session_,
                Address=Session_["Address"],
                Action="Balance"
            )
        else:
            Payload = {
                "PrivKey": Form["PrivateKey"],
                "Secret": Form["Phrase"]
            }
            Payload = Json.dumps(Payload)
            Res = Requests.request(url=CORE + "/wallets/delete", method="POST", data=Payload)


            if Res.status_code == 200:
                del Session_["PrivateKey"]
                del Session_["SecretPhrase"]
                del Session_["Address"]
                del Session_["Balance"]


                return redirect("/wallet/connect")
            
            return render_template("Wallets.html", Session=Session_)
    

    if request.method == "GET":
        return render_template(
            "WalletSettings.html",
            Session=Session_,
            Address=Session_["Address"]
        )



@WEB.route("/api/keys", methods=["GET"])
@connected_wallet
def MyApiKey():
    return render_template(
        "YourAPIKey.html",
        Session=Session_,
        API_KEY=Session_["API_KEY"]
    )



@WEB.route("/transaction", methods = ["POST", "GET"])
@connected_wallet
def Transaction():
    if request.method == "POST":
        Payload = Json.loads(request.get_data())


        Currency = Payload["Currency"]
        Wallet = Payload["Receiver"]
        Amount = float(Payload["Amount"])


        # Check if user broke the limits

        if Currency == "EUR":
            if Amount < 3:
                return jsonify({
                    "result": "Min 3 €."
                }), 400

            # Convert those euros in walletcoins
            Amount = Amount / GetPrice()
        else:
            WLLC = Amount * GetPrice()

            if WLLC < 3:
                return jsonify({
                    "result": "Min 3 €."
                }), 400



        if Session_["Balance"] < Amount:
            return jsonify({
                "result": "Insufficient balance. You have got only %s WLLC" % str(Session_["Balance"])
            }), 400

        elif Wallet == Session_["Address"]:
            return jsonify({
                "result": "You can't send money to your self."
            }), 400

        else:
            Payload = {
                "PrivKey": Session_["PrivateKey"],
                "Recipient": Wallet,
                "Amount": Amount
            }
            Payload = Json.dumps(Payload)
            Res = Requests.request(url=CORE + "/wallets/transaction", method="POST", data=Payload)


            if Res.status_code == 200:
                Session_["Balance"] = Res.json()["result"]["Amount"]
                return redirect(url_for("Blockchain"))
            else:
                return jsonify(Res.json()), Res.status_code


    if request.method == "GET":
        return render_template(
            "TransferPage.html",
            Balance=Session_["Balance"],
            Price=GetPrice(),
            Session=Session_
        )



@WEB.route("/buy", methods=['POST', 'GET'])
@connected_wallet
def Buy():
    if request.method == "POST":
        Payload = Json.loads(request.get_data())

        Currency = Payload["Currency"]
        Amount = Payload["Amount"]


        if Currency == "EUR":
            # Convert those euros in walletcoins
            Amount = Amount / GetPrice()


        Payload = {
            "PrivKey": Session_["PrivateKey"],
            "Address": Session_["Address"],
            "Amount": Amount
        }
        Payload = Json.dumps(Payload)
        BuyRequest = Requests.request(url=CORE + "/wallets/buy", method="POST", data=Payload)


        if BuyRequest.status_code == 200:
            Session_["Balance"] = BuyRequest.json()["result"]["Balance"]
            return redirect(url_for("Blockchain"))
        else:
            return jsonify({
                "result": "Error while buying more cryptos."
            }), 500
    

    if request.method == "GET":
        return render_template(
            "Buy.html",
            Balance=Session_["Balance"],
            Price=GetPrice(),
            Session=Session_
        )



@WEB.route("/buy/createOrder", methods=['POST'])
@connected_wallet
def BuyCreateOrder():
    if request.method == "POST":
        Payload = Json.loads(request.get_data())

        Currency = Payload["Currency"]
        Amount = Payload["Amount"]


        # Check if user broke the limits

        if Currency == "EUR":
            if Amount < 10 or Amount > 100000:
                return jsonify({
                    "result": "Min 10 €, Max 100,000 €."
                }), 400

            # Convert those euros in walletcoins
            Amount = Amount / GetPrice()
        else:
            WLLC = Amount * GetPrice()

            if WLLC < 10 or WLLC > 100000:
                return jsonify({
                    "result": "Min 10 €, Max 100,000 €."
                }), 400
        

        # Create the new order

        Payload = {
            "amount": float(str(Amount) + "00"), # "00" is cents
            "currency": "EUR"
        }
        Payload = Json.dumps(Payload)
        Headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer <yourSecretApiKey>'
        }
        Res = Requests.request(url="https://merchant.revolut.com/api/1.0/orders", method="POST", headers=Headers, data=Payload)


        return jsonify({}), 200



@WEB.route("/sell", methods=["POST", "GET"])
@connected_wallet
def Sell():
    if request.method == "POST":
        # In the case of the payout didn't completed, send the payout link to the user to restore his cash

        if "restore" in request.args:
            Id = request.args.get("restore")


            Payout = Requests.request(url=CORE + "/payouts/%s/%s" % (Session_["Address"], Id), method="GET")


            if Payout.status_code == 200:
                PayoutLink = Payout.json()["result"]


                if PayoutLink["Status"] == "processed":
                    return jsonify({}), 500
                
                
                # Fetch the payout link

                Headers = {
                    'Accept': 'application/json',
                    'Authorization': 'Bearer <TOKEN>'
                }
                Payout = Requests.request(url="https://b2b.revolut.com/api/1.0/payout-links/" + PayoutLink["Id"], method="GET", headers=Headers, data={})
                

                if Payout.status_code == 200:
                    return jsonify({
                        "Url": Payout.json()["url"]
                    }), 200
                
                return jsonify({}), 404

        else:
            # Payout user normally

            Payload = Json.loads(request.get_data())

            Currency = Payload["Currency"]
            Amount = Payload["Amount"]
            Price = GetPrice()


            # Check if user broke the limits

            if Currency == "EUR":
                if Amount < 10:
                    return jsonify({
                        "result": "Min 10 €."
                    }), 400

                # Convert those euros in walletcoins
                Amount = Amount / Price
            else:
                WLLC = Amount * Price

                if WLLC < 10:
                    return jsonify({
                        "result": "Min 10 €."
                    }), 400
            

            # Sell walletcoins and send to user his payout link

            if Session_["Balance"] < Amount:
                return jsonify({
                    "result": "Insufficient balance."
                }), 403
            else:
                # Generate link

                LinkPayload = {
                    "counterparty_name": Payload["Name"],
                    "save_counterparty": True,
                    "account_id": "<< MyAcountId >>",
                    "amount": Amount * Price,
                    "currency": "EUR",
                    "reference": "Sell %s WalletCoins." % Amount,
                    "payout_methods": [
                        "revolut",
                        "bank_account"
                    ],
                    "transfer_reason_code": "cryptocurrency_sold"
                }
                LinkPayload = Json.dumps(LinkPayload)
                LinkHeaders = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': 'Bearer <TOKEN>'
                }

                LinkCreate = Requests.request(url="https://b2b.revolut.com/api/1.0/payout-links", method="POST", headers=LinkHeaders, data=LinkPayload)


                if LinkCreate.status_code == 200:
                    # Link created, sell walletcoins & send the payout link to user

                    SellPayload = {
                        "PrivKey": Session_["PrivateKey"],
                        "Address": Session_["Address"],
                        "Amount": Amount
                    }
                    SellPayload = Json.dumps(SellPayload)
                    SellRequest = Requests.request(url=CORE + "/wallets/sell", method="POST", data=SellPayload)


                    if SellRequest.status_code == 200:
                        Session_["Balance"] = SellRequest.json()["result"]["Balance"]


                        # Save payout url

                        Link = LinkCreate.json()
                        SaveLinkPayload = {
                            "Id": Link["id"],
                            "Wallet": Session_["Address"],
                            "Amount": Session_["Balance"]
                        }
                        SaveLinkPayload = Json.dumps(SaveLinkPayload)
                        SaveLinkRequest = Requests.request(url=CORE + "/payouts/create", method="POST", data=SaveLinkPayload)


                        return jsonify({
                            "Url": Link["url"]
                        }), 200
                    else:
                        return jsonify({
                            "result": "Error while selling your cryptos."
                        }), 500
                else:
                    return jsonify({
                        "result": "Error while creating payout link."
                    }), 500
    
    

    if request.method == "GET":
        if "restore" in request.args:
            Id = request.args.get("restore")

            return render_template(
                "Sell.html",
                Balance=Session_["Balance"],
                Price=GetPrice(),
                RestoreId=Id,
                Session=Session_
            )


        return render_template(
            "Sell.html",
            Balance=Session_["Balance"],
            Price=GetPrice(),
            Session=Session_
        )



@WEB.route("/lastPayout", methods=["GET"])
@connected_wallet
def LastPayout():
    Payout = Requests.request(url=CORE + "/payouts/%s/last" % Session_["Address"], method="GET")
    return "Id: " + Payout.json()["result"]["Id"]



@WEB.route("/blockchain", methods = ["GET"])
@connected_wallet
def Blockchain():
    BlockchainChain = Requests.request(url=CORE + "/blockchain", method="GET")


    if BlockchainChain.status_code == 200:
        BlockchainChain = BlockchainChain.json()["result"]

        Balance = Session_["Balance"]
        BalancePrice = GetPrice()
        WalletAddress = Session_["Address"]
        MyBlock = Requests.request(url=CORE + "/block?list=Wallet&wallet=" + WalletAddress, method="GET")


        if BalancePrice != None:
            BalancePrice = BalancePrice * Balance
        else:
            BalancePrice = 0


        if MyBlock.status_code == 200:
            MyBlock = MyBlock.json()["result"]


            if len(MyBlock) > 0:
                MyBlock = MyBlock[0]
                

                return render_template(
                    "Blockchain.html",
                    Session=Session_,
                    Balance=Balance,
                    Price=BalancePrice,
                    WalletAddress=WalletAddress,
                    BlocksList=BlockchainChain,
                    MyBlock=MyBlock
                )
            else:
                return render_template(
                    "Blockchain.html",
                    Session=Session_,
                    Balance=Balance,
                    Price=BalancePrice,
                    WalletAddress=WalletAddress,
                    BlocksList=BlockchainChain
                )
        else:
            return render_template(
                "Blockchain.html",
                Session=Session_,
                Balance=Balance,
                Price=BalancePrice,
                WalletAddress=WalletAddress,
                BlocksList=BlockchainChain
            )

    else:
        Balance = Session_["Balance"]
        BalancePrice = GetPrice()
        WalletAddress = Session_["Address"]


        if BalancePrice != None:
            BalancePrice = BalancePrice * Balance
        else:
            BalancePrice = 0


        return render_template(
            "Blockchain.html",
            Session=Session_,
            Balance=Balance,
            Price=BalancePrice,
            WalletAddress=WalletAddress,
            BlocksList={}
        )



@WEB.route("/block", methods=["GET"])
@connected_wallet
def Block():
    Args = request.args
    BlockNumber = Args.get("number")
    ThisBlock = Requests.request(url=CORE + "/block?list=Number&number=" + str(BlockNumber), method="GET")


    if ThisBlock.status_code != 200:
        return render_template(
            "Block.html",
            Session=Session_,
            Number=BlockNumber
        )
    else:
        ThisBlock = ThisBlock.json()["result"]

        if len(ThisBlock) == 0:
            return render_template(
                "Block.html",
                Session=Session_,
                Number=BlockNumber
            )


    return render_template(
        "Block.html",
        Session=Session_,
        Number=BlockNumber,
        Nonce=ThisBlock[0]["Nonce"],
        Hash=ThisBlock[0]["Hash"],
        PreviousHash=ThisBlock[0]["PrevHash"],
        BlockData=ThisBlock
    )



@WEB.route("/blocks/search", methods=["POST"])
def SearchBlock():
    Payload = Json.loads(request.get_data())
    SearchUrl = ""


    if Functions.IsNumber(Text=Payload["Block"]):
        # Search block by number
        SearchUrl = "/block?list=Number&number=" + str(Payload["Block"])
    else:
        # Search block by wallet
        SearchUrl = "/block?list=Wallet&wallet=" + str(Payload["Block"])
    

    Res = Requests.request(url=CORE + SearchUrl, method="GET")

    if Res.status_code == 200:
        ThisBlock = Res.json()["result"]


        if len(ThisBlock) == 0:
            return jsonify({}), 404

        
        return jsonify({
            "Number": ThisBlock[0]["Block"]
        }), 200


    return jsonify({}), 500



@WEB.route("/payments", methods=["GET"])
def GetPayment():
    Args = request.args


    if not "invoice" in Args:
        return jsonify({
            "result": {
                "message": "Invoice param is missing.",
                "statusCode": 400
            }
        }), 400


    if not "seller" in Args:
        return jsonify({
            "result": {
                "message": "Seller param is missing.",
                "statusCode": 400
            }
        }), 400


    Invoice = Args.get("invoice")
    Seller = Args.get("seller")


    # Fetch the invoice

    Payload = {
        "Invoice": Invoice,
        "Seller": Seller
    }
    Payload = Json.dumps(Payload)
    Req = Requests.request(url=CORE + "/wallets/invoices/get", method="POST", data=Payload)


    if Req.status_code == 200:
        Body = Req.json()["result"]

        return render_template(
            "WebPayments.html",
            Invoice=Invoice,
            Wallet=Seller,
            Amount=Body["Amount"],
            Description=Body["Description"],
            Success=Body["Urls"]["Success"],
            Failed=Body["Urls"]["Failed"],
            Cancel=Body["Urls"]["Cancel"]
        )
    else:
        return jsonify({
            "result": {
                "message": "Failed to complete payment.",
                "statusCode": 500
            }
        }), 500



@WEB.route("/payments/<string:Invoice>/execute", methods=["POST"])
def PaymentsExecute(Invoice):
    Payload = Json.loads(request.get_data())


    if not "Seller" in Payload:
        return jsonify({
            "result": {
                "message": "Seller argument missing.",
                "statusCode": 400
            }
        }), 400


    if not "PrivateKey" in Payload:
        return jsonify({
            "result": {
                "message": "PrivateKey argument missing.",
                "statusCode": 400
            }
        }), 400
    

    if not "SecretPhrase" in Payload:
        return jsonify({
            "result": {
                "message": "SecretPhrase argument missing.",
                "statusCode": 400
            }
        }), 400
    

    ExecutePayload = {
        "InvoiceId": Invoice,
        "Seller": Payload["Seller"],
        "PayerPrivateKey": Payload["PrivateKey"],
        "PayerSecretPhrase": Payload["SecretPhrase"]
    }
    ExecutePayload = Json.dumps(ExecutePayload)
    ExecuteRequest = Requests.request(url=CORE + "/wallets/invoices/execute", method="POST", data=ExecutePayload)
    return jsonify({}), ExecuteRequest.status_code



@WEB.route("/help/center")
def HelpCenter():
    return render_template("HelpCenter.html", Session=Session_)


@WEB.route("/FAQ")
def FAQ():
    return render_template("FAQ.html", Session=Session_)


@WEB.route("/api/rest")
def RestfulApi():
    return render_template("RestApi.html", Session=Session_)


@WEB.route("/api/webPayments")
def WebPaymentsDoc():
    return render_template("WebPaymentsDocumentation.html", Session=Session_)


@WEB.route("/privacy")
def TermsAndPrivacy():
    return render_template("PrivacyAndTerms.html", Session=Session_)



if __name__ == '__main__':
    WEB.secret_key = 'secret123'
    WEB.run(port=3047, debug=True)
