import tkinter
from tkinter import messagebox as mb
from app_images.images import *
import re


class Object:
    """Базовый класс графического объекта"""

    def __init__(self, x, y, w, h, img, canvas, visibility=True, container=[], mode_coord=False, is_enabled=True,
                 anchor='nw'):
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
        self._obj = None  # "ленивая загрузка", смотрите create_obj
        self._container = container
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._angle = 0
        self._name_img = None
        self._mode_coord = mode_coord
        if type(img) == str:
            self._name_img = img
            self._img, self._img_pil = get_image(img, w, h, mode=1)
        else:
            self._img = img
            self._img_pil = None
        self._img_pil_start = self._img_pil
        self._canvas = canvas
        self._anchor = anchor
        self._visibility = visibility
        self._is_enabled = is_enabled
        if visibility:
            self._create_obj()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def w(self):
        return self._w

    @property
    def h(self):
        return self._h

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        if isinstance(value, bool):
            self._visibility = value
        else:
            print("Некорректное значение. Ожидалось логическое значение.")

    @property
    def is_enabled(self):
        return self._is_enabled

    @property
    def container(self):
        return self._container

    def _create_obj(self):
        """Создание объекта на холсте

        :return:
        """
        if isinstance(self._img, ImageTk.PhotoImage):
            if self._mode_coord:
                self._obj = self._canvas.create_image((self._x, self._y), image=self._img)
            else:
                self._obj = self._canvas.create_image((self._x, self._y), image=self._img,
                                                      anchor=self._anchor)
        else:
            self._obj = self._img

    def change_img(self, new_img, w, h):
        """Меняет картинку объекта

        :param new_img:
        :param w:
        :param h:
        :return:
        """
        if not self._mode_coord:
            self._x -= (w - self._w) // 2
            self._y -= (h - self._h) // 2
        self._w = w
        self._h = h
        try:
            self._canvas.delete(self._obj)
        except:
            pass

        if type(new_img) == str:
            self._name_img = new_img
            self._img, self._img_pil = get_image(new_img, w, h, mode=1)
        else:
            self._img = new_img
            self._img_pil = None
        self._img_pil_start = self._img_pil

        if self.visibility:
            self._create_obj()

    def go_to(self, x, y):
        """Изменяет положение объекта

        :param x: новая координата x
        :param y: новая координата y
        :return:
        """
        dx = x - self._x
        dy = y - self._y
        self._canvas.move(self._obj, dx, dy)
        self._x += dx
        self._y += dy

    def hide(self):
        """Скрывает объект

        :return:
        """
        self._canvas.delete(self._obj)
        self.visibility = False

    def show(self):
        """Показывает объект, при условии, что он уже не показан

        :return:
        """
        if self.visibility is False:
            self._create_obj()
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
        self._angle += angle
        self.rotation(self._angle)

    def rotation(self, angle):
        """Поворачивает объект на определённый угол

        :param angle: угол
        :return:
        """
        self._angle = angle
        if self._img_pil is not None:
            self._img_pil = self._img_pil_start.rotate(self._angle)
            self._img = ImageTk.PhotoImage(self._img_pil)

            self._canvas.delete(self._obj)
            self._create_obj()

    def check_point(self, x, y):
        """Проверяет, относится ли данная точка к этому объекту

        :param x: координата x этой точки
        :param y: координата y это точки
        :return:
        """
        if self._mode_coord:
            if (self._x - (self._w / 2) <= x <= self._x + (self._w / 2) and
                    self._y - (self._h / 2) <= y <= self._y + (self._h / 2)):
                return True
        else:
            if self._x <= x <= self._x + self._w and self._y <= y <= self._y + self._h:
                return True
        return False

    def set_disabled(self):
        """Изменяет состояние объекта на неактивное

        :return:
        """
        self._is_enabled = False

    def set_enabled(self):
        """Изменяет состояние объекта на активное

        :return:
        """
        self._is_enabled = True


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
        self.__is_click = False
        if type(img2) == str:
            self.__img2 = get_image(img2, w, h)
        else:
            self.__img2 = img2
        self.__function = function
        self.args = args

    @property
    def function(self):
        return self.__function

    @function.setter
    def function(self, value):
        self.__function = value

    def press(self):
        """При нажатии на кнопки, выполняется её функция

        :return:
        """
        if self.__function is not None and self._is_enabled:
            self.__function(self.args)

    def hide(self):
        """Скрывает данную точку

        :return:
        """
        Object.hide(self)
        self.__is_click = False

    def show(self):
        """Показывает данную точку"""
        Object.show(self)
        self.__is_click = False

    def check(self, x, y, is_click=True):
        """Проверяет, было ли нажатие на кнопку

        :param x: положение курсора по x
        :param y: положение курсора по y
        :param is_click: было ли совершено нажатие
        :return:
        """
        if self._visibility is False:
            return
        if self.check_point(x, y):
            if is_click:
                if not self.__is_click:
                    self.__is_click = True
                    if self.__img2 is not None and self._is_enabled:
                        self._canvas.delete(self._obj)
                        self._obj = self._canvas.create_image((self._x + 0.5 * self._w, self._y + 0.5 * self._h),
                                                              image=self.__img2)

            else:
                if self.__is_click:
                    self.__is_click = False
                    if self.__img2 is not None and self._is_enabled:
                        self._canvas.delete(self._obj)
                        self._create_obj()
                    self.press()
        else:
            if self.__is_click:
                self.__is_click = False
                if self.__img2 is not None and self._is_enabled:
                    self._canvas.delete(self._obj)
                    self._create_obj()


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
        self.__obj = None
        self.__color = color
        self.__x = x
        self.__y = y
        self.__visibility = visibility
        self.__text = text
        self.__canvas = canvas
        self.__font = font
        self.__anchor = anchor
        if self.__visibility:
            self.__create_obj()

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    @property
    def visibility(self):
        return self.__visibility

    @visibility.setter
    def visibility(self, value):
        self.__visibility = value

    def __create_obj(self):
        """Создание текста на холсте

        :return:
        """
        self.__obj = self.__canvas.create_text(self.__x, self.__y, fill=self.__color, font=self.__font, text=self.__text,
                                               anchor=self.__anchor)

    def hide(self):
        """Скрывает текст

        :return:
        """
        self.__canvas.delete(self.__obj)
        self.__visibility = False

    def show(self):
        """Показывает текст, при условии, что он уже не показан

        :return:
        """
        if self.__visibility is False:
            self.__create_obj()
            self.__visibility = True

    def reshow(self):
        """Скрывает и заново показывает текст

        :return:
        """
        self.__canvas.delete(self.__obj)
        self.__create_obj()
        self.__visibility = True

    def set_new_text(self, text):
        """Устанавливает новый текст

        :param text: новый текст объекта
        :return:
        """
        self.__text = text
        if self.__visibility:
            self.reshow()

    def go_to(self, x, y):
        """Перемещает текст по холсту

        :param x: новая координата x
        :param y: новая координата y
        :return:
        """
        dx = x - self.__x
        dy = y - self.__y
        self.__canvas.move(self.__obj, dx, dy)
        self.__x += dx
        self.__y += dy


