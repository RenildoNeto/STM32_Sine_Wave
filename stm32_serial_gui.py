import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
from tkinter import font as tkfont
import threading
import queue
import time

# --- Constants for Futuristic Theming ---
DARK_THEME = {
     "bg": "#121212", #121212
    "fg": "#E0E0E0",
    "primary": "#1E88E5",  # Vibrant blue
    "secondary": "#00ACC1",  # Cyan
    "accent": "#07612C",  # Pink #FF4081
    "success": "#00C853",  # Green
    "warning": "#FFAB00",  # Amber
    "error": "#FF4500",  # Red
    "bg_widget": "#212121",
    "fg_widget": "#FFFFFF",
    "border": "#424242",
    "text_area_bg": "#000000",
    "text_area_fg": "#00FF00",  # Matrix green
    "text_insert_bg": "#00FF00",
    "highlight": "#1E88E5",
    "disabled": "#616161"
}

LIGHT_THEME = {
    "bg": "#FAFAFA",
    "fg": "#212121",
    "primary": "#2962FF",
    "secondary": "#00B8D4",
    "accent": "#FF5252",
    "success": "#00E676",
    "warning": "#FFC400",
    "error": "#FF1744",
    "bg_widget": "#FFFFFF",
    "fg_widget": "#000000",
    "border": "#E0E0E0",
    "text_area_bg": "#FFFFFF",
    "text_area_fg": "#000000",
    "text_insert_bg": "#000000",
    "highlight": "#2962FF",
    "disabled": "#BDBDBD"
}

# --- Translation Dictionary ---
TRANSLATIONS = {
    'en': {
        'title': '⚡ STM32 REAL-TIME SERIAL INTERFACE',
        'status_disconnected': 'Disconnected',
        'status_connected': 'Connected',
        'rx': 'RX: {count} msgs',
        'tx': 'TX: {count} msgs',
        'latency': 'Latency: {ms} ms',
        'connection_protocol': 'CONNECTION PROTOCOL',
        'port': 'PORT:',
        'baudrate': 'BAUDRATE:',
        'connect': '🔗 CONNECT',
        'disconnect': '❌ DISCONNECT',
        'amplitude': 'AMPLITUDE (0-100%)',
        'frequency': 'FREQUENCY (1-1000 Hz)',
        'transmit': '🚀 TRANSMIT SIGNAL PARAMETERS',
        'transmit_success': '✅ TRANSMISSION SUCCESS',
        'serial_monitor': 'REAL-TIME COMMUNICATION CONSOLE',
        'clear_terminal': '🧹 CLEAR TERMINAL',
        'terminal_cleared': '✨ TERMINAL CLEARED',
        'send': 'SEND',
        'theme_toggle': '🌓 TOGGLE QUANTUM THEME',
        'version': 'REAL-TIME SERIAL v2.1',
        'connected_msg': '⚡ Connected to {port} @ {baud} bps\n',
        'disconnected_msg': '🔌 Disconnected from serial interface\n',
        'transmitted': '➡️ Transmitted: A{amp:03d}F{freq:04d}\n',
        'sent': '➡️ Sent: {data}\n',
        'received': '⬅️ Received: {line}\n',
        'terminal_cleared_msg': 'Terminal cleared\n',
        'serial_ports_refreshed': 'Serial ports refreshed\n',
        'error_select_port_baud': 'Please select a serial port and baudrate!',
        'error_amp': 'Amplitude must be between 0 and 100!',
        'error_freq': 'Frequency must be between 1 and 1000!',
        'transmission_error': 'Transmission Error',
        'connection_error': 'Connection Error',
        'disconnected': 'Disconnected',
        'connected': 'Connected',
        'autoconnect': '🔍 AUTO CONNECT',
    },
    'fr': {
        'title': '⚡ INTERFACE SÉRIE TEMPS RÉEL STM32',
        'status_disconnected': 'Déconnecté',
        'status_connected': 'Connecté',
        'rx': 'RX : {count} msgs',
        'tx': 'TX : {count} msgs',
        'latency': 'Latence : {ms} ms',
        'connection_protocol': 'PROTOCOLE DE CONNEXION',
        'port': 'PORT :',
        'baudrate': 'BAUDRATE :',
        'connect': '🔗 CONNECTER',
        'disconnect': '❌ DÉCONNECTER',
        'amplitude': 'AMPLITUDE (0-100%)',
        'frequency': 'FRÉQUENCE (1-1000 Hz)',
        'transmit': '🚀 TRANSMETTRE LES PARAMÈTRES',
        'transmit_success': '✅ TRANSMISSION RÉUSSIE',
        'serial_monitor': 'CONSOLE DE COMMUNICATION TEMPS RÉEL',
        'clear_terminal': '🧹 EFFACER TERMINAL',
        'terminal_cleared': '✨ TERMINAL EFFACÉ',
        'send': 'ENVOYER',
        'theme_toggle': '🌓 THÈME QUANTIQUE',
        'version': 'SÉRIE TEMPS RÉEL v2.1',
        'connected_msg': '⚡ Connecté à {port} @ {baud} bps\n',
        'disconnected_msg': '🔌 Déconnecté de l\'interface série\n',
        'transmitted': '➡️ Transmis : A{amp:03d}F{freq:04d}\n',
        'sent': '➡️ Envoyé : {data}\n',
        'received': '⬅️ Reçu : {line}\n',
        'terminal_cleared_msg': 'Terminal effacé\n',
        'serial_ports_refreshed': 'Ports série actualisés\n',
        'error_select_port_baud': 'Veuillez sélectionner un port série et un baudrate !',
        'error_amp': "L'amplitude doit être comprise entre 0 et 100 !",
        'error_freq': 'La fréquence doit être comprise entre 1 et 1000 !',
        'transmission_error': 'Erreur de transmission',
        'connection_error': 'Erreur de connexion',
        'disconnected': 'Déconnecté',
        'connected': 'Connecté',
        'autoconnect': '🔍 AUTO-CONNEXION',
    }
}

