from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivymd.uix.button.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
import sqlite3
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import ThreeLineIconListItem, MDList, IconLeftWidget
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from first import fScreen
import os

kv = Builder.load_file('Customer.kv')
conn = sqlite3.connect(database = "test2.db")
cursor = conn.cursor()

class CustomerHomepage(Screen):
    def __init__(self, **kwargs):
        super(CustomerHomepage, self).__init__(**kwargs)
        self.tracking_list = MDList()
        self.scrollview = ScrollView(pos_hint = {"center_x": 0.5, "y": 0.2}, size_hint_y = (0.7))
        self.scrollview.add_widget(self.tracking_list)
        self.add_widget(self.scrollview)
        self.update_tracking_info()
        
    def update_tracking_info(self, *args):
        self.tracking_list.clear_widgets()
        orders = self.get_orders_from_database()
        for order in orders:
            item = ThreeLineIconListItem(
                text=order['item_name'],
                secondary_text=str(order['tracking_id']),
                tertiary_text=order['delivery_stat'],
                theme_text_color= 'Custom',
                text_color = (0, 0, 0, 1),
                secondary_theme_text_color = 'Custom',
                secondary_text_color = (1, 0, 0, 1),
                tertiary_theme_text_color = 'Custom',
                tertiary_text_color = (0, 0, 1, 1),)
            icon = IconLeftWidget(icon = "truck-fast")
            item.add_widget(icon)
            item.tracking_id = order['tracking_id']
            item.bind(on_release=lambda item=item: self.on_item_press(item))
            self.tracking_list.add_widget(item)
            #print(order)
    
    def get_orders_from_database(self):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute('SELECT * FROM TrackingList')
        orders = []
        for row in c.fetchall():
            orders.append({
                'tracking_id': row[0],
                'item_name': row[1],
                'delivery_stat': row[4]
            })
        conn.close()
        return orders
    
    def on_item_press(self, item):
        app = MDApp.get_running_app()
        app.root.current = 'Tracking_Info'
        tracking_info_screen = app.root.get_screen('Tracking_Info')
        tracking_info_screen.load_tracking_info(item.tracking_id)

class ProfileCard (MDFloatLayout):
    pass

class CustomerPage(MDApp):
    
    dialog = None
    
    def build(self):
        sm = ScreenManager()
        self.customer_homepage = CustomerHomepage(name= 'CustomerHomepage')
        sm.add_widget(self.customer_homepage)
        sm.add_widget(CustomerHomepage(name= 'CustomerHomepage'))
        sm.add_widget(ProfilePage_Customer(name= 'ProfilePage_Customer'))
        sm.add_widget(ContentAdd(name= 'ContentAdd'))
        sm.add_widget(Tracking_Info(name= 'Tracking_Info'))
        sm.add_widget(fScreen(name = 'fScreen'))
        
        return sm
    
    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Tracking No.",
                type="custom",
                size_hint= [0.8, 0.8],
                content_cls= ContentAdd())
            self.dialog.open()
    
    def on_start(self):
    # Schedule an update of the tracking info every 5 seconds
        Clock.schedule_interval(self.customer_homepage.update_tracking_info, 5)

class ContentAdd(Screen):
        
    def track_btn(self):
        track_trackingID = self.ids.track_trackingID.text
        query = ("INSERT INTO TrackingList(item_name, delivery_stat, tracking_id, cust_addr, pu_addr, delivery_stat) SELECT item_name, delivery_stat, tracking_id, cust_addr, pu_addr, delivery_stat FROM CustomerList where tracking_id = ('%s')" %(track_trackingID))
        cursor.execute(query)
        conn.commit()
            
        if cursor.rowcount > 0:
            self.reset()
            toast('Tracking No. has been added')
        else:
            self.reset()
            toast('Tracking No. does not exist')
            
    def reset(self):
        self.ids.track_trackingID.text = ""

class Tracking_Info(Screen):
        
    def load_tracking_info(self, tracking_id):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute("SELECT * FROM TrackingList WHERE tracking_id = ?", (tracking_id,))
        result = c.fetchone()
        #print(result)
        
        if result is not None:
            self.item_name = str(result[1])
            self.tracking_id = str(result[0])
            self.delivery_stat = str(result[4])
            self.pu_addr = str(result[3])
            self.cust_addr = str(result[2])
            self.eta = str(result[5])
            
        else:
            toast('Invalid tracking ID')
            
        self.update_labels()
        
    def update_labels(self):
        layout = self.ids.tracking_info_layout
        layout.clear_widgets()
        
        layout.add_widget(MDLabel(text="Tracking ID:  %s" %(self.tracking_id), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.5}))

        layout.add_widget(MDLabel(text="Delivery Status:  %s" %(self.delivery_stat), font_style='Body2', size_hint_x=1.0, halign='left', pos_hint= {"x": 0.15, "y": 0.4}))

        layout.add_widget(MDLabel(text="Origin:  %s" %(self.pu_addr), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.3}))

        layout.add_widget(MDLabel(text="Destination:  %s" %(self.cust_addr), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.2}))
        
        #layout.add_widget(MDLabel(text="Estimated Time of Arrival:", font_style='Body2', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.1}))
        #layout.add_widget(MDLabel(text=self.eta, font_style='Body2', size_hint_x=0.4, halign='right', pos_hint= {"x": 0.8, "y": 0.1}))
        
        layout.add_widget(MDLabel(text="Item:  %s" %(self.item_name), font_style='Body1', size_hint_x=0.4, halign='left', pos_hint= {"x": 0.15, "y": 0.1}))
    
class ProfilePage_Customer(Screen):
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
    CustomerPage().run()