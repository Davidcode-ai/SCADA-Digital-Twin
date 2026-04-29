"""
SCADA Digital Twin Simulator for Alberti Steelworks.
This module simulates the physical behavior of industrial machinery (OT)
and provides a real-time IT dashboard for monitoring and safety lock-downs.
"""
import customtkinter as ctk
import time
import random
import threading
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# =====================================================================
# COMUNICACIÓN EN MEMORIA RAM (Adiós al lag de los archivos .json)
# =====================================================================
ESTADO_GLOBAL = {
    "MOTOR": {"nombre": "Motor Principal", "encendido": False, "valor1": 0, "valor2": 25.0, "destruido": False, "alerta": False},
    "HORNO": {"nombre": "Horno de Fundición", "encendido": False, "valor1": 1.0, "valor2": 25.0, "destruido": False, "alerta": False},
    "CINTA": {"nombre": "Cinta Transportadora", "encendido": False, "valor1": 0, "valor2": 0, "destruido": False, "alerta": False}
}

COMANDOS_GLOBAL = {"MOTOR": {}, "HORNO": {}, "CINTA": {}}

# =====================================================================
# PARTE 1: EL CEREBRO OT (A 30 actualizaciones por segundo)
# =====================================================================
def motor_fisico_invisible():
    """
    Background thread simulating the Operational Technology (OT) physical engine.
    It runs at approximately 30 FPS, reading commands from shared memory (RAM)
    and updating the telemetry (temperature, RPM, load) of the machines based on physics math.
    It triggers destruction flags if safety thresholds are critically exceeded.
    """
    while True:
        # 1. Procesar Órdenes directamente de la RAM
        for maq_id, cmd in COMANDOS_GLOBAL.items():
            maq = ESTADO_GLOBAL[maq_id]
            
            if cmd.get("RESET", False):
                maq["destruido"] = False
                maq["alerta"] = False
                if maq_id == "MOTOR": maq["valor2"] = 25.0
                if maq_id == "HORNO": maq["valor2"] = 25.0
                if maq_id == "CINTA": maq["valor2"] = 0
            
            if not maq["destruido"]:
                maq["encendido"] = cmd.get("encendido", False)

        # 2. FÍSICA MOTOR PRINCIPAL (Ajustada para ser súper fluida)
        cmd_motor = COMANDOS_GLOBAL["MOTOR"]
        m = ESTADO_GLOBAL["MOTOR"]
        if not m["destruido"]:
            rpm_obj = 3500 if m["encendido"] else 0
            m["valor1"] += (rpm_obj - m["valor1"]) * 0.05 # Inercia más suave
            
            calor = (m["valor1"] / 1000) ** 1.6 * 0.1
            if cmd_motor.get("fuga_aceite", False): calor *= 4.0
            
            enfriamiento = 0.03
            if cmd_motor.get("ventilador", False) and not cmd_motor.get("romper_ventilador", False):
                enfriamiento += 1.5
                
            m["valor2"] = max(25.0, m["valor2"] + calor - enfriamiento + random.uniform(-0.1, 0.1))
            m["alerta"] = True if m["valor2"] > 95 else False
            if m["valor2"] >= 150:
                m["destruido"] = True
                m["encendido"] = False

        # 3. FÍSICA HORNO
        cmd_horno = COMANDOS_GLOBAL["HORNO"]
        h = ESTADO_GLOBAL["HORNO"]
        if not h["destruido"]:
            fuga_gas = cmd_horno.get("fuga_gas", False)
            extractor = cmd_horno.get("extractor", False)
            
            h["valor1"] = 5.0 if fuga_gas else (1.5 if h["encendido"] else 1.0) 
            temp_obj = 800 if h["encendido"] else 25
            if fuga_gas and h["encendido"]: temp_obj = 1500 
            
            tasa_calentamiento = 2.0
            if extractor: tasa_calentamiento -= 0.8
            
            if h["valor2"] < temp_obj: h["valor2"] += tasa_calentamiento + random.uniform(-0.5, 0.5)
            elif h["valor2"] > temp_obj: h["valor2"] -= 1.0
            
            h["alerta"] = True if h["valor2"] > 900 else False
            if h["valor2"] >= 1200:
                h["destruido"] = True
                h["encendido"] = False

        # 4. FÍSICA CINTA
        cmd_cinta = COMANDOS_GLOBAL["CINTA"]
        c = ESTADO_GLOBAL["CINTA"]
        if not c["destruido"]:
            atasco = cmd_cinta.get("atasco", False)
            rapido = cmd_cinta.get("rapido", False)
            
            vel_obj = 0
            if c["encendido"]: vel_obj = 5.0 if rapido else 2.0
            if atasco: vel_obj = 0.0
            
            c["valor1"] += (vel_obj - c["valor1"]) * 0.1 
            
            if c["encendido"] and not atasco:
                c["valor2"] = random.randint(50, 200) 
            elif atasco and c["encendido"]:
                c["valor2"] += 15 # Se acumula más rápido
            else:
                c["valor2"] = 0
                
            c["alerta"] = True if c["valor2"] > 500 else False
            if c["valor2"] >= 1000: 
                c["destruido"] = True
                c["encendido"] = False

        # Dormimos solo 30 milisegundos (aprox 33 FPS)
        time.sleep(0.03)


