from tkinter import *
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator

lang_dict = GoogleTranslator().get_supported_languages(as_dict=True)

# ---------- THEME ----------
BG_DARK = "#0f0f1e"
BG_PANEL = "#1a1a2e"
ACCENT = "#ff2e63"
ACCENT2 = "#08d9d6"
TEXT_LIGHT = "#eaeaea"
FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_TEXT = ("Segoe UI", 13)

# ---------- LOGIC ----------
def change(text, src, dest):
    src_code = lang_dict.get(src.lower(), "auto")
    dest_code = lang_dict.get(dest.lower(), "en")
    return GoogleTranslator(source=src_code, target=dest_code).translate(text)

def data():
    s, d = comb_sor.get(), comb_dest.get()
    msg = source_text.get(1.0, END).strip()
    if not msg:
        messagebox.showwarning("Empty Text", "Type something first, genius.")
        return
    btn_translate.config(text="Translating...", state=DISABLED, bg="#555")
    root.update_idletasks()
    try:
        result = change(msg, s, d)
        dest_text.delete(1.0, END)
        dest_text.insert(END, result)
        flash_success()
    except Exception as e:
        messagebox.showerror("Translation Error", str(e))
    finally:
        btn_translate.config(text="✨ Translate ✨", state=NORMAL, bg=ACCENT)

def swap_languages():
    s, d = comb_sor.get(), comb_dest.get()
    comb_sor.set(d)
    comb_dest.set(s)
    spin_swap()

def spin_swap():
    # quick color pulse on swap button for feedback
    colors = [ACCENT2, ACCENT, ACCENT2]
    def step(i=0):
        if i < len(colors):
            btn_swap.config(fg=colors[i])
            root.after(120, step, i + 1)
    step()

def flash_success():
    orig = dest_frame.cget("bg")
    dest_border.config(bg=ACCENT2)
    root.after(400, lambda: dest_border.config(bg=BG_PANEL))

def clear_all():
    source_text.delete(1.0, END)
    dest_text.delete(1.0, END)

def copy_result():
    text = dest_text.get(1.0, END).strip()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        copy_status.config(text="Copied!", fg=ACCENT2)
        root.after(1200, lambda: copy_status.config(text=""))

def on_enter(e, widget, color):
    widget.config(bg=color)

def on_leave(e, widget, color):
    widget.config(bg=color)

# ---------- ROOT ----------
root = Tk()
root.title("⚡ NeoTranslate ⚡")
root.geometry("560x620")
root.config(bg=BG_DARK)
root.resizable(False, False)

# ---------- HEADER (canvas gradient fake) ----------
header = Canvas(root, width=560, height=90, bg=BG_DARK, highlightthickness=0)
header.place(x=0, y=0)

steps = 60
for i in range(steps):
    r1, g1, b1 = 0x0f, 0x0f, 0x1e
    r2, g2, b2 = 0xff, 0x2e, 0x63
    ratio = i / steps
    r = int(r1 + (r2 - r1) * ratio * 0.5)
    g = int(g1 + (g2 - g1) * ratio * 0.3)
    b = int(b1 + (b2 - b1) * ratio * 0.5)
    color = f"#{r:02x}{g:02x}{b:02x}"
    header.create_rectangle(i * (560 / steps), 0, (i + 1) * (560 / steps), 90, fill=color, outline=color)

header.create_text(280, 45, text="⚡ NEOTRANSLATE ⚡", font=FONT_TITLE, fill="white")

# ---------- SOURCE PANEL ----------
Label(root, text="🔤 SOURCE TEXT", font=FONT_LABEL, bg=BG_DARK, fg=ACCENT2).place(x=20, y=105)

source_border = Frame(root, bg=ACCENT, bd=0)
source_border.place(x=20, y=130, width=520, height=110)
source_text = Text(source_border, font=FONT_TEXT, wrap=WORD, bg=BG_PANEL, fg=TEXT_LIGHT,
                    insertbackground=TEXT_LIGHT, relief=FLAT, bd=0)
