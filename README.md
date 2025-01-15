# socket-programing
Server-Multi client model

- `client_script.py`: Script to start a UDP client.
- `config.xml`: XML configuration file to store client information.
- `server_messages.data`: File to store server messages.
- `udp_gui_server.py`: Main script to start the UDP server with a GUI.

## Requirements

- Python 3.x
- Tkinter (usually included with Python installations)

## Usage

### Starting the Server

1. Run the `udp_gui_server.py` script to start the server with a GUI:

    ```sh
    python udp_gui_server.py
    ```

2. Enter the server IP and port, then click "Start Server".

### Adding Clients

1. Enter the client ID, IP, and port in the GUI.
2. Click "Add Client" to add the client to the configuration.

### Starting Clients

1. Run the  script to start a client:

    ```sh
    python client_script.py <client_id> <port> <server_ip:server_port>
    ```

    Example:

    ```sh
    python client_script.py 1 54321 127.0.0.1:12345
    ```

2. Enter messages in the client terminal to send them to the server.

### Sending Messages from the Server

1. Select a client from the dropdown menu in the GUI.
2. Enter a message and click "Send Message" to send it to the selected client or broadcast it to all clients.

### Stopping the Server

1. Click "Stop Server" in the GUI to stop the server.

## Configuration

The  file stores client information in the following format:

```xml
<clients>
    <client id="1" ip="192.168.93.108" port="54321" />
</clients>
