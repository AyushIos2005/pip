from tkinter import * 
from tkinter import ttk
from time import strftime

def update_time():
    hr = strftime("%I")      # Hour (12-hour format)
    minute = strftime("%M")  # Minute
    sec = strftime("%S")     # Second
    am_pm = strftime("%p")   # AM/PM

    lab_hr.config(text=hr)
    lab_min.config(text=minute)
    lab_sec.config(text=sec)
    lab_AM.config(text=am_pm)

    clock.after(1000, update_time)


clock = Tk()    


clock.title("Digital Clock")
clock.geometry("700x220")
clock.config(bg="red")
comb_dest = ttk.Combobox(
    clock,
    values=["Clock", "Stopwatch", "Alarm"],
    state="readonly",
    # font=FONT_TEXT
)

comb_dest.current(0)
comb_dest.place(x=20, y=10, width=150)# Hour Label
lab_hr = Label(
    clock,
    text="00",
    fg="black",
    bg="red",
    font=("Times New Roman", 60, "bold")
)
lab_hr.place(x=30, y=40, width=100, height=100)

# :
dot_hr = Label(
    clock,
    text=":",
    fg="black",
    bg="red",
    font=("Times New Roman", 60, "bold")
)
dot_hr.place(x=140, y=40)

# Minute Label
lab_min = Label(
    clock,
    text="00",
    fg="black",
    bg="red",
    font=("Times New Roman", 60, "bold")
)
lab_min.place(x=180, y=40, width=100, height=100)

# :
dot_min = Label(
    clock,
    text=":",
    fg="black",
    bg="red",
    font=("Times New Roman", 60, "bold")
)
dot_min.place(x=290, y=40)

# Second Label
lab_sec = Label(
    clock,
    text="00",
    fg="black",
    bg="red",
    font=("Times New Roman", 60, "bold")
)
lab_sec.place(x=330, y=40, width=100, height=100)

# AM/PM Label
lab_AM = Label(
    clock,
    text="AM",
    fg="black",
    bg="red",
    font=("Times New Roman", 60, "bold")
)
lab_AM.place(x=450, y=40, width=180, height=100)




update_time()

clock.mainloop()








