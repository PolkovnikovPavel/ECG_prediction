import asyncio, time
from data.functions import pw, ph
from data.objects import *
from tkinter.filedialog import askopenfilename
from graphic import Graphic


class MainCycle:
    def __init__(self, canvas, all_gropes):
        self.canvas = canvas
        self.all_gropes = all_gropes
        self.__timer = time.time()
        self.__running = True
        self.type_menu = 'main_menu'
        self.mouse_x = 0
        self.mouse_y = 0
        self.old_mouse_x = 0
        self.old_mouse_y = 0
        self.is_click = False
        self.is_result = False
        self.is_right_click = False
        self.ruler = None
        self.file_name = ''
        self.graphic = None
        self.peed_reading = 25

        self.__create_all_gropes()

    def __create_all_gropes(self):
        self.main_grope = self.all_gropes[0]
        self.view_grope = self.all_gropes[1]

    def start(self):
        while self.__running:

            self.canvas.update()
            dt = time.time() - self.__timer
            dt = (1 / 100) - dt
            if dt > 0:
                time.sleep(dt)

            self.__timer = time.time()

    def get_mouse(self):
        return self.mouse_x, self.mouse_y, self.is_click

    def close_window(self, *args):
        self.__running = False

    def get_running(self):
        return self.__running

    def mouse_wheel(self, event, *args):
        print(event.delta)

    def mouse_move(self, event, *args):
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.view_grope.check(self.mouse_x, self.mouse_y, is_clik=self.is_click)
        if self.type_menu == 'view_menu':
            if self.is_result:
                if not self.obj_result.check_point(self.mouse_x, self.mouse_y):
                    self.is_result = False
                    self.hide_result()
            else:
                if self.obj_result.check_point(self.mouse_x, self.mouse_y):
                    self.is_result = True
                    self.show_result()
            if self.is_right_click and self.ruler is not None:
                self.canvas.delete(self.ruler[2])
                self.canvas.delete(self.ruler[3])
                line1 = self.canvas.create_line(self.ruler[0], self.ruler[1], self.mouse_x, self.mouse_y, width=ph(0.4))
                line2 = self.canvas.create_line(self.ruler[0], self.ruler[1], self.mouse_x, self.ruler[1], width=ph(0.3),
                                                dash=(ph(0.7), ph(0.3)))
                text = self.ruler[4]
                text.set_new_text(str(round(abs(self.ruler[0] - self.mouse_x) * self.graphic.get_size_one_pixel(), 1)))
                text.go_to(self.ruler[0] + (self.mouse_x - self.ruler[0]) / 2, self.ruler[1] - ph(4))
                self.ruler = [self.ruler[0], self.ruler[1], line1, line2, text]

    def pressing_keyboard(self, event, *args):
        print(event.char)

    def click(self, event, *args):
        self.is_click = True
        self.old_mouse_x = self.mouse_x
        self.old_mouse_y = self.mouse_y
        for grope in self.all_gropes:
            grope.check(self.mouse_x, self.mouse_y, is_clik=True)

    def click_out(self, event, *args):
        self.is_click = False
        for grope in self.all_gropes:
            grope.check(self.mouse_x, self.mouse_y, is_clik=False)

    def right_click(self, event, *args):
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.is_right_click = True

        if self.ruler is not None:
            self.canvas.delete(self.ruler[2])
            self.canvas.delete(self.ruler[3])
            self.ruler[4].hide()

        if self.type_menu == 'view_menu':
            line1 = self.canvas.create_line(self.mouse_x, self.mouse_y, self.mouse_x, self.mouse_y, width=ph(0.4))
            line2 = self.canvas.create_line(self.mouse_x, self.mouse_y, self.mouse_x, self.mouse_y, width=ph(0.3), dash=(pw(1.2), ph(0.4)))
            text = Text(self.mouse_x, self.mouse_y - ph(4), '0', self.canvas, font=f'Times {ph(4)} italic bold')
            self.ruler = [self.mouse_x, self.mouse_y, line1, line2, text]


    def right_click_out(self, event, *args):
        self.is_right_click = False

    def start_main_menu(self, *args):
        self.type_menu = 'main_menu'
        self.main_grope.show_all()

    def start_view_menu(self, *args):
        self.type_menu = 'view_menu'
        self.view_grope.delete()
        bg = Object(0, 0, pw(100), ph(100), 'background_view_menu.png', self.canvas)
        self.view_grope.add_objects(bg)

        btn = Button(pw(94), ph(1), ph(5), ph(5), 'question_button.png', self.canvas,
                     function=self.show_hide_instruction, container=[False], visibility=False)
        btn.args = btn
        self.view_grope.add_objects(btn)

        btn = Button(pw(80), ph(1), ph(5), ph(5), 'restart.png', self.canvas, 'restart_2.png',
                     function=self.start_scanning, container=[False], visibility=False)
        self.view_grope.add_objects(btn)

        btn = Button(pw(2), ph(3), ph(10), ph(5), 'tabl_left.png', self.canvas, 'tabl.png', self.start_main_menu)
        self.view_grope.add_objects(btn)
        self.obj_graphic = ObjectGraphic(self.canvas, self.graphic, self.file_name, 0, ph(10), pw(100), ph(75), scan_graphic=self.scan_graphic)
        self.view_grope.add_objects(self.obj_graphic)

        self.obj_result = Object(pw(85), ph(87), pw(10), ph(10), 'button_result.png', self.canvas)
        self.view_grope.add_objects(self.obj_result)

        self.view_grope.show_all()
        self.main_grope.hide_all()

    def set_file_name(self, *args):
        filename = askopenfilename()
        self.file_name = filename
        print(self.file_name)

    def start_scanning(self, *args):
        if not self.file_name:
            return
        self.graphic = Graphic(self.file_name, self.peed_reading)
        self.graphic.graph_detection()
        self.start_view_menu()

    def scan_graphic(self, *args):
        for key in self.obj_graphic.dict_of_points:
            self.graphic.dict_of_points[key] = []
            for point in self.obj_graphic.dict_of_points[key]:
                self.graphic.dict_of_points[key].append(point.get_cor_point())
        self.graphic.characteristics = []
        self.graphic.find_heart_rate()
        print(self.graphic.characteristics[0])

    def show_hide_instruction(self, *args):
        obj = args[0]
        is_open = obj.container[0]
        if is_open:
            obj.change_img('question_button.png', ph(5), ph(5))
            obj.go_to(pw(94), ph(1))
            obj.container[0] = False
        else:
            obj.change_img('question_button_2.png', pw(100), ph(100))
            obj.go_to(0, 0)
            obj.container[0] = True

    def show_result(self):
        self.obj_result.change_img('button_result_2.png', pw(50), ph(50))
        self.obj_result.go_to(pw(45), ph(47))
        text = self.graphic.get_text_of_general_information()
        self.test_result = Text(pw(65), ph(75), text, self.canvas, font=f'Times {ph(2)} italic bold')

    def hide_result(self):
        self.obj_result.change_img('button_result.png', pw(10), ph(10))
        self.obj_result.go_to(pw(85), ph(87))
        self.test_result.hide()


