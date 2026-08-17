# Internet Speed Checker
from tkinter import *
import threading
import speedtest


def speedcheck():
    """Kick off the speed test on a background thread so the GUI
    never freezes ('Not Responding') while it runs."""
    button.config(state=DISABLED, text="Testing...")
    lab_down.config(text="...", fg="Red")
    lab_up.config(text="...", fg="Red")
    error_lab.config(text="")  # clear any previous error
    threading.Thread(target=_run_test, daemon=True).start()


def _run_test():
    """Runs on a background thread. Never touch widgets directly here -
    only schedule updates back onto the main thread via sp.after()."""
    try:
        test = speedtest.Speedtest()
        test.get_servers()
        down = f"{round(test.download() / 10**6, 3)} mbps"
        up = f"{round(test.upload() / 10**6, 3)} mbps"
        sp.after(0, lambda: _on_success(down, up))
    except Exception as e:
        sp.after(0, lambda: _on_error(e))


def _on_success(down, up):
    lab_down.config(text=down)
    lab_up.config(text=up)
    button.config(state=NORMAL, text="Check Speed")


def _on_error(e):
    lab_down.config(text="--")
    lab_up.config(text="--")
    # Show a short, readable message in the GUI itself
    error_lab.config(text=f"⚠ Test failed: {e}")
    button.config(state=NORMAL, text="Check Speed")


sp = Tk()
sp.title("INTERNET TESTER")
sp.geometry("500x520")
sp.config(bg="Blue")

lab = Label(sp, text="INTERNET SPEED TESTER", font=('Times New Roman', 20, "bold"), bg="Blue", fg="Red")
lab.place(x=55, y=30, height=50, width=380)

lab = Label(sp, text="Download Speed", font=('Times New Roman', 20, "bold"), bg="Blue", fg="Red")
lab.place(x=55, y=115, height=50, width=380)

lab_down = Label(sp, text="00", font=('Times New Roman', 20, "bold"), bg="Blue", fg="Red")
lab_down.place(x=55, y=180, height=50, width=380)

lab = Label(sp, text="Upload Speed", font=('Times New Roman', 20, "bold"), bg="Blue", fg="Red")
lab.place(x=55, y=265, height=50, width=380)

lab_up = Label(sp, text="00", font=('Times New Roman', 20, "bold"), bg="Blue", fg="Red")
lab_up.place(x=55, y=330, height=50, width=380)

button = Button(sp, text="Check Speed", font=('Times New Roman', 20, "bold"),
                 relief=RAISED, bg="Red", fg="White", command=speedcheck)
button.place(x=55, y=400, height=50, width=380)

# Error message area - wraps long errors, stays hidden (empty) when there's no error
error_lab = Label(sp, text="", font=('Times New Roman', 11), bg="Blue", fg="Yellow",
                   wraplength=460, justify=CENTER)
error_lab.place(x=20, y=465, height=45, width=460)

sp.mainloop()