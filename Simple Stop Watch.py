import tkinter as tk
from tkinter import messagebox
from datetime import datetime

ticks = 0
timer_active = False
saved_laps = []
saved_lap_secs = []

def to_hhmmss(raw_secs):
    return datetime.utcfromtimestamp(raw_secs).strftime('%H:%M:%S')

def _keep_ticking(display_lbl):
    def _inner():
        global ticks
        if not timer_active:
            return
        display_lbl['text'] = 'Ready!' if ticks == 0 else to_hhmmss(ticks)
        display_lbl.after(1000, _inner)
        ticks += 1
    _inner()

def _update_pb():
    
    if saved_lap_secs:
        pb_best['text']  = f"Best:   {to_hhmmss(min(saved_lap_secs))}"
        pb_worst['text'] = f"Worst:  {to_hhmmss(max(saved_lap_secs))}"
    else:
        pb_best['text']  = "Best:   --:--:--"
        pb_worst['text'] = "Worst:  --:--:--"

def press_start(lbl):
    global timer_active
    timer_active = True
    _keep_ticking(lbl)
    lbl['fg'] = '#27ae60'
    btn_start['state']  = 'disabled'
    btn_pause['state']  = 'normal'
    btn_clear['state']  = 'normal'
    btn_addlap['state'] = 'normal'

def press_pause():
    global timer_active
    timer_active = False
    timer_disp['fg'] = '#e74c3c'
    btn_start['state']  = 'normal'
    btn_pause['state']  = 'disabled'
    btn_addlap['state'] = 'disabled'

def press_clear(lbl):
    global ticks
    ticks = 0
    saved_laps.clear()
    saved_lap_secs.clear()
    lbl['text'] = '00:00:00'
    lbl['fg']   = '#2c3e50'
    lap_history.delete(0, tk.END)
    _update_pb()
    if not timer_active:
        btn_clear['state']  = 'disabled'
        btn_addlap['state'] = 'disabled'

def press_addlap():
    if not timer_active or ticks == 0:
        return
    snap = ticks - 1  
    snap_str = to_hhmmss(snap)
    saved_laps.append(snap_str)
    saved_lap_secs.append(snap)
    idx = len(saved_laps)
    lap_history.insert(tk.END, f"  Lap {idx:02d}   {snap_str}")
    lap_history.yview(tk.END)
    _update_pb()

def export_session():
    if not saved_laps:
        messagebox.showwarning("No laps yet", "Add at least one lap before exporting.")
        return
    ts = datetime.now()
    out_file = f"session_{ts.strftime('%d%m%Y_%H%M%S')}.txt"
    try:
        with open(out_file, 'w') as f:
            f.write(f"Session recorded: {ts.strftime('%d-%m-%Y %H:%M:%S')}\n\n")
            for i, lt in enumerate(saved_laps, 1):
                f.write(f"  Lap {i:02d}: {lt}\n")
            f.write("\n")
            if saved_lap_secs:
                f.write(f"Best:  {to_hhmmss(min(saved_lap_secs))}\n")
                f.write(f"Worst: {to_hhmmss(max(saved_lap_secs))}\n")
            f.write(f"\n{len(saved_laps)} laps total\n")
        messagebox.showinfo("Export done", f"Saved as:\n{out_file}")
    except IOError as e:
        messagebox.showerror("Export failed", f"Couldn't write file:\n{e}")


win = tk.Tk()
win.title("Stopwatch")
win.minsize(320, 480)
win.resizable(False, False)
win.configure(bg='#f0f0f0')

tk.Label(win, text="Stopwatch", font='Verdana 14 bold',
         bg='#f0f0f0', fg='#2c3e50').pack(pady=(12, 0))

timer_disp = tk.Label(win, text='Ready!', fg='#2c3e50',
                      font='Verdana 36 bold', bg='#f0f0f0')
timer_disp.pack(pady=10)

btn_row = tk.Frame(win, bg='#f0f0f0')
btn_row.pack(pady=5)

_common = dict(width=6, font='Verdana 10', fg='white', relief='flat')

btn_start  = tk.Button(btn_row, text='Start', bg='#27ae60', **_common,
                       command=lambda: press_start(timer_disp))
btn_pause  = tk.Button(btn_row, text='Stop',  bg='#e74c3c', **_common,
                       state='disabled', command=press_pause)
btn_clear  = tk.Button(btn_row, text='Reset', bg='#95a5a6', **_common,
                       state='disabled', command=lambda: press_clear(timer_disp))
btn_addlap = tk.Button(btn_row, text='Lap',   bg='#2980b9', **_common,
                       state='disabled', command=press_addlap)

for _b in (btn_start, btn_pause, btn_clear, btn_addlap):
    _b.pack(side='left', padx=3)

pb_panel = tk.Frame(win, bg='#e8e8e8')
pb_panel.pack(fill='x', padx=15, pady=(10, 0))

pb_best  = tk.Label(pb_panel, text="Best:   --:--:--",
                    font='Courier 10', bg='#e8e8e8', fg='#27ae60', anchor='w')
pb_worst = tk.Label(pb_panel, text="Worst:  --:--:--",
                    font='Courier 10', bg='#e8e8e8', fg='#e74c3c', anchor='w')
pb_best.pack(fill='x',  padx=10, pady=(6, 0))
pb_worst.pack(fill='x', padx=10, pady=(0, 6))

tk.Label(win, text="Lap History", font='Verdana 10 bold',
         bg='#f0f0f0', fg='#2c3e50').pack(pady=(10, 2))

hist_frame = tk.Frame(win, bg='#f0f0f0')
hist_frame.pack(padx=15, fill='both', expand=True)

hist_scroll = tk.Scrollbar(hist_frame)
hist_scroll.pack(side='right', fill='y')

lap_history = tk.Listbox(hist_frame, font='Courier 11', height=8,
                         bg='white', fg='#2c3e50', selectbackground='#d6eaf8',
                         relief='flat', bd=1, highlightthickness=0,
                         yscrollcommand=hist_scroll.set)
lap_history.pack(side='left', fill='both', expand=True)
hist_scroll.config(command=lap_history.yview)

tk.Button(win, text='Export Session', font='Verdana 10',
          bg='#8e44ad', fg='white', relief='flat',
          padx=10, pady=5, command=export_session).pack(pady=12)

win.mainloop()
