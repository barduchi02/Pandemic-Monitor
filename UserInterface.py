import DataProcessor
import Utils
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as dat

import tkinter as tk
from tkinter import ttk

# import test

matplotlib.use("TkAgg")
style.use('ggplot')

f = Figure(figsize=(6, 5), dpi=100)
a = f.add_subplot(111)

dp = DataProcessor.DataProcessor()


class InterfaceController:
    refresh = True
    countries = []
    regions = []
    country_buttons = []
    region_buttons = []
    type_buttons = []
    plot_countries = False
    measures = dp.get_measure_types()
    toggle_menu = []

    def stop(self):
        self.refresh = False

    def resume(self):
        self.refresh = True

    def add_country_button(self, button):
        self.country_buttons.append((button, Utils.random_color()))

    def add_region_button(self, button):
        self.region_buttons.append((button, Utils.random_color()))

    def clean_region_button(self):
        self.region_buttons = []
        self.regions = []

    def add_type_button(self, button):
        self.type_buttons.append(button)

    def add_toggle_menu(self, button):
        self.toggle_menu.append(button)

    def get_countries(self, order):
        c = dp.country_names(order)
        if len(self.countries) == 0:
            self.countries = c
        return c

    def get_regions(self, order):
        selected = []
        for i in range(0, len(self.country_buttons)):
            if self.country_buttons[i][0].get():
                selected.append(self.countries[i])

        r = dp.region_names(order, selected)
        if len(self.regions) == 0:
            self.regions = r
        return r

    def change_plot(self):
        self.plot_countries = not self.plot_countries
        '''
        if self.plot_countries:
            test.dataframe_not_in_list(self.countries, dp.processedCensusDts)
        else:
            test.dataframe_not_in_list(self.regions, dp.processedCensusDts)
        '''
        self.resume()

    def get_selected_measures(self):
        pm = []
        i = 0
        for list_measures in self.measures.values():
            for measure in list_measures:
                if (self.toggle_menu[i].get()) and (measure not in pm):
                    pm.append(measure)
                i += 1
        return pm

    def select_measures(self, new_selections):
        i = 0
        for list_measures in self.measures.values():
            for measure in list_measures:
                if measure in new_selections:
                    self.toggle_menu[i].set(True)
                else:
                    self.toggle_menu[i].set(False)
                i += 1


ic = InterfaceController()


