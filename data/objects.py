import tkinter, random
from app_images.images import *


class Object:
    def __init__(self, x, y, w, h, img, canvas, visibility=True, container=[], mode_coord=False):
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
        if visibility:
            self.create_obj()

    def create_obj(self):
        if isinstance(self.img, ImageTk.PhotoImage):
            if self.mode_coord:
                self.obj = self.canvas.create_image((self.x, self.y), image=self.img)
            else:
                self.obj = self.canvas.create_image((self.x + 0.5 * self.w, self.y + 0.5 * self.h), image=self.img)
        else:
            self.obj = self.img

    def change_img(self, new_img, w, h):
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
        dx = x - self.x
        dy = y - self.y
        self.canvas.move(self.obj, dx, dy)
        self.x += dx
        self.y += dy

    def hide(self):
        self.canvas.delete(self.obj)
        self.visibility = False

    def show(self):
        if not self.visibility:
            self.create_obj()
            self.visibility = True

    def reshow(self):
        self.hide()
        self.show()

    def rotation_on(self, angle):
        self.angle += angle
        self.rotation(self.angle)

    def rotation(self, angle):
        self.angle = angle
        if self.img_pil is not None:
            self.img_pil = self.img_pil_start.rotate(self.angle)
            self.img = ImageTk.PhotoImage(self.img_pil)

            self.canvas.delete(self.obj)
            self.create_obj()

    def check_point(self, x, y):
        if self.mode_coord:
            if (self.x - (self.w / 2) <= x <= self.x + (self.w / 2) and
                    self.y - (self.h / 2) <= y <= self.y + (self.h / 2)):
                return True
        else:
            if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
                return True
        return False


class Button(Object):
    def __init__(self, x, y, w, h, img, canvas, img2=None, function=None, args=[], visibility=True, container=[]):
        Object.__init__(self, x, y, w, h, img, canvas, visibility=visibility, container=container)
        self.is_click = False
        if type(img2) == str:
            self.img2 = get_image(img2, w, h)
        else:
            self.img2 = img2
        self.function = function
        self.args = args

    def press(self):
        if self.function is not None:
            self.function(self.args)

    def hide(self):
        Object.hide(self)
        self.is_click = False

    def show(self):
        Object.show(self)
        self.is_click = False

    def check(self, x, y, is_click=True):
        if not self.visibility:
            return
        if self.check_point(x, y):
            if is_click:
                if not self.is_click:
                    self.is_click = True
                    if self.img2 is not None:
                        self.canvas.delete(self.obj)
                        self.obj = self.canvas.create_image((self.x + 0.5 * self.w, self.y + 0.5 * self.h),
                                                            image=self.img2)

            else:
                if self.is_click:
                    self.is_click = False
                    if self.img2 is not None:
                        self.canvas.delete(self.obj)
                        self.create_obj()
                    self.press()
        else:
            if self.is_click:
                self.is_click = False
                if self.img2 is not None:
                    self.canvas.delete(self.obj)
                    self.create_obj()


class Text:
    def __init__(self, x, y, text, canvas, font='Times 25 italic bold', visibility=True):
        self.x = x
        self.y = y
        self.visibility = visibility
        self.text = text
        self.canvas = canvas
        self.font = font
        if self.visibility:
            self.create_obj()
        else:
            self.obj = None

    def create_obj(self):
        self.obj = self.canvas.create_text(self.x, self.y, font=self.font, text=self.text)

    def hide(self):
        self.canvas.delete(self.obj)
        self.visibility = False

    def show(self):
        self.create_obj()
        self.visibility = True

    def reshow(self):
        self.canvas.delete(self.obj)
        self.create_obj()
        self.visibility = True

    def set_new_text(self, text):
        self.text = text
        if self.visibility:
            self.reshow()

    def go_to(self, x, y):
        dx = x - self.x
        dy = y - self.y
        self.canvas.move(self.obj, dx, dy)
        self.x += dx
        self.y += dy


class Group:
    def __init__(self):
        self.all_objects = []
        self.visibility = True
        self.container = []

    def add_objects(self, *objects):
        for object in objects:
            self.all_objects.append(object)

    def delete(self, *objects):
        if len(objects) == 0:
            self.all_objects = []
        for object in objects:
            del self.all_objects[self.all_objects.index(object)]

    def hide_all(self):
        self.visibility = False
        for object in self.all_objects:
            object.hide()

    def all_move_on(self, dx, dy):
        for object in self.all_objects:
            object.go_to(object.x + dx, object.y + dy)

    def show_all(self):
        self.visibility = True
        for object in self.all_objects:
            object.show()

    def check(self, x, y, is_click=True):
        if not self.visibility:
            return
        for object in self.all_objects:
            if isinstance(object, Button) or isinstance(object, ObjectGraphic):
                object.check(x, y, is_click)


