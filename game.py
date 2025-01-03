import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation
import random
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from fpdf import FPDF

# Sabitler ve Parametreler
g = 9.81  # Yer çekimi ivmesi (m/s²)
rho_air = 1.225  # Havanın yoğunluğu (kg/m³)
drag_coefficient = 1.2  # Aracın aerodinamik katsayısı
car_mass = 798  # Aracın Kütlesi (kg)
car_area = 1.5  # Aracın ön yüz kesiti (m²)

tyre_types = {
    "Yumuşak": (0.0005, 1.3),
    "Orta": (0.0003, 1.2),
    "Sert": (0.0002, 1.1)
}

weather_conditions = {
    "Sunny": 1.0,
    "Rainy": 0.8,
    "Windy": 0.9,
    "Foggy": 0.7
}

# Simülasyon Fonksiyonu
def simulate_tyre_performance(time_step, tyre_type, speed, weather, downforce):
    k_wear, grip_factor = tyre_types[tyre_type]

    # Lastik sıcaklığı
    T_env = random.randint(15, 40)
    surface_condition_factor = weather_conditions[weather] * random.uniform(0.7, 1.2)
    tyre_temp = T_env + grip_factor * speed * 0.1 * surface_condition_factor

    # Sürtünme kuvveti
    load = (car_mass * g + downforce) * grip_factor
    friction_force = load * surface_condition_factor

    # Aşınma
    wear = k_wear * load * (speed**2) * 0.001

    # Aerodinamik direnç
    air_resistance = 0.5 * rho_air * drag_coefficient * car_area * (speed / 3.6) ** 2

    return wear, tyre_temp, friction_force, air_resistance

# Veriyi CSV'ye kaydetme fonksiyonu
def save_simulation_data(data, filename="simulation_data.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# PDF Raporlama
class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Simulasyon Raporu", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Sayfa {self.page_no()}", 0, 0, "C")

    def add_simulation_details(self, sim_data):
        self.set_font("Arial", size=12)
        self.cell(0, 10, f"Lastik Türü: {sim_data['tyre_type']}", 0, 1)
        self.cell(0, 10, f"Hava Durumu: {sim_data['weather']}", 0, 1)
        self.cell(0, 10, f"Araç Hızı: {sim_data['speed']} km/h", 0, 1)

    def add_plot(self, plot_filename):
        self.image(plot_filename, x=10, y=None, w=180)

# Gerçek Zamanlı Animasyon Fonksiyonu
def real_time_simulation(tyre_type, speed, weather):
    time_step = 0
    time = []
    wear_data = []
    temp_data = []
    friction_data = []

    current_temp = 25
    total_wear = 0

    sim_data = {
        "tyre_type": tyre_type,
        "speed": speed,
        "weather": weather,
        "time_series": []
    }

    def update(frame):
        nonlocal time_step, total_wear, current_temp

        time_step += 0.1
        wear, current_temp, friction, air_res = simulate_tyre_performance(
            time_step, tyre_type, speed, weather, downforce=3000
        )
        total_wear += wear

        time.append(time_step)
        wear_data.append(total_wear)
        temp_data.append(current_temp)
        friction_data.append(friction)

        # Veri kaydını genişletme
        sim_data["time_series"].append({
            "time": round(time_step, 1),
            "wear": total_wear,
            "temp": current_temp,
            "friction": friction
        })

        # Grafik Güncelleme
        ax1.clear()
        ax2.clear()
        ax3.clear()

        ax1.plot(time, wear_data, color="red", label="Lastik Aşınması")
        ax2.plot(time, temp_data, color="blue", label="Lastik Sıcaklığı")
        ax3.plot(time, friction_data, color="green", label="Sürtünme Kuvveti")

        ax1.legend(loc="upper left")
        ax2.legend(loc="upper left")
        ax3.legend(loc="upper left")

        ax1.set_ylabel("Aşınma (%)")
        ax2.set_ylabel("Sıcaklık (°C)")
        ax3.set_ylabel("Kuvvet (N)")
        ax3.set_xlabel("Zaman (saniye)")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    sns.set(style="darkgrid")

    ani = FuncAnimation(fig, update, interval=100)
    plt.tight_layout()
    plt.show()

    # Veri kaydı
    save_simulation_data(sim_data)
    messagebox.showinfo("Simülasyon Bitti", "Veriler JSON formatında kaydedildi!")

# Tkinter Arayüz
def start_simulation():
    tyre_choice = tyres.get()
    speed_choice = int(speed_entry.get()) if speed_entry.get() else 150
    weather_choice = weather_combobox.get() if weather_combobox.get() else "Sunny"

    if not tyre_choice:
        messagebox.showerror("Hata", "Lütfen bir lastik türü seçiniz!")
        return

    real_time_simulation(tyre_choice, speed_choice, weather_choice)

# Arayüz Başlatma
root = tk.Tk()
root.title("Geliştirilmiş Formula 1 Simülasyonu")

# Lastik Türü Seçimi
tk.Label(root, text="Lastik Türü").grid(row=0, column=0)
tyres = ttk.Combobox(root, values=list(tyre_types.keys()))
tyres.grid(row=0, column=1)

# Araç Hızı Girişi
tk.Label(root, text="Araç Hızı (km/saat)").grid(row=1, column=0)
speed_entry = tk.Entry(root)
speed_entry.grid(row=1, column=1)

# Hava Durumu Seçimi
tk.Label(root, text="Hava Durumu").grid(row=2, column=0)
weather_combobox = ttk.Combobox(root, values=list(weather_conditions.keys()))
weather_combobox.grid(row=2, column=1)

# Simülasyon Başlat Butonu
tk.Button(root, text="Simülasyonu Başlat", command=start_simulation).grid(row=3, columnspan=2)

root.mainloop()
