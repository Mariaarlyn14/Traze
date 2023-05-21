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
from kivymd.uix.button.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from map_Dijkstra import Dijkstra_Screen
from map_ACO import ACO_Screen
from kivymd.uix.list import ThreeLineIconListItem, MDList, IconLeftWidget
from kivy.uix.scrollview import ScrollView
import sqlite3
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivymd.uix.button import MDIconButton
import os

kv = Builder.load_file('DeliveryPerson.kv')


class ProfileCard (MDFloatLayout):
    pass
    
class ProfilePage_DeliveryPerson(Screen):
    def clear_login_info(self):
        file_path = "login.txt"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            pass

    def logout(self):
        self.clear_login_info()
        MDApp.get_running_app().root.current = 'LoginScreen'

class DeliveryPersonHomepage(Screen):
    
    def __init__(self, **kwargs):
        super(DeliveryPersonHomepage, self).__init__(**kwargs)
        self.addr_list = MDList()
        self.scrollview = ScrollView(pos_hint = {"center_x": 0.5, "y": 0.1}, size_hint_y = (0.8))
        self.scrollview.add_widget(self.addr_list)
        self.add_widget(self.scrollview)
        self.update_addr_list()
        
    def update_addr_list(self, *args):
        self.addr_list.clear_widgets()
        orders = self.get_list_from_database()
        for order in orders:
            #print(order)
            item = ThreeLineIconListItem(
                text=order['pu_addr'],
                secondary_text = order['cust_addr'],
                tertiary_text = order['item_name'],
                theme_text_color= 'Custom',
                text_color = (0, 0, 1, 1),
                secondary_theme_text_color = 'Custom',
                secondary_text_color = (1, 0, 0, 1),)
            icon = IconLeftWidget(icon = "map-marker-distance")
            item.add_widget(icon)
            item.item_name = order['item_name']
            item.origin_addr = order['pu_addr']
            item.dest_addr = order['cust_addr']
            item.bind(on_release=lambda item=item: self.on_item_press(item))
            self.addr_list.add_widget(item)
            
    def get_list_from_database(self):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute('SELECT * FROM CustomerList ORDER BY CASE WHEN category="Perishable" THEN 1 ELSE 2 END, CASE WHEN delivery_stat = "Delivered" THEN 3 ELSE 2 END DESC')
        orders = []
        for row in c.fetchall():
            orders.append({
                'cust_addr': row[4],
                'pu_addr': row[5],
                'item_name': row[3]
            })
        conn.close()
        return orders
    
    def on_item_press(self, item):
        app = MDApp.get_running_app()
        app.root.current = 'Delivery_Info'
        tracking_info_screen = app.root.get_screen('Delivery_Info')
        tracking_info_screen.load_delivery_info(item.item_name, item.origin_addr, item.dest_addr)
        #self.show_dijkstra_for_item(item)
        

