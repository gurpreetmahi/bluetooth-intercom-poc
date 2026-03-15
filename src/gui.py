"""
GUI - Tkinter-based graphical interface for Bluetooth Intercom
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from threading import Thread


class IntercomGUI:
    """Main GUI application window"""
    
    def __init__(self, config: dict, bluetooth_manager, audio_router):
        self.config = config
        self.bluetooth_manager = bluetooth_manager
        self.audio_router = audio_router
        self.logger = logging.getLogger(__name__)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Bluetooth Intercom POC")
        
        # Parse window size from config
        size = config['gui']['window_size']
        self.root.geometry(size)
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Build UI
        self._build_ui()
        
        # Bind keyboard events
        if config['ptt']['enabled']:
            self._bind_ptt_key()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _build_ui(self):
        """Build the user interface"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Bluetooth Intercom Gateway", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Device A Section
        device_a_frame = ttk.LabelFrame(main_frame, text="Device A (Person A)", padding="10")
        device_a_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.device_a_combo = ttk.Combobox(device_a_frame, width=30, state='readonly')
        self.device_a_combo.grid(row=0, column=0, pady=5)
        
        self.device_a_status = ttk.Label(device_a_frame, text="Status: Disconnected", 
                                         foreground="red")
        self.device_a_status.grid(row=1, column=0, pady=5)
        
        self.device_a_connect_btn = ttk.Button(device_a_frame, text="Connect", 
                                               command=self._connect_device_a)
        self.device_a_connect_btn.grid(row=2, column=0, pady=5)
        
        # Device B Section
        device_b_frame = ttk.LabelFrame(main_frame, text="Device B (Person B)", padding="10")
        device_b_frame.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.device_b_combo = ttk.Combobox(device_b_frame, width=30, state='readonly')
        self.device_b_combo.grid(row=0, column=0, pady=5)
        
        self.device_b_status = ttk.Label(device_b_frame, text="Status: Disconnected", 
                                         foreground="red")
        self.device_b_status.grid(row=1, column=0, pady=5)
        
        self.device_b_connect_btn = ttk.Button(device_b_frame, text="Connect", 
                                               command=self._connect_device_b)
        self.device_b_connect_btn.grid(row=2, column=0, pady=5)
        
        # Control Section
        control_frame = ttk.LabelFrame(main_frame, text="Intercom Control", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.discover_btn = ttk.Button(control_frame, text="Discover Devices", 
                                       command=self._discover_devices)
        self.discover_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="Start Intercom", 
                                    command=self._start_intercom, state='disabled')
        self.start_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Intercom", 
                                   command=self._stop_intercom, state='disabled')
        self.stop_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # PTT Button (if enabled)
        if self.config['ptt']['enabled']:
            self.ptt_btn = ttk.Button(control_frame, text="Push to Talk (SPACE)", 
                                     state='disabled')
            self.ptt_btn.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.status_text = tk.Text(status_frame, height=8, width=60, state='disabled')
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(status_frame, orient='vertical', 
                                 command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text['yscrollcommand'] = scrollbar.set
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def _bind_ptt_key(self):
        """Bind Push-To-Talk keyboard key"""
        key = self.config['ptt']['key']
        
        # Bind key press and release
        self.root.bind(f'<KeyPress-{key}>', lambda e: self._ptt_pressed())
        self.root.bind(f'<KeyRelease-{key}>', lambda e: self._ptt_released())
    
    def _discover_devices(self):
        """Discover Bluetooth devices"""
        self._log_status("Discovering Bluetooth devices...")
        
        def discover_thread():
            devices = self.bluetooth_manager.discover_devices()
            
            # Update UI on main thread
            self.root.after(0, lambda: self._update_device_list(devices))
        
        Thread(target=discover_thread, daemon=True).start()
    
    def _update_device_list(self, devices):
        """Update device dropdown lists"""
        device_names = [f"{d.alias} ({d.address})" for d in devices]
        
        self.device_a_combo['values'] = device_names
        self.device_b_combo['values'] = device_names
        
        if devices:
            self._log_status(f"Found {len(devices)} device(s)")
        else:
            self._log_status("No devices found")
    
    def _connect_device_a(self):
        """Connect to Device A"""
        selection = self.device_a_combo.current()
        if selection < 0:
            messagebox.showwarning("No Selection", "Please select a device first")
            return
        
        device = self.bluetooth_manager.devices[selection]
        self._log_status(f"Connecting to {device.alias}...")
        
        if self.bluetooth_manager.set_device_a(device):
            self.device_a_status.config(text="Status: Connected", foreground="green")
            self._check_ready_to_start()
        else:
            self.device_a_status.config(text="Status: Error", foreground="red")
    
    def _connect_device_b(self):
        """Connect to Device B"""
        selection = self.device_b_combo.current()
        if selection < 0:
            messagebox.showwarning("No Selection", "Please select a device first")
            return
        
        device = self.bluetooth_manager.devices[selection]
        self._log_status(f"Connecting to {device.alias}...")
        
        if self.bluetooth_manager.set_device_b(device):
            self.device_b_status.config(text="Status: Connected", foreground="green")
            self._check_ready_to_start()
        else:
            self.device_b_status.config(text="Status: Error", foreground="red")
    
    def _check_ready_to_start(self):
        """Check if both devices are connected and enable start button"""
        if (self.bluetooth_manager.device_a and 
            self.bluetooth_manager.device_b and
            len(self.bluetooth_manager.get_connected_devices()) == 2):
            self.start_btn.config(state='normal')
            self._log_status("Ready to start intercom!")
    
    def _start_intercom(self):
        """Start the intercom"""
        self._log_status("Starting intercom...")
        
        # TODO: Setup audio streams with actual device indices
        # For now, this is a placeholder
        
        self.audio_router.start_routing()
        
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        if self.config['ptt']['enabled']:
            self.ptt_btn.config(state='normal')
        
        self._log_status("Intercom active!")
    
    def _stop_intercom(self):
        """Stop the intercom"""
        self._log_status("Stopping intercom...")
        
        self.audio_router.stop_routing()
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if self.config['ptt']['enabled']:
            self.ptt_btn.config(state='disabled')
        
        self._log_status("Intercom stopped")
    
    def _ptt_pressed(self):
        """Handle PTT key press"""
        self.audio_router.set_ptt(True)
        if hasattr(self, 'ptt_btn'):
            self.ptt_btn.config(text="🔴 TRANSMITTING")
    
    def _ptt_released(self):
        """Handle PTT key release"""
        self.audio_router.set_ptt(False)
        if hasattr(self, 'ptt_btn'):
            self.ptt_btn.config(text="Push to Talk (SPACE)")
    
    def _log_status(self, message: str):
        """Log message to status text box"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        
        self.logger.info(message)
    
    def _on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.audio_router.cleanup()
            self.bluetooth_manager.cleanup()
            self.root.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.logger.info("Starting GUI")
        self.root.mainloop()
