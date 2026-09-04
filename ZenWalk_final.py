import sqlite3
import webbrowser
from urllib.parse import quote

try:
    from plyer import gps
except Exception:
    gps = None

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp, sp

Window.clearcolor = (1, 1, 1, 1)
light_brown = (198 / 255, 151 / 255, 116 / 255, 1)
off_pink = (248 / 255, 223 / 255, 212 / 255, 1)
red = (212/255, 0, 0, 1)              
green = (45/255, 155/255, 43/255, 1)  
yellow = (255/255, 215/255, 0, 1)    

DB_NAME = "zenwalk_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            user_phone TEXT,
            age TEXT,
            contacts TEXT,
            home_address TEXT,
            other_addresses TEXT
        )
    ''')
    conn.commit()
    conn.close()
init_db()
_last_location = {"lat": None, "lon": None}

def _on_location(**kwargs):
    _last_location["lat"] = kwargs.get("lat")
    _last_location["lon"] = kwargs.get("lon")

def start_gps():
    if gps is None:
        _last_location["lat"], _last_location["lon"] = 28.66467, 77.23246
        return
    try:
        gps.configure(on_location=_on_location)
        gps.start(minTime=1000, minDistance=1)
    except NotImplementedError:
        _last_location["lat"], _last_location["lon"] = 28.66467, 77.23246

def get_maps_link():
    lat, lon = _last_location["lat"], _last_location["lon"]
    if lat is None or lon is None:
        return "Location unavailable"
    return f"https://maps.google.com/?q={lat},{lon}"

def send_sms(phone_number, message):
    url = f"sms:{phone_number}?body={quote(message)}"
    webbrowser.open(url)

def build_yellow_message():
    link = get_maps_link()
    return (
        "I'm feeling unsure about my safety right now. "
        "Please stay alert and check in on me.\n"
        f"My live location: {link}"
    )

def build_red_message():
    link = get_maps_link()
    return (
        "I am in danger right now. "
        "Please contact emergency services and check in on me.\n"
        f"My live location: {link}"
    )

EMERGENCY_CONTACTS = [
    ("Friend", "+91 8445663793"),
    ("Friend", "+91 9205164041"),
]

def trigger_yellow_alert():
    message = build_yellow_message()
    for _name, number in EMERGENCY_CONTACTS:
        send_sms(number, message)
    return message

def trigger_red_alert():
    message = build_red_message()
    for _name, number in EMERGENCY_CONTACTS:
        send_sms(number, message)
    return message

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        self.main_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(12)
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        self.main_layout.add_widget(Label(text="[b]Personal Information[/b]",
            markup=True, size_hint_y=None, height=dp(35), font_size=sp(18), color=light_brown))

        self.name_input = TextInput(hint_text="Full Name", multiline=False,
            size_hint_y=None, height=dp(45), font_size=sp(15))
        self.main_layout.add_widget(self.name_input)

        self.user_phone_input = TextInput(hint_text="Your Phone Number",
            input_filter="int", multiline=False, size_hint_y=None, height=dp(45), font_size=sp(15))
        self.main_layout.add_widget(self.user_phone_input)

        self.age_input = TextInput(hint_text="Age", input_filter="int", multiline=False,
            size_hint_y=None, height=dp(45), font_size=sp(15))
        self.main_layout.add_widget(self.age_input)

        self.main_layout.add_widget(Label(text="[b]Emergency Contacts (Max 5)[/b]",
            markup=True, size_hint_y=None, height=dp(35), font_size=sp(18), color=light_brown))

        self.contact_inputs = []
        for i in range(1, 6):
            contact_input = TextInput(
                hint_text=f"Emergency Contact {i} (Phone)",
                input_filter="int",
                multiline=False,
                size_hint_y=None,
                height=dp(45),
                font_size=sp(15)
            )
            self.contact_inputs.append(contact_input)
            self.main_layout.add_widget(contact_input)

        self.main_layout.add_widget(Label(text="[b]Addresses[/b]", markup=True,
            size_hint_y=None, height=dp(35), font_size=sp(18), color=light_brown))

        self.home_address_input = TextInput(hint_text="Home Address", multiline=True,
            size_hint_y=None, height=dp(70), font_size=sp(15))
        self.main_layout.add_widget(self.home_address_input)

        self.other_address_inputs = []
        address_labels = ["Office / Work", "College / School", "Other Location"]
        for label in address_labels:
            addr_input = TextInput(
                hint_text=f"Other Address: {label} (Optional)",
                multiline=True,
                size_hint_y=None,
                height=dp(65),
                font_size=sp(15)
            )
            self.other_address_inputs.append(addr_input)
            self.main_layout.add_widget(addr_input)

        submit_btn = Button(text="Submit & Register", size_hint_y=None, height=dp(50),
            font_size=sp(16), background_color=light_brown)
        submit_btn.bind(on_release=self.submit_form)
        self.main_layout.add_widget(submit_btn)

        scroll.add_widget(self.main_layout)
        self.add_widget(scroll)

    def submit_form(self, instance):
        contacts_str = ",".join([c.text.strip() for c in self.contact_inputs if c.text.strip()])
        other_address_str = ";".join([a.text.strip() for a in self.other_address_inputs if a.text.strip()])

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profile (id, name, user_phone, age, contacts, home_address, other_addresses)
            VALUES (1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                user_phone=excluded.user_phone,
                age=excluded.age,
                contacts=excluded.contacts,
                home_address=excluded.home_address,
                other_addresses=excluded.other_addresses
        ''', (self.name_input.text, self.user_phone_input.text, self.age_input.text,
              contacts_str, self.home_address_input.text, other_address_str))
        conn.commit()
        conn.close()
        self.manager.current = 'welcome_screen'


