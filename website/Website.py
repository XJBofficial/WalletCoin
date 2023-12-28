from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from functools import wraps

import requests as Requests
import datetime as DateTime
import stripe as Stripe
import time as Time
import json as Json
import Functions
import os as OS


#StripePUBLIC_KEY = "pk_test_51N5EBzHImWZNuXQo8QWI4wAJzHDqQIYUNYf9g5M14dmFGVKnLEOLukHeqLQYxyL7IsS5hCRhn97fJi467pTtjI8a002EtFkSLD"
#StripeSECRET_KEY = "sk_test_51N5EBzHImWZNuXQojVDpV2LDUIhfDcHnqqC97QDODdbc4LdQjtmtbjHBBZNVIw45VUKUXx9D4a5CuNKJ45rObDy500cHgGYGJa"
StripePUBLIC_KEY = "pk_live_51N5EBzHImWZNuXQolpw4D5mStlDSOkba9NuvDBDuPl3tRcjHEkJQDle01kR3nMEBRkJeJyHm8vvdVuRK4rhvwxUk008xIcdQ9x"
StripeSECRET_KEY = "<< MY_SECRET_KEY >>"
Stripe.api_key = StripePUBLIC_KEY
Stripe.secret_key = StripeSECRET_KEY

WEB = Flask(__name__)
WEB.config.from_mapping(SECRET_KEY = OS.environ.get('SECRET_KEY') or 'dev_key')

Session_ = session

