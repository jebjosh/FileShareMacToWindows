import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import os
import time

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Program")
        self.root.geometry("500x400")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Server tab
        self.server_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.server_frame, text="Server")
        
        # Create Client tab
        self.client_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.client_frame, text="Client")
        
        # Server variables
        self.server_socket = None
        self.server_thread = None
        self.is_server_running = False
        
        # Client variables
        self.client_socket = None
        self.client_thread = None
        self.is_client_connected = False
        
        self.setup_server_tab()
        self.setup_client_tab()
        
    def setup_server_tab(self):
        # Server controls
        server_frame = ttk.LabelFrame(self.server_frame, text="Server Controls")
        server_frame.pack(fill='x', padx=10, pady=5)
        
        self.server_status = tk.StringVar(value="Server Stopped")
        status_label = ttk.Label(server_frame, textvariable=self.server_status)
        status_label.pack(pady=5)
        
        self.server_port = tk.StringVar(value="12345")
        port_frame = ttk.Frame(server_frame)
        port_frame.pack(pady=5)
        ttk.Label(port_frame, text="Port:").pack(side='left')
        ttk.Entry(port_frame, textvariable=self.server_port, width=10).pack(side='left', padx=5)
        
        self.start_server_btn = ttk.Button(server_frame, text="Start Server", command=self.start_server)
        self.start_server_btn.pack(pady=5)
        
        self.stop_server_btn = ttk.Button(server_frame, text="Stop Server", command=self.stop_server, state='disabled')
        self.stop_server_btn.pack(pady=5)
        
        # Server log
        log_frame = ttk.LabelFrame(self.server_frame, text="Server Log")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.server_log = tk.Text(log_frame, height=10)
        self.server_log.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.server_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.server_log.configure(yscrollcommand=scrollbar.set)
        
    def setup_client_tab(self):
        # Client controls
        client_frame = ttk.LabelFrame(self.client_frame, text="Client Controls")
        client_frame.pack(fill='x', padx=10, pady=5)
        
        self.client_status = tk.StringVar(value="Client Disconnected")
        status_label = ttk.Label(client_frame, textvariable=self.client_status)
        status_label.pack(pady=5)
        
        # Connection settings
        conn_frame = ttk.Frame(client_frame)
        conn_frame.pack(pady=5)
        
        ttk.Label(conn_frame, text="IP Address:").pack(side='left')
        self.client_ip = tk.StringVar(value="192.168.1.100")  # Change this to your PC's IP
        ttk.Entry(conn_frame, textvariable=self.client_ip, width=15).pack(side='left', padx=5)
        
        ttk.Label(conn_frame, text="Port:").pack(side='left')
        self.client_port = tk.StringVar(value="12345")
        ttk.Entry(conn_frame, textvariable=self.client_port, width=10).pack(side='left', padx=5)
        
        self.connect_btn = ttk.Button(client_frame, text="Connect", command=self.connect_to_server)
        self.connect_btn.pack(pady=5)
        
        self.disconnect_btn = ttk.Button(client_frame, text="Disconnect", command=self.disconnect_from_server, state='disabled')
        self.disconnect_btn.pack(pady=5)
        
        # File selection
        file_frame = ttk.LabelFrame(client_frame, text="File Transfer")
        file_frame.pack(fill='x', padx=10, pady=5)
        
        self.selected_file = tk.StringVar()
        file_btn = ttk.Button(file_frame, text="Select File", command=self.select_file)
        file_btn.pack(pady=5)
        
        file_label = ttk.Label(file_frame, textvariable=self.selected_file)
        file_label.pack(pady=5)
        
        self.send_file_btn = ttk.Button(file_frame, text="Send File", command=self.send_file, state='disabled')
        self.send_file_btn.pack(pady=5)
        
        # Client log
        log_frame = ttk.LabelFrame(self.client_frame, text="Client Log")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.client_log = tk.Text(log_frame, height=10)
        self.client_log.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.client_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.client_log.configure(yscrollcommand=scrollbar.set)
        
    def log_server(self, message):
        self.server_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.server_log.see(tk.END)
        
    def log_client(self, message):
        self.client_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.client_log.see(tk.END)
        
    def start_server(self):
        try:
            port = int(self.server_port.get())
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            self.is_server_running = True
            
            self.start_server_btn.config(state='disabled')
            self.stop_server_btn.config(state='normal')
            self.server_status.set("Server Running")
            self.log_server(f"Server started on port {port}")
            
            # Start server thread
            self.server_thread = threading.Thread(target=self.server_listen, daemon=True)
            self.server_thread.start()
            
        except Exception as e:
            self.log_server(f"Error starting server: {str(e)}")
            self.server_status.set("Server Error")
            self.start_server_btn.config(state='normal')
            self.stop_server_btn.config(state='disabled')
            
    def stop_server(self):
        self.is_server_running = False
        if self.server_socket:
            self.server_socket.close()
        self.log_server("Server stopped")
        self.server_status.set("Server Stopped")
        self.start_server_btn.config(state='normal')
        self.stop_server_btn.config(state='disabled')
        
    def server_listen(self):
        while self.is_server_running:
            try:
                client_socket, address = self.server_socket.accept()
                self.log_server(f"Connection from {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
                client_thread.start()
                
            except Exception as e:
                if self.is_server_running:
                    self.log_server(f"Error accepting connection: {str(e)}")
                break
                
    def handle_client(self, client_socket):
        try:
            while True:
                # Receive file name
                filename_length = int.from_bytes(client_socket.recv(4), 'big')
                filename = client_socket.recv(filename_length).decode('utf-8')
                
                if not filename:
                    break
                    
                self.log_server(f"Receiving file: {filename}")
                
                # Receive file size
                file_size = int.from_bytes(client_socket.recv(8), 'big')
                
                # Receive file data
                received = 0
                with open(filename, 'wb') as f:
                    while received < file_size:
                        data = client_socket.recv(4096)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                
                self.log_server(f"File {filename} received successfully")
                
        except Exception as e:
            self.log_server(f"Error handling client: {str(e)}")
        finally:
            client_socket.close()
            
    def connect_to_server(self):
        try:
            ip = self.client_ip.get()
            port = int(self.client_port.get())
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.is_client_connected = True
            
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
            self.send_file_btn.config(state='normal')
            self.client_status.set("Connected")
            self.log_client(f"Connected to {ip}:{port}")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_files, daemon=True)
            receive_thread.start()
            
        except Exception as e:
            self.log_client(f"Connection failed: {str(e)}")
            self.client_status.set("Connection Failed")
            
    def disconnect_from_server(self):
        self.is_client_connected = False
        if self.client_socket:
            self.client_socket.close()
        self.log_client("Disconnected")
        self.client_status.set("Disconnected")
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.send_file_btn.config(state='disabled')
        
    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file.set(os.path.basename(file_path))
            
    def send_file(self):
        if not self.is_client_connected:
            messagebox.showwarning("Warning", "Please connect to a server first!")
            return
            
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
            
        try:
            filename = os.path.basename(file_path)
            
            # Send file name
            filename_bytes = filename.encode('utf-8')
            self.client_socket.send(len(filename_bytes).to_bytes(4, 'big'))
            self.client_socket.send(filename_bytes)
            
            # Send file size
            file_size = os.path.getsize(file_path)
            self.client_socket.send(file_size.to_bytes(8, 'big'))
            
            # Send file data
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.client_socket.send(data)
                    
            self.log_client(f"File {filename} sent successfully")
            
        except Exception as e:
            self.log_client(f"Error sending file: {str(e)}")
            
    def receive_files(self):
        try:
            while self.is_client_connected:
                # Receive file name
                filename_length = int.from_bytes(self.client_socket.recv(4), 'big')
                filename = self.client_socket.recv(filename_length).decode('utf-8')
                
                if not filename:
                    break
                    
                self.log_client(f"Receiving file: {filename}")
                
                # Receive file size
                file_size = int.from_bytes(self.client_socket.recv(8), 'big')
                
                # Receive file data
                received = 0
                with open(filename, 'wb') as f:
                    while received < file_size:
                        data = self.client_socket.recv(4096)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                
                self.log_client(f"File {filename} received successfully")
                
        except Exception as e:
            if self.is_client_connected:
                self.log_client(f"Error receiving file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()
