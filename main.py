import youtube_dl

from kivymd.app import MDApp
from kivy.lang import Builder

from threading import Thread
#from kivymd.theming import ThemeManager
from kivymd.uix.snackbar import Snackbar
#from kivymd.icon_definitions import md_icons

str1 = '''
#:import web webbrowser



NavigationLayout:
    ScreenManager:
        Screen:
            BoxLayout:
                orientation: 'vertical'
                MDToolbar:
                    id: toolbar
                    title: 'Menu'
                    md_bg_color: app.theme_cls.primary_color
                    background_palette: 'Primary'
                    background_hue: '500'
                    left_action_items: [['menu', lambda x: nav_drawer.toggle_nav_drawer()]]
                BoxLayout:
                    size_hint_y: 0.3
                    orientation: 'horizontal'
                    MDTextField:
                        id: searchfield
                        hint_text: "Enter a valid link"
                        required: True
                        helper_text_mode: "on_error"
                        size_hint: 0.9, None
                        height: self.minimum_height
                        disabled: True
                    MDIconButton:
                        icon: 'clipboard-text'
                        size_hint: 0.1, 1
                        on_release: app.pastebutton()
                BoxLayout:
                    orientation: 'horizontal'
                    MDSpinner:
                        id: spinner
                        active: False
                        size_hint: 0.1, 0.1
                    MDLabel:
                        id: info_screen
                        font_style: 'H5'
                        theme_text_color: 'Primary'
                        text: ""
                        halign: 'center'       
                FloatLayout:
                    id: formats
                    size_hint: 1, 1
                MDRaisedButton:
                    size_hint_x: 0.95
                    pos_hint: {'center_x' : 0.5 , 'center_y': 0.5}
                    text: 'Download'
                    on_release: app.downloadbutton()
                MDProgressBar:
                    size_hint_y: 0.1
                    id: pbar
                    value: 0
    MDNavigationDrawer:
        id: nav_drawer
        BoxLayout:
            orientation: "vertical"
            padding: "8dp"
            spacing: "8dp"
            AnchorLayout:
                anchor_x: "left"
                anchor_y: "top"
                size_hint_y: None
                height: avatar.height
                Image:
                    id: avatar
                    size_hint: None, None
                    size: "56dp", "56dp"
                    source: "icon"
        
            MDLabel:
                text: "Charalampos Bekiaris"
                font_style: "Button"
                size_hint_y: None
                height: self.texture_size[1]
        
            MDLabel:
                text: "charalbek@gmail.com"
                font_style: "Caption"
                size_hint_y: None
                height: self.texture_size[1]
                
            MDList:
                id: md_list
                OneLineListItem:
                    text: "Dark Theme"
                    on_press:
                        app.ToggleTheme()
                OneLineAvatarListItem:
                    text: "View on github"
                    on_press:
                        web.open('https://github.com/J0K3RAS/PyYTDownloader')
                    IconLeftWidget:
                        icon: "github-circle"
                    

'''


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        Snackbar(text=msg).show()

class PyYTDownloader(MDApp):
    #theme_cls = ThemeManager()
    
    def build(self):
        self.layout = Builder.load_string(str1)
        return self.layout
    
    def ToggleTheme(self):
        if self.theme_cls.theme_style == 'Dark':
            self.theme_cls.theme_style = 'Light'
            self.theme_cls.primary_palette = 'Blue'
            #self.layout.ids['dts'].active = False
        else:
            self.theme_cls.theme_style = 'Dark'
            self.theme_cls.primary_palette = 'Orange'
            #self.layout.ids['dts'].active = True
    
    def open_dialog(self):
        content = Builder.load_string(self.video_select())
        self.layout.ids.formats.add_widget(content)
            

    def my_hook(self, d):
        if d['status'] == 'downloading':
            total = d['total_bytes']
            downloaded = d['downloaded_bytes']
            percentage = float((downloaded/total)*100)
            self.layout.ids['info_screen'].text = str(int(percentage))
            self.layout.ids['pbar'].value = float(percentage)  
        elif d['status'] == 'finished':
            self.notification('Download Completed')
    
    def Stage1_url_processing(self):
        #global ydl
        global meta
        global song
        global ydl_opts
        self.layout.ids.formats.clear_widgets()
        meta = []
        try:
            #ydl_opts = {'outtmpl': '/storage/emulated/0/%(title)s.%(ext)s','logger': MyLogger(),'progress_hooks': [self.my_hook],'nocheckcertificate': True}
            ydl_opts = {'logger': MyLogger(),'progress_hooks': [self.my_hook],'nocheckcertificate': True}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song = str(self.layout.ids.searchfield.text)
            self.layout.ids.spinner.active = True
            self.layout.ids.info_screen.text = 'Please wait\nSearching for track info...' 
            def callback():
                def callback1():
                    global meta
                    meta = ydl.extract_info(song, download=False)
                t = Thread(target=callback1)
                t.start()
                while True:
                    if not  t.is_alive():
                        self.layout.ids.spinner.active = False
                        self.layout.ids.info_screen.text = 'Done Searching' 
                        self.open_dialog()

                        break
            Thread(target=callback, daemon = True).start()
                        
        except Exception:
            self.notification('Invalid URL')
        
    def video_select(self):
        global formats
        try:
            layout = '''
#:import ydl_opts __main__.ydl_opts
GridLayout:
    pos_hint: {'center_x': 0.5, 'center_y':0.75}
    cols: 4
    MDCheckbox:
        id: mp3
        group: 'test'
        on_state: ydl_opts['format'] = 'bestaudio/best'  
    MDLabel:
        font_style: 'Subtitle1'
        theme_text_color: 'Primary'
        text: 'Audio'
        halign: 'center' '''
            formats = {}
            lista = []
            for i in meta['formats']:
                if i['ext'] == 'mp4':
                    formats[i['format_note']] = i['format_id']
                    lista.append(i['format_note'])
            for i in range(len(formats)):
                sublayout = '''
    MDCheckbox:
        id: {}
        group: 'test'
        on_state: app.active_checkbox('{}')      
    MDLabel:
        font_style: 'Subtitle1'
        theme_text_color: 'Primary'
        text: '{}'
        halign: 'center' '''.format(lista[i],lista[i],lista[i])
                
                layout += sublayout
            return layout
        except Exception as e:
            print(e)

    def pastebutton(self):
        self.layout.ids.searchfield.text = ''
        self.layout.ids.searchfield.paste()
        self.Stage1_url_processing()

        
    def active_checkbox(self, iden_num):
        tag_id = formats[iden_num]
        ydl_opts['format'] = tag_id + '+ bestaudio/best'
            
    def notification(self, text):
        Snackbar(text = text).show()
        
    def downloadbutton(self):
        def callback():
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song = str(self.layout.ids.searchfield.text)
                target = ydl.download([song])
                return
        Thread(target=callback).start()

if __name__ == '__main__':
    PyYTDownloader().run()
