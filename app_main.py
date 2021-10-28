import cv2 as cv

from data.main_cycle import *
from data.objects import *
from graphic import Graphic


# имеет смысл только при полном экране (оно меняет временно разришение экрана)
# print(ScreenRes.get_modes())
# x = ScreenRes.get_modes()
# ScreenRes.set(1280, 720)
# ScreenRes.set() # Set defaults


# ▼ инициализация ▼
master = tkinter.Tk()
# master.attributes('-fullscreen', True)  # полный экран
screen_w = 1280  # master.winfo_screenwidth()
screen_h = 720  # master.winfo_screenheight()
initialize_w_and_h(screen_w, screen_h)
canvas = tkinter.Canvas(master, bg='#000000', height=screen_h, width=screen_w)
canvas.pack(fill=tkinter.BOTH, expand=1)

print(screen_w, screen_h)


all_gropes = []

main_grope = Group()
all_gropes.append(main_grope)
view_grope = Group()
all_gropes.append(view_grope)
main_cycle = MainCycle(canvas, all_gropes)


bg = Object(0, 0, pw(100), ph(100), 'background.png', canvas)  # с этого места идёт создание необходимых объектов
main_grope.add_objects(bg)
exit_btn = Button(pw(95), ph(3), ph(5), ph(5), 'exit_button.png', canvas, 'exit_button_2.png', main_cycle.close_window)
main_grope.add_objects(exit_btn)

btn = Button(pw(28), ph(47.5), pw(5), ph(5), 'exit_button.png', canvas, 'exit_button_2.png', main_cycle.set_file_name)
main_grope.add_objects(btn)

btn = Button(pw(45), ph(47.5), pw(10), ph(5), 'start_scanning.png', canvas, 'start_scanning_2.png', main_cycle.start_scanning)
main_grope.add_objects(btn)
# TODO переработать вопрос, сделать так, чтобы подсказка закрывалась при нажатии в любом месте
# TODO сделать кнопку для перезапуска графика
# TODO если точки наложились друг на друга, то одно из них удалить

master.protocol("WM_DELETE_WINDOW", main_cycle.close_window)  # ▼ всё что ниже - неизменно ▼
master.bind('<Motion>', main_cycle.mouse_move)
master.bind('<Button-1>', main_cycle.click)
master.bind('<ButtonRelease-1>', main_cycle.click_out)
master.bind('<MouseWheel>', main_cycle.mouse_wheel)
master.bind('<Key>', main_cycle.pressing_keyboard)

main_cycle.start()
ScreenRes.set() # Set defaults разрешение экрана