def animate(i):

    if ic.refresh:
        a.clear()
        lines = []
        if ic.plot_countries:
            for i in range(len(ic.countries)):
                if ic.country_buttons[i][0].get():
                    if ic.type_buttons[0].get():
                        xar, yar = dp.plot_graph_country(Utils.CONFIRMED, ic.countries[i],
                                                         per_million=ic.type_buttons[6].get())
                        lines = a.plot_date(xar, yar, color=ic.country_buttons[i][1], ls='-', marker='None',
                                            label=(ic.countries[i] + ' ' + Utils.CONFIRMED))
                    if ic.type_buttons[1].get():
                        xar, yar = dp.plot_graph_country(Utils.MORTALITY, ic.countries[i],
                                                         brazil_registry=ic.type_buttons[7].get())
                        lines = a.plot_date(xar, yar, color=ic.country_buttons[i][1], ls='--', marker='*',
                                            label=(ic.countries[i] + ' ' + Utils.MORTALITY))
                    if ic.type_buttons[2].get():
                        xar, yar = dp.plot_graph_country(Utils.DEATHS, ic.countries[i],
                                                         per_million=ic.type_buttons[6].get(),
                                                         brazil_registry=ic.type_buttons[7].get())
                        lines = a.plot_date(xar, yar, color=ic.country_buttons[i][1], ls='--', marker='None',
                                            label=(ic.countries[i] + ' ' + Utils.DEATHS))
                    if ic.type_buttons[3].get():
                        xar, yar = dp.plot_graph_country(Utils.RECOVERED, ic.countries[i],
                                                         per_million=ic.type_buttons[6].get())
                        lines = a.plot_date(xar, yar, color=ic.country_buttons[i][1], ls='-.', marker='None',
                                            label=(ic.countries[i] + ' ' + Utils.RECOVERED))
                    if ic.type_buttons[4].get():
                        xar, yar = dp.plot_graph_country(Utils.RT, ic.countries[i])
                        lines = a.plot_date(xar, yar, color=ic.country_buttons[i][1], ls=':', marker='None',
                                            label=(ic.countries[i]) + ' ' + Utils.RT)
                    if ic.type_buttons[5].get():
                        xar, yar = dp.plot_graph_government(ic.countries[i], ic.get_selected_measures())
                        lines = a.plot_date(xar, yar, color=ic.country_buttons[i][1], ls='-', marker='x',
                                            label=(ic.countries[i]) + " Gov. measures")
        else:
            for i in range(len(ic.regions)):
                if ic.region_buttons[i][0].get():
                    if ic.type_buttons[0].get():
                        xar, yar = dp.plot_graph_region(Utils.CONFIRMED, ic.regions[i],
                                                        per_million=ic.type_buttons[6].get())
                        lines = a.plot_date(xar, yar, color=ic.region_buttons[i][1], ls="-", marker='None',
                                            label=(ic.regions[i] + ' ' + Utils.CONFIRMED))
                    if ic.type_buttons[1].get():
                        xar, yar = dp.plot_graph_region(Utils.MORTALITY, ic.regions[i],
                                                        brazil_registry=ic.type_buttons[7].get())
                        lines = a.plot_date(xar, yar, color=ic.region_buttons[i][1], ls="--", marker="*",
                                            label=(ic.regions[i] + ' ' + Utils.MORTALITY))
                    if ic.type_buttons[2].get():
                        xar, yar = dp.plot_graph_region(Utils.DEATHS, ic.regions[i],
                                                        per_million=ic.type_buttons[6].get(),
                                                        brazil_registry=ic.type_buttons[7].get())
                        lines = a.plot_date(xar, yar, color=ic.region_buttons[i][1], ls="--", marker='None',
                                            label=(ic.regions[i]) + ' ' + Utils.DEATHS)
                    if ic.type_buttons[3].get():
                        xar, yar = dp.plot_graph_region(Utils.RECOVERED, ic.regions[i],
                                                        per_million=ic.type_buttons[6].get())
                        lines = a.plot_date(xar, yar, color=ic.region_buttons[i][1], ls="-.", marker='None',
                                            label=(ic.regions[i]) + ' ' + Utils.RECOVERED)
                    if ic.type_buttons[4].get():
                        xar, yar = dp.plot_graph_region(Utils.RT, ic.regions[i])
                        lines = a.plot_date(xar, yar, color=ic.region_buttons[i][1], ls=":", marker='None',
                                            label=(ic.regions[i] + ' ' + Utils.RT))

        a.set_xlabel('Days')
        a.set_ylabel('Factors')
        a.set_title('Factors X Days')
        f.tight_layout()
        f.subplots_adjust(bottom=0.15)
        if len(lines) != 0:
            a.legend()
            formatter = dat.DateFormatter('%d/%m')

            a.xaxis.set_major_formatter(formatter)
            a.xaxis.set_tick_params(rotation=30, labelsize=10)

        ic.stop()


class PandemicMonitorApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="Data/virus.ico")
        tk.Tk.wm_title(self, "Pandemic Monitor Client")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menu_bar = tk.Menu(self, font=Utils.LARGE_FONT)
        self.configure(menu=menu_bar)

        measures_menu = tk.Menu(menu_bar, tearoff=0, font=Utils.LARGE_FONT)
        menu_bar.add_cascade(label="Government Measures", menu=measures_menu)

        for category, measures in ic.measures.items():
            category_menu = tk.Menu(measures_menu, tearoff=0, font=Utils.LARGE_FONT)
            measures_menu.add_cascade(label=category, menu=category_menu)
            for i in range(len(measures)):
                ic.add_toggle_menu(tk.BooleanVar())
                category_menu.add_checkbutton(label=measures[i], variable=ic.toggle_menu[-1])

        self.frames = {}

        for F in (StartPage, EndPage):  # I can put more pages here
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Options(tk.Frame):

    check_buttons = []
    is_region = False

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        ic.change_plot()
        self.lift()

    def reorder_buttons(self, order):
        pass

    def select_containment_success(self):
        for ck in self.check_buttons:
            if dp.success_in_region(ck.cget("text"), self.is_region):
                ck.select()
            else:
                ck.deselect()

    def get_selected(self):
        selected = []
        if not self.is_region:
            for i in range(0, len(ic.countries)):
                if ic.country_buttons[i][0].get():
                    selected.append(ic.countries[i])
        return selected


class CountryOptions(Options):
    def __init__(self, *args, **kwargs):
        Options.__init__(self, *args, **kwargs)

        country_label = tk.Label(self, text="Countries", font=Utils.LARGE_FONT)
        country_label.grid(row=0, column=0, columnspan=6)

        country_names = ic.get_countries(Utils.ALPHABETICAL)
        i = 1
        j = 0
        for country_name in country_names:
            country_button = tk.BooleanVar()
            if country_name == 'US':
                country_button.set(True)
            ic.add_country_button(country_button)
            ck = tk.Checkbutton(self, text=country_name, variable=country_button, font=Utils.SMALL_FONT,
                                bg=ic.country_buttons[-1][1], command=lambda: ic.resume())
            self.check_buttons.append(ck)
            ck.grid(row=i, column=j, sticky=tk.W)
            i += 1
            if i == 36:
                j += 1
                i = 1

    def reorder_buttons(self, order):
        country_names = ic.get_countries(order)

        i = 1
        j = 0
        for country_name in country_names:
            for ck in self.check_buttons:
                if ck.cget("text") == country_name:
                    ck.grid_forget()
                    ck.grid(row=i, column=j, sticky=tk.W)
                    i += 1
                    if i == 36:
                        j += 1
                        i = 1
                    break


class RegionOptions(Options):

    def __init__(self, *args, **kwargs):
        Options.__init__(self, *args, **kwargs)

        self.is_region = True

        region_label = tk.Label(self, text="Specific Areas", font=Utils.LARGE_FONT)
        region_label.grid(row=0, column=0, columnspan=6)

        region_names = ic.get_regions(Utils.ALPHABETICAL)
        i = 1
        j = 0
        for region_name in region_names:
            region_button = tk.BooleanVar()
            ic.add_region_button(region_button)
            ck = tk.Checkbutton(self, text=region_name, variable=region_button, font=Utils.SMALL_FONT,
                                bg=ic.region_buttons[-1][1], command=lambda: ic.resume())
            self.check_buttons.append(ck)
            ck.grid(row=i, column=j, sticky=tk.W)
            i += 1
            if i == 36:
                j += 1
                i = 1

    def reorder_buttons(self, order):
        region_names = ic.get_regions(order)

        i = 1
        j = 0
        for region_name in region_names:
            for ck in self.check_buttons:
                if ck.cget("text") == region_name:
                    ck.grid_forget()
                    ck.grid(row=i, column=j, sticky=tk.W)
                    i += 1
                    if i == 36:
                        j += 1
                        i = 1


