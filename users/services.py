import stripe
from forex_python.converter import CurrencyRates

from config.settings import STRIPE_API_KEY
from users.models import User

stripe.api_key = STRIPE_API_KEY


def convert_rub_to_usd(amount):
    """Конвертирует рубли в доллары"""

    c = CurrencyRates()
    rate = c.get_rate("RUB", "USD")
    return int(amount * rate)


def create_stripe_product(name):
    """Создаёт Stripe Product для курса или урока"""

    product = stripe.Product.create(name=name)
    return product


def create_stripe_price(product, amount):
    """Создает цену в страйпе"""

    price = stripe.Price.create(
        currency="usd",
        unit_amount=amount * 100,
        product=product.id,
    )
    return price


def create_stripe_checkout_session(price):
    """Создает сессию на оплату в страйпе"""

    session = stripe.checkout.Session.create(
        success_url="https://127.0.0.1:8000/",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")


def retrieve_stripe_checkout_session(session_id):
    """Получает информацию о Stripe Checkout Session по session_id."""

    session = stripe.checkout.Session.retrieve(session_id)
    return session


def deactivate_inactive_users_service(cutoff_date):
    """Деактивирует пользователей, не заходивших в систему дольше заданного срока."""

    return User.objects.filter(
        is_active=True,
        last_login__lt=cutoff_date,
    ).update(is_active=False)
