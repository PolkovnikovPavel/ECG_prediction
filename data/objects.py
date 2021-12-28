import tkinter, random
from app_images.images import *


class Object:
    """Базовый класс графического объекта"""
    def __init__(self, x, y, w, h, img, canvas, visibility=True, container=[], mode_coord=False, is_enabled=True):
        """Конструктор базового класса графического объекта

        :param x: координата x расположения объекта на холсте
        :param y: координата y расположения объекта на холсте
        :param w: длина объекта
        :param h: ширина объекта
        :param img: картинка объекта (как объект изображения, либо название файла)
        :param canvas: холст
        :param visibility: логический параметр видимости объекта (True/False)
        :param container: контейнер
        :param mode_coord: режим координат
        :param is_enabled: состояние объекта (активное, неактивное), то есть, отвечает ли он на взаимодействие
        """
        self.container = container
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = 0
        self.name_img = None
        self.mode_coord = mode_coord
        if type(img) == str:
            self.name_img = img
            self.img, self.img_pil = get_image(img, w, h, mode=1)
        else:
            self.img = img
            self.img_pil = None
        self.img_pil_start = self.img_pil
        self.canvas = canvas
        self.visibility = visibility
        self.is_enabled = is_enabled
        if visibility:
            self.create_obj()

    def create_obj(self):
        """Создание объекта на холсте

        :return:
        """
        if isinstance(self.img, ImageTk.PhotoImage):
            if self.mode_coord:
                self.obj = self.canvas.create_image((self.x, self.y), image=self.img)
            else:
                self.obj = self.canvas.create_image((self.x + 0.5 * self.w, self.y + 0.5 * self.h), image=self.img)
        else:
            self.obj = self.img

    def change_img(self, new_img, w, h):
        """Меняет картинку объекта

        :param new_img:
        :param w:
        :param h:
        :return:
        """
        if not self.mode_coord:
            self.x -= (w - self.w) // 2
            self.y -= (h - self.h) // 2
        self.w = w
        self.h = h
        try:
            self.canvas.delete(self.obj)
        except Exception:
            pass

        if type(new_img) == str:
            self.name_img = new_img
            self.img, self.img_pil = get_image(new_img, w, h, mode=1)
        else:
            self.img = new_img
            self.img_pil = None
        self.img_pil_start = self.img_pil

        if self.visibility:
            self.create_obj()

    def go_to(self, x, y):
        """Изменяет положение объекта

        :param x: новая координата x
        :param y: новая координата y
        :return:
        """
        dx = x - self.x
        dy = y - self.y
        self.canvas.move(self.obj, dx, dy)
        self.x += dx
        self.y += dy

    def hide(self):
        """Скрывает объект

        :return:
        """
        self.canvas.delete(self.obj)
        self.visibility = False

    def show(self):
        """Показывает объект

        :return:
        """
        if not self.visibility:
            self.create_obj()
            self.visibility = True

    def reshow(self):
        """Скрывает и показывает объект

        :return:
        """
        self.hide()
        self.show()

    def rotation_on(self, angle):
        """Дополнительно поворачивает объект на определённый угол

        :param angle: угол
        :return:
        """
        self.angle += angle
        self.rotation(self.angle)

    def rotation(self, angle):
        """Поворачивает объект на определённый угол

        :param angle: угол
        :return:
        """
        self.angle = angle
        if self.img_pil is not None:
            self.img_pil = self.img_pil_start.rotate(self.angle)
            self.img = ImageTk.PhotoImage(self.img_pil)

            self.canvas.delete(self.obj)
            self.create_obj()

    def check_point(self, x, y):
        """Проверяет, относится ли данная точка к этому объекту

        :param x: координата x этой точки
        :param y: координата y это точки
        :return:
        """
        if self.mode_coord:
            if (self.x - (self.w / 2) <= x <= self.x + (self.w / 2) and
                    self.y - (self.h / 2) <= y <= self.y + (self.h / 2)):
                return True
        else:
            if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
                return True
        return False

    def set_disabled(self):
        """Изменяет состояние объекта на неактивное

        :return:
        """
        self.is_enabled = False

    def set_enabled(self):
        """Изменяет состояние объекта на активное

        :return:
        """
        self.is_enabled = True


