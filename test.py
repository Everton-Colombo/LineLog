import tkinter as tk

root = tk.Tk()
photo = tk.PhotoImage(file='sprites/minus.png')
tk.Button(root, image=photo, width=16, height=16, relief=None).pack()
root.mainloop()