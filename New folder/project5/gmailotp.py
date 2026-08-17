import random
import smtplib
import time
from tkinter import *
from tkinter import messagebox

otp = ""
otp_time = 0


def generate_otp():
    return str(random.randint(100000, 999999))


def send_email_otp():
    global otp, otp_time

    receiver_email = entry_email.get()

    if receiver_email == "":
        messagebox.showerror("Error", "Enter email first!")
        return

    otp = generate_otp()
    otp_time = time.time()

    sender_email = "ver045208@gmail.com"
    app_password = "abcdefghijklmnop"

    message = f"Subject: OTP\n\nYour OTP is {otp}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()

        messagebox.showinfo("Success", "OTP Sent!")
        start_timer()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def verify_otp():
    current_time = time.time()

    if current_time - otp_time > 60:
        result_label.config(text="⏱ OTP Expired!", fg="orange")
        return

    if entry_otp.get() == otp:
        result_label.config(text="✅ Verified", fg="#00ffcc")
    else:
        result_label.config(text="❌ Wrong OTP", fg="red")


# -------- TIMER --------
def start_timer():
    update_timer(60)


def update_timer(time_left):
    if time_left >= 0:
        timer_label.config(text=f"⏳ {time_left}s")
        root.after(1000, update_timer, time_left - 1)
    else:
        timer_label.config(text="Expired")


# -------- UI --------
root = Tk()
root.title("Email_Sender_vgi")
root.geometry("500x500")
root.configure(bg="#0f172a")
root.attributes("-alpha", 0.95)  # transparency

# Glass Frame
frame = Frame(root, bg="#1e293b", bd=0)
frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=320, height=400)

# Title
Label(frame, text="OTP Verification", font=("Segoe UI", 16, "bold"),
      bg="#1e293b", fg="white").pack(pady=15)

# Email
Label(frame, text="Email", bg="#1e293b", fg="#cbd5e1").pack()
entry_email = Entry(frame, font=("Segoe UI", 11), bd=0,
                    bg="#334155", fg="white", insertbackground="white")
entry_email.pack(pady=8, ipadx=10, ipady=5)

# Send Button
Button(frame, text="Send OTP", command=send_email_otp,
       bg="#6366f1", fg="white", bd=0,
       font=("Segoe UI", 10, "bold"),
       activebackground="#4f46e5",
       padx=10, pady=6).pack(pady=10)

# OTP Entry
Label(frame, text="Enter OTP", bg="#1e293b", fg="#cbd5e1").pack()
entry_otp = Entry(frame, font=("Segoe UI", 11), bd=0,
                  bg="#334155", fg="white", insertbackground="white")
entry_otp.pack(pady=8, ipadx=10, ipady=5)

# Timer
timer_label = Label(frame, text="", bg="#1e293b",
                    fg="#facc15", font=("Segoe UI", 10))
timer_label.pack()

# Verify Button
Button(frame, text="Verify", command=verify_otp,
       bg="#10b981", fg="white", bd=0,
       font=("Segoe UI", 10, "bold"),
       activebackground="#059669",
       padx=10, pady=6).pack(pady=15)

# Result
result_label = Label(frame, text="", bg="#1e293b",
                     font=("Segoe UI", 11, "bold"))
result_label.pack()

root.mainloop()