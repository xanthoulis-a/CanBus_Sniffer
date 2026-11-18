import csv
import queue
import serial
import serial.tools.list_ports
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class CanSnifferGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("DRT Formula Student - CAN Sniffer Suite")
        self.root.geometry("1280x760")

        self.serial_port = None
        self.is_running = False
        self.is_paused = False
        self.packet_count = 0
        self.raw_data_log = []
        self.data_queue = queue.Queue(maxsize=3000)
        self.active_search_filters = set()

        top_frame = ttk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=8)

        conn_frame = ttk.LabelFrame(top_frame, text="Hardware Link")
        conn_frame.pack(side="left", fill="y", padx=(0, 8))

        ttk.Label(conn_frame, text="Port:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.port_combobox = ttk.Combobox(
            conn_frame,
            values=self.get_filtered_ports(),
            width=18,
            state="readonly",
        )
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5)

        self.refresh_btn = ttk.Button(
            conn_frame, text="Refresh", width=7, command=self.refresh_ports
        )
        self.refresh_btn.grid(row=0, column=2, padx=2, pady=5)

        ttk.Label(conn_frame, text="Baud:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.baud_combobox = ttk.Combobox(
            conn_frame,
            values=["115200", "230400", "921600", "2000000"],
            width=10,
            state="readonly",
        )
        self.baud_combobox.set("115200")
        self.baud_combobox.grid(
            row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5
        )

        self.connect_btn = ttk.Button(
            conn_frame, text="Connect", command=self.toggle_connection
        )
        self.connect_btn.grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5
        )

        ctrl_frame = ttk.LabelFrame(top_frame, text="Session Controls & Filters")
        ctrl_frame.pack(side="left", fill="both", expand=True, padx=(0, 0))

        f_row1 = ttk.Frame(ctrl_frame)
        f_row1.pack(fill="x", padx=5, pady=5)

        self.clear_btn = ttk.Button(
            f_row1, text="Clear Table", command=self.clear_table
        )
        self.clear_btn.pack(side="left", padx=3)

        self.pause_btn = ttk.Button(
            f_row1, text="Pause Feed", command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=3)

        self.export_btn = ttk.Button(
            f_row1, text="Export CSV", command=self.export_csv
        )
        self.export_btn.pack(side="left", padx=3)

        self.status_label = ttk.Label(
            f_row1,
            text="Status: Disconnected",
            foreground="red",
            font=("Arial", 10, "bold"),
        )
        self.status_label.pack(side="right", padx=10)

        f_row2 = ttk.Frame(ctrl_frame)
        f_row2.pack(fill="x", padx=5, pady=5)

        f_row3 = ttk.Frame(ctrl_frame)
        f_row3.pack(fill="x", padx=5, pady=5)

        ttk.Label(f_row2, text="Filter Subsystem:").pack(side="left", padx=3)
        self.filter_subsys_combo = ttk.Combobox(
            f_row2,
            values=[
                "All Subsystems",
                "VCU (Vehicle Control)",
                "Inverter / Motor",
                "BMS",
                "ACU",
                "CB DL (Control Box Datalogger)",
                "Aero DL (Aero Datalogger)",
                "General Telemetry",
            ],
            width=20,
            state="readonly",
        )
        self.filter_subsys_combo.set("All Subsystems")
        self.filter_subsys_combo.pack(side="left", padx=3)
        self.filter_subsys_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.apply_filter()
        )

        ttk.Label(f_row2, text="Search ID:").pack(side="left", padx=(15, 3))
        self.search_entry = ttk.Entry(f_row2, width=12)
        self.search_entry.pack(side="left", padx=3)
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search_key_release(e))

        # Row 3: Active ID filter tags display frame matching your screenshot
        ttk.Label(f_row3, text="Searching ID/ID's:").pack(side="left", padx=3, pady=5)

        self.badge_frame = ttk.Frame(f_row3)
        self.badge_frame.pack(side="left", fill="x", expand=True, padx=5)

        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = (
            "Timestamp",
            "CanID",
            "Subsystem",
            "DLC",
            "PayloadHex",
            "DecodedSignals",
        )
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )

        self.tree.heading("Timestamp", text="Time (s)")
        self.tree.heading("CanID", text="CAN ID")
        self.tree.heading("Subsystem", text="Subsystem / Device")
        self.tree.heading("DLC", text="DLC")
        self.tree.heading("PayloadHex", text="Raw Payload (Hex)")
        self.tree.heading("DecodedSignals", text="Decoded Signals / Parameters")

        self.tree.column("Timestamp", width=90, anchor="center")
        self.tree.column("CanID", width=80, anchor="center")
        self.tree.column("Subsystem", width=170, anchor="w")
        self.tree.column("DLC", width=50, anchor="center")
        self.tree.column("PayloadHex", width=220, anchor="w")
        self.tree.column("DecodedSignals", width=510, anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        footer_frame = ttk.Frame(root)
        footer_frame.pack(fill="x", padx=10, pady=5)
        self.counter_label = ttk.Label(
            footer_frame,
            text="Packets Captured: 0 | Queue Health: Nominal | Mode: Live",
        )
        self.counter_label.pack(side="left")

        self.all_captured_records = []
        self.process_queue()

    def get_filtered_ports(self):
        valid_ports = []
        ports = serial.tools.list_ports.comports()
        excluded_keywords = [
            "bluetooth",
            "audio",
            "headphone",
            "airpods",
            "handsfree",
            "wireless",
            "iphone",
            "phone",
            "speaker",
        ]
        for p in ports:
            desc_lower = p.description.lower()
            device_lower = p.device.lower()
            hwid_lower = str(p.hwid).lower()
            if any(
                    ex in desc_lower or ex in device_lower or ex in hwid_lower
                    for ex in excluded_keywords
            ):
                continue
            is_valid_usb = any(
                keyword in desc_lower or keyword in device_lower or keyword in hwid_lower
                for keyword in [
                    "usbmodem",
                    "usbserial",
                    "stm32",
                    "cp210",
                    "ftdi",
                    "ch340",
                    "acm",
                    "usb",
                ]
            )
            if is_valid_usb:
                valid_ports.append(p.device)
        if not valid_ports:
            for p in ports:
                desc_lower = p.description.lower()
                device_lower = p.device.lower()
                if not any(
                        ex in desc_lower or ex in device_lower for ex in excluded_keywords
                ):
                    valid_ports.append(p.device)
        return valid_ports

    def refresh_ports(self):
        self.root.update_idletasks()
        ports = self.get_filtered_ports()
        self.port_combobox["values"] = ports
        if ports:
            self.port_combobox.current(0)
        else:
            self.port_combobox.set("")

    def toggle_connection(self):
        self.root.update_idletasks()
        if not self.is_running:
            port = self.port_combobox.get()
            baud = int(self.baud_combobox.get())
            if not port:
                messagebox.showerror(
                    "Error",
                    "No valid CAN sniffer port detected/selected. Check your USB connection.",
                )
                return
            try:
                self.serial_port = serial.Serial(port, baud, timeout=0.05)
                self.is_running = True
                self.connect_btn.config(text="Disconnect")
                self.status_label.config(text="Status: Connected", foreground="green")
                self.reader_thread = threading.Thread(
                    target=self.serial_read_loop, daemon=True
                )
                self.reader_thread.start()
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
        else:
            self.is_running = False
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Status: Disconnected", foreground="red")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="Resume Feed")
            self.status_label.config(text="Status: Paused", foreground="orange")
        else:
            self.pause_btn.config(text="Pause Feed")
            self.status_label.config(text="Status: Connected", foreground="green")

    def serial_read_loop(self):
        start_time = time.time()
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    line = (
                        self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                    )
                    if line:
                        timestamp = time.time() - start_time
                        if self.data_queue.full():
                            try:
                                self.data_queue.get_nowait()
                            except queue.Empty:
                                pass
                        self.data_queue.put((timestamp, line))
                else:
                    time.sleep(0.002)
            except Exception:
                self.is_running = False
                break

    def process_queue(self):
        processed = 0
        try:
            while not self.data_queue.empty() and processed < 50:
                timestamp, line = self.data_queue.get_nowait()
                self.parse_and_store_record(timestamp, line)
                processed += 1
        except queue.Empty:
            pass
        self.root.after(20, self.process_queue)

    def parse_and_store_record(self, timestamp, line):
        try:
            parts = line.split()
            if len(parts) < 2:
                return
            can_id_str = parts[0]
            dlc = parts[1]
            raw_bytes = [int(b) for b in parts[2:]]
            hex_str = " ".join([f"0x{b:02X}" for b in raw_bytes])
            subsystem, decoded_text = self.decode_can_frame(can_id_str, raw_bytes)

            self.packet_count += 1
            record = {
                "timestamp": f"{timestamp:.3f}",
                "can_id": can_id_str,
                "subsystem": subsystem,
                "dlc": dlc,
                "hex_payload": hex_str,
                "decoded": decoded_text,
            }

            self.all_captured_records.append(record)
            self.raw_data_log.append([
                record["timestamp"],
                record["can_id"],
                record["subsystem"],
                record["dlc"],
                record["hex_payload"],
                record["decoded"],
            ])

            if not self.is_paused:
                self.check_and_insert_tree(record)

            self.counter_label.config(
                text=(
                    f"Packets Captured: {self.packet_count} | Queue Size:"
                    f" {self.data_queue.qsize()} | Mode:"
                    f" {'Paused' if self.is_paused else 'Live'}"
                )
            )

            if len(self.all_captured_records) > 5000:
                self.all_captured_records.pop(0)
        except Exception:
            pass

    def check_and_insert_tree(self, record):
        selected_subsys = self.filter_subsys_combo.get()
        search_query = self.search_entry.get().strip().lower()

        if (
                selected_subsys != "All Subsystems"
                and selected_subsys not in record["subsystem"]
        ):
            return
        if search_query and search_query not in record["can_id"].lower():
            return

        self.tree.insert(
            "",
            0,
            values=(
                record["timestamp"],
                record["can_id"],
                record["subsystem"],
                record["dlc"],
                record["hex_payload"],
                record["decoded"],
            ),
        )

        if len(self.tree.get_children()) > 500:
            self.tree.delete(self.tree.get_children()[-1])

    def on_search_key_release(self, event):
        query = self.search_entry.get().strip()
        if query:
            self.active_search_filters.add(query)
        else:
            self.active_search_filters.clear()

        self.update_filter_badges()
        self.apply_filter()

    def update_filter_badges(self):
        for widget in self.badge_frame.winfo_children():
            widget.destroy()

        for fid in sorted(self.active_search_filters):
            badge_btn = tk.Button(
                self.badge_frame,
                text=f"{fid} ✕",
                bg="#1f2937",
                fg="#38bdf8",
                activebackground="#7f1d1d",
                activeforeground="#fca5a5",
                relief="flat",
                font=("Courier", 10, "bold"),
                command=lambda f=fid: self.remove_search_filter(f)
            )
            badge_btn.pack(side="left", padx=2, pady=2)

    def remove_search_filter(self, fid):
        self.active_search_filters.discard(fid)
        if fid in self.search_entry.get():
            self.search_entry.delete(0, tk.END)
        self.update_filter_badges()
        self.apply_filter()

    def apply_filter(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for record in reversed(self.all_captured_records):
            self.check_and_insert_tree(record)

    def decode_can_frame(self, can_id_str, data):
        try:
            if can_id_str.startswith("0x") or can_id_str.startswith("0X"):
                can_id = int(can_id_str, 16)
            else:
                can_id = int(can_id_str)
        except ValueError:
            return "Unknown", "Format Error"

        if can_id == 0x350:
            brake = data[0] if len(data) > 0 else 0
            accel = data[1] if len(data) > 1 else 0
            return "VCU (Vehicle Control)", f"Brake Pedal: {brake}%, Accel Pedal: {accel}%"

        elif can_id == 0x181:
            val_id = data[0] if len(data) > 0 else 0
            return "Inverter / Motor", f"Value ID: {val_id}, Payload: {' '.join([f'0x{b:02X}' for b in data])}"

        elif can_id == 0x300 or (0x521 <= can_id <= 0x528) or (0x700 <= can_id <= 0x701):
            return "BMS / ACU (Accumulator)", f"Accumulator Data: {' '.join([f'0x{b:02X}' for b in data])}"

        elif can_id == 0x400 or 0x450 <= can_id <= 0x451 or can_id == 0x650:
            return "CB DL (Control Box Datalogger)", f"CB DL Payload: {' '.join([f'0x{b:02X}' for b in data])}"

        elif 0x601 <= can_id <= 0x603:
            return "Aero DL (Aero Datalogger)", f"Aero Sensor Data: {' '.join([f'0x{b:02X}' for b in data])}"

        else:
            return "General Telemetry", f"Payload: {' '.join([str(b) for b in data])}"

    def clear_table(self):
        self.root.update_idletasks()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.packet_count = 0
        self.raw_data_log.clear()
        self.all_captured_records.clear()
        self.active_search_filters.clear()
        self.search_entry.delete(0, tk.END)
        self.update_filter_badges()
        self.counter_label.config(
            text="Packets Captured: 0 | Queue Health: Nominal | Mode: Live"
        )

    def export_csv(self):
        self.root.update_idletasks()
        if not self.raw_data_log:
            messagebox.showwarning(
                "Export Warning", "No telemetry data captured to export."
            )
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            try:
                with open(file_path, mode="w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Timestamp (s)",
                        "CAN ID",
                        "Subsystem",
                        "DLC",
                        "Payload Hex",
                        "Decoded Signals",
                    ])
                    writer.writerows(self.raw_data_log)
                messagebox.showinfo(
                    "Success", f"CSV export completed successfully:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Export Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = CanSnifferGUI(root)
    root.mainloop()o