class Delivery_Info(Screen):

    def load_delivery_info(self, item_name, origin_addr, dest_addr):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute("SELECT * FROM CustomerList WHERE item_name = ?", (item_name,))
        result = c.fetchone()
        print(result)
        
        if result:
            self.tracking_id = str(result[0])
            self.cust_name = str(result[1])
            self.pnum = str(result[2])
            self.item_name = str(result[3])
            self.origin = str(result[5])
            self.dest = str(result[4])
            
            conn = sqlite3.connect('test2.db')
            c = conn.cursor()
            c.execute("INSERT INTO MyLocation (tracking_id, origin_osmid, destination_osmid) VALUES (?,?,?)", (self.tracking_id, self.origin, self.dest))
            conn.commit()
            conn.close()
            
        else:
            toast('Invalid')
            
        self.update_labels()
        
    def clear_mylocation_table(self):
        conn = sqlite3.connect('test2.db')
        c = conn.cursor()
        c.execute("DELETE FROM MyLocation")
        conn.commit()
        conn.close()
        
    def on_back(self):
        self.clear_mylocation_table()
        app = MDApp.get_running_app()
        app.root.current = 'DeliveryPersonHomepage'
        
    
    def show_Dijkstra(self):
        toast("Please Wait...")
        
        self.data1 = sqlite3.connect(database = "test2.db")
        self.cursor1 = self.data1.cursor()
        records = self.cursor1.execute("SELECT * FROM MyLocation LIMIT 1").fetchall()
        for record in records:
            tracking_id = str(record[0])
        
        change_delstat = "Out For Delivery"
        est_t = "UPDATE TrackingList SET delivery_stat = ? WHERE tracking_id = ?"
        est_t1 = "UPDATE CustomerList SET delivery_stat = ? WHERE tracking_id = ?"
        self.cursor1.execute(est_t, (change_delstat, tracking_id))
        self.cursor1.execute(est_t1, (change_delstat, tracking_id))
        self.data1.commit()
        
    
    def goto_Dijkstra(self, app):
        app = MDApp.get_running_app()
    # Remove the Dijkstra_Screen if it already exists in the screen manager
        sm = self.manager
        if 'Dijkstra_Screen' in sm.screen_names:
            sm.remove_widget(sm.get_screen('Dijkstra_Screen'))
            
        dijkstra_screen = Dijkstra_Screen()
        sm.add_widget(dijkstra_screen, name='Dijkstra_Screen')
        if 'Dijkstra_Screen' in app.root.ids:
            app.root.remove_widget(app.root.ids['Dijkstra_Screen'])
    # Create a new Dijkstra_Screen and add it to the screen manager
        layout1 = DijkstraBackButton()
        DijkstraBrowser = Screen(name='Dijkstra_Screen')
        DijkstraBrowser.add_widget(Dijkstra_Screen())
        DijkstraBrowser.add_widget(layout1)
        app.root.add_widget(DijkstraBrowser)
    # Switch to the new Dijkstra_Screen
        app.root.current = 'Dijkstra_Screen'
        
    
    def goto_ACO(self, app):
        app = MDApp.get_running_app()
        sm = self.manager
        if 'ACO_Screen' in sm.screen_names:
            sm.remove_widget(sm.get_screen('ACO_Screen'))
            
        aco_screen = ACO_Screen()
        
        sm.add_widget(aco_screen, name='ACO_Screen')
        if 'ACO_Screen' in app.root.ids:
            app.root.remove_widget(app.root.ids['ACO_Screen'])
    # Create a new Dijkstra_Screen and add it to the screen manager
        layout2 = ACOBackButton()
        ACOBrowser = Screen(name='ACO_Screen')
        ACOBrowser.add_widget(ACO_Screen())
        ACOBrowser.add_widget(layout2)
        app.root.add_widget(ACOBrowser)
    # Switch to the new Dijkstra_Screen
        app.root.current = 'ACO_Screen'
        
    def Delivered(self, instance):
        self.conn = sqlite3.connect('test2.db')
        self.c = self.conn.cursor()

        records = self.c.execute("SELECT * FROM MyLocation LIMIT 1").fetchall()
        for record in records:
            tracking_id = str(record[0])
        #c.execute("SELECT * FROM CustomerList WHERE item_name = ?", (item_name,))
        change_delstat = "Delivered"
        query = "UPDATE TrackingList SET delivery_stat = ? WHERE tracking_id = ?"
        self.c.execute(query, (change_delstat, tracking_id))
        self.conn.commit()
        query1= "UPDATE CustomerList SET delivery_stat = ? WHERE tracking_id = ?"
        self.c.execute(query1, (change_delstat, tracking_id))
        self.conn.commit()
        self.conn.close()
        
        toast("Parcel has been Delivered...")
        
    def delivered_button_release(self, app):
        self.clear_mylocation_table()
        app = MDApp.get_running_app()
        app.root.current = "DeliveryPersonHomepage"
    
    def update_labels(self):
        layout = self.ids.tracking_info_layout
        layout.clear_widgets()
        
        layout.add_widget(MDLabel(text="Tracking No:  %s" %(self.tracking_id), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.55}))

        layout.add_widget(MDLabel(text="Customer Name:  %s" %(self.cust_name), font_style='Body1', size_hint_x=1.0, halign='left', pos_hint= {"x": 0.15, "y": 0.47}))

        layout.add_widget(MDLabel(text="Phone No:  %s" %(self.pnum), font_style='Body1', size_hint_x=1.0, halign='left', pos_hint= {"x": 0.15, "y": 0.39}))

        layout.add_widget(MDLabel(text="Item Name:  %s" %(self.item_name), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.31}))
        
        layout.add_widget(MDLabel(text="Origin:  %s" %(self.origin), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.23}))
        
        layout.add_widget(MDLabel(text="Destination:  %s" %(self.dest), font_style='Body1', size_hint_x=0.8, halign='left', pos_hint= {"x": 0.15, "y": 0.15}))
    
        Dijkstra_button = MDRaisedButton(text="View Route", md_bg_color= (0, 0, 0, 1), font_size= "13sp", size_hint= (0.62, 0.09), pos_hint= {"center_x": 0.7, "center_y": 0.45})
        Dijkstra_button.bind(on_press = lambda instance: toast("Please Wait", self.show_Dijkstra()))
        Dijkstra_button.bind(on_release= self.goto_Dijkstra)
        layout.add_widget(Dijkstra_button)
        
        ACO_button = MDRaisedButton(text="View Other Route", md_bg_color= (0, 0, 0, 1), font_size= "13sp", size_hint= (0.62, 0.09), pos_hint= {"center_x": 0.7, "center_y": 0.33})
        ACO_button.bind(on_release = self.goto_ACO)
        layout.add_widget(ACO_button)
        
        Delivered_button = MDRaisedButton(text="Delivered", md_bg_color= (0, 0, 0, 1), font_size= "13sp", size_hint= (0.62, 0.09), pos_hint= {"center_x": 0.7, "center_y": 0.21})
        Delivered_button.bind(on_press = self.Delivered)
        Delivered_button.bind(on_release = self.delivered_button_release)
        layout.add_widget(Delivered_button)
        
        
