import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import stripe
from base.decorator import token_required
from base.schema import account_link_schema,ma, customer_schema, card_schema, checkout_session_schema

load_dotenv()


app = Flask(__name__)

api = Api(app)
ma.init_app(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
stripe.api_key = os.getenv('STRIPE_KEY')



class CreateStripeAccount(Resource):
    def post(self):
        try:
            account = stripe.Account.create(
                type='express',
                # country='IN',
                capabilities={
                    'card_payments': {'requested': True},
                    'transfers': {'requested': True},
                }
            )
            return {'status': 1, 'message': 'Account created', 'data': account.id}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400





class VerifyStripeAccount(Resource):
    @token_required
    def get(self, account_id):
        try:
            account = stripe.Account.retrieve(account_id)
            capabilities = account.get('capabilities', {})
            card_payments_enabled = capabilities.get('card_payments', 'inactive') == 'active'
            transfers_enabled = capabilities.get('transfers', 'inactive') == 'active'
            
            if card_payments_enabled and transfers_enabled:
                return {'status': 1, 'message': 'Account retrieved and capabilities are active', 'data': account.to_dict()}
            else:
                return {'status': 0, 'message': 'Account does not have required capabilities active', 'data': account.to_dict()}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400


class AccountLink(Resource):
    @token_required
    
    def post(self):
        # Validate the incoming JSON data
        json_data = request.get_json()
        if not json_data:
            return {'status': 0, 'message': 'No input data provided'}, 400

        errors = account_link_schema.validate(json_data)
        if errors:
            return {'status': 0, 'message': 'Validation failed', 'error': errors}, 400

        try:
            account_id = json_data['account_id']
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url='https://your-redirect-url.com/refresh',
                return_url='https://your-redirect-url.com/redirect',
                type='account_onboarding',
            )
            return {'status': 1, 'message': 'Account link created', 'data': account_link.to_dict()}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400

class RedirectResource(Resource):
    @token_required
    
    def get(self):
        return {"status": 1, "message": "Redirect successful"}

class RefreshResource(Resource):
    @token_required
    
    def get(self):
        return {"status": 0, "message": "Refresh required"}

class PaymentSucessResource(Resource):
    @token_required
    
    def get(self):
        return {"status": 1, "message": "payment completed"}

class PaymentFailResource(Resource):
    @token_required
    
    def get(self):
        return {"status": 0, "message": "payment failed"}

class CreateCustomer(Resource):
    @token_required
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'status': 0, 'message': 'No input data provided'}, 400

        errors = customer_schema.validate(json_data)
        if errors:
            return {'status': 0, 'message': 'Validation failed', 'error': errors}, 400

        try:
            customer = stripe.Customer.create(email=json_data['email'])
            return {'status': 1, 'message': 'Customer created', 'data': customer.id}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400


class RetrieveCustomer(Resource):
    @token_required
    
    def get(self, customer_id):
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {'status': 1, 'message': 'Customer retrieved', 'data': customer.to_dict()}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400

class AddCard(Resource):
    @token_required
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'status': 0, 'message': 'No input data provided'}, 400

        errors = card_schema.validate(json_data)
        if errors:
            return {'status': 0, 'message': 'Validation failed', 'error': errors}, 400

        try:
            card = stripe.Customer.create_source(
                json_data['customer_id'],
                source=json_data['card_token']
            )
            return {'status': 1, 'message': 'Card added', 'data': card.to_dict()}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400

class ListCards(Resource):
    @token_required
    
    def get(self, customer_id):
        try:
            cards = stripe.Customer.list_sources(
                customer_id,
                object='card'
            )
            return {'status': 1, 'message': 'Cards retrieved', 'data': [card.to_dict() for card in cards['data']]}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400



class CreateCheckoutSession(Resource):
    @token_required
    
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {'status': 0, 'message': 'No input data provided'}, 400

        errors = checkout_session_schema.validate(json_data)
        if errors:
            return {'status': 0, 'message': 'Validation failed', 'error': errors}, 400

        success_url = 'http://127.0.0.1:5000/payment_success'
        cancel_url = 'http://127.0.0.1:5000/payment_failed'
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': json_data['currency'],
                        'product_data': {
                            'name': 'Product Name',
                        },
                        'unit_amount': json_data['amount'],
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url= success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                payment_intent_data={
                    'application_fee_amount': 123,  # Application fee in the smallest currency unit (e.g., paise for INR)
                    'transfer_data': {
                        'destination': json_data['seller_account_id'],
                    },
                },
                customer= json_data['customer_id']
            )
            return {'status': 1, 'message': 'Checkout session created', 'data':{'session_id':session.id, "url":session.url}}
        except Exception as e:
            return {'status': 0, 'message': 'Something went wrong', 'error': str(e)}, 400



class RetrieveCustomerPayments(Resource):
    @token_required
    
    def get(self, customer_id):
        try:
            # Retrieve the list of PaymentIntents for the customer
            payment_intents = stripe.PaymentIntent.list(customer=customer_id)
            return jsonify({'status': 1, 'message': 'Payments retrieved', 'data': [pi.to_dict() for pi in payment_intents['data']]})
        except Exception as e:
            return jsonify({'status': 0, 'message': 'Something went wrong', 'error': str(e)}), 400
        

class RetrieveSellerTransfers(Resource):
    @token_required
    
    def get(self, seller_account_id):
        try:
            # Retrieve the list of transfers for the seller account
            transfers = stripe.Transfer.list(destination=seller_account_id)
            return jsonify({'status': 1, 'message': 'Transfers retrieved', 'data': [transfer.to_dict() for transfer in transfers['data']]})
        except Exception as e:
            return jsonify({'status': 0, 'message': 'Something went wrong', 'error': str(e)}), 400

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


if __name__ == '__main__':
    app.run(debug=True)
