import RevolutCheckout from '@revolut/checkout'


RevolutCheckout.payments({
  publicToken: '<yourPublicAPIKey>' // Merchant public API key
})
.then((paymentInstance) => {
  const revolutPay = paymentInstance.revolutPay

  const paymentOptions = {
    currency: 'EUR',
    totalAmount: parseInt(CalculatePrice().toString() + "00"), // In lowest denomination e.g., cents

    createOrder: () => {
      return CreatePayment()
      .then((order) => ({
        publicId: order.public_id,
      }))
    }
  }

  revolutPay.mount(document.getElementById('revolut-pay'), paymentOptions)

  revolutPay.on('payment', (event) => {
    switch (event.type) {
      case 'cancel': {
        if (event.dropOffState === 'payment_summary') {
          Notification.innerHTML = "What a shame, please complete your payment";
        }
        break;
      }

      case 'success':
        // Give the cryptos to user

        fetch("/buy", {
            method: "POST",
            body: JSON.stringify({
                "Currency": Currency,
                "Amount": parseFloat(Amount.value)
            })
        })
        break;

      case 'error':
        Notification.innerHTML = "Something went wrong while completing payment.";
        break;
    }
  })
})


function CreatePayment() {
    if (MinBetweenMax() && Amount.value > 0) {
        fetch("/buy/createOrder", {
            method: "POST",
            body: JSON.stringify({
                "Currency": Currency,
                "Amount": parseFloat(Amount.value)
            })
        })
    }
}