class Point(Object):
    def __init__(self, x, y, w, h, canvas, type_point='R', point=(0, 0), visibility=True, container=[],
                 mode_coord=False, graphic=None):
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

    def check(self, x, y, is_click=True, is_taken_one=False):
        if not self.visibility:
            return

        if self.is_moving:
            if is_click:
                self.go_to(x, y)
            else:
                if self.graphic.trash.check_point(self.x, self.y):
                    self.graphic.del_point(self)
                    self.hide()
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
        return self.point


class ObjectGraphic:
    def __init__(self, canvas, graphic, path_to_file, x=0, y=0, w=1280, h=600, visibility=True, scan_graphic=None):
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

        self.create_all_obj()

    def create_all_obj(self):
        obj = Object(self.x, self.y, self.w, self.h, self.path_to_file, self.canvas)
        self.group.add_objects(obj)
        self.trash = Object(0, ph(85), pw(105), ph(20), 'air.png', self.canvas, False)
        self.group.add_objects(self.trash)

        for key in self.dict_of_points:
            for point in self.graphic.dict_of_points[key]:
                x, y = (point[0]) * (self.w / self.img_w), point[1] * (self.h / self.img_h)
                x, y = x + self.x, y + self.y
                obj = Point(x, y, ph(4), ph(4), self.canvas, key, point, mode_coord=True, graphic=self)
                self.group.add_objects(obj)
                self.dict_of_points[key].append(obj)

        obj = Object(pw(12), ph(87), ph(10), ph(10), 'add_point_lp.png', self.canvas, container=['LP'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(19), ph(87), ph(10), ph(10), 'add_point_p.png', self.canvas, container=['P'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(26), ph(87), ph(10), ph(10), 'add_point_q.png', self.canvas, container=['Q'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(33), ph(87), ph(10), ph(10), 'add_point_r.png', self.canvas, container=['R'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(40), ph(87), ph(10), ph(10), 'add_point_s.png', self.canvas, container=['S'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(47), ph(87), ph(10), ph(10), 'add_point_rs.png', self.canvas, container=['RS'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(54), ph(87), ph(10), ph(10), 'add_point_lt.png', self.canvas, container=['LT'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(61), ph(87), ph(10), ph(10), 'add_point_t.png', self.canvas, container=['T'])
        self.adding_group.add_objects(obj)
        obj = Object(pw(68), ph(87), ph(10), ph(10), 'add_point_rt.png', self.canvas, container=['RT'])
        self.adding_group.add_objects(obj)

    def temporarily_hide_points(self, *args):
        obj = args[0]
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                point.hide()
        obj.function = self.temporarily_show_points
        obj.change_img('hide_points_2.png', ph(5), ph(5))

    def temporarily_show_points(self, *args):
        obj = args[0]
        for key in self.dict_of_points:
            for point in self.dict_of_points[key]:
                point.show()
        obj.function = self.temporarily_hide_points
        obj.change_img('hide_points.png', ph(5), ph(5))

    def del_point(self, point):
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
        # self.scan_graphic()

    def reset_all_points(self):
        for key in self.dict_of_points:
            for i in range(len(self.graphic.dict_of_points[key])):
                point = self.graphic.dict_of_points[key][i]
                obj = self.dict_of_points[key][i]
                x, y = (point[0]) * (self.w / self.img_w), point[1] * (self.h / self.img_h)
                x, y = x + self.x, y + self.y
                obj.go_to(x, y)
                it_var = len(self.graphic.dict_of_points[key])
                while len(self.dict_of_points[key]) > len(self.graphic.dict_of_points[key]):
                    self.del_point(self.dict_of_points[key][it_var])

    def show(self):
        self.visibility = True
        self.group.show_all()
        self.adding_group.show_all()

    def hide(self):
        self.visibility = False
        self.group.hide_all()
        self.adding_group.hide_all()

    def check_point(self, x, y):
        if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
            return True
        return False

    def check(self, x, y, is_click=True):
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
                    if btn.check_point(x, y):
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
