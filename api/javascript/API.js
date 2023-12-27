const Express = require("express");
const { XMLHttpRequest } = require("xhr2");
const Server = Express();
const PORT = 3049;

const CORE = "http://127.0.0.1:3048";


Server.use(Express.json());
Server.use(Express.urlencoded({ extended: true }));


Server.listen(PORT, () => {
	console.log("Listening on port " + PORT);
})



Server.get("/api/price", (req, res) => {
    var HTTP = new XMLHttpRequest();

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Couldn't fetch price.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("GET", CORE + "/price");
    HTTP.send(null);
})



Server.get("/api/price/chart", (req, res) => {
    var { list } = req.query;
    let RequestUrl = CORE + "/price/hours";
    
    console.log(list);

    if ( list ) {
        // Listing argument passed

        switch (list) {
            case "months":
                var { year } = req.query;
                

                if ( ! year ) {
                    return res.status(400).send({
                        "result": {
                            "message": "Year argument missing.",
                            "statusCode": 400
                        }
                    })
                } else {
                    RequestUrl = CORE + "/price/" + list + "?year=" + year;
                }
                break;
            
            case "days":
                var { month } = req.query;
                var { year } = req.query;
                

                if ( ! year || ! month ) {
                    return res.status(400).send({
                        "result": {
                            "message": "Year or month argument missing.",
                            "statusCode": 400
                        }
                    })
                } else {
                    RequestUrl = CORE + "/price/" + list + "?year=" + year + "&month=" + month;
                }
                break;
            
            case "hours":
                var { day } = req.query;
                var { month } = req.query;
                var { year } = req.query;
                

                if ( ! year || ! month || ! day ) {
                    return res.status(400).send({
                        "result": {
                            "message": "Year, month or day argument missing.",
                            "statusCode": 400
                        }
                    })
                } else {
                    RequestUrl = CORE + "/price/" + list + "?year=" + year + "&month=" + month + "&day=" + day;
                }
                break;
            
            default:
                return res.status(400).send({
                    "result": {
                        "message": "Invalid listing argument.",
                        "statusCode": 400
                    }
                })
        }
    }


    var HTTP = new XMLHttpRequest();

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Couldn't fetch price data.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("GET", RequestUrl);
    HTTP.send(null);
})



Server.post("/api/wallet/auth", (req, res) => {
    var { private_key } = req.body;
    var { secret_phrase } = req.body;
    var { wallet } = req.body;
    var { api_key } = req.body;


    // Validate api credentials = = = = = = = = = = = = = = = = = =

    var ValidateHTTP = new XMLHttpRequest();
    

    ValidateHTTP.onerror = function() {
        return res.status(ValidateHTTP.status).send({
            "result": {
                "message": "Invalid credentials.",
                "statusCode": ValidateHTTP.status
            }
        })
    }

    var ValidatePayload = {
        "Wallet": wallet,
        "Key": api_key
    }
    ValidatePayload = JSON.stringify(ValidatePayload)
    ValidateHTTP.open("POST", CORE + "/wallets/validateApiKey");
    ValidateHTTP.send(ValidatePayload);

    // Validation finished = = = = = = = = = = = = = = = = = = = =


    var HTTP = new XMLHttpRequest();
    var Payload = {
        "PrivKey": private_key,
        "Secret": secret_phrase
    };
    Payload = JSON.stringify(Payload);

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Unable connect your wallet.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("POST", CORE + "/wallets/connect");
    HTTP.send(Payload);
})



Server.post("/api/wallet/transaction", (req, res) => {
    var { private_key } = req.body;
    var { recipient } = req.body;
    var { amount } = req.body;
    var { wallet } = req.body;
    var { api_key } = req.body;


    // Validate api credentials = = = = = = = = = = = = = = = = = =

    var ValidateHTTP = new XMLHttpRequest();
    

    ValidateHTTP.onerror = function() {
        return res.status(ValidateHTTP.status).send({
            "result": {
                "message": "Invalid credentials.",
                "statusCode": ValidateHTTP.status
            }
        })
    }

    var ValidatePayload = {
        "Wallet": wallet,
        "Key": api_key
    }
    ValidatePayload = JSON.stringify(ValidatePayload)
    ValidateHTTP.open("POST", CORE + "/wallets/validateApiKey");
    ValidateHTTP.send(ValidatePayload);

    // Validation finished = = = = = = = = = = = = = = = = = = = =


    var HTTP = new XMLHttpRequest();
    var Payload = {
        "PrivKey": private_key,
        "Recipient": recipient,
        "Amount": parseFloat(amount)
    };
    Payload = JSON.stringify(Payload);

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Unable connect your wallet.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("POST", CORE + "/wallets/transaction");
    HTTP.send(Payload);
})