class StartPage(tk.Frame):
    country_frame = 'nan'
    region_frame = None
    combobox_order = 'nan'

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().grid(row=0, column=0, rowspan=18, columnspan=5, sticky=tk.NSEW)
        canvas.draw()
        # canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row=18, column=0, columnspan=5)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        # canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # canvas._tkcanvas.grid(row=2, column=0)

        self.country_frame = CountryOptions(self)
        self.country_frame.grid(row=1, column=6, rowspan=20, columnspan=20, sticky=tk.NSEW)

        # self.region_frame = RegionOptions(self)
        # self.region_frame.grid(row=1, column=6, rowspan=20, columnspan=20, sticky=tk.NSEW)

        self.country_frame.show()

        type_label = tk.Label(self, text="Show data about:", font=Utils.MEDIUM_FONT)
        type_label.grid(row=19, column=0)

        confirmed_button = tk.BooleanVar()
        confirmed_button.set(True)
        ck = tk.Checkbutton(self, text=Utils.CONFIRMED, variable=confirmed_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(confirmed_button)
        ck.grid(row=19, column=1)

        mortality_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text=Utils.MORTALITY, variable=mortality_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(mortality_button)
        ck.grid(row=19, column=2)

        death_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text=Utils.DEATHS, variable=death_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(death_button)
        ck.grid(row=19, column=3)

        recovered_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text=Utils.RECOVERED, variable=recovered_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(recovered_button)
        ck.grid(row=19, column=4)

        rt_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text=Utils.RT, variable=rt_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(rt_button)
        ck.grid(row=19, column=5)

        measures_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text="Government Measures", variable=measures_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(measures_button)
        ck.grid(row=20, column=0)

        per_million_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text="Per million", variable=per_million_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(per_million_button)
        ck.grid(row=20, column=1)

        brazil_registry_button = tk.BooleanVar()
        ck = tk.Checkbutton(self, text="Brazil Reg Data", variable=brazil_registry_button, font=Utils.MEDIUM_FONT,
                            command=lambda: ic.resume())
        ic.add_type_button(brazil_registry_button)
        ck.grid(row=20, column=2)

        button = ttk.Button(self, text="Change areas", command=self.change_areas)
        button.grid(row=20, column=3)

        order_label = tk.Label(self, text="Order by:", font=Utils.MEDIUM_FONT)
        order_label.grid(row=20, column=4)

        self.combobox_order = ttk.Combobox(self, values=[Utils.ALPHABETICAL, Utils.PER_CAPITA_INCOME,
                                                         Utils.POPULATIONAL_DENSITY, Utils.LARGER_RISK_GROUP])
        self.combobox_order.grid(row=20, column=5)
        self.combobox_order.current(0)
        self.combobox_order.bind("<<ComboboxSelected>>", self.reorder_areas)

        button = ttk.Button(self, text="Success in Containment!", command=self.containment_success)
        button.grid(row=21, column=0)

        button = ttk.Button(self, text="Similar Measures", command=self.similar_measures)
        button.grid(row=21, column=1)

        button = ttk.Button(self, text="Save Measures", command=self.save_measures)
        button.grid(row=21, column=2)

    def change_areas(self):
        if ic.plot_countries:
            if self.region_frame is not None:
                self.region_frame.destroy()
                ic.clean_region_button()
            self.region_frame = RegionOptions(self)
            self.region_frame.grid(row=1, column=6, rowspan=20, columnspan=20, sticky=tk.NSEW)
            self.region_frame.show()
        else:
            self.country_frame.show()

    def reorder_areas(self, event=None):
        self.region_frame.reorder_buttons(self.combobox_order.get())
        self.country_frame.reorder_buttons(self.combobox_order.get())

    def containment_success(self):
        if ic.plot_countries:
            self.country_frame.select_containment_success()
        else:
            self.region_frame.select_containment_success()
        ic.resume()

    def similar_measures(self):
        ic.select_measures(dp.similar_country_measure(self.country_frame.get_selected()))
        ic.resume()

    def save_measures(self):
        dp.save_measures(self.country_frame.get_selected(), ic.get_selected_measures())


class EndPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=Utils.LARGE_FONT)
        label.pack(pady=10, padx=10)


app = PandemicMonitorApp()
app.geometry("%dx%d+0+0" % (app.winfo_screenwidth(), app.winfo_screenheight()))
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()
