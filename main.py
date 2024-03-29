import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import rcParams

SERIE = "Série"
PARALELLE = "Parallèle"
WIEN = "Pont de Wien"

THEME = "breeze"

def calcul_gains(frequences, r, c, circuit_type):
    gains = []

    if circuit_type == SERIE:
        for f in frequences:
            omega = 2 * np.pi * f
            impedance = 1j / (omega * c)
            gain = np.abs(impedance / np.sqrt(r**2 + np.abs(impedance)**2))
            gains.append(gain)

    elif circuit_type == PARALELLE:
        for f in frequences:
            omega = 2 * np.pi * f
            impedance = 1 / (1j * omega * r * c)
            gain = 1 / np.sqrt(1 + np.abs(impedance)**2)
            gains.append(gain)

    elif circuit_type == WIEN:
        for f in frequences:
            gain = np.abs(1 / (3 * 2 * np.pi * f * r * c))
            gains.append(gain)

    else:
        raise Exception("Mode de simulation non pris en charge")

    return gains

def calcul_dephasages(frequences, r, c, circuit_type):
    dephasages = []

    if circuit_type == SERIE:
        for f in frequences:
            dephasage = np.angle(1 / (1 + 1j * 2 * np.pi * f * r * c))
            dephasages.append(dephasage)

    elif circuit_type == PARALELLE:
        for f in frequences:
            dephasage = np.angle(1 / (1j * 2 * np.pi * f * r * c))
            dephasages.append(dephasage)

    elif circuit_type == WIEN:
        for f in frequences:
            dephasage = np.angle((1 - 2j * np.pi * f * r * c) / (1 + 2j * np.pi * f * r * c))
            dephasages.append(dephasage)

    else:
        raise Exception("Mode de simulation non pris en charge")

    return dephasages

def calcul_tensions(frequences, r, c, circuit_type, time, amplitude=1):
    tensions = []

    if circuit_type == SERIE:
        for f in frequences:
            tension = (1 - np.exp(-time / (r * c)))
            tensions.append(tension)

    elif circuit_type == PARALELLE:
        for f in frequences:
            tension = np.exp(-time / (r * c))
            tensions.append(tension)

    elif circuit_type == WIEN:
        for f in frequences:
            tension = amplitude * np.sin(2 * np.pi * f * time)
            tensions.append(tension)

    else:
        raise Exception("Mode de simulation non pris en charge")

    return tensions

def check_val(*vals, type_val=float, positive_only=True, croissant=False, null=True):
    errors = []
    new_vals = []
    for val in vals:
        try:
            val = type_val(val)
        except ValueError:
            errors.append(f"Erreur: {val} doit être un nombre.")
            continue
        if type_val in (float, int):
            if positive_only and val<0:
                errors.append(f"Erreur: {val} doit être un positif.")
                continue
            if not null and val==0:
                errors.append(f"Erreur: {val} doit être non null.")
                continue
        new_vals.append(val)

    sorted_vals = list(new_vals).copy()
    sorted_vals.sort()
    if croissant and new_vals != sorted_vals:
        errors.append(f"Erreur: les valeurs doivent être croissantes.")
        return [], errors
    else:
        print(new_vals, errors, positive_only)
        return new_vals, errors

            


def gen_plot():
    for widget in param_frame.winfo_children():
        if isinstance(widget, tk.Label) and widget.cget("fg") == "red":
            widget.destroy()

    try:
        freq_deb = frequence_deb_input.get()
        freq_fin = frequence_fin_input.get()
        r = r_input.get()
        c = c_input.get()
        time_deb = temps_deb_input.get()
        time_fin = temps_fin_input.get()
        circuit_type = circuit_type_select.get()
    except Exception as e:
        print("Erreur")
        print(e)
        return

    error_message = ""

    res = check_val(freq_deb, freq_fin, croissant=True)
    if not res[1]:
        freq_deb, freq_fin = res[0]
    else:
        for m in res[1]:
            error_message+=f"{m}\n"
    
    res = check_val(time_deb, time_fin, croissant=True)
    if not res[1]:
        time_deb, time_fin = res[0]
    else:
        for m in res[1]:
            error_message+=f"{m}\n"

    res = check_val(r, c, null=False)
    if not res[1]:
        r, c = res[0]
    else:
        for m in res[1]:
            error_message+=f"{m}\n"
    if error_message:
        error_message = tk.Label(param_frame, text=error_message, fg="red")
        error_message.pack()
        return

    frequences = np.logspace(np.log10(freq_deb), np.log10(freq_fin), num=100, base=10)
    time = np.linspace(time_deb, time_fin, num=1000)  # Pour le calcul de la tension
    
    gains = calcul_gains(frequences, r, c, circuit_type)
    dephasages = calcul_dephasages(frequences, r, c, circuit_type)
    tensions = calcul_tensions(frequences, r, c, circuit_type, time)

    for widget in graph_frame.winfo_children():
        widget.destroy()

    # Graphiques de gains
    if root.winfo_width()-param_frame.winfo_width() == 1:
        size = None
    else:
        size = [(root.winfo_width()-param_frame.winfo_width())/rcParams['figure.dpi'], (root.winfo_height()-40)/rcParams['figure.dpi']]

    graphs = plt.figure(figsize=size)
    graph_grains = graphs.add_subplot(3, 1, 1)
    graph_grains.semilogx(frequences[:len(gains)], 20 * np.log10(gains))
    graph_grains.set_xlabel("Fréquence (Hz)")
    graph_grains.set_ylabel("Gain (dB)")
    graph_grains.set_title(f"Gain d'un circuit RC en {circuit_type}")
    if circuit_type in [SERIE, PARALELLE]:
        graph_grains.legend((f"Frequence de coupure : {(1/(2 * np.pi * r * c)):.2f} Hz",))
        graph_grains.axvline(x=1/(2 * np.pi * r * c), color='black')

    # Graphique de déphasage
    graph_dephasage = graphs.add_subplot(3, 1, 2)
    graph_dephasage.semilogx(frequences, dephasages)
    graph_dephasage.set_xlabel("Fréquence (Hz)")
    graph_dephasage.set_ylabel("Phase (Radian)")
    graph_dephasage.set_title(f"Déphasage d'un circuit RC en {circuit_type}")

    # Graphique de tension
    graph_tension = graphs.add_subplot(3, 1, 3)
    for tension in tensions:
        graph_tension.plot(time, tension)
    graph_tension.set_xlabel("Temps (s)")
    graph_tension.set_ylabel("Tension (V)")
    graph_tension.set_title(f"Tension du circuit ({circuit_type})")
    
    graphs.subplots_adjust(hspace=0.995)
    canvas = FigureCanvasTkAgg(graphs, master=graph_frame)
    plot_widget = canvas.get_tk_widget()
    plot_widget.pack()

    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()

    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Fenetre Tkinter
