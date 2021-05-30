import threading
from typing import List

from kivy.lang.builder import Builder
from kivy.properties import StringProperty, Clock, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd import color_definitions
from kivymd.app import MDApp
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase, MDTabs

from google_req import get_res

buil_strng = '''
MDBoxLayout:
    orientation: 'vertical'

    MDToolbar:
        id: toolbar
        pos_hint: {"top": 1}
        elevation: 10
        title: app.first_screen_text
        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]

    MDNavigationLayout:

        x: toolbar.height

        ScreenManager:
            id: screen_manager
            First:
            Second:

        MDNavigationDrawer:
            id: nav_drawer

            ContentNavigationDrawer:
                id: content_drawer
                screen_manager: screen_manager
                nav_drawer: nav_drawer
                
<ContentNavigationDrawer>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"

    AnchorLayout:
        anchor_x: "left"
        size_hint_y: None
        height: avatar.height

        Image:
            id: avatar
            size_hint: None, None
            size: "200dp", "80dp"
            source: "image/alphacine_logo.png"

    MDLabel:
        text: "Hannibal inc."
        font_style: "Body1"
        size_hint_y: None
        height: self.texture_size[1]
        
    MDSeparator:
        height: "2dp"
        
    MDLabel:
        id: card_count
        text: ""
        font_style: "Body1"
        size_hint_y: None
        height: self.texture_size[1]
                

<ScrollableLabel>:
    MDLabel:
        id: sc_label
        size_hint_y: None
        height: self.texture_size[1]
        # text_size: self.width, None
        text: root.text
        theme_text_color: "ContrastParentBackground"


<First>:
    name:'first'
        
    MDTextFieldRound:
        id : movie_text
        normal_color: 1, 1, 1, 1  # app.theme_cls.primary_color
        color_active: 1, 1, 1, 1
        cursor_color: 0, 0, 0, 1
        cursor_width: '1sp'
        icon_left: "magnify"
        size_hint:(0.7,0.1)
        pos_hint:{'center_x':0.5,'center_y':0.9}
        hint_text:'Quel film souhaitez-vous aller voir ?'
        
    MDTextField:
        id: city_text 
        pos_hint:{'center_x':0.5,'center_y':0.78}
        hint_text: "Où ? (Paris par défaut)"
        size_hint:(0.6,0.1)
        helper_text: "Recherche de cinés autour de..."
        helper_text_mode: "on_focus"
    
    MDBoxLayout:
        adaptive_size: True
        pos_hint: {"center_x": .5, "center_y": .68}
        spacing: 50
        alignment: 'horizontal'
        MyToggleButton:
            id: ugc 
            text: "UGC"
        
        MyToggleButton:
            id: cinepass        
            text: "CinéPass"
            
        MyToggleButton:
            id: cip 
            text: "CIP"
    
    DaysBoxLayout:
        id: check_days
        pos_hint: {'center_x':0.5,'center_y':0.5}
    
    MDRaisedButton:
        text:'Rechercher'
        pos_hint: {'center_x':0.5,'center_y':0.3}
        on_press:
            app.search_movie()

    MDLabel:
        id: text_progress
        text:app.tobeupd
        halign: 'center'
        pos_hint:{'center_y':0.2}
        
    MDFloatingActionButton:
        id: go_to_second_button  
        icon: 'arrow-right'
        opposite_colors: True
        elevation: 10
        theme_text_color: "Custom"
        md_bg_color: app.theme_cls.primary_color
        pos_hint: {'center_x': .85, 'center_y': .15}
        on_release: app.go_to_second(self)
        
<Second>:
    name: 'second'
    MDTabs:
        id: tabs

<MCQLabel@ButtonBehavior+Label>:
    text_size: self.size
    halign: 'center'
    font_size: '13sp'
    color: 0, 0, 0, 1


<MCQLabelCheckBox@MDBoxLayout>:
    text_top: ''
    text_bottom: ''
    orientation: 'vertical'
    size_hint_x: .5
    active_b: False
    active_t: False

    MCQLabel:
        on_press: cb_t._do_press()
        text: root.text_top
        valign: 'bottom'
        
    MDCheckbox:
        id: cb_t
        valign:'top'
        active: root.active_t
        
    MDCheckbox:
        id: cb_b
        valign:'bottom'
        active: root.active_b

    MCQLabel:
        on_press: cb_b._do_press()
        text: root.text_bottom
        valign: 'top'
        
<DaysBoxLayout@MDBoxLayout>:
    size_hint_y: .2
    orientation: 'horizontal'
    
    MDLabel:
        valign: 'middle'
        halign: 'right'
        text: 'Dans'
        text_size: self.size
    
    MCQLabelCheckBox:
        id: 04
        text_top:"0"
        text_bottom: "4"
        active_t:"0"
        
    MCQLabelCheckBox:
        id: 15
        text_top:"1"
        text_bottom: "5"

    MCQLabelCheckBox:
        id: 26
        text_top:"2"
        text_bottom: "6"
        
    MCQLabelCheckBox:
        id: 37
        text_top:"3"
        text_bottom: "7"

    MDLabel:
        valign: 'middle'
        halign: 'left'
        text: 'jours'
        text_size: self.size
'''