# --- Serial Controller with Threading ---
class SerialController:
    """Handles serial port connection, disconnection, and data transfer with threading."""
    def __init__(self):
        self.ser = None
        self.connected = False
        self.read_thread = None
        self.stop_event = threading.Event()
        self.data_queue = queue.Queue()
        self.lock = threading.Lock()
        self.last_read_time = 0
        self.data_buffer = b''

    def connect(self, port, baudrate=115200):
        try:
            with self.lock:
                self.ser = serial.Serial(
                    port, 
                    baudrate, 
                    timeout=0.01,  # Non-blocking with short timeout
                    write_timeout=1
                )
                self.connected = True
                self.stop_event.clear()
                
                # Start the reading thread
                self.read_thread = threading.Thread(
                    target=self._read_serial, 
                    daemon=True
                )
                self.read_thread.start()
                return True
        except Exception as e:
            messagebox.showerror('Connection Error', f'Failed to connect: {e}')
            return False

    def disconnect(self):
        self.stop_event.set()
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=0.1)
            
        with self.lock:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = None
            self.connected = False

    def send(self, data):
        if self.connected:
            try:
                with self.lock:
                    self.ser.write(data.encode())
                return True
            except Exception as e:
                messagebox.showerror('Transmission Error', f'Failed to send data: {e}')
                return False
        else:
            messagebox.showwarning('Transmission Error', 'Serial is not connected!')
            return False

    def send_amp_freq(self, amplitude, frequency):
        print(f"Sending amplitude: {amplitude}, frequency: {frequency}")
        cmd = f'A{amplitude:03d}F{frequency:04d}\n'
        return self.send(cmd)

    def get_data(self):
        """Get all available data from the queue"""
        data_lines = []
        while not self.data_queue.empty():
            try:
                data_lines.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return data_lines

    def _read_serial(self):
        """Thread function to read serial data in real-time"""
        buffer = b''
        while not self.stop_event.is_set() and self.connected:
            try:
                with self.lock:
                    if self.ser and self.ser.is_open:
                        # Read all available data
                        data = self.ser.read(self.ser.in_waiting or 1)
                        if data:
                            buffer += data
                            # Process complete lines
                            while b'\n' in buffer:
                                line, buffer = buffer.split(b'\n', 1)
                                decoded = line.decode(errors='ignore').strip()
                                if decoded:
                                    self.data_queue.put(decoded)
                    else:
                        time.sleep(0.01)  # Short sleep if not connected
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(0.1)

        # Process any remaining data in buffer
        if buffer:
            decoded = buffer.decode(errors='ignore').strip()
            if decoded:
                self.data_queue.put(decoded)

