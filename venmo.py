"""
Questions:
 

    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other. 
    Consider the following: if user A is paying user B, user's A balance should be used if 
    there's enough balance to cover the whole payment, if not, 
    user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, 
    and then Carol paid Bobby $15, it should look something like this
   

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_feed()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note
 

class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

        self.stored_payment = []
        self.friends = []

    def store_payment_log(self, target, amount, note):
        # Bobby paid Carol $5.00 for Coffee
        self.stored_payment.append(f'{self.username} paid {target} ${float(amount):.2f} for {note}')

    def add_friend_log(self, friend_username):
        self.friends.append(f'{self.username} added {friend_username} as a friend')

    def retrieve_feed(self):
        # Returns a combined feed of payments (both outgoing and incoming) and friend activities
        return self.stored_payment + self.friends

    def add_friend(self, new_friend):
        # Check user is not adding themselves
        if self.username == new_friend.username:
            raise ValueError("Cannot add yourself as a friend")
        
        # Check if this friend is already added by looking for a matching friend log entry
        friend_log_prefix = f'{self.username} added {new_friend.username}'
        if any(friend.startswith(friend_log_prefix) for friend in self.friends):
            return  # Friend already added, do nothing
            
        # Add friend log
        self.add_friend_log(new_friend.username)

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        '''
            Complete the `User.pay()` method to allow users to pay each other. 
        Consider the following: if user A is paying user B, user's A balance should be used if 
        there's enough balance to cover the whole payment, if not, 
        user's A credit card should be charged instead.
        '''
        if self.balance >= float(amount):
            # pay with balance
            payment = self.pay_with_balance(target, amount, note)
        else:
            # pay with card
            payment = self.pay_with_card(target, amount, note)
            
        # Store payment log for feed (both for sender and receiver)
        self.store_payment_log(target.username, amount, note)
        
        # Store the payment in the target's feed as well (incoming payment)
        target.stored_payment.append(f'{self.username} paid {target.username} ${float(amount):.2f} for {note}')
        
        return payment

        
    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        try:
            self.balance = self.balance - amount
            payment = Payment(amount, self, target, note)
            target.add_to_balance(amount)
            return payment
        except PaymentException as ex:
            raise PaymentException(f'There was a Payment exception:{ex}')
        finally:
            return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed):
        # Bobby paid Carol $5.00 for Coffee
        # Carol paid Bobby $15.00 for Lunch
        if not feed:
            print("No activities to show in the feed.")
            return
            
        for activity in feed:
            print(activity)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")
 
            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures for each test method"""
        self.valid_username = "ValidUser123"
        self.invalid_username = "inv@lid"
        self.valid_card = "4111111111111111"
        self.invalid_card = "1234567890123456"
        
    def test_valid_user_creation(self):
        """Test creating a user with valid username"""
        user = User(self.valid_username)
        self.assertEqual(user.username, self.valid_username)
        self.assertEqual(user.balance, 0.0)
        self.assertIsNone(user.credit_card_number)
        
    def test_invalid_user_creation(self):
        """Test creating a user with invalid username raises exception"""
        with self.assertRaises(UsernameException):
            User(self.invalid_username)
    
    def test_add_credit_card(self):
        """Test adding a valid credit card"""
        user = User(self.valid_username)
        user.add_credit_card(self.valid_card)
        self.assertEqual(user.credit_card_number, self.valid_card)
        
    def test_add_invalid_credit_card(self):
        """Test adding an invalid credit card raises exception"""
        user = User(self.valid_username)
        with self.assertRaises(CreditCardException):
            user.add_credit_card(self.invalid_card)
    
    def test_add_multiple_credit_cards(self):
        """Test that adding a second credit card raises exception"""
        user = User(self.valid_username)
        user.add_credit_card(self.valid_card)
        with self.assertRaises(CreditCardException):
            user.add_credit_card(self.valid_card)
            
    def test_add_to_balance(self):
        """Test adding to user's balance"""
        user = User(self.valid_username)
        initial_balance = user.balance
        amount = 100.0
        user.add_to_balance(amount)
        self.assertEqual(user.balance, initial_balance + amount)
        
    def test_pay_with_sufficient_balance(self):
        """Test paying when balance is sufficient"""
        payer = User("Payer")
        receiver = User("Receiver")
        payer.add_to_balance(100.0)
        initial_payer_balance = payer.balance
        initial_receiver_balance = receiver.balance
        amount = 50.0
        
        payer.pay(receiver, amount, "Test payment")
        
        self.assertEqual(payer.balance, initial_payer_balance - amount)
        self.assertEqual(receiver.balance, initial_receiver_balance + amount)
        
    def test_pay_with_insufficient_balance(self):
        """Test paying when balance is insufficient (should use credit card)"""
        payer = User("Payer")
        receiver = User("Receiver")
        payer.add_credit_card(self.valid_card)
        payer.add_to_balance(10.0)
        amount = 50.0
        
        payment = payer.pay(receiver, amount, "Test payment")
        
        self.assertIsInstance(payment, Payment)
        self.assertEqual(receiver.balance, amount)
        
    def test_pay_with_insufficient_balance_no_card(self):
        """Test paying when balance is insufficient and no card is available"""
        payer = User("Payer")
        receiver = User("Receiver")
        payer.add_to_balance(10.0)
        
        with self.assertRaises(PaymentException):
            payer.pay(receiver, 50.0, "Test payment")
            
    def test_pay_negative_amount(self):
        """Test trying to pay a negative amount"""
        payer = User("Payer")
        receiver = User("Receiver")
        payer.add_to_balance(100.0)
        
        with self.assertRaises(PaymentException):
            payer.pay(receiver, -10.0, "Test payment")
            
    def test_pay_self(self):
        """Test trying to pay yourself"""
        user = User("SelfPayer")
        user.add_to_balance(100.0)
        
        with self.assertRaises(PaymentException):
            user.pay(user, 50.0, "Paying myself")
            
    def test_add_friend(self):
        """Test adding a friend"""
        user = User("User1")
        friend = User("Friend1")
        initial_friends_count = len(user.friends)
        
        user.add_friend(friend)
        
        self.assertEqual(len(user.friends), initial_friends_count + 1)
        self.assertTrue(any("User1 added Friend1 as a friend" in f for f in user.friends))
        
    def test_add_self_as_friend(self):
        """Test trying to add yourself as a friend"""
        user = User("User1")
        
        with self.assertRaises(ValueError):
            user.add_friend(user)
            
    def test_add_duplicate_friend(self):
        """Test adding the same friend twice (should not duplicate)"""
        user = User("User1")
        friend = User("Friend1")
        
        user.add_friend(friend)
        initial_friends_count = len(user.friends)
        
        # Try adding the same friend again
        user.add_friend(friend)
        
        # Friend count should not increase
        self.assertEqual(len(user.friends), initial_friends_count)