Server.post("/api/wallet/withdraw", (req, res) => {
    var { private_key } = req.body;
    var { withdraw_to } = req.body;
    var { amount } = req.body;
    var { wallet } = req.body;
    var { api_key } = req.body;


    // Validate api credentials = = = = = = = = = = = = = = = = = =

    var ValidateHTTP = new XMLHttpRequest();
    

    ValidateHTTP.onerror = function() {
        return res.status(ValidateHTTP.status).send({
            "result": {
                "message": "Invalid credentials.",
                "statusCode": ValidateHTTP.status
            }
        })
    }

    var ValidatePayload = {
        "Wallet": wallet,
        "Key": api_key
    }
    ValidatePayload = JSON.stringify(ValidatePayload)
    ValidateHTTP.open("POST", CORE + "/wallets/validateApiKey");
    ValidateHTTP.send(ValidatePayload);

    // Validation finished = = = = = = = = = = = = = = = = = = = =


    var HTTP = new XMLHttpRequest();
    var Payload = {
        "PrivKey": private_key,
        "Recipient": withdraw_to,
        "Amount": parseFloat(amount)
    };
    Payload = JSON.stringify(Payload);

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Unable connect your wallet.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("POST", CORE + "/wallets/transaction");
    HTTP.send(Payload);
})



Server.post("/api/wallet/deposit", (req, res) => {
    var { private_key } = req.body;
    var { deposit_to } = req.body;
    var { amount } = req.body;
    var { wallet } = req.body;
    var { api_key } = req.body;


    // Validate api credentials = = = = = = = = = = = = = = = = = =

    var ValidateHTTP = new XMLHttpRequest();
    

    ValidateHTTP.onerror = function() {
        return res.status(ValidateHTTP.status).send({
            "result": {
                "message": "Invalid credentials.",
                "statusCode": ValidateHTTP.status
            }
        })
    }

    var ValidatePayload = {
        "Wallet": wallet,
        "Key": api_key
    }
    ValidatePayload = JSON.stringify(ValidatePayload)
    ValidateHTTP.open("POST", CORE + "/wallets/validateApiKey");
    ValidateHTTP.send(ValidatePayload);

    // Validation finished = = = = = = = = = = = = = = = = = = = =


    var HTTP = new XMLHttpRequest();
    var Payload = {
        "PrivKey": private_key,
        "Recipient": deposit_to,
        "Amount": parseFloat(amount)
    };
    Payload = JSON.stringify(Payload);

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Unable connect your wallet.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("POST", CORE + "/wallets/transaction");
    HTTP.send(Payload);
})



Server.post("/api/webPayments", (req, res) => {
    var { description } = req.body;
    var { amount } = req.body;
    var { success_url } = req.body;
    var { failed_url } = req.body;
    var { cancel_url } = req.body;
    var { private_key } = req.body;
    var { wallet } = req.body;
    var { api_key } = req.body;


    if ( ! success_url || ! failed_url || ! cancel_url ) {
        return res.status(400).send({
            "result": {
                "message": "Success or failed or cancel url missing.",
                "statusCode": 400
            }
        })
    }


    // Validate api credentials = = = = = = = = = = = = = = = = = =

    var ValidateHTTP = new XMLHttpRequest();
    

    ValidateHTTP.onerror = function() {
        return res.status(ValidateHTTP.status).send({
            "result": {
                "message": "Invalid credentials.",
                "statusCode": ValidateHTTP.status
            }
        })
    }

    var ValidatePayload = {
        "Wallet": wallet,
        "Key": api_key
    }
    ValidatePayload = JSON.stringify(ValidatePayload)
    ValidateHTTP.open("POST", CORE + "/wallets/validateApiKey");
    ValidateHTTP.send(ValidatePayload);

    // Validation finished = = = = = = = = = = = = = = = = = = = =


    var HTTP = new XMLHttpRequest();
    var Payload = {
        "PrivKey": private_key,
        "Description": description,
        "Amount": parseFloat(amount),
        "Urls": {
            "Success": success_url,
            "Failed": failed_url,
            "Cancel": cancel_url
        }
    };
    Payload = JSON.stringify(Payload);

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Unable to start a new invoice.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("POST", CORE + "/wallets/invoices/create");
    HTTP.send(Payload);
})



Server.get("/api/webPayments", (req, res) => {
    var { seller } = req.query;
    var { invoice } = req.query;
    var HTTP = new XMLHttpRequest();
    var Payload = {
        "Seller": seller,
        "InvoiceId": invoice
    };
    Payload = JSON.stringify(Payload);

    HTTP.onload = function() {
        return res.status(200).send(HTTP.responseText);
    }

    HTTP.onerror = function() {
        return res.status(HTTP.status).send({
            "result": {
                "message": "Unable to fetch this invoice.",
                "statusCode": HTTP.status
            }
        })
    }

    HTTP.open("POST", CORE + "/wallets/invoices/get");
    HTTP.send(Payload);
})
