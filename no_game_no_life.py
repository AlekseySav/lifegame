import numpy as np
import os
from tkinter import Tk, Canvas, Entry, Label, messagebox

long_path = os.path.dirname(__file__)

if long_path[0] == '/':
    long_path += '/'
else:
    long_path += '\\'

def error(msg):
    messagebox.showerror("Game 'Life'", msg)
    exit(1)


def init_figure(file):
    global population

    f = open(long_path + file, "rt")
    sx, sy = 0, 0
    y = 0

    for i in f.readlines():
        if i[0] == ';':
            continue
        if sx == 0:
            sx = int(i)
        elif sy == 0:
            sy = int(i)
            if max(sx, sy) > nr:
                error(file + " needs at least field " + str(sx) + "x" + str(sy))
        else:
            print(len(i))
            if len(i) != sx + 1:
                error(file + " failed")

            for x in range(sx):
                population[x, y] = 1 if i[x] == '#' else 0
            y += 1

    if y != sy:
        error(file + " failed")
    f.close()



def next_population(population):
    neighbors = sum([
        np.roll(np.roll(population, -1, 1), 1, 0),
        np.roll(np.roll(population, 1, 1), -1, 0),
        np.roll(np.roll(population, 1, 1), 1, 0),
        np.roll(np.roll(population, -1, 1), -1, 0),
        np.roll(population, 1, 1),
        np.roll(population, -1, 1), 
        np.roll(population, 1, 0),
        np.roll(population, -1, 0)])
    return (neighbors == 3) | (population & (neighbors == 2))

def setup(nr1, figure):
    global population, nr, configured, cell, speed, size, rects, calc_diff, objects, canv

    msg.destroy()
    fig.destroy()
    nr = nr1
    speed = 10000 // (nr * nr)
    size = (500 // nr) * nr
    cell = size // nr
    canv = Canvas(main, width=size, height=size, bg='#000000')
    canv.pack()

    rects = [[0 for j in range(nr)] for j in range(nr)]
    calc_diff = [0 for _ in range(size)]
    objects = [0 for _ in range(size)]

    population = np.array([0 for i in range(nr * nr)]).reshape(nr, nr)

    if figure != "": init_figure(figure)

    for x in range(nr):
        for y in range(nr):
            if population[x, y] == 0:
                rects[x][y] = canv.create_rectangle(cell * x, cell * y, cell * (x + 1), cell * (y + 1), fill='#000000')
            else:
                rects[x][y] = canv.create_rectangle(cell * x, cell * y, cell * (x + 1), cell * (y + 1), fill='#007000')

    configured = True



calc_diff_ind = 0
paused = False
started = False
configured = False

def get_y(x):
    return size // 2 - (calc_diff[(calc_diff_ind + x) % size])

def pause(e):
    global paused
    paused = not paused


def graphic_calc(e):
    global started

    if not configured:
        setup(int(msg.get()), str(fig.get()))
        return
    if not started:
        started = True
        update_clock()
        return

    global paused
    global objects

    if paused:
        for i in objects:
            canv.delete(i)
        paused = False
        return

    paused = True

    objects[0] = canv.create_rectangle(0, 0, size, size, fill="#000000")

    x1, y1 = 0, get_y(0)
    for x in range(1, size):
        y = get_y(x)
        objects[x] = canv.create_line(x1, y1, x, y, fill='#007000')
        x1, y1 = x, y


def delete_cell(e):
    if not configured:
        return

    x, y = e.x, e.y
    x, y = x // cell, y // cell
    canv.delete(rects[x][y])
    if started:
        population[x, y] = 0
    else:
        population[x, y] = 1
        rects[x][y] = canv.create_rectangle(cell * x, cell * y, cell * (x + 1), cell * (y + 1), fill='#007000')


main = Tk()
main.geometry("500x500")

l1 = Label(main, text="set size:")
l1.place(relx=.3, rely=.1, anchor="c")
msg = Entry(main)
msg.place(relx=.6, rely=.1, anchor="c")

l2 = Label(main, text="figure:")
l2.place(relx=.3, rely=.2, anchor="c")
fig = Entry(main)
fig.place(relx=.6, rely=.2, anchor="c")

l2 = Label(main, text="Press <Enter> if done")
l2.place(relx=.5, rely=.3, anchor="c")

main.bind('<Return>', graphic_calc)
main.bind('<space>', pause)
main.bind('<Button-1>', delete_cell)


def update_clock():
    global population
    global calc_diff_ind

    if not paused:
        count = 0

        nnext = next_population(population)
        diff = nnext - population
        population = nnext
        
        for x in range(nr):
            for y in range(nr):
                if diff[x, y] != 0:
                    canv.delete(rects[x][y])
                    if diff[x, y] == 1:
                        count += 1
                        rects[x][y] = canv.create_rectangle(cell * x, cell * y, cell * (x + 1), cell * (y + 1), fill='#007000')
                    else:
                        count -= 1
                        rects[x][y] = canv.create_rectangle(cell * x, cell * y, cell * (x + 1), cell * (y + 1), fill='#000000')
        
        print("cels: %+d" % count)
        calc_diff[calc_diff_ind] = count
        calc_diff_ind = (calc_diff_ind + 1) % size

    main.after(speed, update_clock)


main.mainloop()
