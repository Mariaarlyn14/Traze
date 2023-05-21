from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from account import LoginScreen, RegisterAccountScreen
from first import fScreen
import sqlite3
from Customer import CustomerHomepage, ProfilePage_Customer, ContentAdd, Tracking_Info
from Seller import SellerHomepage, ProfilePage_Seller, Customer_Info, Add_Customer
from DeliveryPerson import (
    DeliveryPersonHomepage, Delivery_Info, ProfilePage_DeliveryPerson,
    Dijkstra_Screen, ACO_Screen, DijkstraBackButton, ACOBackButton
)
from map_Dijkstra import Dijkstra_Screen
from map_ACO import ACO_Screen


class MainApp(MDApp):
    dialog = None
    paused_screen = None  # Set the initial screen here

    def build(self):
        sm = ScreenManager()
        sm.add_widget(fScreen(name='fScreen'))
        sm.add_widget(LoginScreen(name='LoginScreen'))
        sm.add_widget(RegisterAccountScreen(name='RegisterAccountScreen'))
        self.customer_homepage = CustomerHomepage(name='CustomerHomepage')
        sm.add_widget(self.customer_homepage)
        sm.add_widget(ProfilePage_Customer(name='ProfilePage_Customer'))
        sm.add_widget(ContentAdd(name='ContentAdd'))
        self.seller_homepage = SellerHomepage(name='SellerHomepage')
        sm.add_widget(self.seller_homepage)
        sm.add_widget(Add_Customer(name='Add_Customer'))
        sm.add_widget(Customer_Info(name='Customer_Info'))
        sm.add_widget(Tracking_Info(name='Tracking_Info'))
        sm.add_widget(ProfilePage_Seller(name='ProfilePage_Seller'))
        self.deliveryperson_homepage = DeliveryPersonHomepage(name='DeliveryPersonHomepage')
        sm.add_widget(self.deliveryperson_homepage)
        sm.add_widget(ProfilePage_DeliveryPerson(name='ProfilePage_DeliveryPerson'))
        sm.add_widget(Delivery_Info(name='Delivery_Info'))
        sm.add_widget(Dijkstra_Screen(name='Dijkstra_Screen'))
        sm.add_widget(ACO_Screen(name='ACO_Screen'))

        layout1 = DijkstraBackButton()
        DijkstraBrowser = Screen(name='Dijkstra_Screen')
        DijkstraBrowser.add_widget(Dijkstra_Screen())
        DijkstraBrowser.add_widget(layout1)
        sm.add_widget(DijkstraBrowser)

        layout2 = ACOBackButton()
        ACOBrowser = Screen(name='ACO_Screen')
        ACOBrowser.add_widget(ACO_Screen())
        ACOBrowser.add_widget(layout2)
        sm.add_widget(ACOBrowser)

        return sm

    def on_start(self):
        sm = self.root
        if self.paused_screen is None:
            username = self.load_login_info()
            if username is not None:
                role = self.get_user_role(username)
                if role == 'Customer':
                    sm.current = 'CustomerHomepage'
                elif role == 'Seller':
                    sm.current = 'SellerHomepage'
                elif role == 'Delivery Person':
                    sm.current = 'DeliveryPersonHomepage'
        else:
            sm.current = self.paused_screen

        Clock.schedule_interval(self.customer_homepage.update_tracking_info, 5)
        Clock.schedule_interval(self.seller_homepage.update_cust_list, 5)
        Clock.schedule_interval(self.deliveryperson_homepage.update_addr_list, 5)

    def on_pause(self):
        sm = self.root
        if sm.current != 'fScreen':
            self.paused_screen = sm.current
        return True

    def on_resume(self):
        sm = self.root
        if self.paused_screen is not None:
            sm.current = self.paused_screen
        else:
            username = self.load_login_info()
            if username is not None:
                role = self.get_user_role(username)
                if role == 'Customer':
                    sm.current = 'CustomerHomepage'
                elif role == 'Seller':
                    sm.current = 'SellerHomepage'
                elif role == 'Delivery Person':
                    sm.current = 'DeliveryPersonHomepage'
            else:
                sm.current = 'fScreen'

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

    def get_user_role(self, username):
        # Assuming you have a function to fetch the user's role from the database
        # Modify this function as per your database structure and access method
        # Example:
        conn = sqlite3.connect(database="test2.db")
        cursor = conn.cursor()
        query = "SELECT role FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0]
        else:
            return None


if __name__ == '__main__':
    app = MainApp()
    app.run()