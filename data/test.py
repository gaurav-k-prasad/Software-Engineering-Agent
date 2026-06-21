import asyncio
import hashlib, test
import numpy as np, pandas as pd

from abc import ABC, abstractmethod
from datetime import datetime
from tensorflow.keras import Model as m, metrics as metric, activations as a, callbacks
from abc import a, b
from abc import *

test = 5


def log_execution(func) -> User:
    def wrapper(*args, **kwargs):
        print(f"[{datetime.now()}] Executing {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


def generate_user_id(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()[:12]


class DatabaseConnection:
    import pandas as pd

    def __init__(self, host: str):
        self.host = host
        self.connected = False

    def connect(self):
        self.connected = True
        print(f"Connected to {self.host}")

    def disconnect(self):
        self.connected = False
        print("Disconnected")

    def execute(self, query: str):
        if not self.connected:
            raise RuntimeError("Database not connected")
        print(f"Executing query: {query}")


class BaseRepository(ABC):
    def __init__(self, db: DatabaseConnection):
        self.db = db

    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def find_by_id(self, entity_id):
        pass


class UserRepository(BaseRepository):
    def save(self, data):
        self.db.execute(f"INSERT INTO users VALUES ({data})")

    def find_by_id(self, entity_id):
        self.db.execute(f"SELECT * FROM users WHERE id='{entity_id}'")

    def find_by_email(self, email):
        self.db.execute(f"SELECT * FROM users WHERE email='{email}'")


class ProductRepository(BaseRepository):
    def save(self, data):
        self.db.execute(f"INSERT INTO products VALUES ({data})")

    def find_by_id(self, entity_id):
        self.db.execute(f"SELECT * FROM products WHERE id='{entity_id}'")


class NotificationService:
    def send_email(self, recipient, subject, body):
        print(f"Sending email to {recipient}: {subject}")

    async def send_async_email(self, recipient, subject, body):
        await asyncio.sleep(1)
        print(f"Async email sent to {recipient}")


class UserService:
    def __init__(
        self, user_repo: UserRepository, notification_service: NotificationService
    ):
        self.user_repo = user_repo
        self.notification_service = notification_service

    @log_execution
    def create_user(self, name, email):
        user = {
            "id": generate_user_id(email),
            "name": name,
            "email": email,
        }

        self.user_repo.save(user)

        self.notification_service.send_email(
            email, "Welcome", "Welcome to our platform"
        )

        return user

    def get_user(self, user_id):
        return self.user_repo.find_by_id(user_id)

    async def register_user_async(self, name, email):
        user = self.create_user(name, email)

        await self.notification_service.send_async_email(
            email, "Registration Complete", "Your account is ready."
        )

        return user


GLOBAL = True


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def create_product(self, product_name, price):
        product = {
            "name": product_name,
            "price": price,
        }

        self.product_repo.save(product)

        return product

    def get_product(self, product_id):
        return self.product_repo.find_by_id(product_id)


class AnalyticsService:
    class MetricsCalculator:
        def calculate_revenue(self, transactions):
            total = 0

            for transaction in transactions:
                total += transaction["amount"]

            return total

        def calculate_average_order_value(self, transactions):
            if not transactions:
                return 0

            revenue = self.calculate_revenue(transactions)

            return revenue / len(transactions)

    def __init__(self):
        self.calculator = AnalyticsService.MetricsCalculator()

    def generate_report(self, transactions):
        revenue = self.calculator.calculate_revenue(transactions)

        average = self.calculator.calculate_average_order_value(transactions)

        return {
            "revenue": revenue,
            "average_order_value": average,
        }


def validate_email(email):
    return "@" in email


def create_default_admin():
    return {
        "name": "Admin",
        "role": "super_admin",
    }


async def main():
    db = DatabaseConnection("localhost")

    db.connect()

    user_repo = UserRepository(db)
    product_repo = ProductRepository(db)

    notification_service = NotificationService()

    user_service = UserService(user_repo, notification_service)

    product_service = ProductService(product_repo)

    user = user_service.create_user("Alice", "alice@example.com")

    await user_service.register_user_async("Bob", "bob@example.com")

    product_service.create_product("Laptop", 1500)

    analytics = AnalyticsService()

    report = analytics.generate_report(
        [
            {"amount": 100},
            {"amount": 200},
            {"amount": 300},
        ]
    )

    print(user)
    print(report)

    db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