source_text.place(x=2, y=2, width=516, height=106)

# ---------- LANGUAGE ROW ----------
languages = sorted([lang.title() for lang in lang_dict.keys()])

style = ttk.Style()
style.theme_use("default")
style.configure("Neo.TCombobox",
                 fieldbackground=BG_PANEL,
                 background=BG_PANEL,
                 foreground=TEXT_LIGHT,
                 arrowcolor=ACCENT2,
                 borderwidth=0)

Label(root, text="From", font=("Segoe UI", 9, "italic"), bg=BG_DARK, fg="#888").place(x=25, y=250)
comb_sor = ttk.Combobox(root, values=languages, state="readonly", style="Neo.TCombobox", font=FONT_TEXT)
comb_sor.place(x=20, y=270, width=170, height=32)
comb_sor.set("English")

btn_swap = Button(root, text="⇄", font=("Segoe UI", 18, "bold"), bg=BG_DARK, fg=ACCENT2,
                   relief=FLAT, bd=0, activebackground=BG_DARK, activeforeground=ACCENT,
                   command=swap_languages, cursor="hand2")
btn_swap.place(x=250, y=268, width=60, height=38)

Label(root, text="To", font=("Segoe UI", 9, "italic"), bg=BG_DARK, fg="#888").place(x=375, y=250)
comb_dest = ttk.Combobox(root, values=languages, state="readonly", style="Neo.TCombobox", font=FONT_TEXT)
comb_dest.place(x=370, y=270, width=170, height=32)
comb_dest.set("Hindi")

# ---------- TRANSLATE BUTTON (glow-ish) ----------
btn_translate = Button(root, text="✨ Translate ✨", font=("Segoe UI", 14, "bold"),
                        bg=ACCENT, fg="white", activebackground=ACCENT2, activeforeground=BG_DARK,
                        relief=FLAT, bd=0, cursor="hand2", command=data)
btn_translate.place(x=160, y=320, width=240, height=48)
btn_translate.bind("<Enter>", lambda e: on_enter(e, btn_translate, ACCENT2))
btn_translate.bind("<Leave>", lambda e: on_leave(e, btn_translate, ACCENT))

# ---------- RESULT PANEL ----------
result_header = Frame(root, bg=BG_DARK)
result_header.place(x=20, y=385, width=520, height=25)
Label(result_header, text="🌍 TRANSLATED TEXT", font=FONT_LABEL, bg=BG_DARK, fg=ACCENT).pack(side=LEFT)
copy_status = Label(result_header, text="", font=("Segoe UI", 9, "bold"), bg=BG_DARK, fg=ACCENT2)
copy_status.pack(side=RIGHT, padx=5)
btn_copy = Button(result_header, text="📋 Copy", font=("Segoe UI", 9, "bold"), bg=BG_DARK, fg="#888",
                   relief=FLAT, bd=0, cursor="hand2", command=copy_result, activebackground=BG_DARK,
                   activeforeground=ACCENT2)
btn_copy.pack(side=RIGHT)

dest_border = Frame(root, bg=BG_PANEL, bd=0)
dest_border.place(x=20, y=415, width=520, height=130)
dest_frame = dest_border
dest_text = Text(dest_border, font=FONT_TEXT, wrap=WORD, bg=BG_PANEL, fg=ACCENT2,
                  insertbackground=TEXT_LIGHT, relief=FLAT, bd=0)
dest_text.place(x=2, y=2, width=516, height=126)

# ---------- FOOTER ----------
btn_clear = Button(root, text="🗑 Clear All", font=("Segoe UI", 10, "bold"), bg=BG_DARK, fg="#888",
                    relief=FLAT, bd=0, cursor="hand2", command=clear_all, activebackground=BG_DARK,
                    activeforeground=ACCENT)
btn_clear.place(x=20, y=560)

Label(root, text="made with tkinter + vgi", font=("Segoe UI", 8, "italic"), bg=BG_DARK, fg="#444").place(x=380, y=590)

root.mainloop()