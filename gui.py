from tkinter     import *
from tkinter.ttk import *
from tkinter     import filedialog
from tkinter     import messagebox

import os
import traceback
import time

import addon

class AddonFrame(Label):
    def __init__(self, master, addon, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.addon = addon
        self.create_widgets()
        self.pack()

    def extract_file(self):
        index = self.files_list.curselection()
        if not index:
            messagebox.showinfo("", "No file selected")
            return
        index = index[0]
        file = self.files_list.get(index)

        file_ext = "*" + os.path.splitext(file)[1]
        file_type = file_ext[2:].upper() + " file"
        path = filedialog.asksaveasfilename(
            filetypes = [
                (file_type, file_ext),
                ("All files", "*.*")
            ]
        )
        if not path:
            return

        self.addon.entries[index].save(path)

    def extract_all(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.progress_bar = Progressbar(self)
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.addon.entries)
        self.progress_bar.grid(row = 6, columnspan = 3)
        for i, entry in enumerate(self.addon.entries):
            self.progress_bar["value"] = i
            self.master.update()
            file_path = os.path.join(folder_path, entry.name)
            file_path = os.path.split(file_path) # (path, filename)
            os.makedirs(file_path[0], exist_ok = True)
            entry.save(os.path.join(*file_path))
        self.progress_bar.destroy()
        del self.progress_bar
        messagebox.showinfo("", "%s files extracted" % len(self.addon.entries))

    def create_widgets(self):
        self.name_label   = Label(self, text = "Name:")
        self.author_label = Label(self, text = "Author:")
        self.type_label   = Label(self, text = "Type:")
        self.desc_label   = Label(self, text = "Description:")
        self.files_label  = Label(self, text = "Files:")

        self.name_label.grid(column = 0, sticky = W)
        self.author_label.grid(column = 0, sticky = W)
        self.type_label.grid(column = 0, sticky = W)
        self.desc_label.grid(column = 0, sticky = W)
        self.files_label.grid(column = 0, sticky = W, rowspan = 2)

        self.name_text = Entry(self, width = 50)
        self.name_text.insert(INSERT, self.addon.name)
        self.name_text.config(state = "readonly")
        self.author_text = Entry(self, width = 50)
        self.author_text.insert(INSERT, self.addon.author)
        self.author_text.config(state = "readonly")
        self.type_text = Entry(self, width = 50)
        self.type_text.insert(INSERT, self.addon.type)
        self.type_text.config(state = "readonly")
        self.desc_text = Entry(self, width = 50)
        self.desc_text.insert(INSERT, self.addon.desc)
        self.desc_text.config(state = "readonly")

        self.name_text.grid(column = 1, row = 0, sticky = W)
        self.author_text.grid(column = 1, row = 1, sticky = W)
        self.type_text.grid(column = 1, row = 2, sticky = W)
        self.desc_text.grid(column = 1, row = 3, sticky = W)


        self.files_list = Listbox(self, height = 3, width = 50)
        for entry in self.addon.entries:
            self.files_list.insert(END, entry.name)
        self.files_list.grid(column = 1, row = 4, sticky = W, rowspan = 2)

        self.extract_file_button = Button(self, text = "Extract", command = self.extract_file)
        self.extract_file_button.grid(column = 2, row = 4, sticky = W)

        self.extract_all_button  = Button(self, text = "Extract all", command = self.extract_all)
        self.extract_all_button.grid(column = 2, row = 5)

class Application(Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.addons = {}
        self.tabs   = {}
        self.master.title("Garry's Mod Addon Viewer")
        self.create_widgets()
        self.master.geometry("650x300")
        self.pack()

    def create_widgets(self):
        self.menu_bar = Menu(self.master, tearoff=0)
        self.file_menu = Menu(self.menu_bar)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Exit", command=self.close_file)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.master.config(menu=self.menu_bar)
        self.notebook = Notebook(self)
        # self.notebook.pack()

    def open_file(self):
        fname = filedialog.askopenfilename(
            filetypes = [
                ("Garry's Mod Addon", "*.gma"),
                ("All files", "*")
            ]
        )

        if fname:
            try:
                self.add_addon(fname)
            except BaseException as e:
                ename = e.__class__.__name__
                traceback.print_exc()
                messagebox.showerror(ename, traceback.format_exc())

    def close_file(self):
        self.master.destroy() # maybe not the best way

    def add_addon(self, path):
        if path in self.addons:
            messagebox.showinfo("", path + " is already loaded as " + self.addons[path].name)
            return
        self.addons[path] = addon.load(path)
        self.update_notebook()

    def update_notebook(self):
        self.notebook.destroy()
        self.tabs.clear()
        self.notebook = Notebook(self)
        for path, addon in self.addons.items():
            self.tabs[addon.name] = AddonFrame(self.notebook, addon)
            self.notebook.add(self.tabs[addon.name], text = addon.name, padding = 10)
        self.notebook.pack()
