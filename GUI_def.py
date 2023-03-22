import matplotlib
import matplotlib.ticker
import matplotlib.dates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import messagebox, ttk
import pickle
from datetime import date, timedelta
import main_database_integration as mdb
import outer_database_integration as odb
import xtra_widgets as xw
matplotlib.use('TkAgg')

TITLE_FONT = ('Helvetica', 20, 'bold')
FIELD_FONT = ('Helvetica', 10, 'bold')
FIELD_CONTENT_FONT = ('Helvetica', 9)

with open('settings.config', 'rb') as file:     # Get settings dict
    settings = pickle.load(file)
with open('languages/{}.lang'.format(settings["language"]), 'rb') as file:
    lang = pickle.load(file)

MONTH_DAYS = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

class LineLogApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("LineLog")

        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.menu_bars = {}

        self.curr_user_info = []
        self.curr_user_info_con = [tk.StringVar(value='_'), tk.StringVar(value='_'), tk.StringVar(value='_')]

        for F in (LoginPage, HomePage, SellPage, ProductsPage, CostumersPage, StatsPage, SettingsPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(CostumersPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if hasattr(frame, "geometry"):  self.geometry(frame.geometry)
        if hasattr(frame, "OnEnter"): frame.OnEnter()
        self.config(menu=frame.menu_bar if hasattr(frame, "menu_bar") else tk.Menu(self))    # Updates Menu_bar
        frame.tkraise()


class LoginPage(tk.Frame):

    def login(self, usr, pw, controller):
        result = odb.validate_user(usr, pw)
        if result == 1:
            self.username_var.set('')
            self.password_var.set('')
            controller.curr_user_info = list(odb.get_user_info(usr))
            controller.curr_user_info_con[0].set(controller.curr_user_info[0])
            controller.curr_user_info_con[1].set(controller.curr_user_info[1])
            controller.curr_user_info_con[2].set(controller.curr_user_info[2])
            controller.show_frame(HomePage)
        elif result == -1:
            messagebox.showerror(lang['login_page']['invalid_credentials_popup_title'],
                                 lang['login_page']['invalid_credentials_popup_msg'])
        elif result == -2:
            messagebox.showwarning(lang['login_page']['incorrect_usrname_popup_title'],
                                   lang['login_page']['incorrect_usrname_popup_msg'])
        else:
            messagebox.showwarning(lang['login_page']['incorrect_pw_popup_title'],
                                   lang['login_page']['incorrect_pw_popup_msg'])

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.geometry = "200x250"

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.input_frame = tk.Frame(self, bd=1, padx=5, pady=5, relief="sunken")

        self.title = tk.Label(self, text=lang['login_page']['title'], font=TITLE_FONT)
        self.username_label = tk.Label(self.input_frame, text=lang['login_page']['usr'], font=FIELD_FONT)
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.input_frame, textvariable=self.username_var, width=25)
        self.password_label = tk.Label(self.input_frame, text=lang['login_page']['pw'], font=FIELD_FONT)
        self. password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.input_frame, textvariable=self.password_var, show='*')
        self.password_entry.bind("<Return>", lambda event: self.login(self.username_var.get(), self.password_var.get(),
                                                                      controller))
        self.login_button = tk.Button(self.input_frame, text=lang['login_page']['login_button'], font=FIELD_FONT,
                                      command=lambda: self.login(self.username_var.get(), self.password_var.get(),
                                                                 controller))

        self.title.grid(row=0, column=0, sticky='w')
        self.input_frame.grid(row=1, column=0)
        self.username_label.grid(row=0, column=0)
        self.username_entry.grid(row=1, column=0, sticky='w')
        self.password_label.grid(row=2, column=0)
        self.password_entry.grid(row=3, column=0, sticky='ew')
        self.login_button.grid(row=4, column=0, sticky='ew', pady=10)


