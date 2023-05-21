from kivy.lang import Builder
from kivymd.app import MDApp
import sqlite3
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from Customer import CustomerHomepage
from Seller import SellerHomepage
from DeliveryPerson import DeliveryPersonHomepage


account_kv = Builder.load_file('account.kv')

class RegisterAccountScreen(Screen):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect(database="test2.db")
        self.cursor = self.conn.cursor()

    def select(self):
        print(self.ids.user.text)
    
    def create_user(self, fullname, username, email, phone, address, password, role):
        sql = "INSERT INTO users (fullname, username, email, phone, address, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)"
        values = (fullname, username, email, phone, address, password, role)
        self.cursor.execute(sql, values)
        self.conn.commit()
        return True
    
    def register_btn_click(self):
        fullname = self.ids.fullname.text
        username = self.ids.username.text
        email = self.ids.email.text
        phone = self.ids.phone.text
        address = self.ids.address.text
        password = self.ids.password.text
        role = self.ids.role.text
        create_user = self.create_user(fullname, username, email, phone, address, password, role)
        if create_user:
            self.reset()
            toast('user account created successfully')
        if not create_user:
            toast('account not created')
            
    def reset(self):
        self.ids.fullname.text = ""
        self.ids.username.text = ""
        self.ids.email.text = ""
        self.ids.phone.text = ""
        self.ids.address.text = ""
        self.ids.password.text = ""


class LoginScreen(Screen):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect(database="test2.db")
        self.cursor = self.conn.cursor()

    def store_login_info(self, username):
        with open("login.txt", "w") as file:
            file.write(username)

    def load_login_info(self):
        try:
            with open("login.txt", "r") as file:
                username = file.read()
                return username.strip()
        except FileNotFoundError:
            return None

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(query, (username,))
        user = self.cursor.fetchone()

        if user is None:
            return False

        stored_password = user[6]

        if password == stored_password:
            return True
        else:
            return False

    def user_login(self):
        username = self.ids.login_username.text
        password = self.ids.login_password.text
        login = self.login(username, password)

        if login:
            self.reset()
            query = "SELECT role FROM users where username = ?"
            self.cursor.execute(query, (username,))
            role = self.cursor.fetchone()[0]

            if role == 'Customer':
                self.manager.current = 'CustomerHomepage'

            if role == 'Seller':
                self.manager.current = 'SellerHomepage'

            if role == 'Delivery Person':
                self.manager.current = 'DeliveryPersonHomepage'

            self.store_login_info(username)  # Store the login info
        else:
            toast('You have entered wrong user credentials')

    def reset(self):
        self.ids.login_username.text = ""
        self.ids.login_password.text = ""

    def on_pre_enter(self):
        # Check if there is a logged-in user and navigate to the corresponding screen
        username = self.load_login_info()
        if username is not None:
            query = "SELECT role FROM users where username = ?"
            self.cursor.execute(query, (username,))
            role = self.cursor.fetchone()[0]

            if role == 'Customer':
                self.manager.current = 'CustomerHomepage'

            if role == 'Seller':
                self.manager.current = 'SellerHomepage'

            if role == 'Delivery Person':
                self.manager.current = 'DeliveryPersonHomepage'
        else:
            self.manager.current = 'LoginScreen'


class MainApp(MDApp):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(CustomerHomepage(name='CustomerHomepage'))
        sm.add_widget(SellerHomepage(name='SellerHomepage'))
        sm.add_widget(DeliveryPersonHomepage(name='DeliveryPersonHomepage'))

        return sm
