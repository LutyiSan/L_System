


from kivy.config import Config
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.animation import Animation
from kivy.properties import NumericProperty
from sql import *

Config.set('graphics', 'resizable', True)
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')

Builder.load_file('kivy_files/run_time.kv')


class MainArea(Image):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MainArea, self).__init__(**kwargs)
        self.spin = 360
        self.anim = Animation(angle=self.spin, duration=2)
        self.anim += Animation(angle=self.spin, duration=2)
        self.anim.repeat = True
        self.anim.start(self)
        self.color_normal = 0, 1, 0, 1
        self.color_alarm = 1, 0, 0, 1
        self.color_fault = 0, 0, 1, 1
        self.stop_color = 0.2, 0.2, 0.2, 0
        self.signal_id = str
        self.value = str
        self.flag = str
        self.anim_class = str

    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0

    def update_screen(self, dt):
        sql_kivy = SQL()
        sql_kivy.connection_to_db('scada')
        data = sql_kivy.get_kivy()
        sql_kivy.exit_from_db()
        for sig in data:
            self.signal_id = str(sig[0])
            self.value = str(sig[1])
            self.flag = str(sig[2])
            self.anim_class = str(sig[3])
            if self.signal_id in self.ids:
                if self.anim_class == "text":
                    self.ids[self.signal_id].text = self.value
                    if self.flag == 'normal':
                        self.ids[self.signal_id].color = self.color_normal
                    elif self.flag == 'alarm':
                        self.ids[self.signal_id].color = self.color_alarm
                    elif self.flag == 'fault':
                        self.ids[self.signal_id].color = self.color_fault
                    else:
                        pass
                    print(self.anim_class)
                elif self.anim_class == 'rotation':
                    print(self.anim_class, '2222')
                    if self.value == 'active' and self.flag == 'normal':
                        pass
                    elif self.value == 'active' and self.flag == 'alarm':
                        self.ids[self.signal_id].color = self.color_alarm
                    elif self.value == 'active' and self.flag == 'fault':
                        self.ids[self.signal_id].source = "file_base/pump_fault.png"
                    elif self.value == 'inactive' and self.flag == 'normal':
                        self.ids[self.signal_id].color = self.stop_color
                    elif self.value == 'inactive' and self.flag == 'alarm':
                        self.ids[self.signal_id].source = "file_base/pump_alarm.png"
                    elif self.value == 'inactive' and self.flag == 'fault':
                        self.ids[self.signal_id].source = "file_base/pump_fault.png"
                    else:
                        pass
                elif self.anim_class == 'hide':
                    if self.value == 'inactive':
                        self.ids[self.signal_id].color = self.stop_color
                elif self.anim_class == 'hide_reverse':
                    if self.value == 'active':
                        self.ids[self.signal_id].color = self.stop_color
            else:
                pass

    def set_to_device(self, signal_id, value_data):
        rpc = RPC(signal_id, value_data)
        rpc.do_it()

class ConfigApp(App):
    def build(self):
        schema = MainArea()
        Clock.schedule_interval(schema.update_screen, 10.0)
        return schema


ConfigApp().run()