try:
    from ttkthemes import ThemedTk
    root = ThemedTk(theme=THEME)
except:
    root = tk.Tk()

root.title("Analyse d'un circuit RC")

# Frame des parametres
param_frame = ttk.Frame(root)
param_frame.pack(side=tk.LEFT)

# List des types de circuit
circuit_type_frame = ttk.Frame(param_frame)
circuit_type_frame.pack(anchor="w")

circuit_type_label = ttk.Label(circuit_type_frame, text="Type du Circuit :")
circuit_type_label.pack(side=tk.LEFT)
circuit_type_select = ttk.Combobox(circuit_type_frame, values=[SERIE, PARALELLE, WIEN])
circuit_type_select.set(SERIE)
circuit_type_select.pack(side=tk.RIGHT)

# Frequences
freq_frame1 = ttk.Frame(param_frame)
freq_frame1.pack(anchor="w")
freq_frame2 = ttk.Frame(param_frame)
freq_frame2.pack(anchor="w")

frequence_deb_label = ttk.Label(freq_frame1, text="Frequence début (Hz):")
frequence_deb_label.pack(side=tk.LEFT)
frequence_deb_input = ttk.Entry(freq_frame1)
frequence_deb_input.insert(0, "10")
frequence_deb_input.pack(side=tk.RIGHT)

frequence_fin_label = ttk.Label(freq_frame2, text="Frequence fin (Hz):")
frequence_fin_label.pack(side=tk.LEFT)
frequence_fin_input = ttk.Entry(freq_frame2)
frequence_fin_input.insert(0, "100000")
frequence_fin_input.pack(side=tk.RIGHT)

# RC
r_frame = ttk.Frame(param_frame)
r_frame.pack(anchor="w")
c_frame = ttk.Frame(param_frame)
c_frame.pack(anchor="w")

r_label = ttk.Label(r_frame, text="R (ohms):")
r_label.pack(side=tk.LEFT)
r_input = ttk.Entry(r_frame)
r_input.insert(0, "1000")
r_input.pack(side=tk.RIGHT)

c_label = ttk.Label(c_frame, text="C (farads):")
c_label.pack(side=tk.LEFT)
c_input = ttk.Entry(c_frame)
c_input.insert(0, "1e-6")
c_input.pack(side=tk.RIGHT)

# Periode de l'etude
temps_frame1 = ttk.Frame(param_frame)
temps_frame1.pack(anchor="w")
temps_frame2 = ttk.Frame(param_frame)
temps_frame2.pack(anchor="w")

temps_deb_label = ttk.Label(temps_frame1, text="Temps debut (s):")
temps_deb_label.pack(side=tk.LEFT)
temps_deb_input = ttk.Entry(temps_frame1)
temps_deb_input.insert(0, "0")
temps_deb_input.pack(side=tk.RIGHT)

temps_fin_label = ttk.Label(temps_frame2, text="Temps fin (s):")
temps_fin_label.pack(side=tk.LEFT)
temps_fin_input = ttk.Entry(temps_frame2)
temps_fin_input.insert(0, "0.01")
temps_fin_input.pack(side=tk.RIGHT)

# Bouton pour générer le graphique
plot_button = ttk.Button(param_frame, text="Générer", command=gen_plot)
plot_button.pack()

# Frame pour le graphique
graph_frame = ttk.Frame(root)
graph_frame.pack(side=tk.RIGHT)

if __name__ == "__main__":
    root.mainloop()