colors = color_definitions.colors.copy()
colors['Yellow'] = {

    "50": "FFFF50",
    "100": "FFFG40",
    "200": "FFFD30",
    "300": "FFEC20",
    "400": "FFDC10",
    "500": "FECC00",
    "600": "EEBC00",
    "700": "DFAC00",
    "800": "D0A900",
    "900": "C9A800",
    "A100": "C0A000",
    "A200": "B99500",
    "A400": "B08000",
    "A700": "A97000",
}


class MyToggleButton(MDFillRoundFlatButton, MDToggleButton):
    def __init__(self, **kwargs):
        self.background_down = MDApp.get_running_app().theme_cls.primary_dark
        super().__init__(**kwargs)


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class ContentNavigationDrawer(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class First(Screen):
    pass


class Second(Screen):
    pass


class Cinema:

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address

    @property
    def id(self) -> str:
        return self.name + self.address


class Session:
    def __init__(self, sched: str, version: str):
        self.sched = sched
        self.version = version


class CineSessions:
    def __init__(self, cine: Cinema, sessions: List[Session]):
        self.cine = cine
        self.sessions = sessions


class CineSessionsCard(MDCard):
    def __init__(self, cine_sessions: CineSessions, **kwargs):
        self.cine_sessions = cine_sessions
        self.orientation = 'vertical'
        super().__init__(**kwargs)

        self.padding = "8dp"
        self.size_hint_x = .9
        self.pos_hint = {"center_x": .5, "center_y": .7}

        label = MDLabel(text=cine_sessions.cine.name)
        label.font_style = 'H5'
        label.theme_text_color = "Primary"
        label.size_hint_y = None
        label.pos_hint_y = 'center'

        self.add_widget(label)
        self.add_widget(MDSeparator(height='2dp', size_hint_x='.5'))
        label = MDLabel(text=cine_sessions.cine.address)
        label.font_style = 'Body1'
        label.size_hint_y = None
        label.pos_hint_y = 'top'
        self.add_widget(label)

        aux = dict()
        for session in cine_sessions.sessions:
            if session.version not in aux:
                aux[session.version] = []
            aux[session.version].append(session.sched)
        i = 0
        for k, v in aux.items():
            label = MDLabel(text=f"{k}: {' - '.join(v)}")
            label.font_style = 'Body1'
            label.size_hint_y = None
            label.pos_hint_x = 'justify'
            label.pos_hint_y = 'bottom' if i == 1 else 'top'
            label.text_size = label.size
            self.add_widget(label)


class TabDay(MDFloatLayout, MDTabsBase):

    def __draw_shadow__(self, origin, end, context=None):
        pass

    def __init__(self, date: str, cine_cards: List[CineSessionsCard], **kw):
        self.date = date
        self.cine_cards = cine_cards
        super().__init__(title=date, **kw)
        scroll = ScrollView()
        grid = GridLayout(cols=1, padding=(10, 10), spacing=(10, 30), size_hint_y=None, row_default_height=400)
        grid.bind(minimum_height=grid.setter("height"))
        for card in cine_cards:
            grid.add_widget(card)
        scroll.add_widget(grid)
        self.add_widget(scroll)


class MovieSearch(MDApp):
    tobeupd = StringProperty()
    first_screen_text: str = 'AlphaCiné - Allons au ciné ?...'

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Yellow"
        self.tobeupd = '-'
        self.dataset = [None]
        Clock.schedule_interval(lambda dt: self.check_dataset(), 1)
        self.top_strng = Builder.load_string(buil_strng)
        self.strng = self.top_strng.ids.screen_manager
        self.tabs: MDTabs = self.strng.get_screen('second').ids.tabs
        self.check_days = self.strng.get_screen('first').ids.check_days
        return self.top_strng

    def go_to_first(self, *args):
        self.strng.get_screen('first').ids.text_progress.text = '-'
        self.strng.get_screen('second').manager.current = 'first'
        self.top_strng.ids.toolbar.left_action_items = [
            ["menu", lambda x: self.top_strng.ids.nav_drawer.set_state("open")]]
        self.top_strng.ids.toolbar.title = self.first_screen_text

    def go_to_second(self, *args):
        if len(self.tabs.get_tab_list()) == 0:
            Snackbar(text='Aucune requête déjà effectuée').open()
            return
        self.strng.get_screen('second').manager.current = 'second'
        self.top_strng.ids.toolbar.left_action_items = [
            ["arrow-left", lambda x: self.go_to_first()]]
        self.top_strng.ids.toolbar.title = self.movie_text

    def search_movie(self):
        dates = []
        for id in self.check_days.ids:
            i, j = id
            if getattr(self.check_days.ids, id).ids.cb_t.state == 'down':
                dates.append(i)
            if getattr(self.check_days.ids, id).ids.cb_b.state == 'down':
                dates.append(j)
        dates.sort()
        cards = set()
        if self.strng.get_screen('first').ids.cip.state == 'down':
            cards.add('Ciné Carte CIP')
        if self.strng.get_screen('first').ids.cinepass.state == 'down':
            cards.add('cinépass')
        if self.strng.get_screen('first').ids.ugc.state == 'down':
            cards.add('ugc illimité')

        self.movie_text = self.strng.get_screen('first').ids.movie_text.text
        self.city_text = self.strng.get_screen('first').ids.city_text.text

        if self.movie_text.split() != []:
            self.dataset = [None]
            if self.city_text == '':
                city = 'Paris'
            else:
                city = self.city_text
            th = threading.Thread(target=lambda: get_res(
                movie=self.movie_text,
                city=city,
                dates=dates,
                cards=cards,
                progress_bar=self,
                res_ph=self.dataset
            ))
            th.start()
        else:
            Snackbar(text='Indiquez un film dans la barre de recherche').open()

    def check_dataset(self):
        if self.dataset[0] is None:
            return
        remove_first_tab = len(self.tabs.get_tab_list()) >= 1
        while len(self.tabs.get_tab_list()) > 1:
            # cannot remove current tab...
            self.tabs.remove_widget(
                self.tabs.get_tab_list()[-1]
            )
        aux = list(map(lambda r: tuple(r[1].to_numpy()), self.dataset[0].reset_index().iterrows()))
        aux_d = dict()
        for el in aux:
            date = el[0]
            if date not in aux_d:
                aux_d[date] = {}
            cine = Cinema(name=el[1].split('|')[0], address=el[1].split('|')[1])
            session = Session(sched=el[3], version=el[2])
            if cine.id not in aux_d[date]:
                aux_d[date][cine.id] = []
            aux_d[date][cine.id].append((cine, session))

        print(aux_d)
        for date, cine_id_dic in aux_d.items():
            cine = None
            cine_sessions_cards = []
            for cine_id, cine_sess_s in cine_id_dic.items():
                sessions = []
                for cin, sess in cine_sess_s:
                    cine = cin
                    sessions.append(sess)
                cine_sessions_cards.append(CineSessionsCard(CineSessions(cine, sessions)))
            tab_day = TabDay(date=date, cine_cards=cine_sessions_cards)
            self.tabs.add_widget(tab_day)

        # self.data_table.row_data = list(map(lambda r: tuple(r[1].to_numpy()), self.dataset[0].reset_index().iterrows()))

        self.dataset = [None]
        self.strng.get_screen('second').manager.current = 'second'
        self.top_strng.ids.toolbar.left_action_items = [
            ["arrow-left", lambda x: self.go_to_first()]]
        self.top_strng.ids.toolbar.title = self.movie_text

        # remove first tab
        if remove_first_tab:
            self.tabs.remove_widget(
                    self.tabs.get_tab_list()[0]
                )

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    MovieSearch().run()