class Button(Object):
    """Класс объекта кнопка"""
    def __init__(self, x, y, w, h, img, canvas, img2=None, function=None, args=[], visibility=True, container=[]):
        """Конструктор класса кнопка

        :param x: координата x расположения кнопки на холсте
        :param y: координата y расположения кнопки на холсте
        :param w: длина кнопки
        :param h: ширина кнопки
        :param img: картинка кнопки (как объект изображения, либо название файла)
        :param canvas: холст
        :param img2: картинка кнопки, после нажатия на неё
        :param function: та функция, которую будет выполнять эта кнопка
        :param args: дополнительные аргументы
        :param visibility: логический параметр видимости объекта (True/False)
        :param container: контейнер
        """
        Object.__init__(self, x, y, w, h, img, canvas, visibility=visibility, container=container)
        self.is_click = False
        if type(img2) == str:
            self.img2 = get_image(img2, w, h)
        else:
            self.img2 = img2
        self.function = function
        self.args = args

    def press(self):
        """При нажатии на кнопки, выполняется её функция

        :return:
        """
        if self.function is not None and self.is_enabled:
            self.function(self.args)

    def hide(self):
        """Скрывает данную точку

        :return:
        """
        Object.hide(self)
        self.is_click = False

    def show(self):
        """Показывает данную точку"""
        Object.show(self)
        self.is_click = False

    def check(self, x, y, is_click=True):
        """Проверяет, было ли нажатие на кнопку

        :param x: положение курсора по x
        :param y: положение курсора по y
        :param is_click: было ли совершено нажатие
        :return:
        """
        if not self.visibility:
            return
        if self.check_point(x, y):
            if is_click:
                if not self.is_click:
                    self.is_click = True
                    if self.img2 is not None and self.is_enabled:
                        self.canvas.delete(self.obj)
                        self.obj = self.canvas.create_image((self.x + 0.5 * self.w, self.y + 0.5 * self.h),
                                                            image=self.img2)

            else:
                if self.is_click:
                    self.is_click = False
                    if self.img2 is not None and self.is_enabled:
                        self.canvas.delete(self.obj)
                        self.create_obj()
                    self.press()
        else:
            if self.is_click:
                self.is_click = False
                if self.img2 is not None and self.is_enabled:
                    self.canvas.delete(self.obj)
                    self.create_obj()


class Text:
    """Класс текста, расположенного на холсте (не текстовое поле)"""
    def __init__(self, x, y, text, canvas, anchor='nw', font='Montserrat 25', visibility=True, color='black'):
        """Конструктор класса объекта текст

        :param x: координата x расположения текста на холсте
        :param y: координата y расположения текста на холсте
        :param text: текст, который будет выводиться
        :param canvas: холст
        :param anchor: положение якоря, определяется в сторонах света ('nw', 'e'...)
        :param font: характеристики шрифта текста
        :param visibility: логический параметр видимости объекта (True/False)
        :param color: цвет текста
        """
        self.color = color
        self.x = x
        self.y = y
        self.visibility = visibility
        self.text = text
        self.canvas = canvas
        self.font = font
        self.anchor = anchor
        if self.visibility:
            self.create_obj()
        else:
            self.obj = None

    def create_obj(self):
        """Создание текста на холсте

        :return:
        """
        self.obj = self.canvas.create_text(self.x, self.y, fill=self.color, font=self.font, text=self.text,
                                           anchor=self.anchor)

    def hide(self):
        """Скрывает текст

        :return:
        """
        self.canvas.delete(self.obj)
        self.visibility = False

    def show(self):
        """Показывает текст

        :return:
        """
        self.create_obj()
        self.visibility = True

    def reshow(self):
        """Скрывает и заново показывает текст

        :return:
        """
        self.canvas.delete(self.obj)
        self.create_obj()
        self.visibility = True

    def set_new_text(self, text):
        """Устанавливает новый текст

        :param text: новый текст объекта
        :return:
        """
        self.text = text
        if self.visibility:
            self.reshow()

    def go_to(self, x, y):
        """Перемещает текст по холсту

        :param x: новая координата x
        :param y: новая координата y
        :return:
        """
        dx = x - self.x
        dy = y - self.y
        self.canvas.move(self.obj, dx, dy)
        self.x += dx
        self.y += dy