class DijkstraBackButton(BoxLayout):
    def __init__(self, **kwargs):
        super(DijkstraBackButton, self).__init__(**kwargs)
        self.browser_widget1 = Dijkstra_Screen()
        self.size_hint = (1, None)
        self.height = Window.height*0.1
        self.padding = (20, 0)
        self.spacing = 20
        self.create_widgets()

    def create_widgets(self):
        back_button = MDIconButton(icon='arrow-left', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                   pos_hint={'center_y': 0.5}, md_bg_color=(0, 0, 0, 1), on_release= self.go_back)
        self.add_widget(back_button)

    def go_back(self, *args):
        self.parent.parent.current = 'Delivery_Info'
        
        
class ACOBackButton(BoxLayout):
    def __init__(self, **kwargs):
        super(ACOBackButton, self).__init__(**kwargs)
        self.browser_widget1 = ACO_Screen()
        self.size_hint = (1, None)
        self.height = Window.height*0.1
        self.padding = (20, 0)
        self.spacing = 20
        self.create_widgets()

    def create_widgets(self):
        back_button = MDIconButton(icon='arrow-left', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                            pos_hint={'center_y': 0.5}, md_bg_color=(0, 0, 0, 1), on_release= self.go_back)
        self.add_widget(back_button)

    def go_back(self, *args):
        self.parent.parent.current = 'Delivery_Info'
        

class DeliveryPersonPage(MDApp):
    
    dialog = None
    
    def build(self):
        sm = ScreenManager()
        self.deliveryperson_homepage = DeliveryPersonHomepage (name= 'DeliveryPersonHomepage')
        sm.add_widget(self.deliveryperson_homepage)
        sm.add_widget(ProfilePage_DeliveryPerson(name= 'ProfilePage_DeliveryPerson'))
        sm.add_widget(Delivery_Info(name='Delivery_Info'))
        
        layout1 = DijkstraBackButton()
        DijkstraBrowser = Screen(name = 'Dijkstra_Screen')
        DijkstraBrowser.add_widget(Dijkstra_Screen())
        DijkstraBrowser.add_widget(layout1)
        sm.add_widget(DijkstraBrowser)
        
        layout2 = ACOBackButton()
        ACOBrowser = Screen(name = 'ACO_Screen')
        ACOBrowser.add_widget(ACO_Screen())
        ACOBrowser.add_widget(layout2)
        sm.add_widget(ACOBrowser)
        
        layout3 = BoxLayout(orientation='vertical')
        layout3.add_widget(Dijkstra_Screen())
        
        return sm
    
    
    def on_start(self):
    # Schedule an update of the tracking info every 5 seconds
        Clock.schedule_interval(self.deliveryperson_homepage.update_addr_list, 5)
    

if __name__ == "__main__":
    DeliveryPersonPage().run()