import tkinter as tk
from tkinter import ttk
import socket
import threading
import time


class MainApp:

    def __init__(self, root, wisun_port, arduino_port):

        self.root = root

        self.root.title("Wi-SUN EV Charger")

        self.root.attributes('-fullscreen', True)

        self.root.configure(bg="#0f172a")

        # =====================================================
        # SOCKET
        # =====================================================

        self.arduino_socks = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.arduino_socks.connect(
            (socket.gethostname(), arduino_port)
        )

        # =====================================================
        # VARIABLES
        # =====================================================

        self.ble_status = tk.StringVar(value="WAITING")

        self.wisun_status = tk.StringVar(value="CONNECTED")

        self.charger_status = tk.StringVar(value="AVAILABLE")

        self.fault_status = tk.StringVar(value="NO FAULT")

        # =====================================================
        # HEADER
        # =====================================================

        header = tk.Frame(root, bg="#111827", height=80)

        header.pack(fill="x")

        tk.Label(
            header,
            text="⚡ Wi-SUN Smart EV Charger",
            font=("Helvetica", 30, "bold"),
            fg="white",
            bg="#111827"
        ).pack(pady=20)

        # =====================================================
        # MAIN FRAME
        # =====================================================

        main = tk.Frame(root, bg="#0f172a")

        main.pack(fill="both", expand=True)

        # =====================================================
        # LEFT PANEL
        # =====================================================

        left = tk.Frame(main, bg="#1e293b", width=400)

        left.pack(side="left", fill="y", padx=20, pady=20)

        self.create_card(left, "BLE STATUS", self.ble_status)

        self.create_card(left, "Wi-SUN STATUS", self.wisun_status)

        self.create_card(left, "CHARGER STATUS", self.charger_status)

        self.create_card(left, "FAULT STATUS", self.fault_status)

        # =====================================================
        # RIGHT PANEL
        # =====================================================

        right = tk.Frame(main, bg="#111827")

        right.pack(side="right", fill="both", expand=True)

        self.main_label = tk.Label(
            right,
            text="CHARGER AVAILABLE",
            font=("Helvetica", 35, "bold"),
            fg="#22c55e",
            bg="#111827"
        )

        self.main_label.pack(pady=80)

        # =====================================================
        # PROGRESS BAR
        # =====================================================

        self.progress = ttk.Progressbar(
            right,
            orient="horizontal",
            length=700,
            mode="determinate"
        )

        self.progress.pack(pady=40)

        self.percent = tk.Label(
            right,
            text="0%",
            font=("Helvetica", 24, "bold"),
            fg="white",
            bg="#111827"
        )

        self.percent.pack()

        # =====================================================
        # CLOCK
        # =====================================================

        self.clock = tk.Label(
            root,
            text="",
            font=("Helvetica", 16),
            fg="white",
            bg="#111827"
        )

        self.clock.pack(fill="x")

        self.update_clock()

        # =====================================================
        # START THREAD
        # =====================================================

        threading.Thread(
            target=self.read_arduino,
            daemon=True
        ).start()

    # =========================================================
    # CARD
    # =========================================================

    def create_card(self, parent, title, variable):

        frame = tk.Frame(parent, bg="#334155")

        frame.pack(fill="x", padx=15, pady=15)

        tk.Label(
            frame,
            text=title,
            font=("Helvetica", 14),
            fg="#cbd5e1",
            bg="#334155"
        ).pack(anchor="w", padx=10, pady=5)

        tk.Label(
            frame,
            textvariable=variable,
            font=("Helvetica", 22, "bold"),
            fg="white",
            bg="#334155"
        ).pack(anchor="w", padx=10, pady=10)

    # =========================================================
    # CLOCK
    # =========================================================

    def update_clock(self):

        current = time.strftime("%d-%m-%Y    %H:%M:%S")

        self.clock.config(text=current)

        self.root.after(1000, self.update_clock)

    # =========================================================
    # PROGRESS
    # =========================================================

    def animate_progress(self):

        for i in range(101):

            self.progress["value"] = i

            self.percent.config(text=f"{i}%")

            self.root.update()

            time.sleep(0.05)

    # =========================================================
    # SOCKET READER
    # =========================================================

    def read_arduino(self):

        while True:

            try:

                msg = self.arduino_socks.recv(
                    1024
                ).decode().strip()

                print("Received:", msg)

                # =============================================

                if "CONNECTED" in msg:

                    self.ble_status.set("CONNECTED")

                    self.main_label.config(
                        text="BLE DEVICE CONNECTED",
                        fg="#22c55e"
                    )

                # =============================================

                elif "CHARGING" in msg:

                    self.charger_status.set("CHARGING")

                    self.main_label.config(
                        text="EV CHARGING",
                        fg="#facc15"
                    )

                    threading.Thread(
                        target=self.animate_progress,
                        daemon=True
                    ).start()

                # =============================================

                elif "AVAILABLE" in msg:

                    self.charger_status.set("AVAILABLE")

                    self.main_label.config(
                        text="CHARGER AVAILABLE",
                        fg="#22c55e"
                    )

                    self.progress["value"] = 0

                    self.percent.config(text="0%")

                # =============================================

                elif "FAULT" in msg:

                    self.fault_status.set("FAULT DETECTED")

                    self.main_label.config(
                        text="FAULT DETECTED",
                        fg="#ef4444"
                    )

                # =============================================

                elif "DISCONNECTED" in msg:

                    self.ble_status.set("DISCONNECTED")

                    self.main_label.config(
                        text="BLE DEVICE DISCONNECTED",
                        fg="#ef4444"
                    )

            except Exception as e:

                print("Socket Error:", e)

                break