# --- Main Application ---
class App(tk.Tk):
    """The main application window with real-time performance."""
    def __init__(self):
        super().__init__()
        self.title('⚡ STM32 Real-Time Serial Interface')
        self.geometry('800x850')
        self.resizable(True, True)
        self.minsize(700, 750)
        
        # Performance metrics
        self.update_interval = 50  # ms (20 updates per second)
        self.last_update = 0
        self.received_count = 0
        self.sent_count = 0

        # Custom font for futuristic look
        self.custom_font = tkfont.Font(family="Segoe UI", size=10)
        self.title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.mono_font = tkfont.Font(family="Consolas", size=10)

        self.serial_ctrl = SerialController()
        self.is_dark = True
        self.theme = DARK_THEME

        # Language settings
        self.lang = 'en'
        self.trans = TRANSLATIONS[self.lang]

        self._setup_styles()
        self._create_widgets()
        self._apply_theme()
        self._set_connection_state(False)
        
        # Try autoconnect at startup
        self.after(300, self.autoconnect_serial)
        # Start the GUI update loop
        self.after(self.update_interval, self._update_serial_monitor)

    def _setup_styles(self):
        """Configures all ttk styles based on the current theme."""
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Base styles
        self.style.configure('.',
                           background=self.theme["bg"],
                           foreground=self.theme["fg"],
                           font=self.custom_font,
                           borderwidth=0,
                           relief='flat')

        # Frame styles
        self.style.configure('TFrame', background=self.theme["bg"])
        self.style.configure('Bordered.TFrame', background=self.theme["bg"], 
                           bordercolor=self.theme["border"], borderwidth=2)
        
        # Label styles
        self.style.configure('TLabel', background=self.theme["bg"], 
                           foreground=self.theme["fg"])
        self.style.configure('Title.TLabel', font=self.title_font,
                           foreground=self.theme["primary"])
        self.style.configure('Status.TLabel', font=("Segoe UI", 9),
                           foreground=self.theme["disabled"])

        # LabelFrame styles
        self.style.configure('TLabelframe', background=self.theme["bg"],
                           foreground=self.theme["primary"],
                           bordercolor=self.theme["border"],
                           font=self.title_font)
        self.style.configure('TLabelframe.Label', background=self.theme["bg"],
                           foreground=self.theme["primary"])

        # Entry and Combobox styles
        self.style.configure('TEntry', fieldbackground=self.theme["bg_widget"],
                           foreground=self.theme["fg_widget"],
                           insertcolor=self.theme["text_insert_bg"],
                           bordercolor=self.theme["border"],
                           lightcolor=self.theme["border"],
                           darkcolor=self.theme["border"],
                           padding=5)
        self.style.configure('TCombobox', fieldbackground=self.theme["bg_widget"],
                           foreground=self.theme["fg_widget"],
                           selectbackground=self.theme["highlight"],
                           selectforeground=self.theme["fg_widget"],
                           insertcolor=self.theme["text_insert_bg"],
                           bordercolor=self.theme["border"],
                           padding=5)
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', self.theme["bg_widget"])],
                      foreground=[('readonly', self.theme["fg_widget"])],
                      selectbackground=[('readonly', self.theme["highlight"])],
                      selectforeground=[('readonly', self.theme["fg_widget"])])

        # Button styles
        self.style.configure('TButton', background=self.theme["primary"],
                           foreground=self.theme["fg_widget"],
                           font=self.custom_font,
                           padding=8,
                           borderwidth=0,
                           focuscolor=self.theme["bg"])
        self.style.map('TButton',
                      background=[('active', self.theme["secondary"]),
                                 ('pressed', self.theme["accent"]),
                                 ('disabled', self.theme["disabled"])],
                      foreground=[('active', self.theme["fg_widget"]),
                                 ('pressed', self.theme["fg_widget"]),
                                 ('disabled', self.theme["bg_widget"])])

        # Special buttons
        self.style.configure('Accent.TButton', background=self.theme["accent"])
        self.style.configure('Success.TButton', background=self.theme["success"])
        self.style.configure('Warning.TButton', background=self.theme["warning"])
        self.style.configure('Error.TButton', background=self.theme["error"])

        # Scale styles
        self.style.configure('Horizontal.TScale', background=self.theme["bg"],
                           troughcolor=self.theme["border"],
                           darkcolor=self.theme["primary"],
                           lightcolor=self.theme["primary"],
                           bordercolor=self.theme["border"],
                           gripcount=0)

    def _create_widgets(self):
        """Creates and places all widgets in the window."""
        self.main_frame = ttk.Frame(self, style='Bordered.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        self.title_label = ttk.Label(header_frame, text=self.trans['title'], style='Title.TLabel')
        self.title_label.pack(side='left')
        
        self.status_label = ttk.Label(header_frame, text=self.trans['status_disconnected'], style='Status.TLabel')
        self.status_label.pack(side='right')
        
        # Performance metrics
        metrics_frame = ttk.Frame(self.main_frame)
        metrics_frame.pack(fill='x', pady=5)
        
        self.rx_label = ttk.Label(metrics_frame, text=self.trans['rx'].format(count=0), style='Status.TLabel')
        self.rx_label.pack(side='left', padx=5)
        
        self.tx_label = ttk.Label(metrics_frame, text=self.trans['tx'].format(count=0), style='Status.TLabel')
        self.tx_label.pack(side='left', padx=5)
        
        self.latency_label = ttk.Label(metrics_frame, text=self.trans['latency'].format(ms=0), style='Status.TLabel')
        self.latency_label.pack(side='right', padx=5)

        # --- Serial Configuration Frame ---
        config_frame = ttk.LabelFrame(self.main_frame, text=self.trans['connection_protocol'])
        config_frame.pack(fill='x', pady=5)
        config_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform='col')

        # Port selection
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_var = tk.StringVar(value=ports[0] if ports else '')
        ttk.Label(config_frame, text=self.trans['port']).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.port_menu = ttk.Combobox(config_frame, values=ports, textvariable=self.port_var, 
                                     state='readonly', width=18)
        self.port_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Refresh button
        self.refresh_btn = ttk.Button(config_frame, text='🔄', width=3,
                                    command=self.refresh_ports)
        self.refresh_btn.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        # Baudrate selection
        baudrates = ["9600", "19200", "38400", "57600", "115200", "230400", "500000", "1000000", "2000000"]
        self.baud_var = tk.StringVar(value="115200")
        ttk.Label(config_frame, text=self.trans['baudrate']).grid(row=0, column=3, padx=5, pady=5, sticky='e')
        self.baud_menu = ttk.Combobox(config_frame, values=baudrates, textvariable=self.baud_var, 
                                    state='readonly', width=12)
        self.baud_menu.grid(row=0, column=4, padx=5, pady=5, sticky='ew')

        # Connection buttons
        self.connect_btn = ttk.Button(config_frame, text=self.trans['connect'], 
                                    command=self.connect_serial, style='Success.TButton')
        self.connect_btn.grid(row=0, column=5, padx=5, pady=5, sticky='ew')
        
        self.disconnect_btn = ttk.Button(config_frame, text=self.trans['disconnect'], 
                                       command=self.disconnect_serial, style='Error.TButton')
        self.disconnect_btn.grid(row=0, column=6, padx=5, pady=5, sticky='ew')

        # Auto Connect button
        self.autoconnect_btn = ttk.Button(config_frame, text=self.trans.get('autoconnect', 'Auto Connect'),
                                          command=self.autoconnect_serial, style='TButton')
        self.autoconnect_btn.grid(row=0, column=7, padx=5, pady=5, sticky='ew')

        # --- Control Panel ---
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill='x', pady=10)
        control_frame.columnconfigure((0, 1), weight=1)

        # Amplitude control
        self.amp_var = tk.IntVar(value=50)
        amp_frame = ttk.LabelFrame(control_frame, text=self.trans['amplitude'])
        amp_frame.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        amp_frame.columnconfigure(0, weight=1)
        
        self.amp_scale = ttk.Scale(amp_frame, from_=0, to=100, orient='horizontal', 
                                 variable=self.amp_var, command=self._safe_set_amp)
        self.amp_scale.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self.amp_entry = ttk.Entry(amp_frame, textvariable=self.amp_var, width=10, 
                                 justify='center', style='TEntry')
        self.amp_entry.grid(row=1, column=0, pady=(0, 10))

        # Frequency control
        self.freq_var = tk.IntVar(value=100)
        freq_frame = ttk.LabelFrame(control_frame, text=self.trans['frequency'])
        freq_frame.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        freq_frame.columnconfigure(0, weight=1)
        
        self.freq_scale = ttk.Scale(freq_frame, from_=1, to=1000, orient='horizontal', 
                                  variable=self.freq_var, command=self._safe_set_freq)
        self.freq_scale.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self.freq_entry = ttk.Entry(freq_frame, textvariable=self.freq_var, width=10, 
                                  justify='center', style='TEntry')
        self.freq_entry.grid(row=1, column=0, pady=(0, 10))

        # Send button
        self.send_btn = ttk.Button(self.main_frame, text=self.trans['transmit'], 
                                 command=self.send_command, 
                                 style='Accent.TButton')
        self.send_btn.pack(fill='x', pady=10, ipady=10)

        # --- Serial Monitor ---
        monitor_frame = ttk.LabelFrame(self.main_frame, text=self.trans['serial_monitor'])
        monitor_frame.pack(fill='both', expand=True, pady=5)
        
        # Text area with custom tags for coloring
        self.uart_text = scrolledtext.ScrolledText(
            monitor_frame, 
            height=10, 
            state='disabled', 
            wrap='word', 
            relief='flat', 
            borderwidth=0,
            font=self.mono_font,
            padx=10,
            pady=10
        )
        self.uart_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure text tags for different message types
        self.uart_text.tag_config('info', foreground=self.theme["secondary"])
        self.uart_text.tag_config('sent', foreground=self.theme["primary"])
        self.uart_text.tag_config('received', foreground=self.theme["success"])
        self.uart_text.tag_config('error', foreground=self.theme["error"])
        self.uart_text.tag_config('warning', foreground=self.theme["warning"])
        self.uart_text.tag_config('system', foreground=self.theme["accent"])

        # --- Console Control Panel ---
        console_ctrl_frame = ttk.Frame(monitor_frame)
        console_ctrl_frame.pack(fill='x', pady=(5, 0))
        
        # Clear terminal button
        self.clear_btn = ttk.Button(console_ctrl_frame, text=self.trans['clear_terminal'], 
                                  command=self.clear_terminal, style='Warning.TButton')
        self.clear_btn.pack(side='left', padx=(0, 10))
        
        # Manual Command Input
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(console_ctrl_frame, textvariable=self.input_var, 
                                   style='TEntry')
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', lambda e: self.send_serial())
        
        self.send_serial_btn = ttk.Button(console_ctrl_frame, text=self.trans['send'], 
                                        command=self.send_serial, style='TButton')
        self.send_serial_btn.pack(side='left')

        # --- Footer ---
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill='x', pady=(10, 0))
        
        # Theme toggle button
        self.mode_btn = ttk.Button(footer_frame, text=self.trans['theme_toggle'], 
                                  command=self.toggle_mode, style='TButton')
        self.mode_btn.pack(side='right')
        
        self.version_label = ttk.Label(footer_frame, text=self.trans['version'], style='Status.TLabel')
        self.version_label.pack(side='left')

        # --- Language Dropdown ---
        self.lang_var = tk.StringVar(value='en')
        lang_menu = ttk.Combobox(footer_frame, values=['en', 'fr'], textvariable=self.lang_var, state='readonly', width=5)
        lang_menu.pack(side='right', padx=(0, 10))
        lang_menu.bind('<<ComboboxSelected>>', self.change_language)

    def change_language(self, event=None):
        self.lang = self.lang_var.get()
        self.trans = TRANSLATIONS[self.lang]
        # Update all visible text
        self.title_label.config(text=self.trans['title'])
        self.status_label.config(text=self.trans['status_disconnected'])
        self.rx_label.config(text=self.trans['rx'].format(count=self.received_count))
        self.tx_label.config(text=self.trans['tx'].format(count=self.sent_count))
        self.latency_label.config(text=self.trans['latency'].format(ms=self.update_interval))
        self.connect_btn.config(text=self.trans['connect'])
        self.disconnect_btn.config(text=self.trans['disconnect'])
        self.send_btn.config(text=self.trans['transmit'])
        self.clear_btn.config(text=self.trans['clear_terminal'])
        self.send_serial_btn.config(text=self.trans['send'])
        self.mode_btn.config(text=self.trans['theme_toggle'])
        self.version_label.config(text=self.trans['version'])
        # Update group/frame labels
        self.main_frame.winfo_children()[2].config(text=self.trans['connection_protocol'])
        self.main_frame.winfo_children()[3].winfo_children()[0].config(text=self.trans['amplitude'])
        self.main_frame.winfo_children()[3].winfo_children()[1].config(text=self.trans['frequency'])
        self.main_frame.winfo_children()[5].config(text=self.trans['serial_monitor'])
        # Update port/baud labels
        config_frame = self.main_frame.winfo_children()[2]
        config_frame.winfo_children()[0].config(text=self.trans['port'])
        config_frame.winfo_children()[3].config(text=self.trans['baudrate'])
        # Update Auto Connect button
        if hasattr(self, 'autoconnect_btn'):
            self.autoconnect_btn.config(text=self.trans.get('autoconnect', 'Auto Connect'))

    def _set_connection_state(self, connected):
        state = 'normal' if connected else 'disabled'
        self.amp_scale.config(state=state)
        self.amp_entry.config(state=state)
        self.freq_scale.config(state=state)
        self.freq_entry.config(state=state)
        self.send_btn.config(state=state)
        self.input_entry.config(state=state)
        self.send_serial_btn.config(state=state)
        self.status_label.config(
            text=self.trans['status_connected'] if connected else self.trans['status_disconnected'],
            foreground=self.theme["success"] if connected else self.theme["error"]
        )

    # --- Core Functionality ---
    def connect_serial(self):
        port, baud = self.port_var.get(), self.baud_var.get()
        if not port or not baud:
            messagebox.showerror(self.trans['connection_error'], self.trans['error_select_port_baud'])
            return
            
        if self.serial_ctrl.connect(port, int(baud)):
            self._log_to_monitor(self.trans['connected_msg'].format(port=port, baud=baud), 'system')
            self._set_connection_state(True)
            # Reset metrics
            self.received_count = 0
            self.sent_count = 0
            self._update_metrics()

    def disconnect_serial(self):
        self.serial_ctrl.disconnect()
        self._log_to_monitor(self.trans['disconnected_msg'], 'system')
        self._set_connection_state(False)

    def send_command(self):
        amp, freq = self.amp_var.get(), self.freq_var.get()
        
        # Validation
        if not (0 <= amp <= 100):
            messagebox.showerror(self.trans['transmission_error'], self.trans['error_amp'])
            return
        if not (1 <= freq <= 1000):
            messagebox.showerror(self.trans['transmission_error'], self.trans['error_freq'])
            return
            
        if self.serial_ctrl.send_amp_freq(amp, freq):
            self._log_to_monitor(self.trans['transmitted'].format(amp=amp, freq=freq), 'sent')
            self.sent_count += 1
            self._update_metrics()
            # Visual feedback
            self.send_btn.config(text=self.trans['transmit_success'])
            self.after(1000, lambda: self.send_btn.config(text=self.trans['transmit']))

    def send_serial(self):
        self.input_entry.update_idletasks()  # Ensure latest value is read
        data = self.input_var.get().strip()
        if data:
            padded = data.rjust(9, '0')[-9:]  # Always 8 chars, pad left with zeros, trim if too long
            if self.serial_ctrl.send(padded + '\n'):
                self._log_to_monitor(self.trans['sent'].format(data=padded), 'sent')
                self.sent_count += 1
                self._update_metrics()
                self.input_var.set('')
                # Visual feedback
                self.send_serial_btn.config(text='✓')
                self.after(500, lambda: self.send_serial_btn.config(text=self.trans['send']))

    def _update_serial_monitor(self):
        """Check for new serial data and update the monitor"""
        current_time = time.time()
        
        # Process all available serial data
        data_lines = self.serial_ctrl.get_data()
        if data_lines:
            for line in data_lines:
                self._log_to_monitor(self.trans['received'].format(line=line), 'received')
                self.received_count += 1
            
            # Update metrics immediately when we receive data
            self._update_metrics()
            self.last_update = current_time
        else:
            # Only update metrics periodically if no new data
            if current_time - self.last_update > 0.5:  # Update every 500ms if no data
                self._update_metrics()
        
        # Schedule next update
        self.after(self.update_interval, self._update_serial_monitor)

    def _update_metrics(self):
        """Update performance metrics display"""
        self.rx_label.config(text=self.trans['rx'].format(count=self.received_count))
        self.tx_label.config(text=self.trans['tx'].format(count=self.sent_count))
        self.latency_label.config(text=self.trans['latency'].format(ms=self.update_interval))

    def _log_to_monitor(self, message, tag='info'):
        """Helper to log messages to the serial monitor text area."""
        self.uart_text.config(state='normal')
        self.uart_text.insert('end', message, tag)
        self.uart_text.see('end')
        self.uart_text.config(state='disabled')

    def clear_terminal(self):
        """Clear the terminal output."""
        self.uart_text.config(state='normal')
        self.uart_text.delete(1.0, 'end')
        self.uart_text.config(state='disabled')
        self._log_to_monitor(self.trans['terminal_cleared_msg'], 'system')
        
        # Visual feedback
        self.clear_btn.config(text=self.trans['terminal_cleared'])
        self.after(1000, lambda: self.clear_btn.config(text=self.trans['clear_terminal']))

    def toggle_mode(self):
        """Toggle between dark and light themes."""
        self.is_dark = not self.is_dark
        self.theme = DARK_THEME if self.is_dark else LIGHT_THEME
        self._setup_styles()
        self._apply_theme()
        self.mode_btn.config(text=self.trans['theme_toggle'])

    def refresh_ports(self):
        """Refresh the list of available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        current_value = self.port_var.get()
        self.port_menu['values'] = ports
        if ports and current_value not in ports:
            self.port_var.set(ports[0])
        elif not ports:
            self.port_var.set('')
        self._log_to_monitor(self.trans['serial_ports_refreshed'], 'system')

    def on_closing(self):
        """Handle application closing"""
        self.serial_ctrl.disconnect()
        self.destroy()

    def _apply_theme(self):
        """Applies theme colors to all widgets."""
        self.configure(bg=self.theme["bg"])
        # Apply to non-ttk widgets
        if hasattr(self, 'uart_text'):
            self.uart_text.configure(
                bg=self.theme["text_area_bg"],
                fg=self.theme["text_area_fg"],
                insertbackground=self.theme["text_insert_bg"]
            )
            # Update text tags
            self.uart_text.tag_config('info', foreground=self.theme["secondary"])
            self.uart_text.tag_config('sent', foreground=self.theme["primary"])
            self.uart_text.tag_config('received', foreground=self.theme["success"])
            self.uart_text.tag_config('error', foreground=self.theme["error"])
            self.uart_text.tag_config('warning', foreground=self.theme["warning"])
            self.uart_text.tag_config('system', foreground=self.theme["accent"])

    def _safe_set_amp(self, v):
        try:
            self.amp_var.set(int(float(v)))
        except (ValueError, TypeError):
            pass

    def _safe_set_freq(self, v):
        try:
            self.freq_var.set(int(float(v)))
        except (ValueError, TypeError):
            pass

    def autoconnect_serial(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        baudrates = ["9600", "19200", "38400", "57600", "115200", "230400", "500000", "1000000", "2000000"]
             
        for port in ports:
            print(f"Trying port: {port}")
            # reversed(baudrates)
           for baud in baudrates:
               try:
                   if self.serial_ctrl.connect(port, int(baud)):
                       self.port_var.set(port)
                       self.baud_var.set(baud)
                       self._log_to_monitor(self.trans['connected_msg'].format(port=port, baud=baud), 'system')
                       self._set_connection_state(True)
                       self.received_count = 0
                       self.sent_count = 0
                       self._update_metrics()
                       return True
               except Exception:
                   continue
        self._log_to_monitor('No available COM port/baudrate for autoconnect\n', 'error')
        return False

if __name__ == '__main__':
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