class Group:
    """Класс объекта группа"""

    def __init__(self):
        """Конструктор класса группа"""
        self.__all_objects = []
        self.__visibility = True
        self.__container = []

    @property
    def all_objects(self):
        return self.__all_objects

    @property
    def visibility(self):
        return self.__visibility

    def add_objects(self, *objects):
        """Добавляет в группу новые объекты

        :param objects: Объекты, которые нужно добавить в группу
        :return:
        """
        for object in objects:
            self.__all_objects.append(object)

    def delete(self, *objects):
        """Удаляет из группы данные объекты

        :param objects: объекты, которые нужно удалить
        :return:
        """
        if len(objects) == 0:
            self.__all_objects = []
        for object in objects:
            del self.__all_objects[self.__all_objects.index(object)]

    def hide_all(self):
        """Скрывает все объекты группы

        :return:
        """
        self.__visibility = False
        for object in self.__all_objects:
            object.hide()

    def all_move_on(self, dx, dy):
        """Перемещает все объекты группы

        :param dx: смещение по оси x
        :param dy: смещение по оси y
        :return:
        """
        for object in self.__all_objects:
            object.go_to(object.__x + dx, object.__y + dy)

    def show_all(self):
        """Показывает все объекты

        :return:
        """
        self.__visibility = True
        for object in self.__all_objects:
            object.show()

    def check(self, x, y, is_click=True):
        """Проверяет, было ли совершенно нажатие на какой-либо объект из группы

        :param x: положение курсора по оси x
        :param y: положение курсора по оси y
        :param is_click: было ли совершенно нажатие
        :return:
        """
        if not self.__visibility:
            return
        for object in self.__all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic) or isinstance(object, CropClass) or \
                    isinstance(object, CroppingPlate):
                object.check(x, y, is_click)

    def set_disabled(self, list_of_exceptions=[]):
        """Изменяет состояние каждого объекта группы, кроме объектов из списка исключений, на неактивное

        :param list_of_exceptions: список объектов-исключений
        :return:
        """
        if not self.__visibility:
            return
        for object in self.__all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic) or isinstance(object, Object) or \
                    isinstance(object, CroppingPlate) or isinstance(object, CropClass):
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
        if not self.__visibility:
            return
        for object in self.__all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic) or isinstance(object, Object) or \
                    isinstance(object, CroppingPlate) or isinstance(object, CropClass):
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
        self.__is_moving = False
        self.__type_point = type_point
        self.__point = [point[0], point[1]]
        self.graphic = graphic
        self.__old_x = x
        self.__old_y = y
        self.__is_hurt_trash = False
        self.__id = None

    @property
    def point(self):
        return self.__point

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def is_moving(self):
        return self.__is_moving

    def check(self, x, y, is_click=True, is_taken_one=False):
        """Проверяет, были ли совершенно нажатие на точку

        :param x: положение курсора по x
        :param y: положение курсора по y
        :param is_click: было ли совершенно нажатие
        :param is_taken_one: выбрана ли точка
        :return:
        """
        if self._visibility is False:
            return

        if self._is_enabled:
            if self.__is_moving:
                if is_click:
                    self.go_to(x, y)
                else:
                    if self.graphic.trash.check_point(self._x, self._y):
                        self.graphic.del_point(self)
                        self.hide()
                        self.graphic.scan_graphic()
                        return

                    self.__is_moving = False
                    self.go_to(x, y)
                    dx, dy = x - self.__old_x, y - self.__old_y
                    self.__point[0] += dx * (self.graphic.img_w / self.graphic.w)
                    self.__point[1] += dy * (self.graphic.img_h / self.graphic.h)
                    self.graphic.scan_graphic()
            else:
                if is_click:
                    if self.check_point(x, y) and not is_taken_one and not self.graphic.point_is_taken:
                        self.__is_moving = True
                        self.graphic.point_is_taken = True
                        self.__old_x = x
                        self.__old_y = y

    def get_cor_point(self):
        """Возвращает координаты точки

        :return: (координаты точки)
        """
        return self.__point


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
        self.__trash = None  # Ленивая загрузка
        self.__canvas = canvas
        self.__graphic = graphic
        self.__path_to_file = path_to_file
        self.__visibility = visibility
        self.__group = Group()
        self.__adding_group = Group()
        self.__scan_graphic = scan_graphic
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h
        self.__is_click = False
        self.__point_is_taken = False
        im = Image.open(self.__path_to_file)
        self.__img_w, self.__img_h = im.size
        self.__dict_of_points = {'R': [],
                                 'Q': [],
                                 'S': [],
                                 'T': [],
                                 'P': [],
                                 'LP': [],
                                 'RS': [],
                                 'LT': [],
                                 'RT': []}
        self.__is_enabled = is_enabled

        self.__create_all_obj()

    @property
    def trash(self):
        return self.__trash

    @property
    def visibility(self):
        return self.__visibility

    @visibility.setter
    def visibility(self, value):
        self.__visibility = value

    @property
    def w(self):
        return self.__w

    @property
    def h(self):
        return self.__h

    @property
    def point_is_taken(self):
        return self.__point_is_taken

    @point_is_taken.setter
    def point_is_taken(self, value):
        self.__point_is_taken = value

    @property
    def img_w(self):
        return self.__img_w

    @property
    def img_h(self):
        return self.__img_h

    @property
    def dict_of_points(self):
        return self.__dict_of_points

    @property
    def scan_graphic(self):
        return self.__scan_graphic

    def __create_all_obj(self):
        """Создаёт все объекты

        :return:
        """
        obj = Object(self.__x, self.__y, self.__w, self.__h, self.__path_to_file, self.__canvas)
        self.__group.add_objects(obj)
        self.__trash = Object(0, ph(85), pw(105), ph(20), 'air.png', self.__canvas, False)
        self.__group.add_objects(self.__trash)

        for key in self.__dict_of_points:
            it_var = 0
            for point in self.__graphic.dict_of_points[key]:
                x, y = (point[0]) * (self.__w / self.__img_w), point[1] * (self.__h / self.__img_h)
                x, y = x + self.__x, y + self.__y
                obj = Point(x, y, ph(4), ph(4), self.__canvas, key, point, mode_coord=True, graphic=self)
                obj.__id = it_var  # С помощью задания этого идентификатора здесь можно будет отслеживать добавленные
                # пользователем точки
                it_var += 1
                self.__group.add_objects(obj)
                self.__dict_of_points[key].append(obj)

        obj = Object(pw(19), ph(87), ph(10), ph(10), 'add_point_lp.png', self.__canvas, container=['LP'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(26), ph(87), ph(10), ph(10), 'add_point_p.png', self.__canvas, container=['P'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(33), ph(87), ph(10), ph(10), 'add_point_q.png', self.__canvas, container=['Q'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(40), ph(87), ph(10), ph(10), 'add_point_r.png', self.__canvas, container=['R'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(47), ph(87), ph(10), ph(10), 'add_point_s.png', self.__canvas, container=['S'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(54), ph(87), ph(10), ph(10), 'add_point_rs.png', self.__canvas, container=['RS'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(61), ph(87), ph(10), ph(10), 'add_point_lt.png', self.__canvas, container=['LT'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(68), ph(87), ph(10), ph(10), 'add_point_t.png', self.__canvas, container=['T'])
        self.__adding_group.add_objects(obj)
        obj = Object(pw(75), ph(87), ph(10), ph(10), 'add_point_rt.png', self.__canvas, container=['RT'])
        self.__adding_group.add_objects(obj)

    def temporarily_hide_points(self, *args):
        """Скрывает точки при нажатии кнопки

        :param args:
        :return:
        """
        obj = args[0]
        for key in self.__dict_of_points:
            for point in self.__dict_of_points[key]:
                point.hide()
        obj.function = self.temporarily_show_points
        obj.change_img('hide_points_2.png', ph(5), ph(5))

    def temporarily_show_points(self, *args):
        """Показывает точки повторном нажатии кнопки

        :param args:
        :return:
        """
        obj = args[0]
        for key in self.__dict_of_points:
            for point in self.__dict_of_points[key]:
                point.show()
        obj.function = self.temporarily_hide_points
        obj.change_img('hide_points.png', ph(5), ph(5))

    def del_point(self, point):
        """Удаляет точку

        :param point: объект Point
        :return:
        """
        cor_point = point.point
        for key in self.__dict_of_points:
            new_list = []
            for p in self.__dict_of_points[key]:
                if p.point == cor_point:
                    point.hide()
                    del point
                else:
                    new_list.append(p)
            self.__dict_of_points[key] = new_list

    def reset_all_points(self):
        """При перезапуске графика эта процедура удаляет все добавленные пользователем точки и добавляет все удалённые

        :return:
        """
        # Этот цикл удаляет все точки, добавленные пользователем. Эти точки не имеют у себя значения id. Это значение
        # появляется только при создании точек в начале обработки
        for key in self.__dict_of_points:
            for point in self.__dict_of_points[key]:
                if point.id is None:
                    try:
                        self.del_point(point)
                    except:
                        pass

        for key in self.__dict_of_points:
            for i in range(len(self.__graphic.dict_of_points[key])):
                try:
                    obj = self.__dict_of_points[key][i]
                except IndexError:
                    # Обработчик ошибок на случай, если пользователь удалил крайнюю точку
                    point = self.__graphic.dict_of_points[key][i]
                    x, y = (point[0]) * (self.__w / self.__img_w), point[1] * (self.__h / self.__img_h)
                    x, y = x + self.__x, y + self.__y
                    self.__dict_of_points[key].insert(i, Point(x, y, ph(4), ph(4), self.__canvas, key,
                                                               self.__graphic.dict_of_points[key][i], mode_coord=True,
                                                               graphic=self))
                    self.__dict_of_points[key][i].id = i
                    pass
                else:
                    # Проверка, соответствует ли идентификатор точки её порядковому номеру
                    if obj.id == i:
                        # Если соответствует, то значит её нужно просто передвинуть
                        point = self.__graphic.dict_of_points[key][i]
                        x, y = (point[0]) * (self.__w / self.__img_w), point[1] * (self.__h / self.__img_h)
                        x, y = x + self.__x, y + self.__y
                        obj.go_to(x, y)
                        obj.point[0], obj.point[1] = point[0], point[1]
                    elif obj.id is not None:
                        # Если соответствия нет, видимо пользователь удалил одну из точек. Необходимо добавить новую
                        # точку в словарь точек
                        point = self.__graphic.dict_of_points[key][i]
                        x, y = (point[0]) * (self.__w / self.__img_w), point[1] * (self.__h / self.__img_h)
                        x, y = x + self.__x, y + self.__y
                        self.__dict_of_points[key].insert(i, Point(x, y, ph(4), ph(4), self.__canvas, key,
                                                                   self.__graphic.dict_of_points[key][i], mode_coord=True,
                                                                   graphic=self))
                        self.__dict_of_points[key][i].id = i

    def show(self):
        """Показывает график

        :return:
        """
        self.__visibility = True
        self.__group.show_all()
        self.__adding_group.show_all()

    def hide(self):
        """Скрывает объект

        :return:
        """
        self.__visibility = False
        self.__group.hide_all()
        self.__adding_group.hide_all()

    def check_point(self, x, y):
        """Проверка, находится ли точка на графике

        :param x: координата x
        :param y: координата y
        :return:
        """
        if self.__x <= x <= self.__x + self.__w and self.__y <= y <= self.__y + self.__h:
            return True
        return False

    def check(self, x, y, is_click=True):
        """Проверяет, было ли нажатие на точки либо на кнопки по добавлению точек

        :param x: положение курсора по x
        :param y: положение курсора по y
        :param is_click: было ли совершенно нажатие
        :return:
        """
        if not self.__visibility:
            return
        is_taken_one = False
        if is_click:
            for key in self.__dict_of_points:
                for point in self.__dict_of_points[key]:
                    if point.is_moving:
                        is_taken_one = True
                        break
            if not is_taken_one:
                self.__point_is_taken = False
                for btn in self.__adding_group.all_objects:
                    if btn.check_point(x, y) and btn.is_enabled:
                        type_p = btn.container[0]
                        px, py = x // (self.__w / self.__img_w), y // (self.__h / self.__img_h)
                        obj = Point(x, y, ph(4), ph(4), self.__canvas, type_p, (px, py), mode_coord=True, graphic=self)
                        obj.__is_moving = True
                        self.__dict_of_points[type_p].append(obj)
                        self.__group.add_objects(obj)

        for key in list(self.__dict_of_points.keys())[::-1]:
            for point in self.__dict_of_points[key]:
                point.check(x, y, is_click, is_taken_one)

        self.__is_click = is_click

    def set_disabled(self):
        """Устанавливает для всех кнопок для добавления точек и для самих точек неактивное состояние

        :return:
        """
        self.__adding_group.set_disabled()
        for key in self.__dict_of_points:
            for point in self.__dict_of_points[key]:
                point.set_disabled()
        self.__is_enabled = False

    def set_enabled(self):
        """Устанавливает для всех кнопок для добавления точек и для самих точек активное состояние

        :return:
        """
        self.__adding_group.set_enabled()
        for key in self.__dict_of_points:
            for point in self.__dict_of_points[key]:
                point.set_enabled()
        self.__is_enabled = True


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
        :param visibility: разрешение на отображение этого объекта
        :param anchor: положение якоря, определяется в сторонах света ('nw', 'e'...)
        :param bg_color: цвет заднего фона
        :param font: тип размер, начертание шрифта ("тип", размер, "начертание")
        :param font_color: цвет шрифта
        :param border_width: ширина границы текстового окна
        :param wrap_type: перенос строки ('char', 'none', 'word')
        :return:
        """
        self.__anchor = anchor
        self.__bg_color = bg_color
        self.__font = font
        self.__font_color = font_color
        self.__border_width = border_width
        self.__text_box = None
        self.__wrap_type = wrap_type
        self.__window = None
        super().__init__(x, y, w, h, None, canvas, visibility)

    def _create_obj(self):
        """Создание текстового окна на холсте

        :return:
        """
        frame = tkinter.Frame(self._canvas, background='#000000')

        scrollbar = tkinter.Scrollbar(frame)
        self.__text_box = tkinter.Text(frame, height=self._h, width=self._w, bd=self.__border_width,
                                       wrap=self.__wrap_type, yscrollcommand=scrollbar.set, font=self.__font,
                                       background=self.__bg_color, foreground=self.__font_color)
        scrollbar.configure(command=self.__text_box.yview)
        scrollbar.pack(side='right', fill='y')
        self.__text_box.pack()

        self.__window = self._canvas.create_window(self._x, self._y, anchor=self.__anchor, window=frame)

    def check(self, is_click):
        if self.visibility is False:
            return
        if is_click:
            self.hide()

    def insert_text(self, text):
        """Вставляет текст из аргумента в текстовое поле

        :param text: текст для вставки
        :return:
        """
        self.__text_box.insert(1.0, text)

    def change_window_state(self, state='disabled'):
        """Изменяет состояния окна

        :param state: состояние окна (normal/disabled)
        :return:
        """
        if state == 'disabled':
            self.__text_box.configure(state='disabled')
        elif state == 'normal':
            self.__text_box.configure(state='normal')

    def hide(self):
        """Скрывает объект

        :return:
        """
        self._canvas.delete(self.__window)
        self.__text_box = None
        self.__window = None
        self.visibility = False

    def show(self):
        """Показывает объект, если это допустимо

        :return:
        """
        if self.visibility:
            self._create_obj()
            self.visibility = True


class CroppingPlate(Object):
    """Класс панели для кадрирования изображений"""

    def __init__(self, x, y, w, h, img, canvas, type_of_plate='upper'):
        """Конструктор класса панели кадрирования

        :param x: координата x этой панели (учитывайте якорь!)
        :param y: координата y этой панели (учитывайте якорь!)
        :param w: ширина этой панели (стандартно - 100%)
        :param h: ширина этой панели (стандартно - 100%)
        :param img: изображение панели
        :param canvas: холст
        :param type_of_plate: тип панели (upper, lower, left, right)
        """
        anchor = ''
        self.__type_of_plate = type_of_plate
        if self.__type_of_plate == 'upper' or self.__type_of_plate == 'lower':
            self.__locked_coord = 'x'
            if self.__type_of_plate == 'upper':
                anchor = 'sw'
            else:
                anchor = 'nw'
        elif self.__type_of_plate == 'left' or self.__type_of_plate == 'right':
            self.__locked_coord = 'y'
            if self.__type_of_plate == 'left':
                anchor = 'ne'
            else:
                anchor = 'nw'
        super().__init__(x, y, w, h, img, canvas, visibility=False, container=[], mode_coord=False, is_enabled=True,
                         anchor=anchor)
        self.__is_moving = False
        self.__default_x = x
        self.__default_y = y

    @property
    def type_of_plate(self):
        return self.__type_of_plate

    @property
    def default_x(self):
        return self.__default_x

    @default_x.setter
    def default_x(self, value):
        self.__default_x = value

    @property
    def default_y(self):
        return self.__default_y

    @default_y.setter
    def default_y(self, value):
        self.__default_y = value

    def check_plate(self, x, y):
        """Проверяет, находится ли данная точка в области этой панели

        :param x: координата x данной точки
        :param y: координата y данной точки
        :return: True/False
        """
        if self.__type_of_plate == 'upper':
            if (self._x <= x <= self._x + self._w) and (self._y - self._h <= y <= self._y):
                return True
            else:
                return False
        if self.__type_of_plate == 'lower':
            if (self._x <= x <= self._x + self._w) and (self._y <= y <= self._y + self._h):
                return True
            else:
                return False
        if self.__type_of_plate == 'left':
            if (self._x - self._w <= x <= self._x) and (self._y <= y <= self._y + self._h):
                return True
            else:
                return False
        if self.__type_of_plate == 'right':
            if (self._x <= x <= self._x + self._w) and (self._y <= y <= self._y + self._h):
                return True
            else:
                return False

    def check(self, x, y, is_click=True):
        """Проверяет, было ли совершено перемещение панели и изменяет её положение

        :param x: новая координата x
        :param y:новая координата y
        :param is_click: было ли совершено нажатие
        :return:
        """
        if self._visibility is False:
            return

        is_checked = self.check_plate(x, y)
        if self._is_enabled:
            if self.__is_moving:
                if is_click and is_checked:
                    if self.__type_of_plate == 'upper':
                        self.go_to(x, y + ph(2))
                    elif self.__type_of_plate == 'lower':
                        self.go_to(x, y - ph(2))
                    elif self.__type_of_plate == 'left':
                        self.go_to(x + pw(1), y)
                    elif self.__type_of_plate == 'right':
                        self.go_to(x - pw(1), y)
                else:
                    self.__is_moving = False
                    if self.__type_of_plate == 'upper':
                        self.go_to(x, y + ph(2))
                    elif self.__type_of_plate == 'lower':
                        self.go_to(x, y - ph(2))
                    elif self.__type_of_plate == 'left':
                        self.go_to(x + pw(1), y)
                    elif self.__type_of_plate == 'right':
                        self.go_to(x - pw(1), y)
            else:
                if is_click and is_checked:
                    self.__is_moving = True

    def go_to(self, x, y):
        """Изменяет положение панели, учитывая её вид

        :param x: новая координата x
        :param y: новая координата y
        :return:
        """
        dx, dy = 0, 0
        if self.__locked_coord == 'x':
            dx = 0
            if y < ph(5) or y > ph(95):
                dy = 0
            else:
                dy = y - self._y
        elif self.__locked_coord == 'y':
            if x < pw(1) or x > pw(99):
                dx = 0
            else:
                dx = x - self._x
            dy = 0
        self._canvas.move(self._obj, dx, dy)
        self._x += dx
        self._y += dy

    def get_cords(self):
        """Возвращает координаты пластины

        :return:
        """
        return [self._x, self._y]


class CropClass:
    """Класс изображения кадрирования"""

    def __init__(self, canvas, path_to_file, list_of_plates, x=0, y=ph(10)):
        """Конструктор класса изображения кадрирования

        :param canvas: холст
        :param path_to_file: путь к файлу
        :param list_of_plates: список пластин кадрирования
        :param x: координата x изображения
        :param y: координата y изображения
        """
        self.__object = None
        self.__canvas = canvas
        self.__path_to_file = path_to_file
        self.__group_of_plates = Group()
        for plate in list_of_plates:
            self.__group_of_plates.add_objects(plate)
        self.__x = x
        self.__y = y
        self.__w = 0
        self.__h = ph(75)
        if ':/' not in self.__path_to_file:
            self.__img = Image.open(f'app_images/{self.__path_to_file}')
        else:
            self.__img = Image.open(self.__path_to_file)
        self.__img_coef = 1
        self.__crop_left = 0
        self.__crop_upper = 0
        self.__crop_right = 0
        self.__crop_lower = 0
        self.__create_obj()

    def __create_obj(self):
        """Создаёт объект изображения

        :return:
        """
        self.__w = self.__img.width * self.__h // self.__img.height
        if self.__w > pw(100):
            self.__w = pw(100)
            self.__h = self.__img.height * self.__w // self.__img.width
            self.__img_coef = self.__w / self.__img.width
        else:
            self.__img_coef = self.__h / self.__img.height
        if self.__w == pw(100):
            self.__group_of_plates.all_objects[0].x = self.__x - self.__w // 2 + pw(2)
            self.__group_of_plates.all_objects[2].x = self.__x + self.__w // 2 - pw(2)
        else:
            self.__group_of_plates.all_objects[0].x = self.__x - self.__w // 2
            self.__group_of_plates.all_objects[2].x = self.__x + self.__w // 2
        self.__group_of_plates.all_objects[0].default_x = self.__group_of_plates.all_objects[0].x
        self.__group_of_plates.all_objects[2].default_x = self.__group_of_plates.all_objects[2].x
        self.__group_of_plates.all_objects[1].y = self.__y - self.__h // 2
        self.__group_of_plates.all_objects[1].default_y = self.__group_of_plates.all_objects[1].y
        self.__group_of_plates.all_objects[3].y = self.__y + self.__h // 2
        self.__group_of_plates.all_objects[3].default_y = self.__group_of_plates.all_objects[3].y
        self.__object = Object(self.__x, self.__y, self.__w, self.__h, self.__path_to_file, self.__canvas, anchor='center')

    def crop(self):
        """Обрезает изображение

        :return:
        """
        dict_of_cords = {}
        dict_of_default_cords = {}
        for plate in self.__group_of_plates.all_objects:
            dict_of_cords[f'{plate.type_of_plate}'] = plate.get_cords()
            dict_of_default_cords[f'{plate.type_of_plate}'] = (plate.default_x, plate.default_y)

        if dict_of_cords['left'][0] <= dict_of_default_cords['left'][0] or dict_of_cords['left'][0] >= \
                dict_of_default_cords['right'][0]:
            self.__crop_left = 0
        else:
            if self.__w == pw(100):
                self.__crop_left = (dict_of_cords['left'][0] - dict_of_default_cords['left'][0] + pw(2)) // self.__img_coef
            else:
                self.__crop_left = (dict_of_cords['left'][0] - dict_of_default_cords['left'][0]) // self.__img_coef
        if dict_of_cords['upper'][1] <= dict_of_default_cords['upper'][1] or dict_of_cords['upper'][1] >= \
                dict_of_default_cords['lower'][1]:
            self.__crop_upper = 0
        else:
            self.__crop_upper = (dict_of_cords['upper'][1] - dict_of_default_cords['upper'][1]) // self.__img_coef
        if dict_of_cords['right'][0] >= dict_of_default_cords['right'][0] or dict_of_cords['right'][0] <= \
                dict_of_default_cords['left'][0]:
            self.__crop_right = self.__img.width
        else:
            if self.__w == pw(100):
                self.__crop_right = (self.__w - (
                            dict_of_default_cords['right'][0] + pw(2) - dict_of_cords['right'][0])) // self.__img_coef
            else:
                self.__crop_right = (self.__w - (
                            dict_of_default_cords['right'][0] - dict_of_cords['right'][0])) // self.__img_coef
        if dict_of_cords['lower'][1] >= dict_of_default_cords['lower'][1] or dict_of_cords['lower'][1] <= \
                dict_of_default_cords['upper'][1]:
            self.__crop_lower = self.__img.height
        else:
            self.__crop_lower = (self.__h - (
                        dict_of_default_cords['lower'][1] - dict_of_cords['lower'][1])) // self.__img_coef
        if self.__crop_upper == 0 and self.__crop_lower == self.__img.height and self.__crop_left == 0 \
                and self.__crop_right == self.__img.width:
            mb.showinfo('Информация', 'Вы не изменили изображение. Файл не был сохранён')
        else:
            cropped_img = self.__img.crop((self.__crop_left, self.__crop_upper, self.__crop_right, self.__crop_lower))
            img_new_name = re.split('\.j', self.__path_to_file)[0]
            img_new_name += '_обрезанный'
            img_new_name += '.j' + re.split('\.j', self.__path_to_file)[1]
            cropped_img.save(img_new_name)
            mb.showinfo('Информация', 'Файл успешно сохранён!')
            return img_new_name

    def show(self):
        """Показывает объект

        :return:
        """
        self.__object.show()
        self.__group_of_plates.show_all()

    def hide(self):
        """Показывает объект

        :return:
        """
        self.__object.hide()
        self.__group_of_plates.hide_all()

    def check(self, x, y, is_click):
        """Проверяет, было ли совершено взаимодействие с пластинами

        :param x:
        :param y:
        :param is_click:
        :return:
        """
        self.__group_of_plates.check(x, y, is_click)

    def set_disabled(self):
        """Устанавливает всем пластинам неактивное состояние

        :return:
        """
        for plate in self.__group_of_plates.all_objects:
            plate.set_disabled()

    def set_enabled(self):
        """Устанавливает всем пластинам активное состояние

        :return:
        """
        for plate in self.__group_of_plates.all_objects:
            plate.set_enabled()

    def set_plates_default(self):
        """Возвращает пластинам положение по умолчанию

        :return:
        """
        for plate in self.__group_of_plates.all_objects:
            plate.go_to(plate.default_x, plate.default_y)