class Group:
    """Класс объекта группа"""
    def __init__(self):
        """Конструктор класса группа"""
        self.all_objects = []
        self.visibility = True
        self.container = []

    def add_objects(self, *objects):
        """Добавляет в группу новые объекты

        :param objects: Объекты, которые нужно добавить в группу
        :return:
        """
        for object in objects:
            self.all_objects.append(object)

    def delete(self, *objects):
        """Удаляет из группы данные объекты

        :param objects: объекты, которые нужно удалить
        :return:
        """
        if len(objects) == 0:
            self.all_objects = []
        for object in objects:
            del self.all_objects[self.all_objects.index(object)]

    def hide_all(self):
        """Скрывает все объекты группы

        :return:
        """
        self.visibility = False
        for object in self.all_objects:
            object.hide()

    def all_move_on(self, dx, dy):
        """Перемещает все объекты группы

        :param dx: смещение по оси x
        :param dy: смещение по оси y
        :return:
        """
        for object in self.all_objects:
            object.go_to(object.x + dx, object.y + dy)

    def show_all(self):
        """Показывает все объекты

        :return:
        """
        self.visibility = True
        for object in self.all_objects:
            object.show()

    def check(self, x, y, is_click=True):
        """Проверяет, было ли совершенно нажатие на какой-либо объект из группы

        :param x: положение курсора по оси x
        :param y: положение курсора по оси y
        :param is_click: было ли совершенно нажатие
        :return:
        """
        if not self.visibility:
            return
        for object in self.all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic):
                object.check(x, y, is_click)

    def set_disabled(self, list_of_exceptions=[]):
        """Изменяет состояние каждого объекта группы, кроме объектов из списка исключений, на неактивное

        :param list_of_exceptions: список объектов-исключений
        :return:
        """
        if not self.visibility:
            return
        for object in self.all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic) or isinstance(object, Object):
                if len(list_of_exceptions) >= 1:
                    for i in list_of_exceptions:
                        if object != i:
                            object.set_disabled()
                        else:
                            list_of_exceptions.remove(i)
                else:
                    object.set_disabled()

    def set_enabled(self):
        """Изменяет состояние каждого объекта группы на активное

        :return:
        """
        if not self.visibility:
            return
        for object in self.all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic) or isinstance(object, Object):
                object.set_enabled()


class Point(Object):
    """Класс объекта точки на графике ЭКГ"""
    def __init__(self, x, y, w, h, canvas, type_point='R', point=(0, 0), visibility=True, container=[],
                 mode_coord=False, graphic=None):
        """Конструктор класса точка

        :param x: координата x расположения точки на холсте
        :param y: координата y расположения точки на холсте
        :param w: длина точки
        :param h: ширина точки
        :param canvas: холст
        :param type_point: тип точки из списка ключевых точек графика
        :param point: координата точки на изображении графика (не в окне программы)
        :param visibility: логический параметр видимости объекта (True/False)
        :param container: контейнер
        :param mode_coord: режим координат
        :param graphic: объект Graphic, на котором есть эта точка
        """
        self.__names = {'R': 'point_r_image.png',
                        'Q': 'point_q_image.png',
                        'S': 'point_s_image.png',
                        'T': 'point_t_image.png',
                        'P': 'point_p_image.png',
                        'LP': 'point_lp_image.png',
                        'RS': 'point_rs_image.png',
                        'LT': 'point_lt_image.png',
                        'RT': 'point_rt_image.png'}
        super().__init__(x, y, w, h, self.__names[type_point], canvas, visibility, container, mode_coord)
        self.is_moving = False
        self.type_point = type_point
        self.point = [point[0], point[1]]
        self.graphic = graphic
        self.old_x = x
        self.old_y = y
        self.is_hurt_trash = False
        self.start_x = 0
        self.start_y = 0
        self.id = None

    def check(self, x, y, is_click=True, is_taken_one=False):
        """Проверяет, были ли совершенно нажатие на точку

        :param x: положение курсора по x
        :param y: положение курсора по y
        :param is_click: было ли совершенно нажатие
        :param is_taken_one: выбрана ли точка
        :return:
        """
        if not self.visibility:
            return

        if self.is_enabled:
            if self.is_moving:
                if is_click:
                    self.go_to(x, y)
                else:
                    if self.graphic.trash.check_point(self.x, self.y):
                        self.graphic.del_point(self)
                        self.hide()
                        self.graphic.scan_graphic()
                        return

                    self.is_moving = False
                    self.go_to(x, y)
                    dx, dy = x - self.old_x, y - self.old_y
                    self.point[0] += dx * (self.graphic.img_w / self.graphic.w)
                    self.point[1] += dy * (self.graphic.img_h / self.graphic.h)
                    self.graphic.scan_graphic()
            else:
                if is_click:
                    if self.check_point(x, y) and not is_taken_one and not self.graphic.point_is_taken:
                        self.is_moving = True
                        self.graphic.point_is_taken = True
                        self.old_x = x
                        self.old_y = y

    def get_cor_point(self):
        """Возвращает координаты точки

        :return: (координаты точки)
        """
        return self.point


