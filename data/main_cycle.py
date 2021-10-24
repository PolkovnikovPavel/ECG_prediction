import asyncio, time
from data.functions import pw, ph
from data.objects import *


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

        self.__create_all_gropes()

    def __create_all_gropes(self):
        self.main_grope = self.all_gropes[0]

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

    def start_main_menu(self, *args):
        self.type_menu = 'main_menu'
        self.main_grope.show_all()
