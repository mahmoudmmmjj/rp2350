from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import serial
import threading
import json

class RP2350Controller(BoxLayout):
    def __init__(self, **kwargs):
        super(RP2350Controller, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 20

        # عنوان الواجهة
        self.add_widget(Label(text='لوحة تحكم RP2350', font_size=24, size_hint_y=None, height=50))

        # أزرار الألوان
        btn_red = Button(text='أحمر (Red)', background_color=(1, 0, 0, 1), font_size=18)
        btn_red.bind(on_press=lambda x: self.send_color("red"))
        self.add_widget(btn_red)

        btn_green = Button(text='أخضر (Green)', background_color=(0, 1, 0, 1), font_size=18)
        btn_green.bind(on_press=lambda x: self.send_color("green"))
        self.add_widget(btn_green)

        btn_blue = Button(text='أزرق (Blue)', background_color=(0, 0, 1, 1), font_size=18)
        btn_blue.bind(on_press=lambda x: self.send_color("blue"))
        self.add_widget(btn_blue)

        # خانة عرض الحالة والردود من البوردة
        self.status_label = Label(text='الحالة: في انتظار الاتصال...', font_size=16, size_hint_y=None, height=80)
        self.add_widget(self.status_label)

        # إعدادات الـ Serial
        self.serial_conn = None
        self.start_serial_listener("COM3", 115200) # عدل البورت حسب جهازك أو موبايلك (لو OTG)

    def start_serial_listener(self, port, baudrate):
        def listen():
            try:
                self.serial_conn = serial.Serial(port, baudrate, timeout=1)
                while True:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        # تحديث الواجهة بأمان عبر Clock من Kivy
                        Clock.schedule_once(lambda dt: self.update_status(line))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f"خطأ في الاتصال: {e}"))

        t = threading.Thread(target=listen, daemon=True)
        t.start()

    def update_status(self, text):
        self.status_label.text = f"رد القطعة: {text}"

    def send_color(self, color_name):
        if self.serial_conn and self.serial_conn.is_open:
            payload = json.dumps({"color": color_name}) + "\n"
            self.serial_conn.write(payload.encode('utf-8'))
            self.status_label.text = f"تم إرسال اللون: {color_name}"
        else:
            self.status_label.text = "البوردة غير متصلة بالبورت!"

class RP2350App(App):
    def build(self):
        return RP2350Controller()

if __name__ == '__main__':
    RP2350App().run()