# =====================================================================
# PARTE 2: LA INTERFAZ SCADA (IT)
# =====================================================================
class SCADA_App(ctk.CTk):
    """
    Main Application Class representing the IT Dashboard.
    Handles the GUI rendering, data visualization through matplotlib,
    and the real-time interaction with the background OT physics engine.
    """
    def __init__(self):
        super().__init__()
        self.title("SCADA SYSTEMS - INDUSTRIA 4.0")
        self.geometry("1100x750") 
        
        self.maquina_actual = None
        self.historial_grafica = []
        self.estado_anterior = {"MOTOR": "OK", "HORNO": "OK", "CINTA": "OK"}
        self.limites = {
            "MOTOR": {"v1_max": 4000, "v2_max": 150},
            "HORNO": {"v1_max": 10, "v2_max": 1200},
            "CINTA": {"v1_max": 10, "v2_max": 1000}
        }
        
        # --- LAYOUT PRINCIPAL ---
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # --- FOOTER ---
        self.footer = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#1a1a1a")
        self.footer.pack(side="bottom", fill="x")
        
        self.lbl_reloj = ctk.CTkLabel(self.footer, text="00:00:00", font=("Consolas", 14, "bold"), text_color="#2ecc71")
        self.lbl_reloj.pack(side="right", padx=20)
        
        ctk.CTkLabel(self.footer, text="👤 OPERARIO: ADMIN_DAW_01 | 🟢 CONEXIÓN ESTABLE", font=("Consolas", 12), text_color="gray").pack(side="left", padx=20)
        
        self.pantallas = {}
        self.crear_pantallas()
        self.mostrar_pantalla("INSTRUCCIONES")
        
        # --- LANZAR LA FÁBRICA EN SEGUNDO PLANO ---
        hilo_ot = threading.Thread(target=motor_fisico_invisible, daemon=True)
        hilo_ot.start()
        
        # Bucle de interfaz a 30 FPS (cada 33 ms)
        self.after(33, self.bucle_actualizacion)
        self.actualizar_reloj()

    def actualizar_reloj(self):
        hora_actual = datetime.now().strftime("%H:%M:%S")
        self.lbl_reloj.configure(text=f"HORA DEL SISTEMA: {hora_actual}")
        self.after(1000, self.actualizar_reloj)

    def log_evento(self, mensaje, tipo="INFO"):
        """
        Appends a timestamped log entry to the system's datalogger.
        Used for auditing critical failures and status changes.
        """
        hora = datetime.now().strftime("%H:%M:%S")
        linea = f"[{hora}] {mensaje}\n"
        self.txt_logs.insert("end", linea)
        self.txt_logs.see("end") 

    def crear_pantallas(self):
        # 1. INSTRUCCIONES
        p_inst = ctk.CTkFrame(self.container)
        ctk.CTkLabel(p_inst, text="MANUAL DE USUARIO Y NORMAS DE USO", font=("Roboto", 30, "bold"), text_color="#3498db").pack(pady=(80, 20))
        texto_instrucciones = (
            "Bienvenido al entorno de simulación SCADA. Por favor, lee cómo operar la planta:\n\n"
            "📍 1. MAPA GLOBAL: Muestra el estado en tiempo real de las 3 máquinas de la fábrica.\n"
            "      Presta atención al 'Registro de Sucesos' inferior para ver el historial de alertas.\n\n"
            "⚙️ 2. CONTROL: Haz clic en cualquier máquina del mapa para acceder a su panel individual.\n"
            "      Desde ahí podrás encender los motores, ventiladores o extractores.\n\n"
            "🔥 3. INYECCIÓN DE FALLOS: Para probar el sistema, usa los interruptores naranjas de cada\n"
            "      máquina. Podrás provocar averías (atascos, fugas de aceite o gas, etc.).\n\n"
            "🔧 4. REPARACIÓN: Si fuerzas una máquina hasta el límite, el sistema de seguridad la bloqueará.\n"
            "      Aparecerá una pantalla roja. Usa el botón verde de 'MANTENIMIENTO' para arreglarla."
        )
        caja_texto = ctk.CTkFrame(p_inst, fg_color="#1e1e1e", corner_radius=10)
        caja_texto.pack(pady=20, padx=50, fill="x")
        ctk.CTkLabel(caja_texto, text=texto_instrucciones, font=("Roboto", 16), justify="left").pack(pady=30, padx=40)
        
        self.check_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(p_inst, text="He leído las instrucciones y sé cómo usar el simulador", variable=self.check_var, command=self.validar_instrucciones, font=("Roboto", 15)).pack(pady=30)
        
        self.btn_continuar = ctk.CTkButton(p_inst, text="INICIAR SIMULACIÓN", font=("Roboto", 16, "bold"), state="disabled", fg_color="gray", width=250, height=50, command=lambda: self.mostrar_pantalla("MAPA"))
        self.btn_continuar.pack(pady=10)
        self.pantallas["INSTRUCCIONES"] = p_inst

        # 2. MAPA
        self.p_mapa = ctk.CTkFrame(self.container)
        ctk.CTkLabel(self.p_mapa, text="MAPA DE PLANTA - ESTADO EN TIEMPO REAL", font=("Roboto", 24, "bold")).pack(pady=10)
        self.lbl_alerta_global = ctk.CTkLabel(self.p_mapa, text="SISTEMA NOMINAL - SIN ALERTAS", text_color="green", font=("Roboto", 16))
        self.lbl_alerta_global.pack(pady=5)
        
        grid_mapa = ctk.CTkFrame(self.p_mapa, fg_color="transparent")
        grid_mapa.pack(pady=10)
        
        self.btn_mapa_motor = ctk.CTkButton(grid_mapa, text="MOTOR\nPRINCIPAL", width=200, height=180, font=("Roboto", 18, "bold"), command=lambda: self.abrir_maquina("MOTOR"))
        self.btn_mapa_motor.grid(row=0, column=0, padx=20, pady=10)
        self.btn_mapa_horno = ctk.CTkButton(grid_mapa, text="HORNO\nFUNDICIÓN", width=200, height=180, font=("Roboto", 18, "bold"), command=lambda: self.abrir_maquina("HORNO"))
        self.btn_mapa_horno.grid(row=0, column=1, padx=20, pady=10)
        self.btn_mapa_cinta = ctk.CTkButton(grid_mapa, text="CINTA\nTRANSPORTADORA", width=200, height=180, font=("Roboto", 18, "bold"), command=lambda: self.abrir_maquina("CINTA"))
        self.btn_mapa_cinta.grid(row=0, column=2, padx=20, pady=10)
        
        log_frame = ctk.CTkFrame(self.p_mapa)
        log_frame.pack(fill="both", expand=True, padx=40, pady=(10, 20))
        ctk.CTkLabel(log_frame, text="REGISTRO DE SUCESOS (DATALOGGER)", font=("Consolas", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        self.txt_logs = ctk.CTkTextbox(log_frame, font=("Consolas", 12), text_color="#d3d3d3", fg_color="#1e1e1e")
        self.txt_logs.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_evento("Sistema central iniciado correctamente.", "INFO")
        self.pantallas["MAPA"] = self.p_mapa

        # 3. MÁQUINA INDIVIDUAL
        self.p_maquina = ctk.CTkFrame(self.container)
        top_bar = ctk.CTkFrame(self.p_maquina, height=50)
        top_bar.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top_bar, text="⬅ VOLVER AL MAPA", width=150, command=lambda: self.mostrar_pantalla("MAPA")).pack(side="left")
        self.lbl_titulo_maquina = ctk.CTkLabel(top_bar, text="MAQUINA", font=("Roboto", 20, "bold"))
        self.lbl_titulo_maquina.pack(side="left", padx=50)
        
        work_area = ctk.CTkFrame(self.p_maquina, fg_color="transparent")
        work_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.frame_controles = ctk.CTkFrame(work_area, width=250)
        self.frame_controles.pack(side="left", fill="y", padx=10)
        frame_datos = ctk.CTkFrame(work_area)
        frame_datos.pack(side="right", fill="both", expand=True, padx=10)
        
        kpi_bar = ctk.CTkFrame(frame_datos, fg_color="transparent")
        kpi_bar.pack(fill="x", pady=10, padx=20)
        
        box_v1 = ctk.CTkFrame(kpi_bar, fg_color="transparent")
        box_v1.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_v1_title = ctk.CTkLabel(box_v1, text="VALOR 1", font=("Roboto", 12, "bold"))
        self.lbl_v1_title.pack()
        self.lbl_v1 = ctk.CTkLabel(box_v1, text="0", font=("Roboto", 40, "bold"))
        self.lbl_v1.pack()
        self.prog_v1 = ctk.CTkProgressBar(box_v1, height=10)
        self.prog_v1.set(0)
        self.prog_v1.pack(fill="x", pady=5)
        
        box_v2 = ctk.CTkFrame(kpi_bar, fg_color="transparent")
        box_v2.pack(side="right", fill="x", expand=True, padx=10)
        self.lbl_v2_title = ctk.CTkLabel(box_v2, text="VALOR 2", font=("Roboto", 12, "bold"))
        self.lbl_v2_title.pack()
        self.lbl_v2 = ctk.CTkLabel(box_v2, text="0", font=("Roboto", 40, "bold"), text_color="#3498db")
        self.lbl_v2.pack()
        self.prog_v2 = ctk.CTkProgressBar(box_v2, height=10)
        self.prog_v2.set(0)
        self.prog_v2.pack(fill="x", pady=5)
        
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values(): spine.set_color('gray')
        
        self.line, = self.ax.plot([], [], color='#e74c3c', linewidth=2.5) 
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_datos)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10, padx=10)
        
        self.pantallas["MAQUINA"] = self.p_maquina
        self.p_muerte = ctk.CTkFrame(self.p_maquina, fg_color="#8B0000")

    def validar_instrucciones(self):
        if self.check_var.get():
            self.btn_continuar.configure(state="normal", fg_color="#2980b9")
        else:
            self.btn_continuar.configure(state="disabled", fg_color="gray")

    def mostrar_pantalla(self, nombre):
        for p in self.pantallas.values(): p.pack_forget()
        self.pantallas[nombre].pack(fill="both", expand=True)
        if nombre == "MAPA": 
            self.maquina_actual = None

    def abrir_maquina(self, id_maquina):
        """
        Dynamically generates the detailed view of a specific machine.
        It binds the control switches to the shared memory commands map.
        """
        self.maquina_actual = id_maquina
        self.historial_grafica = [0] * 100 
        
        for widget in self.frame_controles.winfo_children(): widget.destroy()
        
        if id_maquina == "MOTOR":
            self.lbl_titulo_maquina.configure(text="MOTOR PRINCIPAL")
            self.lbl_v1_title.configure(text="REVOLUCIONES")
            self.lbl_v2_title.configure(text="TEMPERATURA (ºC)")
            self.ax.set_title("Curva de Calentamiento", color="white")
            self.crear_switch(id_maquina, "encendido", "Alimentación Motor")
            self.crear_switch(id_maquina, "ventilador", "Sistema Ventilación")
            ctk.CTkLabel(self.frame_controles, text="INYECCIÓN FALLOS", text_color="orange", font=("Roboto", 12, "bold")).pack(pady=(30,5))
            self.crear_switch(id_maquina, "romper_ventilador", "Bloquear Aspas")
            self.crear_switch(id_maquina, "fuga_aceite", "Fuga de Aceite")
            
        elif id_maquina == "HORNO":
            self.lbl_titulo_maquina.configure(text="HORNO DE FUNDICIÓN")
            self.lbl_v1_title.configure(text="PRESIÓN GAS (Bar)")
            self.lbl_v2_title.configure(text="TEMPERATURA (ºC)")
            self.ax.set_title("Temperatura de Caldera", color="white")
            self.crear_switch(id_maquina, "encendido", "Válvula Principal")
            self.crear_switch(id_maquina, "extractor", "Extractor Humos")
            ctk.CTkLabel(self.frame_controles, text="INYECCIÓN FALLOS", text_color="orange", font=("Roboto", 12, "bold")).pack(pady=(30,5))
            self.crear_switch(id_maquina, "fuga_gas", "Romper Tubería Gas")
            
        elif id_maquina == "CINTA":
            self.lbl_titulo_maquina.configure(text="CINTA TRANSPORTADORA")
            self.lbl_v1_title.configure(text="VELOCIDAD (m/s)")
            self.lbl_v2_title.configure(text="CARGA ACUMULADA (Kg)")
            self.ax.set_title("Nivel de Sobrecarga", color="white")
            self.crear_switch(id_maquina, "encendido", "Motor Tractor")
            self.crear_switch(id_maquina, "rapido", "Marcha Rápida")
            ctk.CTkLabel(self.frame_controles, text="INYECCIÓN FALLOS", text_color="orange", font=("Roboto", 12, "bold")).pack(pady=(30,5))
            self.crear_switch(id_maquina, "atasco", "Atascar Rodillo")

        ctk.CTkButton(self.frame_controles, text="🔧 MANTENIMIENTO", fg_color="#27ae60", hover_color="#2ecc71", font=("Roboto", 14, "bold"), height=40, command=lambda: self.enviar_reset(id_maquina)).pack(side="bottom", pady=20)
        self.mostrar_pantalla("MAQUINA")

    def crear_switch(self, id_maquina, comando, texto):
        val = COMANDOS_GLOBAL[id_maquina].get(comando, False)
        sw = ctk.CTkSwitch(self.frame_controles, text=texto, font=("Roboto", 13), command=lambda: self.actualizar_cmd(id_maquina, comando, sw.get()))
        if val: sw.select()
        sw.pack(pady=10, padx=10, anchor="w")

    def actualizar_cmd(self, id_maq, cmd, valor):
        COMANDOS_GLOBAL[id_maq][cmd] = bool(valor)

    def enviar_reset(self, id_maq):
        """
        Triggers a maintenance protocol. Sends a reset flag to the OT engine
        to restore a locked-down machine to its nominal state.
        """
        COMANDOS_GLOBAL[id_maq] = {"RESET": True}
        self.log_evento(f"Equipo de mantenimiento enviado a {id_maq}.", "REPARADO")
        self.after(200, lambda: self.limpiar_reset(id_maq))
        self.abrir_maquina(id_maq)

    def limpiar_reset(self, id_maq):
        COMANDOS_GLOBAL[id_maq] = {}

    def bucle_actualizacion(self):
        """
        Main GUI loop executed at 30 FPS.
        Reads the shared memory states and updates the progress bars, 
        matplotlib graphs, and background colors to reflect real-time telemetry.
        """
        try:
            # 1. ACTUALIZAR MAPA Y LOGS
            alertas_activas = 0
            for maq_id, btn in [("MOTOR", self.btn_mapa_motor), ("HORNO", self.btn_mapa_horno), ("CINTA", self.btn_mapa_cinta)]:
                maq_data = ESTADO_GLOBAL[maq_id]
                estado_actual = "OK"
                
                if maq_data["destruido"]:
                    btn.configure(fg_color="#8B0000", border_color="red", border_width=3)
                    alertas_activas += 1
                    estado_actual = "CRITICO"
                elif maq_data["alerta"]:
                    btn.configure(fg_color="#f39c12", border_color="yellow", border_width=3)
                    alertas_activas += 1
                    estado_actual = "ALERTA"
                else:
                    btn.configure(fg_color="#1f538d", border_width=0)
                    
                if estado_actual != self.estado_anterior[maq_id]:
                    if estado_actual == "ALERTA":
                        self.log_evento(f"¡ADVERTENCIA! Valores inusuales detectados en {maq_data['nombre']}.", "ALERTA")
                    elif estado_actual == "CRITICO":
                        self.log_evento(f"¡FALLO CATASTRÓFICO! {maq_data['nombre']} ha colapsado. Unidad aislada.", "CRITICO")
                    elif estado_actual == "OK" and self.estado_anterior[maq_id] != "OK":
                        self.log_evento(f"{maq_data['nombre']} vuelve a operar en parámetros normales.", "INFO")
                    self.estado_anterior[maq_id] = estado_actual
            
            if alertas_activas > 0:
                self.lbl_alerta_global.configure(text=f"⚠️ ADVERTENCIA: {alertas_activas} EQUIPOS REQUIEREN ATENCIÓN", text_color="red")
            else:
                self.lbl_alerta_global.configure(text="SISTEMA NOMINAL - SIN ALERTAS", text_color="green")

            # 2. ACTUALIZAR MÁQUINA SELECCIONADA
            if self.maquina_actual:
                maq = ESTADO_GLOBAL[self.maquina_actual]
                limites = self.limites[self.maquina_actual]
                
                if maq["destruido"]:
                    self.p_muerte.place(relx=0, rely=0, relwidth=1, relheight=1)
                    if not hasattr(self, 'lbl_muerte'):
                        self.lbl_muerte = ctk.CTkLabel(self.p_muerte, text="⚠️ UNIDAD FUERA DE SERVICIO ⚠️\nBloqueo de Seguridad Activado", font=("Roboto", 40, "bold"), text_color="white")
                        self.lbl_muerte.pack(expand=True)
                        ctk.CTkButton(self.p_muerte, text="🔧 PROCEDER A REPARACIÓN", fg_color="green", width=250, height=50, command=lambda: [self.enviar_reset(self.maquina_actual), self.p_muerte.place_forget()]).pack(pady=50)
                else:
                    self.p_muerte.place_forget()
                    
                    val1 = maq['valor1']
                    val2 = maq['valor2']
                    self.lbl_v1.configure(text=f"{val1:.1f}" if val1 < 100 else f"{int(val1)}")
                    self.lbl_v2.configure(text=f"{int(val2)}")
                    
                    pct1 = min(val1 / limites["v1_max"], 1.0)
                    pct2 = min(val2 / limites["v2_max"], 1.0)
                    
                    self.prog_v1.set(pct1)
                    self.prog_v2.set(pct2)
                    
                    if maq["alerta"]: 
                        self.lbl_v2.configure(text_color="#e74c3c") 
                        self.prog_v2.configure(progress_color="#e74c3c")
                    elif pct2 > 0.6:
                        self.lbl_v2.configure(text_color="#f1c40f") 
                        self.prog_v2.configure(progress_color="#f1c40f")
                    else: 
                        self.lbl_v2.configure(text_color="#2ecc71") 
                        self.prog_v2.configure(progress_color="#2ecc71")

                    self.historial_grafica.append(val2)
                    if len(self.historial_grafica) > 100: self.historial_grafica.pop(0)
                    self.line.set_ydata(self.historial_grafica)
                    self.line.set_xdata(range(len(self.historial_grafica)))
                    self.ax.set_ylim(0, max(limites["v2_max"] * 0.2, max(self.historial_grafica) + 20))
                    self.ax.set_xlim(0, 100)
                    self.canvas.draw()
        except: pass
        
        # Repite el ciclo en 33 milisegundos (30 FPS reales)
        self.after(33, self.bucle_actualizacion)

if __name__ == "__main__":
    app = SCADA_App()
    app.mainloop()