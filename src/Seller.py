from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.toast import toast
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.list import OneLineIconListItem, MDList, IconLeftWidget
from kivy.uix.scrollview import ScrollView
import sqlite3
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
import os

Builder.load_file('Seller.kv')


class SellerHomepage(Screen):
    def __init__(self, **kwargs):
        super(SellerHomepage, self).__init__(**kwargs)
        self.cust_list = MDList()
        self.scrollview = ScrollView(pos_hint = {"center_x": 0.5, "y": 0.2}, size_hint_y = (0.7))
        self.scrollview.add_widget(self.cust_list)
        self.add_widget(self.scrollview)
        self.update_cust_list()
        
    def update_cust_list(self, *args):
        self.cust_list.clear_widgets()
        orders = self.get_orders_from_database()
        for order in orders:
            item = OneLineIconListItem(
                text=order['cust_name'],)
            icon = IconLeftWidget(icon = "menu")
            item.add_widget(icon)
            item.cust_name = order['cust_name']
            item.bind(on_release=lambda item=item: self.on_item_press(item))
            self.cust_list.add_widget(item)
            
    def get_orders_from_database(self):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute('SELECT * FROM CustomerList')
        orders = []
        for row in c.fetchall():
            orders.append({
                'cust_name': row[1]})
        conn.close()
        return orders
    
    def on_item_press(self, item):
        app = MDApp.get_running_app()
        app.root.current = 'Customer_Info'
        tracking_info_screen = app.root.get_screen('Customer_Info')
        tracking_info_screen.load_cust_info(item.cust_name)
        
class Customer_Page(Screen):
    pass
    

class ProfileCard (MDFloatLayout):
    pass

class SellerPage(MDApp):
    
    dialog = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def build(self):
        sm = ScreenManager()
        self.seller_homepage = SellerHomepage(name= 'SellerHomepage')
        sm.add_widget(self.seller_homepage)
        sm.add_widget(Customer_Info(name= 'Customer_Info'))
        sm.add_widget(ProfilePage_Seller(name= 'ProfilePage_Seller'))
        sm.add_widget(Add_Customer(name= 'Add_Customer'))
        return sm
    
    def on_start(self):
    # Schedule an update of the tracking info every 5 seconds
        Clock.schedule_interval(self.seller_homepage.update_cust_list, 5)
    
class Customer_Info(Screen):
    
    def load_cust_info(self, cust_name):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute("SELECT * FROM CustomerList WHERE cust_name = ?", (cust_name,))
        result = c.fetchone()
        print(result)
        
        if result:
            self.cust_name = str(result[1])
            self.tracking_id = str(result[0])
            self.delivery_stat = str(result[8])
            self.cust_addr = str(result[4])
            self.pnum = str(result[2])
            self.item_name = str(result[3])
            self.date_order = str(result[6])
            
        else:
            toast('Something went wrong')
            
        self.update_labels()
    
    def update_labels(self):
        layout = self.ids.tracking_info_layout
        layout.clear_widgets()
        
        layout.add_widget(MDLabel(text="Name:  %s" %(self.cust_name), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.55}))

        layout.add_widget(MDLabel(text="Tracking No:  %s" %(self.tracking_id), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.47}))

        layout.add_widget(MDLabel(text="Item Name:  %s" %(self.item_name), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.39}))

        layout.add_widget(MDLabel(text="Address:  %s" %(self.cust_addr), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.31}))
        
        layout.add_widget(MDLabel(text="Phone No:  %s" %(self.pnum), font_style='Body1', size_hint_x=0.9, halign='left', pos_hint= {"x": 0.15, "y": 0.23}))
        
        layout.add_widget(MDLabel(text="Date of Order:  %s" %(self.date_order), font_style='Body1', size_hint_x=0.9, halign='left', pos_hint= {"x": 0.15, "y": 0.15}))
        
        layout.add_widget(MDLabel(text="Delivery Status:  %s"  %(self.delivery_stat), font_style='Body2', size_hint_x=1.0, halign='left', pos_hint= {"x": 0.15, "y": 0.07}))

class Add_Customer(Screen):
    dialog = None
    obj = ObjectProperty(None)
    obj_text = StringProperty("")
        
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect(database = "test2.db")
        self.cursor = self.conn.cursor()

    def select(self):
        print(self.ids.category.text)
        
    def add_customer(self, cust_name, cust_phone, item_name, cust_addr,  pu_addr, date_order, category, delivery_stat, eta):
        seller_q = """INSERT INTO CustomerList (cust_name, cust_phone, item_name, cust_addr, pu_addr, date_order, category, delivery_stat, eta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        seller_values = (cust_name, cust_phone, item_name, cust_addr, pu_addr, date_order, category, delivery_stat, eta)
        self.cursor.execute(seller_q, seller_values)
        self.conn.commit()
        return True
        
    def AddCustomer_btn(self):
        cust_name = self.ids.cust_name.text
        cust_phone = self.ids.cust_phone.text
        item_name = self.ids.item_name.text
        cust_addr = self.ids.cust_addr.text
        pu_addr = self.ids.pu_addr.text
        date_order = self.ids.date_order.text
        category = self.ids.category.text
        delivery_stat = "Pending"
        eta = "Pending"
        add_customer = self.add_customer(cust_name, cust_phone, item_name, cust_addr, pu_addr, date_order, category, delivery_stat, eta)
        if add_customer:
            self.reset()
            toast('Customer Added Successfully')
        if not add_customer:
            toast('Adding Customer Failed. Try Again')

    def reset(self):
        self.ids.cust_name.text = ""
        self.ids.cust_phone.text = ""
        self.ids.item_name.text = ""
        self.ids.cust_addr.text = ""
        self.ids.pu_addr.text = ""
        self.ids.date_order.text = ""
        self.ids.category.text = ""
    
class ProfilePage_Seller(Screen):

    def clear_login_info(self):
        file_path = "login.txt"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            pass

    def logout(self):
        self.clear_login_info()
        MDApp.get_running_app().root.current = 'LoginScreen'

if __name__ == "__main__":
    SellerPage().run()