from wtforms import Form, StringField, IntegerField, PasswordField, validators


class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(1, 50)])
    username = StringField('Username', [validators.Length(4, 25)])
    email = StringField('Email', [validators.Length(6, 50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message = 'Passwords do not match')])
    confirm = PasswordField('Confirm Password')


class TransactionForm(Form):
    wallet = StringField('Wallet', [validators.Length(4, 25)])
    amount = StringField('Amount', [validators.Length(1, 50)])


class BuyForm(Form):
    amount = StringField('Amount', [validators.Length(1, 50)])


class BuyStocksForm(Form):
    amount = IntegerField("Amount", [validators.length(1, 100)])


class SellStocksForm(Form):
    amount = IntegerField("Amount", [validators.length(1, 100)])


class CreateGameForm(Form):
    gameName = StringField("Game Name", [validators.Length(0, 100)])
    promotion = StringField("Game Website or Store ( https://... )", None)
    stocksAmount = IntegerField("Stocks Amount", [validators.Length(2, 3)])
