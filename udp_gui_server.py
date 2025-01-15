import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import os
import re

CONFIG_FILE = "config.xml"
DATA_FILE = "server_messages.data"

class UDPServer:
    def __init__(self):
        self.server_socket = None
        self.clients_dict = {}
        self.server_stop_event = threading.Event()
        self.clients_lock = threading.Lock()
        self.initialize_config()

    def initialize_config(self):
        
        if not os.path.exists(CONFIG_FILE):
            root = ET.Element("clients")
            tree = ET.ElementTree(root)
            tree.write(CONFIG_FILE)

    def add_client_to_config(self, client_id, ip, port):
         
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        existing_client = root.find(f"./client[@id='{client_id}']")
        if existing_client is not None:
            existing_client.set("ip", ip)
            existing_client.set("port", str(port))
        else:
            ET.SubElement(root, "client", id=client_id, ip=ip, port=str(port))

        tree.write(CONFIG_FILE)
        print(f"Client {client_id} added/updated in the configuration file.")

    def get_clients_from_config(self):
         
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()
        return [(client.attrib["id"], client.attrib["ip"], int(client.attrib["port"])) for client in root.findall("client")]

    def start_server(self, ip, port):
         
        if self.server_socket:
            print("Server is already running.")
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((ip, port))
        self.server_stop_event.clear()

        with self.clients_lock:
            self.clients_dict.clear()
            clients = self.get_clients_from_config()
            self.clients_dict.update({client_id: (client_ip, client_port) for client_id, client_ip, client_port in clients})

        threading.Thread(target=self.handle_messages, daemon=True).start()
        print(f"Server started on {ip}:{port}")

    def handle_messages(self):
         
        try:
            with open(DATA_FILE, "a") as data_file:
                while not self.server_stop_event.is_set():
                    try:
                        data, addr = self.server_socket.recvfrom(1024)
                        message = data.decode()
                        print(f"Received from {addr}: {message}")
                        self.display_message(addr, message)
                        data_file.write(f"{addr}: {message}\n")
                    except socket.error as e:
                        if not self.server_stop_event.is_set():
                            print(f"Socket error: {e}")
                        break
        except Exception as e:
            print(f"Unexpected error in message handler: {e}")

    def display_message(self, addr, message):
         
        messages_textbox.config(state="normal")
        messages_textbox.insert("end", f"From {addr}: {message}\n")
        messages_textbox.config(state="disabled")

    def stop_server(self):
         
        if not self.server_stop_event.is_set():
            self.server_stop_event.set()
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            print("Server stopped.")

    def create_gui(self):
        
        def validate_ip(ip):
             
            pattern = r"^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\." \
                      r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\." \
                      r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\." \
                      r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$"
            return re.match(pattern, ip) is not None

        def validate_port(port):
             
            return port.isdigit() and 1 <= int(port) <= 65535

        def start_server_action():
            ip = server_ip_entry.get()
            port = server_port_entry.get()
            if not validate_ip(ip):
                messagebox.showerror("Invalid Input", "Please enter a valid IP address.")
                return
            if not validate_port(port):
                messagebox.showerror("Invalid Input", "Please enter a valid port number (1-65535).")
                return
            self.start_server(ip, int(port))
            refresh_clients_menu()
            status_label.config(text="Server is Running", fg="green")

        def stop_server_action():
            self.stop_server()
            status_label.config(text="Server Stopped", fg="red")

        def add_client_action():
            client_id = client_id_entry.get()
            ip = client_ip_entry.get()
            port = client_port_entry.get()
            if not client_id.strip():
                messagebox.showerror("Invalid Input", "Client ID cannot be empty.")
                return
            if not validate_ip(ip):
                messagebox.showerror("Invalid Input", "Please enter a valid IP address.")
                return
            if not validate_port(port):
                messagebox.showerror("Invalid Input", "Please enter a valid port number (1-65535).")
                return
            self.add_client_to_config(client_id, ip, int(port))
            refresh_clients_menu()
            status_label.config(text=f"Client {client_id} added/updated", fg="blue")

        def refresh_clients_menu():
             
            clients = self.get_clients_from_config()
            self.clients_dict.update({client_id: (ip, port) for client_id, ip, port in clients})
            selected_client.set("Broadcast")
            clients_menu["menu"].delete(0, "end")
            clients_menu["menu"].add_command(label="Broadcast", command=lambda: selected_client.set("Broadcast"))
            for client_id in self.clients_dict.keys():
                clients_menu["menu"].add_command(label=client_id, command=lambda c=client_id: selected_client.set(c))

        def send_message_action():
             
            target_client = selected_client.get()
            message = message_entry.get()
            if not message.strip():
                messagebox.showerror("Invalid Input", "Message cannot be empty.")
                return
            message_bytes = f"{target_client}:{message}".encode()
            with self.clients_lock:
                if target_client == "Broadcast":
                    for client_addr in self.clients_dict.values():
                        self.server_socket.sendto(message_bytes, client_addr)
                    messagebox.showinfo(title="Broadcast Message", message="Message sent to all clients.")
                elif target_client in self.clients_dict:
                    self.server_socket.sendto(message_bytes, self.clients_dict[target_client])
                    messagebox.showinfo(title="Message Sent", message=f"Message sent to client {target_client}.")
                else:
                    messagebox.showerror(title="Error", message=f"Client {target_client} not found.")

        root = tk.Tk()
        root.title("UDP Server and Client Manager")
        root.geometry("800x600")

        tk.Label(root, text="Server IP:").grid(row=0, column=0, pady=5)
        server_ip_entry = tk.Entry(root)
        server_ip_entry.grid(row=0, column=1, pady=5)

        tk.Label(root, text="Server Port:").grid(row=1, column=0, pady=5)
        server_port_entry = tk.Entry(root)
        server_port_entry.grid(row=1, column=1, pady=5)

        ttk.Button(root, text="Start Server", command=start_server_action).grid(row=2, column=0, pady=5)
        ttk.Button(root, text="Stop Server", command=stop_server_action).grid(row=2, column=1, pady=5)

        status_label = tk.Label(root, text="Server Stopped", fg="red", font=("Helvetica", 12, "bold"))
        status_label.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Label(root, text="Client ID:").grid(row=4, column=0, pady=5)
        client_id_entry = tk.Entry(root)
        client_id_entry.grid(row=4, column=1, pady=5)

        tk.Label(root, text="Client IP:").grid(row=5, column=0, pady=5)
        client_ip_entry = tk.Entry(root)
        client_ip_entry.grid(row=5, column=1, pady=5)

        tk.Label(root, text="Client Port:").grid(row=6, column=0, pady=5)
        client_port_entry = tk.Entry(root)
        client_port_entry.grid(row=6, column=1, pady=5)

        ttk.Button(root, text="Add Client", command=add_client_action).grid(row=7, column=0, columnspan=2, pady=10)

        tk.Label(root, text="Select Client:").grid(row=8, column=0, pady=5)
        selected_client = tk.StringVar(value="Broadcast")
        clients_menu = ttk.OptionMenu(root, selected_client, "Broadcast", *[])
        clients_menu.grid(row=8, column=1, pady=5)

        tk.Label(root, text="Message:").grid(row=9, column=0, pady=5)
        message_entry = tk.Entry(root)
        message_entry.grid(row=9, column=1, pady=5)

        ttk.Button(root, text="Send Message", command=send_message_action).grid(row=10, column=0, columnspan=2, pady=10)

        tk.Label(root, text="Messages Received:").grid(row=11, column=0, pady=10)
        global messages_textbox
        messages_textbox = tk.Text(root, height=15, width=80, state="disabled")
        messages_textbox.grid(row=12, column=0, columnspan=2)

        root.mainloop()


if __name__ == "__main__":
    server = UDPServer()
    server.create_gui()
