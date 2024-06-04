import yookassa
from yookassa import Payment
import uuid

YOOKASSA_KEY='test_GZFeuwAegTZZELibiDPPCEXjBnbAzd7-jFSDaQkos00'
YOOKASSA_ID='396590'
yookassa.Configuration.account_id = YOOKASSA_ID
yookassa.Configuration.secret_key = YOOKASSA_KEY

def create_payment(amount: str, chat_id: int):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "paymnet_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/inspecttest_bot"
        },
        "capture": True,
        "meta_data": {
            "chat_id": chat_id
        },
        "description": 'Стоимость выполнения заявки...'
    }, id_key)
    return payment.confirmation.confirmation_url, payment.id

def check_payment(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False