class ObjectGraphic:
    """Класс, который графически отображает ЭКГ: фотографию графика, ключевые точки и кнопки для добавления новых
    точек"""
    def __init__(self, canvas, graphic, path_to_file, x=0, y=0, w=1280, h=600, visibility=True, scan_graphic=None,
                 is_enabled=True):
        """Конструктор класса

        :param canvas: холст
        :param graphic: объект класса Graphic
        :param path_to_file: путь к фотографии ЭКГ
        :param x: координата x расположения объекта на холсте
        :param y: координата y расположения объекта на холсте
        :param w: длина объекта
        :param h: ширина объекта
        :param visibility: логический параметр видимости объекта (True/False)
        :param scan_graphic: функция, которая отвечает за обновление объекта на холсте
        :param is_enabled: состояние объекта (активный, неактивный)
        """
        self.canvas = canvas
        self.graphic = graphic
        self.path_to_file = path_to_file
        self.visibility = visibility
        self.group = Group()
        self.adding_group = Group()
        self.scan_graphic = scan_graphic
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.is_click = False
        self.point_is_taken = False
        im = Image.open(self.path_to_file)
        self.img_w, self.img_h = im.size
        self.dict_of_points = {'R': [],
                               'Q': [],
                               'S': [],
                               'T': [],
                               'P': [],
                               'LP': [],
                               'RS': [],
                               'LT': [],
                               'RT': []}
        self.is_enabled = is_enabled

        self.create_all_obj()

    def create_all_obj(self):
        """Создаёт все объекты

        :return:
        """
        obj = Object(self.x, self.y, self.w, self.h, self.path_to_file, self.canvas)
        self.group.add_objects(obj)
        self.trash = Object(0, ph(85), pw(105), ph(20), 'air.png', self.canvas, False)
        self.group.add_objects(self.trash)

        for key in self.dict_of_points:
            it_var = 0
            for point in self.graphic.dict_of_points[key]:
                x, y = (point[0]) * (self.w / self.img_w), point[1] * (self.h / self.img_h)
                x, y = x + self.x, y + self.y
                obj = Point(x, y, ph(4), ph(4), self.canvas, key, point, mode_coord=True, graphic=self)
                obj.id = it_var  # С помощью задания этого идентификатора здесь можно будет отслеживать добавленные
                # пользователем точки
                it_var += 1
                self.group.add_objects(obj)
                self.dict_of_points[key].append(obj)

        obj = Object(pw(19), ph(87), ph(10), ph(10), 'add_point_lp.png', self.canvas, container=['LP'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(26), ph(87), ph(10), ph(10), 'add_point_p.png', self.canvas, container=['P'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(33), ph(87), ph(10), ph(10), 'add_point_q.png', self.canvas, container=['Q'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(40), ph(87), ph(10), ph(10), 'add_point_r.png', self.canvas, container=['R'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(47), ph(87), ph(10), ph(10), 'add_point_s.png', self.canvas, container=['S'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(54), ph(87), ph(10), ph(10), 'add_point_rs.png', self.canvas, container=['RS'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(61), ph(87), ph(10), ph(10), 'add_point_lt.png', self.canvas, container=['LT'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(68), ph(87), ph(10), ph(10), 'add_point_t.png', self.canvas, container=['T'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(75), ph(87), ph(10), ph(10), 'add_point_rt.png', self.canvas, container=['RT'])
        self.adding_group.add_objects(obj)

    def temporarily_hide_points(self, *args):
        """Скрывает точки при нажатии кнопки

        :param args:
        :return:
        """
        obj = args[0]
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                point.hide()
        obj.function = self.temporarily_show_points
        obj.change_img('hide_points_2.png', ph(5), ph(5))

    def temporarily_show_points(self, *args):
        """Показывает точки повторном нажатии кнопки

        :param args:
        :return:
        """
        obj = args[0]
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                point.show()
        obj.function = self.temporarily_hide_points
        obj.change_img('hide_points.png', ph(5), ph(5))

    def del_point(self, point):
        """Удаляет точку

        :param point: объект Point
        :return:
        """
        cor_point = point.point
        for key in self.dict_of_points:
            new_list = []
            for p in self.dict_of_points[key]:
                if p.point == cor_point:
                    point.hide()
                    del point
                else:
                    new_list.append(p)
            self.dict_of_points[key] = new_list

    def reset_all_points(self):
        """При перезапуске графика эта процедура удаляет все добавленные пользователем точки и добавляет все удалённые

        :return:
        """
        # Этот цикл удаляет все точки, добавленные пользователем. Эти точки не имеют у себя значения id. Это значение
        # появляется только при создании точек в начале обработки
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                if point.id is None:
                    try:
                        self.del_point(point)
                    except:
                        pass

        for key in self.dict_of_points:
            for i in range(len(self.graphic.dict_of_points[key])):
                try:
                    obj = self.dict_of_points[key][i]
                except IndexError:
                    # Обработчик ошибок на случай, если пользователь удалил крайнюю точку
                    point = self.graphic.dict_of_points[key][i]
                    x, y = (point[0]) * (self.w / self.img_w), point[1] * (self.h / self.img_h)
                    x, y = x + self.x, y + self.y
                    self.dict_of_points[key].insert(i, Point(x, y, ph(4), ph(4), self.canvas, key,
                                                             self.graphic.dict_of_points[key][i], mode_coord=True,
                                                             graphic=self))
                    self.dict_of_points[key][i].id = i
                    pass
                else:
                    # Проверка, соответствует ли идентификатор точки её порядковому номеру
                    if obj.id == i:
                        # Если соответствует, то значит её нужно просто передвинуть
                        point = self.graphic.dict_of_points[key][i]
                        x, y = (point[0]) * (self.w / self.img_w), point[1] * (self.h / self.img_h)
                        x, y = x + self.x, y + self.y
                        obj.go_to(x, y)
                        # obj.start_x, obj.start_y = point[0], point[1]
                        obj.point[0], obj.point[1] = point[0], point[1]
                    elif obj.id is not None:
                        # Если соответствия нет, видимо пользователь удалил одну из точек. Необходимо добавить новую
                        # точку в словарь точек
                        point = self.graphic.dict_of_points[key][i]
                        x, y = (point[0]) * (self.w / self.img_w), point[1] * (self.h / self.img_h)
                        x, y = x + self.x, y + self.y
                        self.dict_of_points[key].insert(i, Point(x, y, ph(4), ph(4), self.canvas, key,
                                                                 self.graphic.dict_of_points[key][i], mode_coord=True,
                                                                 graphic=self))
                        self.dict_of_points[key][i].id = i

    def show(self):
        """Показывает объект

        :return:
        """
        self.visibility = True
        self.group.show_all()
        self.adding_group.show_all()

    def hide(self):
        """Скрывает объект

        :return:
        """
        self.visibility = False
        self.group.hide_all()
        self.adding_group.hide_all()

    def check_point(self, x, y):
        """Проверка, находится ли точка на графике

        :param x: координата x
        :param y: координата y
        :return:
        """
        if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
            return True
        return False

    def check(self, x, y, is_click=True):
        """Проверяет, было ли нажатие на точки либо на кнопки по добавлению точек

        :param x: положение курсора по x
        :param y: положение курсора по y
        :param is_click: было ли совершенно нажатие
        :return:
        """
        if not self.visibility:
            return
        is_taken_one = False
        if is_click:
            for key in self.dict_of_points:
                for point in self.dict_of_points[key]:
                    if point.is_moving:
                        is_taken_one = True
                        break
            if not is_taken_one:
                self.point_is_taken = False
                for btn in self.adding_group.all_objects:
                    if btn.check_point(x, y) and btn.is_enabled:
                        type_p = btn.container[0]
                        px, py = x // (self.w / self.img_w), y // (self.h / self.img_h)
                        obj = Point(x, y, ph(4), ph(4), self.canvas, type_p, (px, py), mode_coord=True, graphic=self)
                        obj.is_moving = True
                        self.dict_of_points[type_p].append(obj)
                        self.group.add_objects(obj)

        for key in list(self.dict_of_points.keys())[::-1]:
            for point in self.dict_of_points[key]:
                point.check(x, y, is_click, is_taken_one)

        self.is_click = is_click

    def set_disabled(self):
        """Устанавливает для всех кнопок для добавления точек и для самих точек неактивное состояние

        :return:
        """
        self.adding_group.set_disabled()
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                point.set_disabled()
        self.is_enabled = False

    def set_enabled(self):
        """Устанавливает для всех кнопок для добавления точек и для самих точек активное состояние

        :return:
        """
        self.adding_group.set_enabled()
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                point.set_enabled()
        self.is_enabled = True


class TextArea(Object):
    """Класс объекта текстового окна на холсте"""
    def __init__(self, x, y, w, h, canvas, visibility=True, anchor='nw', bg_color='white', font=('Montserrat', 25),
                 font_color='black', border_width=0, wrap_type='word'):
        """Этот класс создаёт поле с текстом

        :param x: координата x якоря
        :param y: координата y якоря
        :param w: ширина текстового блока в количестве символов
        :param h: высота текстового блока в количестве символов
        :param canvas: холст
        :param visibility: логический параметр видимости объекта (True/False)
        :param anchor: положение якоря, определяется в сторонах света ('nw', 'e'...)
        :param bg_color: цвет заднего фона
        :param font: тип размер, начертание шрифта ("тип", размер, "начертание")
        :param font_color: цвет шрифта
        :param border_width: ширина границы текстового окна
        :param wrap_type: перенос строки ('char', 'none', 'word')
        :return:
        """
        self.anchor = anchor
        self.bg_color = bg_color
        self.font = font
        self.font_color = font_color
        self.border_width = border_width
        self.text_box = None
        self.wrap_type = wrap_type
        self.window = None
        super().__init__(x, y, w, h, None, canvas, visibility)

    def create_obj(self):
        """Создание текстового окна на холсте

        :return:
        """
        frame = tkinter.Frame(self.canvas, background='#000000')

        scrollbar = tkinter.Scrollbar(frame)
        self.text_box = tkinter.Text(frame, height=self.h, width=self.w, bd=self.border_width,
                                     wrap=self.wrap_type, yscrollcommand=scrollbar.set, font=self.font,
                                     background=self.bg_color, foreground=self.font_color)
        scrollbar.configure(command=self.text_box.yview)
        scrollbar.pack(side='right', fill='y')
        self.text_box.pack(anchor=self.anchor)

        self.window = self.canvas.create_window(self.x, self.y, anchor=self.anchor, window=frame)

    def check(self, x, y, is_click):
        if self.visibility is False:
            return
        if is_click:
            self.hide()

    def insert_text(self, text):
        """Вставляет текст из аргумента в текстовое поле

        :param text: текст для вставки
        :return:
        """
        self.text_box.insert(1.0, text)

    def change_window_state(self, state='disabled'):
        """Изменяет состояния окна

        :param state: состояние окна (normal/disabled)
        :return:
        """
        if state is 'disabled':
            self.text_box.configure(state='disabled')
        elif state is 'normal':
            self.text_box.configure(state='normal')

    def hide(self):
        """Скрывает объект

        :return:
        """
        self.canvas.delete(self.window)
        self.text_box = None
        self.window = None
        self.visibility = False

    def show(self):
        """Показывает объект, если это допустимо

        :return:
        """
        if self.visibility:
            self.create_obj()
            self.visibility = True
