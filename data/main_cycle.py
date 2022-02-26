import asyncio, time
from data.functions import pw, ph
from data.objects import *
from tkinter.filedialog import askopenfilename
from graphic import Graphic


class MainCycle:
    """Класс основного цикла приложения"""
    def __init__(self, canvas, all_groups, width, height):
        """Конструктор основного цикла программы

        :param canvas: холст
        :param all_groups: список объектов групп приложения (по сути - окон)
        """
        self.canvas = canvas
        self.width = width
        self.height = height
        self.all_groups = all_groups
        self.__timer = time.time()
        self.__running = True
        self.type_menu = 'main_menu'
        self.is_enabled = True
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
        self.mode_switcher = None
        self.obj_graphic = None
        self.question_button_1 = None
        self.question_button_2 = None
        self.instruction_text = None
        self.instruction_background = None
        self.obj_result = None
        self.text_result = None
        self.text_chss = None
        self.time_coef = 0

        self.obj_crop = None
        self.back_crop = None
        self.ok_crop = None
        self.restart_crop = None

        self.dict_of_instruction_sizes = {
            '3840x2160': [51, 13, 32],
            '2560x1440': [45, 12, 24],
            '1920x1080': [44, 12, 18],
            '1680x1050': [41, 12, 17],
            '1600x900': [45, 12, 15],
            '1440x900': [40, 12, 15],
            '1280x1024': [42, 12, 13],
            '1280x960': [42, 12, 13],
            '1280x720': [42, 11, 13],
            '1024x768': [37, 11, 11],
            '832x624': [37, 12, 9],
            '800x600': [41, 12, 8]
        }

        self.dict_of_results_sizes = {
            '3840x2160': [49, 12, 28],
            '1920x1080': [47, 11, 15],
            '1680x1050': [41, 11, 14],
            '1600x900': [46, 11, 12],
            '1440x900': [41, 11, 12],
            '1280x1024': [39, 11, 11],
            '1280x960': [39, 11, 11],
            '1280x720': [45, 11, 10],
            '1024x768': [40, 11, 9],
            '832x624': [35, 10, 8],
            '800x600': [40, 12, 7]
        }

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.__create_all_groups()

    def __create_all_groups(self):
        """Создаёт группы

        :return:
        """
        self.main_group = self.all_groups[0]
        self.view_group = self.all_groups[1]
        self.crop_group = self.all_groups[2]

    def start(self):
        """Запускает основной цикл приложения

        :return:
        """
        while self.__running:

            self.canvas.update()
            dt = time.time() - self.__timer
            dt = (1 / 100) - dt
            if dt > 0:
                time.sleep(dt)

            self.__timer = time.time()

    def get_mouse(self):
        """Получение состояния мыши

        :return: Положение курсора по оси x, по y и данные по нажатию
        """
        return self.mouse_x, self.mouse_y, self.is_click

    def close_window(self, *args):
        """Закрывает приложение

        :param args:
        :return:
        """
        self.__running = False
        self.main_group.hide_all()
        self.view_group.hide_all()
        self.crop_group.hide_all()

    def get_running(self):
        """Возвращает состояние приложение (активно/неактивно)

        :return: состояние приложения
        """
        return self.__running

    def mouse_wheel(self, event, *args):
        """Выводит в консоль событие о повороте колёсика мыши

        :param event:
        :param args:
        :return:
        """
        print(event.delta)

    def mouse_move(self, event, *args):
        """Обработка события перемещения мыши

        :param event:
        :param args:
        :return:
        """
        self.mouse_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        self.mouse_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        if self.type_menu == 'view_menu':
            self.view_group.check(self.mouse_x, self.mouse_y, is_click=self.is_click)
            if self.is_result:
                if not self.obj_result.check_point(self.mouse_x, self.mouse_y):
                    self.is_result = False
                    self.hide_result()
            else:
                if self.obj_result.check_point(self.mouse_x, self.mouse_y):
                    self.is_result = True
                    self.show_result()
            if self.is_right_click and self.ruler is not None and self.is_enabled:
                self.canvas.delete(self.ruler[2])
                self.canvas.delete(self.ruler[3])
                line1 = self.canvas.create_line(self.ruler[0], self.ruler[1], self.mouse_x, self.mouse_y, width=ph(0.4))
                line2 = self.canvas.create_line(self.ruler[0], self.ruler[1], self.mouse_x, self.ruler[1],
                                                width=ph(0.3),
                                                dash=(ph(0.7), ph(0.3)))
                text = self.ruler[4]
                text.set_new_text(str(round(
                    abs(self.ruler[0] - self.mouse_x) * self.graphic.get_size_one_pixel() * self.time_coef, 2)) +
                                  ' сек.')
                text.go_to(self.ruler[0] + (self.mouse_x - self.ruler[0]) / 2, self.ruler[1] - ph(6))
                self.ruler = [self.ruler[0], self.ruler[1], line1, line2, text]
        if self.type_menu == 'crop_menu':
            self.crop_group.check(self.mouse_x, self.mouse_y, is_click=self.is_click)
            if self.ok_crop.check_point(self.mouse_x, self.mouse_y):
                self.crop_group.set_disabled([self.ok_crop])
            elif self.back_crop.check_point(self.mouse_x, self.mouse_y):
                self.crop_group.set_disabled([self.back_crop])
            elif self.restart_crop.check_point(self.mouse_x, self.mouse_y):
                self.crop_group.set_disabled([self.restart_crop])
            else:
                self.crop_group.set_enabled()

    def pressing_keyboard(self, event, *args):
        """Выводит в консоль нажатые на клавиатуре символы

        :param event:
        :param args:
        :return:
        """
        print(event.char)

    def click(self, event, *args):
        """Обработка события нажатия на левую кнопку мыши

        :param event:
        :param args:
        :return:
        """
        self.is_click = True
        self.old_mouse_x = self.mouse_x
        self.old_mouse_y = self.mouse_y
        for group in self.all_groups:
            group.check(self.mouse_x, self.mouse_y, is_click=True)

    def click_out(self, event, *args):
        """Обработка события прекращения нажатия на левую кнопку

        :param event:
        :param args:
        :return:
        """
        self.is_click = False
        for group in self.all_groups:
            group.check(self.mouse_x, self.mouse_y, is_click=False)

    def right_click(self, event, *args):
        """Обработка события нажатия на левую кнопку мыши

        :param event:
        :param args:
        :return:
        """
        self.mouse_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        self.mouse_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        self.is_right_click = True

        if self.type_menu == 'view_menu' and self.is_enabled:
            if self.ruler is not None:
                self.canvas.delete(self.ruler[2])
                self.canvas.delete(self.ruler[3])
                self.ruler[4].hide()
            line1 = self.canvas.create_line(self.mouse_x, self.mouse_y, self.mouse_x, self.mouse_y, width=ph(0.4))
            line2 = self.canvas.create_line(self.mouse_x, self.mouse_y, self.mouse_x, self.mouse_y, width=ph(0.3),
                                            dash=(pw(1.2), ph(0.4)))
            text = Text(self.mouse_x, self.mouse_y - ph(6), '0 сек.', self.canvas, font=f'Montserrat {ph(3)}')
            self.ruler = [self.mouse_x, self.mouse_y, line1, line2, text]

    def right_click_out(self, event, *args):
        """Обработка события прекращения нажатия на правую кнопку мыши

        :param event:
        :param args:
        :return:
        """
        self.is_right_click = False

    def start_main_menu(self, *args):
        """Показывает главное меню приложения

        :param args:
        :return:
        """
        self.type_menu = 'main_menu'
        self.view_group.hide_all()
        self.crop_group.hide_all()
        self.main_group.show_all()
        self.main_group.all_objects[5].hide()
        self.main_group.all_objects[6].hide()

    def start_view_menu(self, *args):
        """Показывает основное окно приложения

        :param args:
        :return:
        """
        self.main_group.all_objects[2].change_img('open_file_3.png', ph(12), ph(12))

        self.type_menu = 'view_menu'
        self.view_group.delete()

        bg = Object(0, 0, pw(100), ph(100), 'background_view_menu.png', self.canvas)
        self.view_group.add_objects(bg)

        self.instruction_background = Object(0, 0, pw(100), ph(100), 'instruction_background.png', self.canvas)
        self.view_group.add_objects(self.instruction_background)

        self.question_button_1 = Button(pw(94), ph(2), ph(6), ph(6), 'question_button.png', self.canvas,
                                        function=self.show_instruction, visibility=False)
        self.view_group.add_objects(self.question_button_1)

        self.question_button_2 = Button(pw(22), ph(20), pw(56), ph(61), 'question_button_2.png', self.canvas,
                                        function=self.hide_instruction, visibility=False)
        self.view_group.add_objects(self.question_button_2)

        complex_res = f'{str(self.screen_w)}x{str(self.screen_h)}'
        instruction_width = 0
        instruction_high = 0
        instruction_font = 0
        for key in self.dict_of_instruction_sizes:
            if key == complex_res:
                instruction_width, instruction_high, instruction_font = self.dict_of_instruction_sizes[key][0], \
                                                                        self.dict_of_instruction_sizes[key][1], \
                                                                        self.dict_of_instruction_sizes[key][2]
        if instruction_high == 0 or instruction_width == 0 or instruction_font == 0:
            #  При нестандартных разрешениях подбирает примерный размер
            self.instruction_text = TextArea(pw(23), ph(26), round(35 + 0.012*pw(56)), round(10.969 + 0.002*ph(61)),
                                             self.canvas, visibility=False,
                                             font=('Montserrat', round(0.197 + 0.0388*ph(61))))
        else:
            self.instruction_text = TextArea(pw(23), ph(26), instruction_width, instruction_high,
                                             self.canvas, visibility=False,
                                             font=('Montserrat', instruction_font))
        self.view_group.add_objects(self.instruction_text)

        btn = Button(pw(82), ph(2.5), ph(5), ph(5), 'restart.png', self.canvas, img2='restart_2.png',
                     function=self.restart_graphic, container=[False], visibility=False)
        self.view_group.add_objects(btn)

        self.mode_switcher = Button(pw(25), ph(1.5), ph(14), ph(7), 'switch_mode.png', self.canvas,
                                    function=self.set_speed_50, container=[False])
        self.view_group.add_objects(self.mode_switcher)

        btn = Button(pw(2), ph(1.6), ph(6), ph(6), 'back_button_view.png', self.canvas, img2='back_button_view_2.png',
                     function=self.start_main_menu)
        self.view_group.add_objects(btn)

        self.obj_graphic = ObjectGraphic(self.canvas, self.graphic, self.file_name, 0, ph(10), pw(100), ph(75),
                                         scan_graphic=self.scan_graphic)
        # ---
        self.time_coef = self.obj_graphic.img_w / self.obj_graphic.w
        self.view_group.add_objects(self.obj_graphic)

        btn = Button(pw(86), ph(2.5), ph(5), ph(5), 'hide_points.png', self.canvas,
                     function=self.obj_graphic.temporarily_hide_points)
        btn.args = btn
        self.view_group.add_objects(btn)

        self.obj_result = Object(pw(88), ph(87), pw(10), ph(10), 'button_result.png', self.canvas)
        self.view_group.add_objects(self.obj_result)

        results_width = 0
        results_high = 0
        results_font = 0
        for key in self.dict_of_results_sizes:
            if key == complex_res:
                results_width, results_high, results_font = self.dict_of_results_sizes[key][0], \
                                                                        self.dict_of_results_sizes[key][1], \
                                                                        self.dict_of_results_sizes[key][2]
        if results_high == 0 or results_width == 0 or results_font == 0:
            #  При нестандартных разрешениях подбирает примерный размер
            self.text_result = TextArea(pw(50), ph(54), round(23 + 0.83 * (pw(56)**0.5)),
                                        round(11.046 - 0.0002 * ph(61)), self.canvas, visibility=False,
                                        font=('Montserrat', round(1.03395 + 0.0292 * ph(61))))
        else:
            self.text_result = TextArea(pw(50), ph(54), results_width, results_high, self.canvas, visibility=False,
                                        font=('Montserrat', results_font))
        self.view_group.add_objects(self.text_result)

        self.text_chss = Text(pw(80), ph(2), f'{round(self.graphic.heart_rate, 1)} уд/мин', self.canvas,
                              font=f'Montserrat {ph(3)}', anchor='ne')
        self.view_group.add_objects(self.text_chss)

        self.view_group.show_all()
        self.instruction_background.hide()
        self.question_button_2.hide()
        self.main_group.hide_all()
        self.crop_group.hide_all()

    def start_crop_menu(self, *args):
        """Показывает окно кадрирования

        :return:
        """
        self.type_menu = 'crop_menu'
        self.crop_group.delete()

        bg = Object(0, 0, pw(100), ph(100), 'background_view_menu.png', self.canvas)
        self.crop_group.add_objects(bg)

        lower_plate = CroppingPlate(0, ph(90), pw(100), ph(100), 'crop_down.png', self.canvas, type_of_plate='lower')
        upper_plate = CroppingPlate(0, ph(10), pw(100), ph(100), 'crop_up.png', self.canvas)
        right_plate = CroppingPlate(pw(90), 0, pw(100), ph(100), 'crop_right.png', self.canvas, type_of_plate='right')
        left_plate = CroppingPlate(pw(10), 0, pw(100), ph(100), 'crop_left.png', self.canvas, type_of_plate='left')

        self.obj_crop = CropClass(self.canvas, self.file_name, [left_plate, upper_plate, right_plate, lower_plate],
                                  x=pw(50), y=ph(50))
        self.crop_group.add_objects(self.obj_crop)

        self.back_crop = Button(pw(2), ph(2), ph(8), ph(8), 'back_button_crop.png', self.canvas,
                                img2='back_button_crop_2.png', function=self.start_main_menu, visibility=False)
        self.crop_group.add_objects(self.back_crop)

        self.ok_crop = Button(pw(92), ph(87), ph(8), ph(8), 'ok_crop.png', self.canvas, img2='ok_crop_2.png',
                              function=self.crop_img, visibility=False)
        self.crop_group.add_objects(self.ok_crop)

        self.restart_crop = Button(pw(93), ph(2), ph(8), ph(8), 'restart_crop.png', self.canvas,
                                   img2='restart_crop_2.png', function=self.set_plates_default, container=[False],
                                   visibility=False)
        self.crop_group.add_objects(self.restart_crop)

        self.main_group.hide_all()
        self.view_group.hide_all()
        self.crop_group.show_all()

    def crop_img(self, *args):
        """Вызывает функцию по кадрированию изображения

        :return:
        """
        self.file_name = self.obj_crop.crop()

    def set_plates_default(self, *args):
        """Возвращает панели кадрирования на исходное положение

        :return:
        """
        self.obj_crop.set_plates_default()

    def set_file_name(self, *args):
        """Открывает окно выбора файла и выводит в консоль название выбранного файла

        :param args:
        :return:
        """
        filename = askopenfilename(filetypes=[('Фотографии ЭКГ', '*jpeg *jpg')])
        self.file_name = filename
        print(self.file_name)
        if self.file_name != '':
            self.main_group.all_objects[4].show()
            self.main_group.all_objects[2].change_img('open_file_3.png', ph(12), ph(12))
        else:
            self.main_group.all_objects[4].hide()
            self.main_group.all_objects[2].change_img('open_file.png', ph(12), ph(12))

    def start_scanning(self, *args):
        """Создаёт объект графика, а затем запускает основное окно

        :param args:
        :return:
        """
        if not self.file_name:
            return
            # self.file_name = 'D:/python/ECG_prediction/images/ECG-1.jpeg'
        self.main_group.all_objects[5].show()
        self.main_group.all_objects[6].show()
        self.canvas.update()
        self.graphic = Graphic(self.file_name, self.speed_reading)
        self.graphic.graph_detection()
        self.start_view_menu()

    def restart_graphic(self, *args):
        """Перезапускает анализ графика, сбрасывает до дефолтных

        :param args:
        :return:
        """
        self.graphic.restart_graphic()
        self.obj_graphic.reset_all_points()
        if self.ruler is not None and self.is_enabled:
            self.canvas.delete(self.ruler[2])
            self.canvas.delete(self.ruler[3])
            self.ruler[4].hide()
            self.ruler = None
        self.update_graph_data()

    def update_graph_data(self):
        """Обновляет информацию о графике (ЧСС и значения интервалов)

        :return:
        """
        self.graphic.find_intervals()
        self.text_chss.set_new_text(f'{round(self.graphic.heart_rate, 1)} уд/мин')

    def scan_graphic(self, *args):
        """Обновляет объект графика на холсте (перерисовывает точки)

        :param args:
        :return:
        """
        for key in self.obj_graphic.dict_of_points:
            self.graphic.dict_of_points[key] = []
            for point in self.obj_graphic.dict_of_points[key]:
                self.graphic.dict_of_points[key].append(point.get_cor_point())
        self.update_graph_data()

    def show_instruction(self, *args):
        """Осуществляет показ инструкции использования программы

        :param args:
        :return:
        """
        self.question_button_1.hide()
        self.instruction_background.show()
        self.question_button_2.show()
        self.instruction_text.visibility = True
        self.instruction_text.show()
        #  Чтение из файла
        with open('app_images/Instruction.txt') as f:
            text = ''
            for line in f:
                text += line
        self.instruction_text.insert_text(text)
        #  Отключение возможности менять текст
        self.instruction_text.change_window_state()
        self.set_all_objects_disabled([self.question_button_2])

    def hide_instruction(self, *args):
        """Осуществляет скрытие инструкции использования программы

        :param args:
        :return:
        """
        self.question_button_1.show()
        self.question_button_2.hide()
        self.instruction_text.hide()
        self.instruction_background.hide()
        self.set_all_objects_enabled()

    def show_result(self):
        """Отображает окно с результатами исследования

        :return:
        """
        if self.obj_result.is_enabled:
            self.obj_result.change_img('button_result_2.png', pw(50), ph(50))
            self.obj_result.go_to(pw(48), ph(47))
            self.text_result.visibility = True
            self.text_result.show()
            self.text_result.insert_text(self.graphic.get_text_of_general_information())
            self.text_result.change_window_state()
            self.set_all_objects_disabled([self.obj_result])

    def hide_result(self):
        """Скрывает окно с результатами исследования

        :return:
        """
        if self.obj_result.is_enabled:
            self.obj_result.change_img('button_result.png', pw(10), ph(10))
            self.obj_result.go_to(pw(88), ph(87))
            self.text_result.hide()
            self.set_all_objects_enabled()

    def set_speed_25(self, *args):
        """Устанавливает скорость записи ЭКГ равную 25 мм/с

        :param args:
        :return:
        """
        self.mode_switcher.change_img('switch_mode.png', ph(14), ph(7))
        self.mode_switcher.function = self.set_speed_50
        self.graphic.speed_of_ecg = 25
        self.speed_reading = 25
        self.update_graph_data()

    def set_speed_50(self, *args):
        """Устанавливает скорость записи ЭКГ равную 50 мм/с

        :param args:
        :return:
        """
        self.mode_switcher.change_img('switch_mode_2.png', ph(14), ph(7))
        self.mode_switcher.function = self.set_speed_25
        self.graphic.speed_of_ecg = 50
        self.speed_reading = 50
        self.update_graph_data()

    def set_all_objects_disabled(self, list_of_exceptions=[]):
        """Всем объектам холста, кроме из списка исключений, присваивается неактивное состояние, т.е. они не реагируют
        на все взаимодействия

        :param list_of_exceptions: список объектов, которые не нужно "выключать"
        :return:
        """
        for group in self.all_groups:
            if group.visibility:
                group.set_disabled(list_of_exceptions)
        self.is_enabled = False

    def set_all_objects_enabled(self):
        """Всем объектам холста присваивается активное состояние

        :return:
        """
        for group in self.all_groups:
            if group.visibility:
                group.set_enabled()
        self.is_enabled = True
