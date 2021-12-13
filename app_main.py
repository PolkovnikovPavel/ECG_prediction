import cv2 as cv

from data.main_cycle import *
from data.objects import *
from graphic import Graphic

# имеет смысл только при полном экране (оно меняет временно разрешение экрана)
# print(ScreenRes.get_modes())
# x = ScreenRes.get_modes()
# ScreenRes.set(1280, 720)
# ScreenRes.set() # Set defaults


# ▼ инициализация ▼
master = tkinter.Tk()
master.iconbitmap('app_images/Logo.ico')
master.title('ЭКГ помощник')
# master.attributes('-fullscreen', True)  # полный экран
screen_w = 1280  # master.winfo_screenwidth()
screen_h = 720  # master.winfo_screenheight()
initialize_w_and_h(screen_w, screen_h)
canvas = tkinter.Canvas(master, bg='#000000', height=screen_h - 2, width=screen_w - 2)
canvas.pack(fill=tkinter.BOTH, expand=1)
master.resizable(False, False)

print(screen_w, screen_h)

all_gropes = []

main_group = Group()
all_gropes.append(main_group)
view_grope = Group()
all_gropes.append(view_grope)
main_cycle = MainCycle(canvas, all_gropes)

bg = Object(0, 0, pw(100), ph(100), 'background.png', canvas)  # с этого места идёт создание необходимых объектов
main_group.add_objects(bg)
exit_btn = Button(pw(95), ph(3), ph(6), ph(6), 'exit_button.png', canvas, 'exit_button_2.png', main_cycle.close_window)
main_group.add_objects(exit_btn)

btn = Button(pw(28), ph(44), ph(12), ph(12), 'open_file.png', canvas, 'open_file_2.png', main_cycle.set_file_name)
main_group.add_objects(btn)

btn = Button(pw(40), ph(44.5), pw(20), pw(6), 'start_scanning.png', canvas, 'start_scanning_2.png',
             main_cycle.start_scanning)
main_group.add_objects(btn)

main_group.add_objects(Text(pw(1), ph(90), f'Сергей - puhovskijsa@kuzstu.ru\nПавел - pavelpolkovnikov334@gmail.com',
                            canvas, font=f'Times {ph(3)} bold', visibility=True, color='#96AABF'))

master.protocol("WM_DELETE_WINDOW", main_cycle.close_window)  # ▼ всё что ниже - неизменно ▼
master.bind('<Motion>', main_cycle.mouse_move)
master.bind('<Button-1>', main_cycle.click)
master.bind('<ButtonRelease-1>', main_cycle.click_out)
master.bind('<Button-3>', main_cycle.right_click)
master.bind('<ButtonRelease-3>', main_cycle.right_click_out)
master.bind('<MouseWheel>', main_cycle.mouse_wheel)
master.bind('<Key>', main_cycle.pressing_keyboard)

main_cycle.start()
ScreenRes.set()  # Set defaults разрешение экрана
