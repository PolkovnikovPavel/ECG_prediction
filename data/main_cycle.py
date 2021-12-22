import asyncio, time
from data.functions import pw, ph
from data.objects import *
from tkinter.filedialog import askopenfilename
from graphic import Graphic


class MainCycle:
    def __init__(self, canvas, all_groups):
        self.canvas = canvas
        self.all_groups = all_groups
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
        self.speed_reading = 25
        self.test_result = None
        self.mode_switcher = None
        self.obj_graphic = None
        self.obj_result = None
        self.text_chss = None
        self.instruction_text = None

        self.__create_all_gropes()

    def __create_all_gropes(self):
        self.main_group = self.all_groups[0]
        self.view_group = self.all_groups[1]

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
        self.main_group.hide_all()
        self.view_group.hide_all()

    def get_running(self):
        return self.__running

    def mouse_wheel(self, event, *args):
        print(event.delta)

    def mouse_move(self, event, *args):
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.view_group.check(self.mouse_x, self.mouse_y, is_click=self.is_click)
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
                line2 = self.canvas.create_line(self.ruler[0], self.ruler[1], self.mouse_x, self.ruler[1],
                                                width=ph(0.3),
                                                dash=(ph(0.7), ph(0.3)))
                text = self.ruler[4]
                text.set_new_text(str(round(
                    abs(self.ruler[0] - self.mouse_x) * self.graphic.get_size_one_pixel(), 1)) + ' сек.')
                text.go_to(self.ruler[0] + (self.mouse_x - self.ruler[0]) / 2, self.ruler[1] - ph(6))
                self.ruler = [self.ruler[0], self.ruler[1], line1, line2, text]

    def pressing_keyboard(self, event, *args):
        print(event.char)

    def click(self, event, *args):
        self.is_click = True
        self.old_mouse_x = self.mouse_x
        self.old_mouse_y = self.mouse_y
        for group in self.all_groups:
            group.check(self.mouse_x, self.mouse_y, is_click=True)

    def click_out(self, event, *args):
        self.is_click = False
        for group in self.all_groups:
            group.check(self.mouse_x, self.mouse_y, is_click=False)

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
            line2 = self.canvas.create_line(self.mouse_x, self.mouse_y, self.mouse_x, self.mouse_y, width=ph(0.3),
                                            dash=(pw(1.2), ph(0.4)))
            text = Text(self.mouse_x, self.mouse_y - ph(6), '0 сек.', self.canvas, font=f'Montserrat {ph(3)}')
            self.ruler = [self.mouse_x, self.mouse_y, line1, line2, text]

    def right_click_out(self, event, *args):
        self.is_right_click = False

    def start_main_menu(self, *args):
        self.type_menu = 'main_menu'
        self.main_group.show_all()

    def start_view_menu(self, *args):
        self.type_menu = 'view_menu'
        self.view_group.delete()

        bg = Object(0, 0, pw(100), ph(100), 'background_view_menu.png', self.canvas)
        self.view_group.add_objects(bg)

        btn = Button(pw(94), ph(2), ph(6), ph(6), 'question_button.png', self.canvas,
                     function=self.show_hide_instruction, container=[False], visibility=False)
        btn.args = btn
        self.view_group.add_objects(btn)

        btn = Button(pw(82), ph(2.5), ph(5), ph(5), 'restart.png', self.canvas, 'restart_2.png',
                     function=self.restart_graphic, container=[False], visibility=False)
        self.view_group.add_objects(btn)

        self.mode_switcher = Button(pw(25), ph(1.5), ph(14), ph(7), 'switch_mode.png', self.canvas,
                                    function=self.set_speed_50, container=[False])
        self.view_group.add_objects(self.mode_switcher)

        btn = Button(pw(2), ph(1.6), ph(6), ph(6), 'back_button.png', self.canvas, 'back_button_2.png',
                     self.start_main_menu)
        self.view_group.add_objects(btn)

        self.obj_graphic = ObjectGraphic(self.canvas, self.graphic, self.file_name, 0, ph(10), pw(100), ph(75),
                                         scan_graphic=self.scan_graphic)
        self.view_group.add_objects(self.obj_graphic)

        btn = Button(pw(86), ph(2.5), ph(5), ph(5), 'hide_points.png', self.canvas,
                     function=self.obj_graphic.temporarily_hide_points)
        btn.args = btn
        self.view_group.add_objects(btn)

        self.obj_result = Object(pw(85), ph(87), pw(10), ph(10), 'button_result.png', self.canvas)
        self.view_group.add_objects(self.obj_result)

        self.text_chss = Text(pw(80), ph(2), f'{round(self.graphic.heart_rate, 1)} уд/мин', self.canvas,
                              font=f'Montserrat {ph(3)}', visibility=False, anchor='ne')
        self.view_group.add_objects(self.text_chss)

        self.view_group.show_all()
        self.main_group.hide_all()

    def set_file_name(self, *args):
        filename = askopenfilename(filetypes=[('Фотографии ЭКГ', '*jpeg *jpg')])
        self.file_name = filename
        print(self.file_name)

    def start_scanning(self, *args):
        if not self.file_name:
            return
        self.graphic = Graphic(self.file_name, self.speed_reading)
        self.graphic.graph_detection()
        self.start_view_menu()

    def restart_graphic(self, *args):
        self.graphic.restart_graphic()
        self.obj_graphic.reset_all_points()
        if self.ruler is not None:
            self.canvas.delete(self.ruler[2])
            self.canvas.delete(self.ruler[3])
            self.ruler[4].hide()
            self.ruler = None
        self.update_graph_data()

    def update_graph_data(self):
        self.graphic.find_intervals()
        self.text_chss.set_new_text(f'{round(self.graphic.heart_rate, 1)} уд/мин')

    def scan_graphic(self, *args):
        for key in self.obj_graphic.dict_of_points:
            self.graphic.dict_of_points[key] = []
            for point in self.obj_graphic.dict_of_points[key]:
                self.graphic.dict_of_points[key].append(point.get_cor_point())
        self.update_graph_data()

    def show_hide_instruction(self, *args):
        obj = args[0]
        is_open = obj.container[0]
        if is_open:
            obj.change_img('question_button.png', ph(6), ph(6))
            obj.go_to(pw(94), ph(2))
            self.instruction_text.hide()
            obj.container[0] = False
        else:
            obj.change_img('question_button_2.png', pw(56), ph(61))
            obj.go_to(pw(22), ph(20))
            self.instruction_text = TextArea(pw(23), ph(27), 43, 11, self.canvas, font=('Montserrat', 19))
            #  Чтение из файла
            with open('data/Instruction.txt') as f:
                text = ''
                for line in f:
                    text += line
            self.instruction_text.insert_text(text)
            #  Отключение возможности менять текст
            self.instruction_text.change_window_state()
            obj.container[0] = True

    def show_result(self):
        self.obj_result.change_img('button_result_2.png', pw(50), ph(50))
        self.obj_result.go_to(pw(45), ph(47))
        text = self.graphic.get_text_of_general_information()
        self.test_result = Text(pw(48), ph(54), text, self.canvas, font=f'Montserrat {ph(1.9)}')

    def hide_result(self):
        self.obj_result.change_img('button_result.png', pw(10), ph(10))
        self.obj_result.go_to(pw(85), ph(87))
        self.test_result.hide()

    def set_speed_25(self, *args):
        self.mode_switcher.change_img('switch_mode.png', ph(14), ph(7))
        self.mode_switcher.function = self.set_speed_50
        self.graphic.speed_of_ecg = 25
        self.speed_reading = 25
        self.update_graph_data()

    def set_speed_50(self, *args):
        self.mode_switcher.change_img('switch_mode_2.png', ph(14), ph(7))
        self.mode_switcher.function = self.set_speed_25
        self.graphic.speed_of_ecg = 50
        self.speed_reading = 50
        self.update_graph_data()