class TestMiniVenmo(unittest.TestCase):
    
    def setUp(self):
        self.venmo = MiniVenmo()
        self.test_balance = 50.0
        self.test_card = "4111111111111111"
        
    def test_create_user(self):
        """Test creating a user through MiniVenmo"""
        username = "TestUser"
        user = self.venmo.create_user(username, self.test_balance, self.test_card)
        
        self.assertEqual(user.username, username)
        self.assertEqual(user.balance, self.test_balance)
        self.assertEqual(user.credit_card_number, self.test_card)
        
    def test_render_feed(self):
        """Test rendering the feed (this only tests that it runs without error)"""
        bobby = self.venmo.create_user("Bobby", 100.0, self.test_card)
        carol = self.venmo.create_user("Carol", 50.0, self.test_card)
        
        bobby.pay(carol, 25.0, "Test payment")
        bobby.add_friend(carol)
        
        feed = bobby.retrieve_feed()
        try:
            self.venmo.render_feed(feed)
            # If we get here, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_feed raised exception {e}")
            
    def test_feed_contains_payments(self):
        """Test that feed contains payment entries"""
        bobby = self.venmo.create_user("Bobby", 100.0, self.test_card)
        carol = self.venmo.create_user("Carol", 50.0, self.test_card)
        
        bobby.pay(carol, 25.0, "Coffee")
        
        # Check sender's feed
        bobby_feed = bobby.retrieve_feed()
        self.assertTrue(any("Bobby paid Carol" in entry for entry in bobby_feed))
        
        # Check recipient's feed
        carol_feed = carol.retrieve_feed()
        self.assertTrue(any("Bobby paid Carol" in entry for entry in carol_feed))
        
    def test_feed_contains_friend_additions(self):
        """Test that feed contains friend addition entries"""
        bobby = self.venmo.create_user("Bobby", 100.0, self.test_card)
        carol = self.venmo.create_user("Carol", 50.0, self.test_card)
        
        bobby.add_friend(carol)
        
        bobby_feed = bobby.retrieve_feed()
        self.assertTrue(any("Bobby added Carol as a friend" in entry for entry in bobby_feed))
        
    def test_feed_format(self):
        """Test the format of feed entries"""
        bobby = self.venmo.create_user("Bobby", 100.0, self.test_card)
        carol = self.venmo.create_user("Carol", 50.0, self.test_card)
        
        bobby.pay(carol, 25.0, "Coffee")
        
        bobby_feed = bobby.retrieve_feed()
        payment_entry = next((entry for entry in bobby_feed if "paid" in entry), None)
        
        self.assertIsNotNone(payment_entry)
        self.assertEqual(payment_entry, "Bobby paid Carol $25.00 for Coffee")
        
    def test_direct_pay_with_balance(self):
        """Test direct use of pay_with_balance method"""
        payer = self.venmo.create_user("DirectPayer", 100.0, self.test_card)
        receiver = self.venmo.create_user("DirectReceiver", 0.0, self.test_card)
        
        initial_payer_balance = payer.balance
        initial_receiver_balance = receiver.balance
        amount = 30.0
        
        payment = payer.pay_with_balance(receiver, amount, "Direct balance payment")
        
        self.assertIsInstance(payment, Payment)
        self.assertEqual(payer.balance, initial_payer_balance - amount)
        self.assertEqual(receiver.balance, initial_receiver_balance + amount)
        
    def test_direct_pay_with_card(self):
        """Test direct use of pay_with_card method"""
        payer = self.venmo.create_user("CardPayer", 0.0, self.test_card)
        receiver = self.venmo.create_user("CardReceiver", 0.0, self.test_card)
        
        initial_receiver_balance = receiver.balance
        amount = 45.0
        
        payment = payer.pay_with_card(receiver, amount, "Direct card payment")
        
        self.assertIsInstance(payment, Payment)
        self.assertEqual(receiver.balance, initial_receiver_balance + amount)
        
    def test_payment_object_properties(self):
        """Test that the Payment object has the correct properties"""
        payer = self.venmo.create_user("PaymentTester", 100.0, self.test_card)
        receiver = self.venmo.create_user("PaymentReceiver", 0.0, self.test_card)
        amount = 42.0
        note = "Payment test"
        
        payment = payer.pay(receiver, amount, note)
        
        self.assertEqual(payment.amount, float(amount))
        self.assertEqual(payment.actor, payer)
        self.assertEqual(payment.target, receiver)
        self.assertEqual(payment.note, note)
        self.assertTrue(hasattr(payment, 'id'))
        self.assertIsInstance(payment.id, str)


if __name__ == '__main__':
    # Comment out the line below to run tests instead of the main application
    # MiniVenmo.run()
    
    # Run all tests
    unittest.main()