CORE = "http://127.0.0.1:3048"
API_CORE = "http://127.0.0.1:3049"
DOMAIN = "https://walletcoincrypto.com"


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
    MarketCap = CryptoCurrencyData["MarketCap"]
    Supply = CryptoCurrencyData["Supply"]
    Bought = CryptoCurrencyData["Bought"]


    return render_template(
        'Index.html',
        Price=Price,
        MarketCap=MarketCap,
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
        MarketCap = Chart["MarketCap"]


        return render_template(
            "PriceChart.html",
            Price=Price,
            Changed=PriceChanged,
            PriceChange=Functions.RemoveUselessNums(str(PriceChange), 2),
            Owned=Functions.RemoveUselessNums(str(Owned), 8),
            ForSell=Functions.RemoveUselessNums(str(ForSell), 8),
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


            # Create a stripe account for this wallet
            
            Account = Stripe.Account.create(
                api_key=StripeSECRET_KEY,
                type="custom",
                capabilities={
                    "card_payments": {
                        "requested": True
                    },
                    "transfers": {
                        "requested": True
                    }
                }
            )

            Stripe.Account.modify(
                api_key=StripeSECRET_KEY,
                stripe_account=Account["id"],
                business_type="individual",
                business_profile={
                    "mcc": "5817",
                    "url": "https://www.youtube.com/channel/UC1nPOWMNYGw3ERLHYH64NSg"
                },
                individual={
                    "address": {
                        "city": "Athens-Greece",
                        "line1": "Πογραδετσ",
                        "postal_code": "12136"
                    },
                    "dob": {
                        "day": 5,
                        "month": 2,
                        "year": 2005
                    },
                    "email": "makegamesandsites@gmail.com",
                    "first_name": "Konstantinos",
                    "last_name": "Papapanagiotou",
                    "phone": "+306970351652"
                },
                tos_acceptance={
                    "date": int(Time.time()),
                    "ip": Requests.get("https://api.ipify.org").text
                }
            )

            StripePayload = {
                "Wallet": Wallet["Address"],
                "StripeId": Account["id"]
            }
            StripePayload = Json.dumps(StripePayload)
            StripeRes = Requests.request(url=CORE + "/stripeAccount/create", method="POST", data=StripePayload)


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
        Payload = request.form
        Amount = int(float(Payload["Amount"]))
        EUR = Amount


        # Convert those euros in walletcoins
        Amount = Amount / GetPrice()

        # Check if user broke the limits

        if EUR < 10 or EUR > 100000:
            return jsonify({
                "result": "Min 10 €, Max 100,000 €."
            }), 400


        # Record this payment

        SavePaymentPayload = {
            #"Id": Args.get("order"),
            "Wallet": Session_["Address"],
            "Amount": int(EUR)
        }
        SavePaymentPayload = Json.dumps(SavePaymentPayload)
        SavePaymentRequest = Requests.request(url=CORE + "/payments/create", method="POST", data=SavePaymentPayload)


        # Execute the payment

        CheckoutSession = None


        try:
            CheckoutSession = Stripe.checkout.Session.create(
                api_key=StripeSECRET_KEY,
                line_items=[
                    {
                        'price_data': {
                            'currency': 'eur',
                            'unit_amount': int(str(int(EUR)) + "00"),
                            "product_data": {
                                "name": "%s WalletCoins" % str(Amount)
                            }
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=DOMAIN + '/buy?payment=' + SavePaymentRequest.json()["result"]["Id"],
                cancel_url=DOMAIN + '/buy',
            )
        
        except Exception as e:
            return str(e)
        

        return redirect(CheckoutSession.url, code=303)
    

    if request.method == "GET":
        Args = request.args


        if "payment" in Args:
            GetPaymentRequest = Requests.request(url=CORE + "/payments/%s/%s" % (Session_["Address"], Args.get("payment")), method="GET")


            if GetPaymentRequest.status_code == 200:
                Res = GetPaymentRequest.json()["result"]
                

                if len(Res) > 0:
                    if Res["Status"] == "Authorizing":
                        # Buy the coins

                        Payload = {
                            "PrivKey": Session_["PrivateKey"],
                            "Address": Session_["Address"],
                            "Amount": Res["Amount"] / GetPrice()
                        }
                        Payload = Json.dumps(Payload)
                        BuyRequest = Requests.request(url=CORE + "/wallets/buy", method="POST", data=Payload)


                        # Update the payment status

                        UpdatePaymentPayload = {
                            "Status": "Success"
                        }
                        UpdatePaymentPayload = Json.dumps(UpdatePaymentPayload)
                        UpdatePayment = Requests.request(url=CORE + "/payments/%s/%s/status" % (Session_["Address"], Args.get("payment")), method="POST", data=UpdatePaymentPayload)


                        if BuyRequest.status_code == 200:
                            Session_["Balance"] = BuyRequest.json()["result"]["Balance"]
                            return redirect(url_for("Blockchain"))


        return render_template(
            "Buy.html",
            Balance=Session_["Balance"],
            Price=GetPrice(),
            Session=Session_
        )



@WEB.route("/sell", methods=["POST", "GET"])
@connected_wallet
def Sell():
    if request.method == "POST":
        # Payout user normally

        Payload = Json.loads(request.get_data())
        Amount = Payload["Amount"]
        Price = GetPrice()


        # Check if user broke the limits

        if Amount < 10:
            return jsonify({
                "result": "Min 10 €."
            }), 400

        # Convert those euros in walletcoins
        Amount = Amount / Price
        

        # Sell walletcoins and send to user his payout link

        if Session_["Balance"] < Amount:
            return jsonify({
                "result": "Insufficient balance."
            }), 403
        else:
            EUR = Amount * GetPrice()
            StripeAccountId = ""


            # First of all, search for the identity of the stripe account

            StripeAccountIdRequest = Requests.request(url=CORE + "/stripeAccount/" + Session_["Address"], method="GET")

            if StripeAccountIdRequest.status_code == 200:
                StripeAccountId = StripeAccountIdRequest.json()["result"]["StripeId"]
            else:
                return jsonify({}), 500


            Stripe.Account.modify(
                api_key=StripeSECRET_KEY,
                stripe_account=StripeAccountId,
                business_type="individual",
                business_profile = {
                        "mcc": "5817",
                        "url": "https://www.youtube.com/channel/UC1nPOWMNYGw3ERLHYH64NSg"
                },
                individual={
                "address": {
                        "city": "Athens-Greece",
                        "line1": "Πογραδετσ",
                        "postal_code": "12136"
                    },
                    "dob": {
                        "day": 5,
                        "month": 2,
                        "year": 2005
                    },
                    "email": "makegamesandsites@gmail.com",
                    "first_name": Payload["Bank"]["HolderName"].split(" ")[0],
                    "last_name": Payload["Bank"]["HolderName"].split(" ")[1],
                    "phone": "+306970351652"
                },
                tos_acceptance={
                    "date": int(Time.time()),
                    "ip": Requests.get("https://api.ipify.org").text
                }
            )


            # Connect your bank account

            ConnectPayload = {
                "country": Payload["Bank"]["CountryCode"],
                "currency": Payload["Bank"]["Currency"].lower(),
                "account_holder_name": Payload["Bank"]["HolderName"],
                "account_holder_type": Payload["Bank"]["HolderType"]
            }


            if Payload["Bank"]["European"]:
                ConnectPayload["account_number"] = Payload["Bank"]["IBAN"]
            else:
                ConnectPayload["routing_number"] = Payload["Bank"]["RoutingNumber"]
                ConnectPayload["account_number"] = Payload["Bank"]["AccountNumber"]
            

            Tok = Stripe.Token.create(
                api_key=StripeSECRET_KEY,
                bank_account=ConnectPayload
            )

            Acc = Stripe.Account.modify(
                StripeAccountId,
                external_account=Tok["id"],
                api_key=StripeSECRET_KEY
            )


            # Save it into the database

            SavePayload = Acc
            SavePayload["Wallet"] = Session_["Address"]
            SavePayload = Json.dumps(SavePayload)

            SaveRes = Requests.request(url=CORE + "/bankAccount/create", method="POST", data=SavePayload)
            

            # Now sell the cryptos

            SellPayload = {
                "PrivKey": Session_["PrivateKey"],
                "Address": Session_["Address"],
                "Amount": Amount
            }
            SellPayload = Json.dumps(SellPayload)
            SellRequest = Requests.request(url=CORE + "/wallets/sell", method="POST", data=SellPayload)


            if SellRequest.status_code == 200:
                Session_["Balance"] = SellRequest.json()["result"]["Balance"]


                # Record this payout in order to payout the user

                SaveLinkPayload = {
                    "Wallet": Session_["Address"],
                    "Destination": StripeAccountId,
                    "WLLC": Amount,
                    "Amount": EUR
                }
                SaveLinkPayload = Json.dumps(SaveLinkPayload)
                SaveLinkRequest = Requests.request(url=CORE + "/payouts/create", method="POST", data=SaveLinkPayload)


                return redirect(url_for("Blockchain"))


            return jsonify({
                "result": "Error while selling your cryptos."
            }), 500
    
    

    if request.method == "GET":
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



# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# API
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

@WEB.route("/api/price")
def APIPrice():
    Res = Requests.request(url=API_CORE + "/api/price", method="GET")
    return jsonify(Res.json()), Res.status_code



@WEB.route("/api/price/chart")
def APIPriceChart():
    List = request.args.get("list")
    Res = None


    if List == "months":
        Year = request.args.get("year")

        if not Year:
            return jsonify({
                "result": {
                    "message": "Missing arguments",
                    "status": 400
                }
            }), 400

        Res = Requests.request(url=API_CORE + "/api/price/chart?list=months&year=%s" % Year, method="GET")
    
    
    if List == "days":
        Year = request.args.get("year")
        Month = request.args.get("month")

        if not Year or not Month:
            return jsonify({
                "result": {
                    "message": "Missing arguments",
                    "status": 400
                }
            }), 400

        Res = Requests.request(url=API_CORE + "/api/price/chart?list=days&year=%s&month=%s" % (Year, Month), method="GET")


    if List == "hours":
        Year = request.args.get("year")
        Month = request.args.get("month")
        Day = request.args.get("day")

        if not Year or not Month or not Day:
            return jsonify({
                "result": {
                    "message": "Missing arguments",
                    "status": 400
                }
            }), 400

        Res = Requests.request(url=API_CORE + "/api/price/chart?list=hours&year=%s&month=%s&day=%s" % (Year, Month, Day), method="GET")


    return jsonify(Res.json()), Res.status_code



@WEB.route("/api/wallet/auth", methods=["POST"])
def APIWalletAuth():
    Payload = Json.loads(request.get_data())

    if not "private_key" in Payload or not "secret_phrase" in Payload or not "wallet" in Payload or not "api_key" in Payload:
        return jsonify({
            "result": {
                "message": "Missing arguments",
                "status": 400
            }
        }), 400


    NewPayload = {
        "private_key": Payload["private_key"],
        "secret_phrase": Payload["secret_phrase"],
        "wallet": Payload["wallet"],
        "api_key": Payload["api_key"]
    }

    Res = Requests.request(url=API_CORE + "/api/wallet/auth", method="POST", data=NewPayload)
    return jsonify(Res.json()), Res.status_code



@WEB.route("/api/wallet/transaction", methods=["POST"])
def APIWalletTransaction():
    Payload = Json.loads(request.get_data())

    if not "private_key" in Payload or not "recipient" in Payload or not "amount" in Payload or not "wallet" in Payload or not "api_key" in Payload:
        return jsonify({
            "result": {
                "message": "Missing arguments",
                "status": 400
            }
        }), 400


    NewPayload = {
        "private_key": Payload["private_key"],
        "recipient": Payload["recipient"],
        "amount": Payload["amount"],
        "wallet": Payload["wallet"],
        "api_key": Payload["api_key"]
    }

    Res = Requests.request(url=API_CORE + "/api/wallet/transaction", method="POST", data=NewPayload)
    return jsonify(Res.json()), Res.status_code



@WEB.route("/api/wallet/withdraw", methods=["POST"])
def APIWalletWithdraw():
    Payload = Json.loads(request.get_data())

    if not "private_key" in Payload or not "withdraw_to" in Payload or not "amount" in Payload or not "wallet" in Payload or not "api_key" in Payload:
        return jsonify({
            "result": {
                "message": "Missing arguments",
                "status": 400
            }
        }), 400


    NewPayload = {
        "private_key": Payload["private_key"],
        "withdraw_to": Payload["withdraw_to"],
        "amount": Payload["amount"],
        "wallet": Payload["wallet"],
        "api_key": Payload["api_key"]
    }

    Res = Requests.request(url=API_CORE + "/api/wallet/withdraw", method="POST", data=NewPayload)
    return jsonify(Res.json()), Res.status_code



@WEB.route("/api/wallet/deposit", methods=["POST"])
def APIWalletDeposit():
    Payload = Json.loads(request.get_data())

    if not "private_key" in Payload or not "deposit_to" in Payload or not "amount" in Payload or not "wallet" in Payload or not "api_key" in Payload:
        return jsonify({
            "result": {
                "message": "Missing arguments",
                "status": 400
            }
        }), 400


    NewPayload = {
        "private_key": Payload["private_key"],
        "deposit_to": Payload["deposit_to"],
        "amount": Payload["amount"],
        "wallet": Payload["wallet"],
        "api_key": Payload["api_key"]
    }

    Res = Requests.request(url=API_CORE + "/api/wallet/deposit", method="POST", data=NewPayload)
    return jsonify(Res.json()), Res.status_code



@WEB.route("/api/webPayments", methods=["POST", "GET"])
def APIWebPayments():
    if request.method == "POST":
        Payload = Json.loads(request.get_data())


        if not "description" in Payload or not "amount" in Payload or not "success_url" in Payload or not "failed_url" in Payload or not "cancel_url" in Payload:
            return jsonify({
                "result": {
                    "message": "Missing arguments",
                    "status": 400
                }
            }), 400


        if not "private_key" in Payload or not "wallet" in Payload or not "api_key" in Payload:
            return jsonify({
                "result": {
                    "message": "Missing arguments",
                    "status": 400
                }
            }), 400


        NewPayload = {
            "description": Payload["description"],
            "amount": Payload["amount"],
            "success_url": Payload["success_url"],
            "failed_url": Payload["failed_url"],
            "cancel_url": Payload["cancel_url"],
            "private_key": Payload["private_key"],
            "wallet": Payload["wallet"],
            "api_key": Payload["api_key"]
        }

        Res = Requests.request(url=API_CORE + "/api/webPayments", method="POST", data=NewPayload)
        return jsonify(Res.json()), Res.status_code


    if request.method == "GET":
        Seller = request.args.get("seller")
        Invoice = request.args.get("invoice")


        if not Seller or not Invoice:
            return jsonify({
                "result": {
                    "message": "Missing arguments",
                    "status": 400
                }
            }), 400
        

        Res = Requests.request(url=API_CORE + "/api/webPayments?seller=%s&invoice=%s" % (Seller, Invoice), method="GET")
        return jsonify(Res.json()), Res.status_code



# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

if __name__ == '__main__':
    WEB.secret_key = 'secret123'
    WEB.run(host="0.0.0.0", port=3047, debug=True)
