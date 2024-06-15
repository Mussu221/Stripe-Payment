from flask_marshmallow import Marshmallow
from marshmallow import fields, validate

ma = Marshmallow()

class AccountLinkSchema(ma.Schema):
    account_id = fields.String(required=True, validate=validate.Length(min=1))

class CustomerSchema(ma.Schema):
    email = fields.Email(required=True)

class CardSchema(ma.Schema):
    customer_id = fields.String(required=True)
    card_token = fields.String(required=True)

class CheckoutSessionSchema(ma.Schema):
    customer_id = fields.String(required=True)
    amount = fields.Integer(required=True, validate=validate.Range(min=1))
    currency = fields.String(required=True, validate=validate.OneOf(["inr"]))
    seller_account_id = fields.String(required=True)


account_link_schema = AccountLinkSchema()
customer_schema = CustomerSchema()
card_schema = CardSchema()
checkout_session_schema =  CheckoutSessionSchema()
