import numpy as np
import matplotlib.pyplot as plt

# Définition des valeurs de R et L
R = 1000  # Résistance en ohms
L = 2E-02  # Inductance en henrys

# Définition de la fréquence angulaire
frequencies = np.logspace(0, 8, 1000)  # Fréquence angulaire de 1 à 10000 rad/s

# Conversion des fréquences angulaires en Hz
frequencies_hz = frequencies / (2 * np.pi)

# Calcul de l'impédance Z
Z = R + 1j * 2 * np.pi * frequencies * L

# Calcul du module et de la phase de Z
module_Z = np.abs(Z)
phase_Z = np.angle(Z, deg=True)

# Fréquence de coupure en Hz
w_coupure_hz = R / (2 * np.pi * L)

# Temps
t = np.linspace(0, 0.1, 1000)  # Temps de 0 à 0.01 s

# Tension en fonction du temps
v_entree = np.sin(100 * t)  # Tension d'entrée sinusoidale
v_sortie = (R / np.sqrt(R**2 + (w_coupure_hz * 2 * np.pi * L)**2)) * np.sin(100 * t - np.arctan(w_coupure_hz * 2 * np.pi * L / R))

# Tracé du diagramme de Bode du module de Z
plt.figure(figsize=(12, 8))

# Diagramme de Bode - Module de Z
plt.subplot(3, 1, 1)
plt.semilogx(frequencies_hz, 20 * np.log10(module_Z))
plt.title('Diagramme de Bode - Module de Z')
plt.xlabel('Fréquence (Hz)')
plt.ylabel('Gain (dB)')
plt.grid(True)
plt.axvline(x=w_coupure_hz, color='r', linestyle='--', label='Fréquence de coupure')
plt.legend()

# Diagramme de Bode - Phase de Z
plt.subplot(3, 1, 2)
plt.semilogx(frequencies_hz, phase_Z)
plt.title('Diagramme de Bode - Phase de Z')
plt.xlabel('Fréquence (Hz)')
plt.ylabel('Phase (degrés)')
plt.grid(True)

# Diagramme de la tension en fonction du temps
plt.subplot(3, 1, 3)
plt.plot(t, v_entree, label='Tension d\'entrée')
plt.plot(t, v_sortie, label='Tension de sortie')
plt.title('Tension en fonction du temps')
plt.xlabel('Temps (s)')
plt.ylabel('Tension (V)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