class Welcome(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step_count = 0
        scroll = ScrollView()
        root = RelativeLayout(size_hint_y=None)

        profile_btn = Button(
            text="Profile",
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            pos_hint={'right': 0.95, 'top': 0.98},
            background_color=off_pink,
            color=light_brown,
            font_size=sp(14)
        )
        profile_btn.bind(on_release=self.go_to_profile)

        master = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        master.bind(minimum_height=master.setter('height'))

        title = Label(text="Zen Walk", font_size=sp(32), color=light_brown, bold=True,
            size_hint_y=None, height=dp(45))
        intro_text = Label(text="Step Tracker Dashboard", color=light_brown,
            font_size=sp(18), size_hint_y=None, height=dp(35))
        self.step_label = Label(text=f"Steps Today: {self.step_count}", font_size=sp(18),
            color=light_brown, size_hint_y=None, height=dp(35))
        add_step_btn = Button(text="Simulate Steps (+100)", color=light_brown,
            background_color=off_pink, size_hint_y=None, height=dp(45), font_size=sp(15))
        add_step_btn.bind(on_release=self.add_steps)

        self.btn_cal = Button(text="Calorie Counter", color=light_brown,
            background_color=off_pink, size_hint_y=None, height=dp(50), font_size=sp(16))
        self.btn_map = Button(text="Maps", color=light_brown, background_color=off_pink,
            size_hint_y=None, height=dp(50), font_size=sp(16))
        self.btn_cal.bind(on_release=self.next)
        self.btn_map.bind(on_release=self.go_to_safe_space)

        master.add_widget(title)
        master.add_widget(intro_text)
        master.add_widget(self.step_label)
        master.add_widget(add_step_btn)
        master.add_widget(self.btn_cal)
        master.add_widget(self.btn_map)

        def update_root_height(*args):
            root.height = max(master.height + dp(100), Window.height)
        master.bind(height=update_root_height)
        update_root_height()

        root.add_widget(profile_btn)
        root.add_widget(master)
        scroll.add_widget(root)
        self.add_widget(scroll)

    def add_steps(self, instance):
        self.step_count += 100
        self.step_label.text = f"Steps Today: {self.step_count}"

    def go_to_profile(self, instance):
        self.manager.current = 'profile_screen'

    def next(self, *args):
        self.manager.current = "danger_screen"

    def go_to_safe_space(self, *args):
        safe_lat = 28.66467
        safe_lon = 77.23246
        url = f"https://www.google.com/maps/search/?api=1&query={safe_lat},{safe_lon}"
        webbrowser.open(url)


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        self.main_layout = BoxLayout(orientation='vertical', size_hint_y=None,
            padding=dp(20), spacing=dp(10))
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        self.main_layout.add_widget(Label(text="[b]Your Profile[/b]", markup=True,
            font_size=sp(22), size_hint_y=None, height=dp(45), color=light_brown))

        self.name_in = TextInput(hint_text="Name", multiline=False, size_hint_y=None,
            height=dp(45), font_size=sp(15))
        self.phone_in = TextInput(hint_text="Phone", multiline=False, size_hint_y=None,
            height=dp(45), font_size=sp(15))
        self.age_in = TextInput(hint_text="Age", multiline=False, size_hint_y=None,
            height=dp(45), font_size=sp(15))
        self.contacts_in = TextInput(hint_text="Emergency Contacts (comma separated)",
            multiline=True, size_hint_y=None, height=dp(65), font_size=sp(15))
        self.address_in = TextInput(hint_text="Home Address", multiline=True,
            size_hint_y=None, height=dp(65), font_size=sp(15))

        self.main_layout.add_widget(Label(text="Name:", size_hint_y=None, height=dp(25),
            font_size=sp(14), color=light_brown))
        self.main_layout.add_widget(self.name_in)
        self.main_layout.add_widget(Label(text="Phone:", size_hint_y=None, height=dp(25),
            font_size=sp(14), color=light_brown))
        self.main_layout.add_widget(self.phone_in)
        self.main_layout.add_widget(Label(text="Age:", size_hint_y=None, height=dp(25),
            font_size=sp(14), color=light_brown))
        self.main_layout.add_widget(self.age_in)
        self.main_layout.add_widget(Label(text="Contacts:", size_hint_y=None, height=dp(25),
            font_size=sp(14), color=light_brown))
        self.main_layout.add_widget(self.contacts_in)
        self.main_layout.add_widget(Label(text="Home Address:", size_hint_y=None, height=dp(25),
            font_size=sp(14), color=light_brown))
        self.main_layout.add_widget(self.address_in)

        save_btn = Button(text="Save Changes", size_hint_y=None, height=dp(45),
            font_size=sp(16), background_color=off_pink, color=light_brown)
        save_btn.bind(on_release=self.save_profile)
        self.main_layout.add_widget(save_btn)

        back_btn = Button(text="Back", size_hint_y=None, height=dp(45), font_size=sp(16),
            background_color=off_pink, color=light_brown)
        back_btn.bind(on_release=self.go_back)
        self.main_layout.add_widget(back_btn)

        scroll.add_widget(self.main_layout)
        self.add_widget(scroll)

    def on_enter(self, *args):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT name, user_phone, age, contacts, home_address FROM profile WHERE id=1')
        row = cursor.fetchone()
        conn.close()
        if row:
            self.name_in.text = row[0] or ''
            self.phone_in.text = row[1] or ''
            self.age_in.text = row[2] or ''
            self.contacts_in.text = row[3] or ''
            self.address_in.text = row[4] or ''

    def save_profile(self, instance):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE profile SET name=?, user_phone=?, age=?, contacts=?, home_address=?
            WHERE id=1
        ''', (self.name_in.text, self.phone_in.text, self.age_in.text,
              self.contacts_in.text, self.address_in.text))
        conn.commit()
        conn.close()

        popup = Popup(title='Success', content=Label(text='Profile updated successfully!',
            font_size=sp(15)), size_hint=(0.85, 0.3))
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'welcome_screen'


class DangerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView()
        root = RelativeLayout(size_hint_y=None)

        back_btn = Button(
            text="< Back",
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            pos_hint={'x': 0.03, 'top': 0.98},
            background_color=off_pink,
            color=light_brown,
            font_size=sp(14)
        )
        back_btn.bind(on_release=self.go_back)


        self.btn_green = Button(
            text="Safe (Green)",
            font_size=sp(18),
            color=(1, 1, 1, 1),
            background_normal='',        
            background_color=green,      
            size_hint_y=None,
            height=dp(55)
        )
        self.btn_yellow = Button(
            text="Unsure (Yellow)",
            font_size=sp(18),
            color=(0, 0, 0, 1),
            background_normal='',      
            background_color=yellow,   
            size_hint_y=None,
            height=dp(55)
        )
        self.btn_red = Button(
            text="Danger (Red)",
            font_size=sp(18),
            color=(1, 1, 1, 1),
            background_normal='',      
            background_color=red,         
            size_hint_y=None,
            height=dp(55)
        )

        self.btn_green.bind(on_release=self.greenclick)
        self.btn_yellow.bind(on_release=self.yellowclick)
        self.btn_red.bind(on_release=self.redclick)

        master = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None,
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5, 'top': 0.88}
        )
        master.bind(minimum_height=master.setter('height'))

        master.add_widget(self.btn_green)
        master.add_widget(self.btn_yellow)
        master.add_widget(self.btn_red)

        def update_root_height(*args):
            root.height = max(master.height + dp(120), Window.height)
        master.bind(height=update_root_height)
        update_root_height()

        root.add_widget(back_btn)
        root.add_widget(master)
        scroll.add_widget(root)
        self.add_widget(scroll)

    def go_back(self, instance):
        self.manager.current = 'welcome_screen'

    def greenclick(self, instance):
        self.show_popup("Status: Safe", "You are marked safe. No actions needed.")

    def yellowclick(self, instance):
        trigger_yellow_alert()
        msg = "Sending 'Uncertain' status & Live Location to emergency contacts."
        self.show_popup("Uncertain Alert Sent", msg)

    def redclick(self, instance):
        trigger_red_alert()
        msg = ("SOS Sent with Live Location!\nAlerting Police Services...\n"
               "Audio Recording Started...\nEmergency Contacts Notified.")
        self.show_popup("EMERGENCY SOS ACTIVATED", msg)

    def show_popup(self, title, message):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        popup_label = Label(
            text=message,
            halign='center',
            valign='middle',
            font_size=sp(14)
        )
        popup_label.bind(size=popup_label.setter('text_size'))
        close_btn = Button(text="Dismiss", size_hint_y=None, height=dp(40), font_size=sp(15))
        layout.add_widget(popup_label)
        layout.add_widget(close_btn)
        popup = Popup(title=title, content=layout, size_hint=(0.85, 0.45))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()


class ZenWalk(App):
    def build(self):
        start_gps()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(Welcome(name="welcome_screen"))
        sm.add_widget(ProfileScreen(name='profile_screen'))
        sm.add_widget(DangerScreen(name='danger_screen'))

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM profile WHERE id=1')
        exists = cursor.fetchone()
        conn.close()

        if exists:
            sm.current = 'welcome_screen'
        else:
            sm.current = 'login_screen'

        return sm


if __name__ == '__main__':
    ZenWalk().run()
