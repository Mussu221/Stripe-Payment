import os
from dotenv import load_dotenv
from flask import Flask
import stripe
from base.main import AddCard, CreateCustomer, CreateStripeAccount, ListCards, CreateCheckoutSession, PaymentFailResource, PaymentSucessResource, RedirectResource, RefreshResource, RetrieveCustomer, RetrieveCustomerPayments, RetrieveSellerTransfers, VerifyStripeAccount, AccountLink
from base.schema import ma
from flask_restful import Api

load_dotenv()

def create_app():
    app = Flask(__name__)

    api = Api(app)
    ma.init_app(app)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    stripe.api_key = os.getenv('STRIPE_KEY')

    api.add_resource(CreateStripeAccount, '/create_account')
    api.add_resource(VerifyStripeAccount, '/verify_account/<string:account_id>')
    api.add_resource(AccountLink, '/account_link')
    api.add_resource(RedirectResource, '/redirect')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(CreateCustomer, '/create_customer')
    api.add_resource(RetrieveCustomer, '/retrieve_customer/<string:customer_id>')
    api.add_resource(AddCard, '/add_card')
    api.add_resource(ListCards, '/list_cards/<string:customer_id>')
    api.add_resource(CreateCheckoutSession, '/create_payment_intent')
    api.add_resource(PaymentSucessResource, '/payment_success')
    api.add_resource(PaymentFailResource, '/payment_failed')
    api.add_resource(RetrieveCustomerPayments, '/retrieve_customer_payments/<string:customer_id>')
    api.add_resource(RetrieveSellerTransfers, '/retrieve_seller_transfers/<string:seller_account_id>')

    return app