class HomePage(tk.Frame):

    def OnEnter(self):
        self.products_box.sv.set('')
        self.products_box.search()
        self.sales_box.sv.set('')
        self.sales_box.search()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.geometry = '725x300'

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label=lang['menu_bar']['sell'], command=lambda: controller.show_frame(SellPage))
        self.menu_bar.add_command(label=lang['menu_bar']['products'],
                                  command=lambda: controller.show_frame(ProductsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['costumers'],
                                  command=lambda: controller.show_frame(CostumersPage))
        self.menu_bar.add_command(label=lang['menu_bar']['stats'], command=lambda: controller.show_frame(StatsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['settings'],
                                  command=lambda: controller.show_frame(SettingsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['log_out'], command=lambda: controller.show_frame(LoginPage))

        self.title = tk.Label(self, text=lang['home_page']['title'], font=TITLE_FONT)
        self.current_user_field = tk.Label(self, text=lang['home_page']['cur_usr'], font=FIELD_FONT)
        self.current_user_content = tk.Label(self, textvariable=controller.curr_user_info_con[0],
                                             font=FIELD_CONTENT_FONT)
        self.role_field = tk.Label(self, text=lang['home_page']['usr_role'], font=FIELD_FONT)
        self.role_content = tk.Label(self, textvariable=controller.curr_user_info_con[1], font=FIELD_CONTENT_FONT)

        self.products_frame = tk.LabelFrame(self, text=lang['home_page']['prods_frame_title'])
        self.sales_frame = tk.LabelFrame(self, text=lang['home_page']['sales_frame_title'], width=500)
        self.products_box = xw.DBSearchBox(self.products_frame, mdb.connection, 'products', 'name',
                                           ('name', 'quantity'), width=25)
        self.sales_box = xw.DBSearchBox(self.sales_frame, mdb.connection,
                                        sql="SELECT costumers.name, CAST(salesHistory.totalPrice AS float) / "
                                            "100.0 FROM salesHistory "
                                            "JOIN costumers ON salesHistory.costumer = costumers._id",
                                        pfilter="WHERE costumers.name LIKE '%{sv}%'",
                                        width=40)

        self.title.grid(row=0, column=0, columnspan=4, sticky='w')
        self.current_user_field.grid(row=1, column=0, sticky='w')
        self.current_user_content.grid(row=1, column=1, sticky='w')
        self.role_field.grid(row=2, column=0, sticky='w')
        self.role_content.grid(row=2, column=1, sticky='w')
        self.products_frame.grid(row=1, column=2, rowspan=10, padx=15)
        self.products_box.grid(row=0, column=0, sticky='ew', padx=5, pady=2)
        self.sales_frame.grid(row=1, column=3, rowspan=10, padx=15)
        self.sales_box.grid(row=0, column=0, sticky='ew', padx=5, pady=2)


class SellPage(tk.Frame):

    def OnEnter(self):
        self.remove_costumer()
        self.selected_product = 0
        self.selected_product_maxquantity = -1
        self.items.clear()
        self.total_price = 0
        self.total_price_var.set('$0.00')
        self.receipt_scrollbox.clear()
        mdb.connection.rollback()
        self.product_searchbox.sv.set('')
        self.product_searchbox.search()

        self.product_manipulation_frame.grid_remove()
        self.remove_item_button.grid_remove()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.cross_image = tk.PhotoImage(file='sprites/cross.png')
        self.tick_image = tk.PhotoImage(file='sprites/tick.png')
        self.plus_image = tk.PhotoImage(file='sprites/plus.png')
        self.minus_image = tk.PhotoImage(file='sprites/minus.png')
        self.trash_image = tk.PhotoImage(file='sprites/trash.png')
        self.right_arrow_image = tk.PhotoImage(file='sprites/right_arrow.png')

        self.geometry = '500x450'

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label=lang['menu_bar']['home'], command=lambda: controller.show_frame(HomePage))
        self.menu_bar.add_command(label=lang['menu_bar']['products'],
                                  command=lambda: controller.show_frame(ProductsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['costumers'],
                                  command=lambda: controller.show_frame(CostumersPage))
        self.menu_bar.add_command(label=lang['menu_bar']['stats'], command=lambda: controller.show_frame(StatsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['settings'],
                                  command=lambda: controller.show_frame(SettingsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['log_out'], command=lambda: controller.show_frame(LoginPage))

        self.title = tk.Label(self, text=lang['sell_page']['title'], font=TITLE_FONT)

        self.costumer_field = tk.Label(self, text=lang['sell_page']['costumer_select_label'], font=FIELD_FONT)
        self.costumer_var = tk.StringVar(value=lang['sell_page']['not_mentioned_preval'])
        self.costumer_id = 0
        self.costumer_content = tk.Label(self, textvariable=self.costumer_var, font=FIELD_CONTENT_FONT)
        self.costumer_delete = tk.Button(self, image=self.minus_image, width=16, height=16, relief='ridge',
                                         command=self.remove_costumer)
        self.costumer_search = tk.Button(self, image=self.plus_image, width=16, height=16, relief='ridge',
                                         command=self.get_costumer)

        self.selected_product = 0
        self.selected_product_maxquantity = -1
        self.add_product_frame = tk.LabelFrame(self, text=lang['sell_page']['add_prod_frame_title'], pady=5)
        self.product_searchbox = xw.DBSearchBox(self.add_product_frame, mdb.connection,
                                                sql="SELECT name, CAST(retailPrice AS float) / 100.0, quantity "
                                                    "FROM products WHERE quantity > 0",
                                                pfilter="AND name LIKE '%{sv}%'",
                                                width=25, height=15)
        self.product_searchbox.scroll_box.list_box.bind("<<ListboxSelect>>", self._on_product_select)
        self.product_manipulation_frame = tk.Frame(self.add_product_frame)
        self.product_quantity_label = tk.Label(self.product_manipulation_frame,
                                               text=lang['sell_page']['quantity_label'])
        self.product_quantity_spinbox = tk.Spinbox(self.product_manipulation_frame, width=5)
        self.product_quantity_spinbox.bind("<Return>", lambda event: self._on_product_add())
        self.add_product_button = tk.Button(self.product_manipulation_frame, image=self.plus_image, width=20, height=20,
                                            command=self._on_product_add)

        self.items = []
        self.selected_receipt_index = -1
        self.receipt_frame = tk.LabelFrame(self, text=lang['sell_page']['receipt_frame_title'], padx=5, pady=6)
        self.receipt_scrollbox = xw.ScrollBox(self.receipt_frame, height=15, width=25)
        self.receipt_scrollbox.list_box.bind("<<ListboxSelect>>", self._on_receipt_select)
        self.total_price = 0.0
        self.total_price_field = tk.Label(self.receipt_frame, text=lang['sell_page']['total_label'], font=FIELD_FONT)
        self.total_price_var = tk.StringVar(value='$0.00')
        self.total_price_l = tk.Label(self.receipt_frame, textvariable=self.total_price_var, font=FIELD_CONTENT_FONT)
        self.remove_item_button = tk.Button(self.receipt_frame, text=lang['sell_page']['remove_item_button'],
                                            command=self._on_product_remove)
        self.cancel_button = tk.Button(self.receipt_frame, image=self.cross_image, width=20, height=20,
                                       command=self.cancel_sale)
        self.pay_button = tk.Button(self.receipt_frame, image=self.tick_image, command=self.checkout,
                                    width=20, height=20)

        self.title.grid(row=0, column=0, columnspan=5, sticky='w')
        self.costumer_field.grid(row=1, column=0, sticky='w')
        self.costumer_content.grid(row=1, column=1, sticky='w')
        self.costumer_delete.grid(row=1, column=2, sticky='w')
        self.costumer_delete.grid_remove()
        self.costumer_search.grid(row=1, column=3, sticky='w')

        self.add_product_frame.grid(row=2, column=0, columnspan=4, rowspan=3, sticky='nsw', padx=5)
        self.product_searchbox.grid(row=0, column=0, sticky='e', padx=7, pady=5)
        self.product_manipulation_frame.grid(row=1, column=0, sticky='ew')
        self.product_quantity_label.grid(row=0, column=0, sticky='w')
        self.product_quantity_spinbox.grid(row=0, column=1, sticky='nsw')
        self.add_product_button.grid(row=0, column=2, sticky='e')

        self.receipt_frame.grid(row=2, column=4, rowspan=5, columnspan=2, sticky='nse', padx=50)
        self.receipt_scrollbox.grid(row=0, column=0, sticky='nsew', columnspan=3)
        self.total_price_field.grid(row=1, column=0, sticky='w')
        self.total_price_l.grid(row=1, column=1, sticky='w')
        self.remove_item_button.grid(row=2, column=0, columnspan=3, sticky='ew')
        self.cancel_button.grid(row=3, column=0, sticky='w')
        self.pay_button.grid(row=3, column=2, sticky='e')

    def get_costumer(self):

        def on_proceed(ref):
            if search_box.scroll_box.list_box.curselection():
                index = search_box.scroll_box.list_box.curselection()[0]
                selection = search_box.scroll_box.list_box.get(index).split(' | ')

                ref.costumer_id = int(selection[0])
                ref.costumer_var.set(selection[1])

                ref.costumer_search.grid_remove()
                ref.costumer_delete.grid()

                get_costumer_frame.destroy()

        get_costumer_frame = tk.Toplevel(self, padx=5, pady=5)
        get_costumer_frame.resizable(0, 0)
        get_costumer_frame.title(lang['sell_page']['search_popup_title'])

        search_box = xw.DBSearchBox(get_costumer_frame, mdb.connection,
                                    "costumers", "name", ("_id", "name"),
                                    width=30)
        search_box.scroll_box.list_box.bind("<Return>", lambda event: on_proceed(self))

        select_button = tk.Button(get_costumer_frame, text=lang['sell_page']['search_popup_select'],
                                  command=lambda: on_proceed(self))
        cancel_button = tk.Button(get_costumer_frame, text=lang['sell_page']['search_popup_cancel'],
                                  command=get_costumer_frame.destroy)

        search_box.grid(row=0, column=0, sticky='nsew', columnspan=2)
        cancel_button.grid(row=1, column=0, sticky='nsew')
        select_button.grid(row=1, column=1, sticky='nsew')

    def _on_product_select(self, event):
        if event.widget.curselection():
            index = event.widget.curselection()[0]
            selection = event.widget.get(index).split(' | ')

            self.selected_product = mdb.connection.execute("SELECT _id FROM products WHERE name = ?",
                                                           (selection[0],)).fetchone()[0]

            self.product_manipulation_frame.grid()

            self.selected_product_maxquantity = int(selection[2])

            self.product_quantity_spinbox.config(from_=0, to=self.selected_product_maxquantity)
        else:
            self.product_manipulation_frame.grid_remove()

    def _on_product_add(self):
        sel_prod_quantity = int(self.product_quantity_spinbox.get())

        if 0 < sel_prod_quantity <= self.selected_product_maxquantity:
            if self.selected_product:
                self.items.append([self.selected_product, int(self.product_quantity_spinbox.get())])
                sel_prod_name, sel_prod_price = mdb.connection.execute("SELECT name, retailPrice FROM products "
                                                                       "WHERE _id = ?",
                                                                       (self.selected_product,)).fetchone()
                self.receipt_scrollbox.insert(tk.END, " | ".join([sel_prod_name, 'x'+str(sel_prod_quantity),
                                                                 '$'+str(sel_prod_price/100 * sel_prod_quantity)]))
                self.total_price += sel_prod_price/100 * sel_prod_quantity
                self.total_price_var.set('${:.2f}'.format(self.total_price))

                mdb.connection.execute("UPDATE products SET quantity = ? WHERE _id = ?",
                                       (self.selected_product_maxquantity - sel_prod_quantity, self.selected_product))
                self.product_searchbox.search()

                # Reset values:
                self.selected_product = 0
                self.product_manipulation_frame.grid_remove()
        else:
            messagebox.showinfo(lang['sell_page']['invalid_quant_popup_title'],
                                lang['sell_page']['invalid_quant_popup_msg'])

    def _on_receipt_select(self, event):
        if event.widget.curselection():
            self.selected_receipt_index = event.widget.curselection()[0]
            self.remove_item_button.grid()
        else:
            self.remove_item_button.grid_remove()

    def _on_product_remove(self):
        product_id = self.items[self.selected_receipt_index][0]
        product_quantity = self.items[self.selected_receipt_index][1]
        product_price = mdb.connection.execute("SELECT retailPrice FROM products WHERE _id = ?",
                                               (product_id,)).fetchone()[0]

        self.total_price -= (product_price/100)*product_quantity
        self.total_price_var.set('${:.2f}'.format(self.total_price))
        self.items.pop(self.selected_receipt_index)
        self.receipt_scrollbox.list_box.delete(self.selected_receipt_index)

        old_quantity = mdb.connection.execute("SELECT quantity FROM products WHERE _id = ?",
                                              (product_id,)).fetchone()[0]
        mdb.connection.execute("UPDATE products SET quantity = ? WHERE _id = ?",
                               (old_quantity + product_quantity, product_id))
        self.product_searchbox.search()

        self.remove_item_button.grid_remove()

    def cancel_sale(self):
        if messagebox.askyesno(lang['sell_page']['cancel_sale_popup_title'],
                               lang['sell_page']['cancel_sale_popup_msg']):
            mdb.connection.rollback()
            self.OnEnter()

    def remove_costumer(self):
        self.costumer_id = 0
        self.costumer_var.set(lang['sell_page']['not_mentioned_preval'])

        self.costumer_delete.grid_remove()
        self.costumer_search.grid()

    def checkout(self):

        if self.costumer_id and self.items:

            def done(s_atr):
                mdb.connection.rollback()
                mdb.register_sale(s_atr.items, s_atr.costumer_id, method_var.get())
                mdb.connection.commit()
                s_atr.OnEnter()

                checkout_frame.destroy()

                messagebox.showinfo(lang['sell_page']['done_popup_title'], lang['sell_page']['done_popup_msg'])

            checkout_frame = tk.Toplevel(self, padx=5, pady=2)
            checkout_frame.title(lang['sell_page']['checkout_popup_title'])

            receipt_frame = tk.LabelFrame(checkout_frame, text=lang['sell_page']['checkout_popup_receipt_frame_title'],
                                          padx=5, pady=6)
            receipt_scrollbox = xw.ScrollBox(receipt_frame, height=15, width=25)
            receipt_scrollbox.special_insert(tk.END, self.receipt_scrollbox.list_box.get(0, tk.END))
            total_price_field = tk.Label(receipt_frame, text=lang['sell_page']['checkout_popup_total'], font=FIELD_FONT)
            total_price_var = tk.StringVar(value=self.total_price_var.get())
            total_price = tk.Label(receipt_frame, textvariable=total_price_var, font=FIELD_CONTENT_FONT)

            payment_method_frame = tk.LabelFrame(checkout_frame,
                                                 text=lang['sell_page']['checkout_popup_paymethod_frame_title'])
            method_var = tk.IntVar(value=1)
            cash_radiob = tk.Radiobutton(payment_method_frame, text=lang['sell_page']['checkout_popup_paymethod_cash'],
                                         variable=method_var, value=1)
            debit_radiob = tk.Radiobutton(payment_method_frame,
                                          text=lang['sell_page']['checkout_popup_paymethod_debit'],
                                          variable=method_var, value=2)
            credit_radiob = tk.Radiobutton(payment_method_frame,
                                           text=lang['sell_page']['checkout_popup_paymethod_credit'],
                                           variable=method_var, value=3)

            done_button = tk.Button(checkout_frame, image=self.tick_image, width=20, height=20,
                                    command=lambda: done(self))
            cancel_button = tk.Button(checkout_frame, image=self.cross_image, width=20, height=20,
                                      command=checkout_frame.destroy)

            #

            receipt_frame.grid(row=0, column=0, sticky='nsew', columnspan=2)
            receipt_scrollbox.grid(row=0, column=0, sticky='nsew', columnspan=3)
            total_price_field.grid(row=1, column=0, sticky='w')
            total_price.grid(row=1, column=1, sticky='w')

            payment_method_frame.grid(row=1, column=0, sticky='nsew', columnspan=2)
            cash_radiob.grid(row=0, column=0, sticky='w')
            debit_radiob.grid(row=1, column=0, sticky='w')
            credit_radiob.grid(row=2, column=0, sticky='w')

            cancel_button.grid(row=2, column=0, sticky='w')
            done_button.grid(row=2, column=1, sticky='e')
        else:
            messagebox.showwarning(lang['sell_page']['proceed_unfinished_sale_popup_title'],
                                   lang['sell_page']['proceed_unfinished_sale_popup_msg'])

    def _on_getcostumer_select_(self, event):
        index = event.widget.curselection()[0]
        selection = event.widget.get(index).split(' | ')
        print(selection)
        self.costumer_id = selection[0]
        self.costumer_var.set(selection[1])


class ProductsPage(tk.Frame):

    def OnEnter(self):
        self.search_products_searchbox.sv.set('')
        self.search_products_searchbox.search()
        self.selected_product_id = 0
        self.info_name_var.set('')
        self.info_quantity_var.set('')
        self.info_cost_var.set('')
        self.info_retail_price_var.set('')
        self.info_profit_percentage_var.set('')
        self.edit_button.grid_remove()
        self.delete_product_button.grid_remove()
        self.movement_scrollbox.clear()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.geometry = '800x425'

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label=lang['menu_bar']['home'], command=lambda: controller.show_frame(HomePage))
        self.menu_bar.add_command(label=lang['menu_bar']['sell'], command=lambda: controller.show_frame(SellPage))
        self.menu_bar.add_command(label=lang['menu_bar']['costumers'],
                                  command=lambda: controller.show_frame(CostumersPage))
        self.menu_bar.add_command(label=lang['menu_bar']['stats'], command=lambda: controller.show_frame(StatsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['settings'],
                                  command=lambda: controller.show_frame(SettingsPage))
        self.menu_bar.add_command(label=lang['menu_bar']['log_out'], command=lambda: controller.show_frame(LoginPage))

        self.title = tk.Label(self, text=lang['products_page']['title'], font=TITLE_FONT)

        self.search_products_frame = tk.LabelFrame(self, text=lang['products_page']['search_prods_frame_title'],
                                                   padx=5, pady=5)
        self.selected_product_id = 0
        self.search_products_searchbox = xw.DBSearchBox(self.search_products_frame, mdb.connection,
                                                        "products", "name", ("_id", "name"),
                                                        width=25, height=15)
        self.search_products_searchbox.scroll_box.list_box.bind("<<ListboxSelect>>", self._on_product_select)
        self.product_info_frame = tk.LabelFrame(self.search_products_frame,
                                                text=lang['products_page']['info_frame_title'], padx=5, pady=2)
        self.info_name_var = tk.StringVar()
        self.info_quantity_var = tk.StringVar()
        self.info_cost_var = tk.StringVar()
        self.info_retail_price_var = tk.StringVar()
        self.info_profit_percentage_var = tk.StringVar()
        self.info_name_f = tk.Label(self.product_info_frame, text=lang['products_page']['info_frame_name'],
                                    font=FIELD_FONT)
        self.info_name_l = tk.Label(self.product_info_frame, textvariable=self.info_name_var,
                                    font=FIELD_CONTENT_FONT)
        self.info_quantity_f = tk.Label(self.product_info_frame, text=lang['products_page']['info_frame_quantity'],
                                        font=FIELD_FONT)
        self.info_quantity_l = tk.Label(self.product_info_frame, textvariable=self.info_quantity_var,
                                        font=FIELD_CONTENT_FONT)
        self.info_cost_f = tk.Label(self.product_info_frame, text=lang['products_page']['info_frame_cost'],
                                    font=FIELD_FONT)
        self.info_cost_l = tk.Label(self.product_info_frame, textvariable=self.info_cost_var, font=FIELD_CONTENT_FONT)
        self.info_retail_price_f = tk.Label(self.product_info_frame,
                                            text=lang['products_page']['info_frame_retail_price'], font=FIELD_FONT)
        self.info_retail_price_l = tk.Label(self.product_info_frame, textvariable=self.info_retail_price_var,
                                            font=FIELD_CONTENT_FONT)
        self.info_profit_percentage_f = tk.Label(self.product_info_frame,
                                                 text=lang['products_page']['info_frame_profit_margin'], font=FIELD_FONT)
        self.info_profit_percentage_l = tk.Label(self.product_info_frame, textvariable=self.info_profit_percentage_var,
                                                 font=FIELD_CONTENT_FONT)

        self.edit_button = tk.Button(self.product_info_frame, text=lang['products_page']['edit_prod_button'],
                                     command=self._on_product_edit)
        self.delete_product_button = tk.Button(self.product_info_frame,
                                               text=lang['products_page']['delete_prod_button'], fg='red',
                                               command=self._on_product_delete)

        self.product_movement_frame = tk.LabelFrame(self.product_info_frame,
                                                    text=lang['products_page']['product_movement_frame_title'], padx=5, pady=2)
        self.movement_scrollbox = xw.ScrollBox(self.product_movement_frame, height=14, width=50)

        self.new_product_button = tk.Button(self.search_products_frame, text=lang['products_page']['new_prod_button'],
                                            fg='lime', command=self._on_new_product)

        self.title.grid(row=0, column=0, sticky='nw')

        self.search_products_frame.grid(row=1, column=0, sticky='nsew', padx=10)
        self.search_products_searchbox.grid(row=0, column=0, sticky='nsew', padx=(5, 25))

        self.product_info_frame.grid(row=0, column=1, sticky='nsew')
        self.info_name_f.grid(row=0, column=0, sticky='w')
        self.info_name_l.grid(row=0, column=1, sticky='w')
        self.info_quantity_f.grid(row=1, column=0, sticky='w')
        self.info_quantity_l.grid(row=1, column=1, sticky='w')
        self.info_cost_f.grid(row=2, column=0, sticky='w')
        self.info_cost_l.grid(row=2, column=1, sticky='w')
        self.info_retail_price_f.grid(row=3, column=0, sticky='w')
        self.info_retail_price_l.grid(row=3, column=1, sticky='w')
        self.info_profit_percentage_f.grid(row=4, column=0, sticky='w')
        self.info_profit_percentage_l.grid(row=4, column=1, sticky='w')

        self.edit_button.grid(row=5, column=0, columnspan=2, sticky='ew')
        self.edit_button.grid_remove()
        self.delete_product_button.grid(row=6, column=0, columnspan=2, sticky='ew')
        self.delete_product_button.grid_remove()

        self.product_movement_frame.grid(row=0, column=2, rowspan=15, sticky='nsew', padx=(10, 0))
        self.movement_scrollbox.grid(row=0, column=0, sticky='nsew')

        self.new_product_button.grid(row=1, column=1, sticky='e', pady=2)

    def _on_product_select(self, event):
        if event.widget.curselection():
            index = event.widget.curselection()[0]
            selection = event.widget.get(index).split(' | ')

            self.selected_product_id = int(selection[0])
            name, quantity, cost, rprice = mdb.connection.execute("SELECT name, quantity, CAST(cost AS float) / 100.0, "
                                                                  "CAST(retailPrice AS float) / 100.0 "
                                                                  "FROM products WHERE _id = ?",
                                                                  (self.selected_product_id,)).fetchone()
            profit_margin = int(100*rprice / cost) - 100

            self.info_name_var.set(name)
            self.info_quantity_var.set(quantity)
            self.info_cost_var.set('${}'.format(cost))
            self.info_retail_price_var.set('${}'.format(rprice))
            self.info_profit_percentage_var.set('{}%'.format(profit_margin))

            self.edit_button.grid()
            self.delete_product_button.grid()

            out_movement = mdb.connection.execute("SELECT itemHistory.UTCTime, itemHistory.quantity, "
                                                  "salesHistory._id, costumers.name "
                                                  "FROM itemHistory "
                                                  "INNER JOIN salesHistory ON itemHistory.sale = salesHistory._id "
                                                  "INNER JOIN costumers ON salesHistory.costumer = costumers._id "
                                                  "WHERE itemHistory.item = ?",
                                                  (self.selected_product_id,)).fetchall()
            in_movement = mdb.connection.execute("SELECT UTCTime, quantity, 'n/a', 'n/a' FROM itemHistory "
                                                 "WHERE item = ? AND sale IS NULL",
                                                 (self.selected_product_id,)).fetchall()

            moves = []
            for move in out_movement:
                ent = ' | '.join([str(x) for x in move])
                moves.append(ent)
            for move in in_movement:
                ent = ' | '.join([str(x) for x in move])
                moves.append(ent)
            moves.sort(reverse=True)
            self.movement_scrollbox.clear()
            self.movement_scrollbox.special_insert(tk.END, tuple(moves))

    def _on_product_edit(self):

        def on_price_change():
            if cost_v.get() and rprice_v.get():
                try:
                    cost, rprice = int(cost_v.get()), int(rprice_v.get())
                except ValueError:
                    pass
                else:
                    profit_v.set('{}%'.format(int(100*rprice / cost) - 100))
            else:
                profit_v.set('n/a')

        def on_done(sref):
            if name_v.get():
                try:
                    new_vals = (name_v.get(), int(quantity_v.get()), int(cost_v.get()), int(rprice_v.get()))
                except ValueError:
                    messagebox.showerror(lang['products_page']['new_prod_invalidvals_popup_title'],
                                         lang['products_page']['new_prod_invalidvals_popup_msg'])
                else:
                    if prev_vals == new_vals:
                        edit_prod_frame.destroy()
                    else:
                        if not new_vals[0] == prev_vals[0]:
                            if mdb.edit_product(sref.selected_product_id, "name", new_vals[0]):  # Executes func.
                                                                                                 # if it rtrns a value
                                                                                                 # its bad
                                mdb.connection.rollback()
                                messagebox.showwarning(lang['products_page']['edit_fail_name_popup_title'],
                                                       lang['products_page']['edit_fail_name_popup_msg'])
                                sref.OnEnter()
                                return
                        if not new_vals[1] == prev_vals[1] and new_vals[1] >= 0:
                            movement = new_vals[1] - prev_vals[1]
                            mdb.edit_product(sref.selected_product_id, "quantity", new_vals[1])
                            mdb.register_item_movement(sref.selected_product_id, movement)

                        if not new_vals[2] == prev_vals[2] and new_vals[2] >= 0:
                            mdb.edit_product(sref.selected_product_id, "cost", new_vals[2])

                        if not new_vals[3] == prev_vals[3] and new_vals[3] >= 0:
                            mdb.edit_product(sref.selected_product_id, "retailPrice", new_vals[3])

                        mdb.connection.commit()
                        sref.OnEnter()
                        edit_prod_frame.destroy()
                        messagebox.showinfo(lang['products_page']['edit_prod_done_popup_title'],
                                            lang['products_page']['edit_prod_done_popup_msg'])

        edit_prod_frame = tk.Toplevel(self)
        edit_prod_frame.title(lang['products_page']['edit_prod_popup_title'])

        prev_vals = mdb.connection.execute("SELECT name, quantity, cost, retailPrice FROM products "
                                           "WHERE _id = ?", (self.selected_product_id,)).fetchone()

        name_l = tk.Label(edit_prod_frame, text=lang['products_page']['edit_prod_name'], font=FIELD_FONT)
        name_v = tk.StringVar(value=prev_vals[0])
        name_e = tk.Entry(edit_prod_frame, textvariable=name_v)
        quantity_l = tk.Label(edit_prod_frame, text=lang['products_page']['edit_prod_quantity'], font=FIELD_FONT)
        quantity_v = tk.StringVar(value=prev_vals[1])
        quantity_e = tk.Entry(edit_prod_frame, textvariable=quantity_v, width=5)
        cost_l = tk.Label(edit_prod_frame, text=lang['products_page']['edit_prod_cost'], font=FIELD_FONT)
        cost_v = tk.StringVar(value=prev_vals[2])
        cost_e = tk.Entry(edit_prod_frame, textvariable=cost_v, width=5)
        cost_v.trace('w', lambda name, index, mode: on_price_change())
        rprice_l = tk.Label(edit_prod_frame, text=lang['products_page']['edit_prod_retail_price'], font=FIELD_FONT)
        rprice_v = tk.StringVar(value=prev_vals[3])
        rprice_e = tk.Entry(edit_prod_frame, textvariable=rprice_v, width=5)
        rprice_v.trace('w', lambda name, index, mode: on_price_change())
        profit_f = tk.Label(edit_prod_frame, text=lang['products_page']['edit_prod_profit_margin'], font=FIELD_FONT)
        profit_v = tk.StringVar(value='n/a')
        on_price_change()
        profit_l = tk.Label(edit_prod_frame, textvariable=profit_v, font=FIELD_CONTENT_FONT)

        cancel_b = tk.Button(edit_prod_frame, text=lang['products_page']['edit_prod_cancel'],
                             command=edit_prod_frame.destroy)
        done_b = tk.Button(edit_prod_frame, text=lang['products_page']['edit_prod_done'], command=lambda: on_done(self))

        name_l.grid(row=0, column=0, sticky='w')
        name_e.grid(row=0, column=1, sticky='w')
        quantity_l.grid(row=1, column=0, sticky='w')
        quantity_e.grid(row=1, column=1, sticky='w')
        cost_l.grid(row=2, column=0, sticky='w')
        cost_e.grid(row=2, column=1, sticky='w')
        rprice_l.grid(row=3, column=0, sticky='w')
        rprice_e.grid(row=3, column=1, sticky='w')
        profit_f.grid(row=4, column=0, sticky='w')
        profit_l.grid(row=4, column=1, sticky='w')

        cancel_b.grid(row=5, column=0, sticky='ew', padx=2, pady=2)
        done_b.grid(row=5, column=1, sticky='ew', padx=2, pady=2)

    def _on_new_product(self):

        def on_price_change():
            if cost_v.get() and rprice_v.get():
                try:
                    cost, rprice = int(cost_v.get()), int(rprice_v.get())
                except ValueError:
                    pass
                else:
                    profit_v.set('{}%'.format(int(100*rprice / cost) - 100))
            else:
                profit_v.set('n/a')

        def on_create(sref):
            if name_v.get():
                try:
                    mdb.new_product(name_v.get(), int(quantity_v.get()), int(cost_v.get()), int(rprice_v.get()))
                except ValueError:
                    messagebox.showerror(lang['products_page']['new_prod_invalidvals_popup_title'],
                                         lang['products_page']['new_prod_invalidvals_popup_msg'])
                else:
                    sref.search_products_searchbox.sv.set('')
                    sref.search_products_searchbox.search()
                    new_prod_frame.destroy()
                    messagebox.showinfo(lang['products_page']['new_prod_done_popup_title'],
                                        lang['products_page']['new_prod_done_popup_msg'])

        new_prod_frame = tk.Toplevel(self)
        new_prod_frame.title(lang['products_page']['new_prod_popup_title'])

        name_l = tk.Label(new_prod_frame, text=lang['products_page']['new_prod_name'], font=FIELD_FONT)
        name_v = tk.StringVar()
        name_e = tk.Entry(new_prod_frame, textvariable=name_v)
        quantity_l = tk.Label(new_prod_frame, text=lang['products_page']['new_prod_initial_quantity'], font=FIELD_FONT)
        quantity_v = tk.StringVar()
        quantity_e = tk.Entry(new_prod_frame, textvariable=quantity_v, width=5)
        cost_l = tk.Label(new_prod_frame, text=lang['products_page']['new_prod_cost'], font=FIELD_FONT)
        cost_v = tk.StringVar()
        cost_e = tk.Entry(new_prod_frame, textvariable=cost_v, width=5)
        cost_v.trace('w', lambda name, index, mode: on_price_change())
        rprice_l = tk.Label(new_prod_frame, text=lang['products_page']['new_prod_retail_price'], font=FIELD_FONT)
        rprice_v = tk.StringVar()
        rprice_e = tk.Entry(new_prod_frame, textvariable=rprice_v, width=5)
        rprice_v.trace('w', lambda name, index, mode: on_price_change())
        profit_f = tk.Label(new_prod_frame, text=lang['products_page']['new_prod_profit_margin'], font=FIELD_FONT)
        profit_v = tk.StringVar(value='n/a')
        profit_l = tk.Label(new_prod_frame, textvariable=profit_v, font=FIELD_CONTENT_FONT)

        cancel_b = tk.Button(new_prod_frame, text=lang['products_page']['new_prod_cancel'],
                             command=new_prod_frame.destroy)
        create_b = tk.Button(new_prod_frame, text=lang['products_page']['new_prod_create'],
                             command=lambda: on_create(self))

        name_l.grid(row=0, column=0, sticky='w')
        name_e.grid(row=0, column=1, sticky='w')
        quantity_l.grid(row=1, column=0, sticky='w')
        quantity_e.grid(row=1, column=1, sticky='w')
        cost_l.grid(row=2, column=0, sticky='w')
        cost_e.grid(row=2, column=1, sticky='w')
        rprice_l.grid(row=3, column=0, sticky='w')
        rprice_e.grid(row=3, column=1, sticky='w')
        profit_f.grid(row=4, column=0, sticky='w')
        profit_l.grid(row=4, column=1, sticky='w')

        cancel_b.grid(row=5, column=0, sticky='ew', padx=2, pady=2)
        create_b.grid(row=5, column=1, sticky='ew', padx=2, pady=2)

    def _on_product_delete(self):
        if messagebox.askyesno(lang['products_page']['delete_prod_popup_title'],
                               lang['products_page']['delete_prod_popup_msg']):
            if mdb.delete_product(self.selected_product_id):
                messagebox.showerror(lang['products_page']['delete_error_popup_title'],
                                     lang['products_page']['delete_error_popup_msg'])
            else:
                self.OnEnter()


class CostumersPage(tk.Frame):

    def OnEnter(self):
        self.selected_costumer_id = 0
        self.info_name_var.set('')
        self.info_phone_var.set('')
        self.info_email_var.set('')
        self.info_bdate_var.set('')
        self.info_gender_var.set('')
        self.search_costumers_searchbox.sv.set('')
        self.search_costumers_searchbox.search()
        self.history_scrollbox.clear()
        self.history_scrollbox.insert(tk.END, "Sale ID | Date and Time | Total Price | Payment Method")
        self.more_info_scrollbox.clear()
        self.more_info_scrollbox.insert(tk.END, "Item Name | Quantity | Price")

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.geometry = '1100x425'

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label="Home", command=lambda: controller.show_frame(HomePage))
        self.menu_bar.add_command(label="Sell", command=lambda: controller.show_frame(SellPage))
        self.menu_bar.add_command(label="Products", command=lambda: controller.show_frame(ProductsPage))
        self.menu_bar.add_command(label="Stats", command=lambda: controller.show_frame(StatsPage))
        self.menu_bar.add_command(label="Settings", command=lambda: controller.show_frame(SettingsPage))
        self.menu_bar.add_command(label="Log Out", command=lambda: controller.show_frame(LoginPage))

        self.title = tk.Label(self, text="Costumers", font=TITLE_FONT)

        self.search_costumers_frame = tk.LabelFrame(self, text="Search Products", padx=5, pady=5)
        self.selected_costumer_id = 0
        self.search_costumers_searchbox = xw.DBSearchBox(self.search_costumers_frame, mdb.connection,
                                                         "costumers", "name", ("_id", "name"),
                                                         width=25, height=15)
        self.search_costumers_searchbox.scroll_box.list_box.bind("<<ListboxSelect>>", self._on_costumer_select)
        self.product_info_frame = tk.LabelFrame(self.search_costumers_frame, text="Info", padx=5, pady=2)
        self.info_name_var = tk.StringVar()
        self.info_phone_var = tk.StringVar()
        self.info_email_var = tk.StringVar()
        self.info_bdate_var = tk.StringVar()
        self.info_gender_var = tk.StringVar()
        self.info_name_f = tk.Label(self.product_info_frame, text="Name: ", font=FIELD_FONT)
        self.info_name_l = tk.Label(self.product_info_frame, textvariable=self.info_name_var,
                                    font=FIELD_CONTENT_FONT)
        self.info_phone_f = tk.Label(self.product_info_frame, text="Phone Number: ", font=FIELD_FONT)
        self.info_phone_l = tk.Label(self.product_info_frame, textvariable=self.info_phone_var,
                                     font=FIELD_CONTENT_FONT)
        self.info_email_f = tk.Label(self.product_info_frame, text="E-Mail: ", font=FIELD_FONT)
        self.info_email_l = tk.Label(self.product_info_frame, textvariable=self.info_email_var, font=FIELD_CONTENT_FONT)
        self.info_bdate_f = tk.Label(self.product_info_frame, text="Birth Date: ", font=FIELD_FONT)
        self.info_bdate_l = tk.Label(self.product_info_frame, textvariable=self.info_bdate_var,
                                     font=FIELD_CONTENT_FONT)
        self.info_gender_f = tk.Label(self.product_info_frame, text="Gender: ", font=FIELD_FONT)
        self.info_gender_l = tk.Label(self.product_info_frame, textvariable=self.info_gender_var,
                                      font=FIELD_CONTENT_FONT)

        self.edit_button = tk.Button(self.product_info_frame, text='Edit Costumer', command=self._on_costumer_edit)
        self.delete_costumer_button = tk.Button(self.product_info_frame, text='Delete Costumer', fg='red',
                                                command=self._on_costumer_delete)

        self.costumer_history_frame = tk.LabelFrame(self.product_info_frame, text="Costumer History", padx=5, pady=2)
        self.history_scrollbox = xw.ScrollBox(self.costumer_history_frame, height=14, width=50)
        self.history_scrollbox.list_box.bind("<<ListboxSelect>>", self._on_history_select)
        self.more_info_scrollbox = xw.ScrollBox(self.costumer_history_frame, height=14, width=30)

        self.new_costumer_button = tk.Button(self.search_costumers_frame, text="New Costumer", fg='lime',
                                             command=self._on_new_costumer)

        self.title.grid(row=0, column=0, sticky='nw')

        self.search_costumers_frame.grid(row=1, column=0, sticky='nsew', padx=10)
        self.search_costumers_searchbox.grid(row=0, column=0, sticky='nsew', padx=(5, 25))

        self.product_info_frame.grid(row=0, column=1, sticky='nsew')
        self.info_name_f.grid(row=0, column=0, sticky='w')
        self.info_name_l.grid(row=0, column=1, sticky='w')
        self.info_phone_f.grid(row=1, column=0, sticky='w')
        self.info_phone_l.grid(row=1, column=1, sticky='w')
        self.info_email_f.grid(row=2, column=0, sticky='w')
        self.info_email_l.grid(row=2, column=1, sticky='w')
        self.info_bdate_f.grid(row=3, column=0, sticky='w')
        self.info_bdate_l.grid(row=3, column=1, sticky='w')
        self.info_gender_f.grid(row=4, column=0, sticky='w')
        self.info_gender_l.grid(row=4, column=1, sticky='w')

        self.edit_button.grid(row=5, column=0, columnspan=2, sticky='ew')
        self.edit_button.grid_remove()
        self.delete_costumer_button.grid(row=6, column=0, columnspan=2, sticky='ew')
        self.delete_costumer_button.grid_remove()

        self.costumer_history_frame.grid(row=0, column=2, rowspan=15, sticky='nsew', padx=(10, 0))
        self.history_scrollbox.grid(row=0, column=0, sticky='nsew')
        self.more_info_scrollbox.grid(row=0, column=1, sticky='nsew')

        self.new_costumer_button.grid(row=1, column=1, sticky='e', pady=2)

    def _on_costumer_select(self, event):
        if event.widget.curselection():
            index = event.widget.curselection()[0]
            selection = event.widget.get(index).split(' | ')

            self.edit_button.grid()
            self.delete_costumer_button.grid()

            self.selected_costumer_id = selection[0]

            name, phone, email, bdate, gender = mdb.connection.execute("SELECT name, phoneNumber, email, dateOfBirth, "
                                                                       "gender FROM costumers WHERE _id = ?",
                                                                       (self.selected_costumer_id,)).fetchone()

            birth_date = pickle.loads(bdate)
            self.info_name_var.set(name)
            self.info_phone_var.set(phone if phone else 'n/a')
            self.info_email_var.set(email if email else 'n/a')
            self.info_bdate_var.set(birth_date.strftime("%d/%m/%y"))
            self.info_gender_var.set("Female" if int(gender) else "Male")

            history = mdb.connection.execute("SELECT _id, UTCTime, CAST(totalPrice AS float)/100.0, "
                                             "paymentMethod FROM salesHistory "
                                             "WHERE costumer = ? ORDER BY UTCTime DESC",
                                             (self.selected_costumer_id,)).fetchall()
            hist = []
            for val in history:
                ent = ' | '.join([str(x) for x in val])
                hist.append(ent)

            self.history_scrollbox.clear()
            self.history_scrollbox.special_insert(tk.END, tuple(hist))

    def _on_history_select(self, event):
        if event.widget.curselection():
            index = event.widget.curselection()[0]
            selection = event.widget.get(index).split(' | ')

            sale_id = selection[0]

            items_raw = mdb.connection.execute("SELECT items FROM salesHistory WHERE _id = ?", (sale_id,)).fetchone()
            items = pickle.loads(items_raw[0])

            result = []
            for item in items:
                name, pprice = mdb.connection.execute("SELECT name, CAST(retailPrice AS float)/100.0 FROM products "
                                                      "WHERE _id = ?",
                                                      (item[0],)).fetchone()
                fprice = pprice * item[1]

                ent = ' | '.join((name, 'x'+str(item[1]), '$'+str(fprice)))
                result.append(ent)

            self.more_info_scrollbox.clear()
            self.more_info_scrollbox.special_insert(tk.END, tuple(result))
        else:
            self.more_info_scrollbox.clear()

    def _on_costumer_edit(self):

        def done(sref):
            new_vals = (name_e.get(), pickle.dumps(date(int(bdate_year.get()), int(bdate_month.get()),
                                                        int(bdate_day.get()))),
                        1 if gender_c.current() else 0, phone_e.get(), email_e.get())

            if not prev_vals == new_vals:
                columns = ('name', 'dateOfBirth', 'gender', 'phoneNumber', 'email')
                for i in range(5):
                    if not prev_vals[i] == new_vals[i]:
                        mdb.edit_costumer(sref.selected_costumer_id, columns[i], new_vals[i])
                sref.OnEnter()
                edit_costumer_frame.destroy()

        edit_costumer_frame = tk.Toplevel(self)
        edit_costumer_frame.title("Edit Costumer")
        edit_costumer_frame.resizable(0, 0)

        prev_vals = mdb.connection.execute("SELECT name, dateOfBirth, gender, phoneNumber, email FROM costumers "
                                           "WHERE _id = ?", (self.selected_costumer_id,)).fetchone()
        prev_bdate = pickle.loads(prev_vals[1])

        name_f = tk.Label(edit_costumer_frame, text='Name: ', font=FIELD_FONT)
        name_e = tk.Entry(edit_costumer_frame)
        name_e.insert(0, prev_vals[0])

        bdate_f = tk.Label(edit_costumer_frame, text="Birth Date: ", font=FIELD_FONT)
        bdate_day = tk.Spinbox(edit_costumer_frame, from_=1, to=31, width=5)
        bdate_day.delete(0, tk.END)
        bdate_day.insert(0, prev_bdate.day)
        bdate_month = tk.Spinbox(edit_costumer_frame, from_=1, to=12, width=5)
        bdate_month.delete(0, tk.END)
        bdate_month.insert(0, prev_bdate.month)
        bdate_year = tk.Spinbox(edit_costumer_frame, from_=1900, to=3000, width=5)
        bdate_year.delete(0, tk.END)
        bdate_year.insert(0, prev_bdate.year)

        gender_f = tk.Label(edit_costumer_frame, text="Gender", font=FIELD_FONT)
        gender_c = ttk.Combobox(edit_costumer_frame, values=["Male", "Female"])
        gender_c.current(1 if int(prev_vals[2]) else 0)

        phone_f = tk.Label(edit_costumer_frame, text="(Optional) Phone Number: ", font=FIELD_FONT)
        phone_e = tk.Entry(edit_costumer_frame)
        phone_e.insert(0, prev_vals[3] if prev_vals[3] else '')

        email_f = tk.Label(edit_costumer_frame, text="(Optional) E-Mail: ", font=FIELD_FONT)
        email_e = tk.Entry(edit_costumer_frame)
        email_e.insert(0, prev_vals[4] if prev_vals[4] else '')

        cancel_b = tk.Button(edit_costumer_frame, text='Cancel', command=edit_costumer_frame.destroy)
        done_b = tk.Button(edit_costumer_frame, text='Done', command=lambda: done(self))

        #

        name_f.grid(row=0, column=0, sticky='w')
        name_e.grid(row=0, column=1, sticky='ew', columnspan=3)

        bdate_f.grid(row=1, column=0, sticky='w')
        bdate_day.grid(row=1, column=1, sticky='ew')
        bdate_month.grid(row=1, column=2, sticky='ew')
        bdate_year.grid(row=1, column=3, sticky='ew')

        gender_f.grid(row=2, column=0, sticky='w')
        gender_c.grid(row=2, column=1, sticky='ew', columnspan=3)

        phone_f.grid(row=3, column=0, sticky='w')
        phone_e.grid(row=3, column=1, sticky='ew', columnspan=3)

        email_f.grid(row=4, column=0, sticky='w')
        email_e.grid(row=4, column=1, sticky='ew', columnspan=3)

        cancel_b.grid(row=5, column=0, sticky='nsew', columnspan=1, padx=2, pady=2)
        done_b.grid(row=5, column=1, sticky='nsew', columnspan=3, padx=2, pady=2)

    def _on_costumer_delete(self):
        if messagebox.askyesno("Delte?", "Are you sure you want to delete this costumer?"):
            print(self.selected_costumer_id)
            if mdb.delete_costumer(self.selected_costumer_id) == 1:
                messagebox.showerror("Error", "Unable to delete costumer:\nCostumer has active history.")
            else:
                self.OnEnter()

    def _on_new_costumer(self):

        def on_create(sref):
            if name_e.get() and 0 < int(bdate_day.get()) <= 31 and 0 < int(bdate_month.get()) <= 12 and \
                    int(bdate_year.get()) >= 1900:
                mdb.new_costumer(name_e.get(), date(int(bdate_year.get()), int(bdate_month.get()),
                                                    int(bdate_day.get())),
                                 1 if gender_c.current() else 0, phone_e.get() if phone_e.get() else None,
                                 email_e.get() if email_e.get else None)
                mdb.connection.commit()
                sref.OnEnter()
                new_costumer_frame.destroy()
                messagebox.showinfo("Done", "Costumer added successfully.")
            else:
                messagebox.showwarning("Warning", "Please make sure the values are valid.")

        new_costumer_frame = tk.Toplevel(self)
        new_costumer_frame.title("New Costumer")
        new_costumer_frame.resizable(0, 0)

        name_f = tk.Label(new_costumer_frame, text='Name: ', font=FIELD_FONT)
        name_e = tk.Entry(new_costumer_frame)

        bdate_f = tk.Label(new_costumer_frame, text="Birth Date: ", font=FIELD_FONT)
        bdate_day = tk.Spinbox(new_costumer_frame, from_=1, to=31, width=5)
        bdate_month = tk.Spinbox(new_costumer_frame, from_=1, to=12, width=5)
        bdate_year = tk.Spinbox(new_costumer_frame, from_=1900, to=3000, width=5)

        gender_f = tk.Label(new_costumer_frame, text="Gender", font=FIELD_FONT)
        gender_c = ttk.Combobox(new_costumer_frame, values=["Male", "Female"])
        gender_c.current(0)

        phone_f = tk.Label(new_costumer_frame, text="(Optional) Phone Number: ", font=FIELD_FONT)
        phone_e = tk.Entry(new_costumer_frame)

        email_f = tk.Label(new_costumer_frame, text="(Optional) E-Mail: ", font=FIELD_FONT)
        email_e = tk.Entry(new_costumer_frame)

        cancel_b = tk.Button(new_costumer_frame, text='Cancel', command=new_costumer_frame.destroy)
        create_b = tk.Button(new_costumer_frame, text='Create', command=lambda: on_create(self))

        #

        name_f.grid(row=0, column=0, sticky='w')
        name_e.grid(row=0, column=1, sticky='ew', columnspan=3)

        bdate_f.grid(row=1, column=0, sticky='w')
        bdate_day.grid(row=1, column=1, sticky='ew')
        bdate_month.grid(row=1, column=2, sticky='ew')
        bdate_year.grid(row=1, column=3, sticky='ew')

        gender_f.grid(row=2, column=0, sticky='w')
        gender_c.grid(row=2, column=1, sticky='ew', columnspan=3)

        phone_f.grid(row=3, column=0, sticky='w')
        phone_e.grid(row=3, column=1, sticky='ew', columnspan=3)

        email_f.grid(row=4, column=0, sticky='w')
        email_e.grid(row=4, column=1, sticky='ew', columnspan=3)

        cancel_b.grid(row=5, column=0, sticky='nsew', columnspan=1, padx=2, pady=2)
        create_b.grid(row=5, column=1, sticky='nsew', columnspan=3, padx=2, pady=2)


class StatsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label="Home", command=lambda: controller.show_frame(HomePage))
        self.menu_bar.add_command(label="Sell", command=lambda: controller.show_frame(SellPage))
        self.menu_bar.add_command(label="Products", command=lambda: controller.show_frame(ProductsPage))
        self.menu_bar.add_command(label="Costumers", command=lambda: controller.show_frame(CostumersPage))
        self.menu_bar.add_command(label="Settings", command=lambda: controller.show_frame(SettingsPage))
        self.menu_bar.add_command(label="Log Out", command=lambda: controller.show_frame(LoginPage))

        self.title = tk.Label(self, text="Statistics", font=TITLE_FONT)

        self.stats_frame = tk.Frame(self, bd=2, relief='sunken')
        self.navigation_structure = {0: {"Sales>>": "goto@1",
                                         "Products>>": "goto@2",
                                         "Costumers>>": "goto@3"},
                                     1: {"Sales History": "set_var@int, 1",
                                         "Sales": "set_var@int, 2",
                                         "Sales Growth": "set_var@int, 3",
                                         "Income": "set_var@int, 4",
                                         "Profits": "set_var@int, 5"},
                                     2: {"Product Popularity": "set_var@int, 6",
                                         "Average Profit Margin": "set_var@int, 7",
                                         "New Products": "set_var@int, 8"},
                                     3: {"Costumers": "set_var@int, 9",
                                         "New Costumers": "set_var@int, 10",
                                         "Average Costumer's Age": "set_var@int, 11",
                                         "Costumers' Gender": "set_var@int, 12"}}
        # Values and Meanings:
        #
        #   1: sales_history            7: avg_profit_margin
        #   2: sales                    8: new_products
        #   3: sales_growth             9: costumers
        #   4: income                   10: new_costumers
        #   5: profits                  11: avg_costumer_age
        #   6: product_popularity       12: costumers'_gender
        #

        self.stats_commands = (self._sales_history, self._sales, self._sales_growth, self._income, self._profits,
                               self._product_popularity, self._avg_profit_margin, self._new_costumers,
                               self._new_products, self._costumers, self._new_costumers, self._avg_costumers_age,
                               self._costumers_gender)
        self.time_period_labels = ("All Time", "This Year", "This Month", "This Week")

        self.navigationbox = xw.NavigationBox(self.stats_frame, self.navigation_structure, text='Available Stats',
                                              size=(30, 15))
        self.select_b = tk.Button(self.navigationbox, text='Select', command=self.on_select)
        self.time_period_frame = tk.LabelFrame(self.stats_frame, text="Time Period")
        self.time_period_var = tk.IntVar(value=1)
        self.all_time_rb = tk.Radiobutton(self.time_period_frame, text='All Time', variable=self.time_period_var,
                                          value=1)
        self.this_year_rb = tk.Radiobutton(self.time_period_frame, text='This Year', variable=self.time_period_var,
                                           value=2)
        self.this_month_rb = tk.Radiobutton(self.time_period_frame, text='This Month', variable=self.time_period_var,
                                            value=3)
        self.this_week_rb = tk.Radiobutton(self.time_period_frame, text='This Week', variable=self.time_period_var,
                                           value=4)
        self.custom_rb = tk.Radiobutton(self.time_period_frame, text='Custom', variable=self.time_period_var, value=5)
        self.custom_time_period_frame = tk.Frame(self.time_period_frame)

        self.all_time_rb.config(command=self._on_time_period_update)
        self.this_year_rb.config(command=self._on_time_period_update)
        self.this_month_rb.config(command=self._on_time_period_update)
        self.this_week_rb.config(command=self._on_time_period_update)
        self.custom_rb.config(command=self._on_time_period_update)

        self.from_l = tk.Label(self.custom_time_period_frame, text='From: ', font=FIELD_FONT)
        self.from_day = tk.Spinbox(self.custom_time_period_frame, from_=1, to=31)
        self.from_month = tk.Spinbox(self.custom_time_period_frame, from_=1, to=12)
        self.from_year = tk.Spinbox(self.custom_time_period_frame, from_=1970, to=9999)
        self.to_l = tk.Label(self.custom_time_period_frame, text="To: ", font=FIELD_FONT)
        self.to_day = tk.Spinbox(self.custom_time_period_frame, from_=1, to=31)
        self.to_month = tk.Spinbox(self.custom_time_period_frame, from_=1, to=12)
        self.to_year = tk.Spinbox(self.custom_time_period_frame, from_=1970, to=9999)
        self.select_date_b = tk.Button(self.time_period_frame, text='Select Date',
                                       command=lambda: self.stats_commands[self.navigationbox.var - 1]())
        # Comment on the previous line: Yes, it has to be a lambda. I know that it would make more sense to just call
        #                               self.stats_commands[self.navigationbox.var -1], but as it turns out, the func-
        #                               tions in self.stats_commands haven't been defined yet, so thats why.

        self.history_frame = tk.Frame(self.stats_frame)
        self.graph_frame = tk.Frame(self.stats_frame)
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plt = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.ax = self.figure.gca()

        self.title.grid(row=0, column=0, sticky='nw')
        self.stats_frame.grid(row=1, column=0, sticky='nsew')
        self.navigationbox.grid(row=0, column=0, rowspan=3, sticky='nsew')
        self.select_b.grid(row=2, column=0, sticky='ew', columnspan=2)
        self.time_period_frame.grid(row=0, column=1, sticky='new', pady=2)
        self.time_period_frame.grid_remove()
        self.all_time_rb.grid(row=0, column=0, sticky='w')
        self.this_year_rb.grid(row=0, column=1, sticky='w')
        self.this_month_rb.grid(row=0, column=2, sticky='w')
        self.this_week_rb.grid(row=0, column=3, sticky='w')
        self.custom_rb.grid(row=0, column=4, sticky='w')
        self.custom_time_period_frame.grid(row=2, column=0, columnspan=6, sticky='ew')
        self.custom_time_period_frame.grid_remove()
        self.from_l.grid(row=0, column=0, sticky='w')
        self.from_day.grid(row=0, column=1, sticky='w')
        self.from_month.grid(row=0, column=2, sticky='w')
        self.from_year.grid(row=0, column=3, sticky='w')
        self.to_l.grid(row=1, column=0, sticky='w')
        self.to_day.grid(row=1, column=1, sticky='w')
        self.to_month.grid(row=1, column=2, sticky='w')
        self.to_year.grid(row=1, column=3, sticky='w')
        self.select_date_b.grid(row=2, column=7, sticky='nsew')
        self.select_date_b.grid_remove()
        self.history_frame.grid(row=1, column=1, sticky='nsew')
        self.history_frame.grid_remove()
        self.graph_frame.grid(row=1, column=1, sticky='nsew')
        self.graph_frame.grid_remove()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.X)
        # self._sales()

    def on_select(self):
        if self.navigationbox.var == 1 or self.navigationbox.var == 12:
            self.time_period_frame.grid_remove()
            self.graph_frame.grid_remove()
        else:
            self.time_period_frame.grid()

        self.history_frame.grid_remove()
        self.stats_commands[self.navigationbox.var - 1]()

    def _on_time_period_update(self):
        if self.time_period_var.get() == 5:
            self.custom_time_period_frame.grid()
            self.select_date_b.grid()
        else:
            self.custom_time_period_frame.grid_remove()
            self.select_date_b.grid_remove()

        self.stats_commands[self.navigationbox.var - 1]()

    # Graphing Functions:
    def _sales_history(self):
        self.history_frame.grid()

        def sale_select(event):
            if event.widget.curselection():
                visual_receipt_box.clear()
                index = event.widget.curselection()[0]
                selection = event.widget.get(index).split(' | ')

                total_v.set('${}'.format(selection[3]))
                profit_v.set('${}'.format(mdb.connection.execute("SELECT CAST(totalProfit AS float) / 100.0 FROM "
                                                                 "salesHistory WHERE _id = ?",
                                                                 (selection[0],)).fetchone()[0]))

                receipt = pickle.loads(mdb.connection.execute("SELECT items FROM salesHistory WHERE _id = ?",
                                                              (selection[0],)).fetchone()[0])
                for items in receipt:
                    # Getting product's info:
                    name, price = mdb.connection.execute("SELECT name, retailPrice FROM products WHERE _id = ?",
                                                         (items[0],)).fetchone()
                    visual_receipt_box.insert(tk.END, "{0} | x{1} | ${2}".format(name, items[1], price / 100))
            else:
                visual_receipt_box.clear()

        history_box = xw.DBSearchBox(self.history_frame, mdb.connection,
                                     sql="SELECT salesHistory._id, costumers.name, "
                                         "salesHistory.UTCTime, CAST(salesHistory.totalPrice AS "
                                         "float) / 100.0, CASE salesHistory.paymentMethod WHEN 1 "
                                         "THEN 'Cash' WHEN 2 THEN 'Debit Card' ELSE 'Credit Card' END"
                                         " FROM salesHistory JOIN costumers ON salesHistory.costu"
                                         "mer = costumers._id ORDER BY salesHistory._id DESC",
                                     pfilter="WHERE costumers.name LIKE '%{sv}%' OR CASE salesHistory.paymentMethod WHE"
                                             "N 1 THEN 'Cash' WHEN 2 THEN 'Debit Card' ELSE 'Credit Card' END LIKE "
                                             "'%{sv}%' OR salesHistory.UTCTime LIKE '%{sv}%'",
                                     width=60, height=25)
        history_box.scroll_box.list_box.bind('<<ListboxSelect>>', sale_select)
        visual_receipt_box = xw.ScrollBox(self.history_frame, text="Sale's Receipt", width=25, height=22)

        total_f = tk.Label(self.history_frame, text='Total: ', font=FIELD_FONT)
        total_v = tk.StringVar()
        total_l = tk.Label(self.history_frame, textvariable=total_v)
        profit_f = tk.Label(self.history_frame, text='Profit: ', font=FIELD_FONT)
        profit_v = tk.StringVar()
        profit_l = tk.Label(self.history_frame, textvariable=profit_v)

        history_box.grid(row=0, column=0, sticky='ne', rowspan=10)
        visual_receipt_box.grid(row=0, column=1, sticky='nw', columnspan=10)
        total_f.grid(row=1, column=1, sticky='w')
        total_l.grid(row=1, column=2, sticky='w')
        profit_f.grid(row=2, column=1, sticky='w')
        profit_l.grid(row=2, column=2, sticky='w')

    def _sales(self):
        self.plt.cla()

        first_date_ever = mdb.connection.execute("SELECT UTCTime FROM salesHistory WHERE _id = 1").fetchone()[0].date()
        last_date_at = date.today()
        all_time_dif = (last_date_at - first_date_ever).days

        # This is for ALL TIME time period
        if self.time_period_var.get() == 1:
            first_date = first_date_ever
            last_date = last_date_at
        elif self.time_period_var.get() == 2:
            first_date = date.today() - timedelta(365)
            last_date = date.today()
        elif self.time_period_var.get() == 3:
            first_date = date.today() - timedelta(MONTH_DAYS[date.today().month - 1])
            last_date = date.today()
        elif self.time_period_var.get() == 4:
            first_date = date.today() - timedelta(7)
            last_date = date.today()
        elif self.time_period_var.get() == 5:
            first_date = date(int(self.from_year.get()), int(self.from_month.get()), int(self.from_day.get()))
            last_date = date(int(self.to_year.get()), int(self.to_month.get()), int(self.to_day.get()))

        last_date += timedelta(1)

        dif = (last_date - first_date).days

        dates, counts = [], []
        print(dif)

        for i in range(dif):
            dates.append(first_date + timedelta(days=i+1))
            counts.append(mdb.connection.execute("SELECT count(*) FROM salesHistory WHERE UTCTime BETWEEN ? AND ?",
                                                 (first_date, first_date + timedelta(days=i+1))).fetchone()[0])
        print(dates, counts)

        # All working here. just need to plot

        if self.time_period_var.get() != 5:
            self.plt.set_title('Sales - {0}'.format(self.time_period_labels[self.time_period_var.get() - 1]))
        else:
            self.plt.set_title('Sales - From: {0}/{1}/{2} To: {3}/{4}/{5}'.format(first_date.day, first_date.month,
                                                                                  first_date.year, last_date.day - 1,
                                                                                  last_date.month, last_date.year))
            # Comment on previous line: That -1 is there to compensate for the 1-day offset we have to apply to the last
            #                           date so that it shows today's sales.
        self.plt.set_xlabel("Time →")
        self.plt.set_ylabel("Sales →")
        if dif > 367:
            self.ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(bymonthday=15))
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%B - %y'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        elif dif > 60:
            self.ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(bymonthday=15))
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b - %y'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        elif dif > 31:
            self.ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(interval=10))
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b - %y'))
            self.ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
        elif dif > 21:
            self.ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=2))
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        elif dif <= 21:
            self.ax.xaxis.set_major_locator(matplotlib.dates.DayLocator())
            self.ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        self.ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(counts[-1]//10 if counts[-1] else 1))
        self.ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator())
        self.plt.tick_params(axis='x', labelrotation=45)

        self.plt.plot(dates, counts, label='Number of Sales', marker='.')

        self.plt.legend()
        self.figure.subplots_adjust(left=0.1, bottom=0.25, right=0.96)

        self.canvas.draw()

        self.graph_frame.grid()

    def _sales_growth(self):
        self.plt.cla()

        first_date_ever = mdb.connection.execute("SELECT UTCTime FROM salesHistory WHERE _id = 1").fetchone()[0].date()
        last_date_at = date.today()
        all_time_dif = (last_date_at - first_date_ever).days

        # This is for ALL TIME time period
        if self.time_period_var.get() == 1:
            first_date = first_date_ever
            last_date = last_date_at
        elif self.time_period_var.get() == 2:
            first_date = date.today() - timedelta(365)
            last_date = date.today()
        elif self.time_period_var.get() == 3:
            first_date = date.today() - timedelta(MONTH_DAYS[date.today().month - 1])
            last_date = date.today()
        elif self.time_period_var.get() == 4:
            first_date = date.today() - timedelta(7)
            last_date = date.today()
        elif self.time_period_var.get() == 5:
            first_date = date(int(self.from_year.get()), int(self.from_month.get()), int(self.from_day.get()))
            last_date = date(int(self.to_year.get()), int(self.to_month.get()), int(self.to_day.get()))

        last_date += timedelta(1)

        dif = (last_date - first_date).days

        dates, counts = [], []
        print(dif)

        for i in range(dif):
            dates.append(first_date + timedelta(days=i + 1))
            counts.append(mdb.connection.execute("SELECT count(*) FROM salesHistory WHERE UTCTime BETWEEN ? AND ?",
                                                 (first_date + timedelta(days=i + 1),
                                                  first_date + timedelta(days=i + 2))).fetchone()[0])
        print(dates, counts)

        # All working here. just need to plot

        if self.time_period_var.get() != 5:
            self.plt.set_title('Sales - {0}'.format(self.time_period_labels[self.time_period_var.get() - 1]))
        else:
            self.plt.set_title('Sales - From: {0}/{1}/{2} To: {3}/{4}/{5}'.format(first_date.day, first_date.month,
                                                                                  first_date.year, last_date.day - 1,
                                                                                  last_date.month, last_date.year))
            # Comment on previous line: That -1 is there to compensate for the 1-day offset we have to apply to the last
            #                           date so that it shows today's sales.
        self.plt.set_xlabel("Time →")
        self.plt.set_ylabel("Sales →")
        if dif > 367:
            self.ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(bymonthday=15))
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%B - %y'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        elif dif > 60:
            self.ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(bymonthday=15))
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b - %y'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        elif dif > 31:
            self.ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator(interval=10))
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b - %y'))
            self.ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
        elif dif > 21:
            self.ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=2))
            self.ax.xaxis.set_minor_locator(matplotlib.dates.DayLocator())
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        elif dif <= 21:
            self.ax.xaxis.set_major_locator(matplotlib.dates.DayLocator())
            self.ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
            self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d'))
            self.ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        self.ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(counts[-1] // 10 if counts[-1] else 1))
        self.ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator())
        self.plt.tick_params(axis='x', labelrotation=45)

        self.plt.plot(dates, counts, label='Number of Sales', marker='.')

        self.plt.legend()
        self.figure.subplots_adjust(left=0.1, bottom=0.25, right=0.96)

        self.canvas.draw()

        self.graph_frame.grid()

    def _income(self):
        pass

    def _profits(self):
        pass

    def _product_popularity(self):
        pass

    def _avg_profit_margin(self):
        pass

    def _new_products(self):
        pass

    def _costumers(self):
        pass

    def _new_costumers(self):
        pass

    def _avg_costumers_age(self):
        pass

    def _costumers_gender(self):
        pass


class SettingsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.menu_bar = tk.Menu(self)
        self.menu_bar.add_command(label="Home", command=lambda: controller.show_frame(HomePage))
        self.menu_bar.add_command(label="Sell", command=lambda: controller.show_frame(SellPage))
        self.menu_bar.add_command(label="Products", command=lambda: controller.show_frame(ProductsPage))
        self.menu_bar.add_command(label="Costumers", command=lambda: controller.show_frame(CostumersPage))
        self.menu_bar.add_command(label="S", command=lambda: controller.show_frame(SettingsPage))
        self.menu_bar.add_command(label="Log Out", command=lambda: controller.show_frame(LoginPage))


if __name__ == '__main__':
    app = LineLogApp()
    app.mainloop()
    odb.connection.close()
    mdb.connection.close()

# TODO: finish hooking up time periods with graph and create graphing functions
# TODO: add support to multiple languages
# TODO: finish langs impolementation and add more languages
# TODO: Fix Bugs

# BUGS:
#


# Board:
#
# TODO: Make the products' prices immutable!!!