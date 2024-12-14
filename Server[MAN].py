#  TPRG 2131 Fall 202x Project 2
# Student Name : Mankaran Singh Chattha
# Student Id : 100944566
# submission Date : 13 December 2024
# This program is strictly my own work. Any material
# beyond course learning materials that is taken from
# the Web or other sources is properly cited, giving.
# credit to the original author(s)
import socket
import json
import PySimpleGUI as sg
import time

def main():
    """Main function to run the server.
    
    The server listens for incoming client connections and displays 6 key system metrics 
    sent from the client. This function creates a GUI to display status, data, and a toggle LED indicator.
    """
    
    # Define the layout of the GUI
    layout = [
        [sg.Text("Server Status:", font=("Helvetica", 12), text_color="white")],
        [sg.Text("Waiting for client...", size=(40, 1), key="-STATUS-", text_color="yellow")],
        [sg.Text("Current Time:"), sg.Text("", key="-TIME-", size=(20, 1))],
        [sg.Text("Connection LED:"), sg.Text("\u25CF", font=("Helvetica", 18), text_color="red", key="-LED-")],
        [sg.Text("Core Temperature (°C):"), sg.Text("", key="-CORE_TEMP-")],
        [sg.Text("GPU Temperature (°C):"), sg.Text("", key="-GPU_TEMP-")],
        [sg.Text("Clock Speed (MHz):"), sg.Text("", key="-CLOCK_SPEED-")],
        [sg.Text("Voltage (V):"), sg.Text("", key="-VOLTAGE-")],
        [sg.Text("Memory Free (MB):"), sg.Text("", key="-MEM_FREE-")],
        [sg.Text("Iteration Count:"), sg.Text("0", key="-ITER_COUNT-")],
        [sg.Button("Exit", key="-EXIT-", size=(10, 1))]
    ]

    # Create the window with the defined layout
    window = sg.Window("Server Application", layout, finalize=True, background_color='black')

    led_on = False  # Initialize LED state

    try:
        # Create a server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", 5000))  # Bind to all interfaces on port 5000
        server_socket.listen(1)  # Listen for incoming connections

        # Wait for the client to connect
        client_socket, addr = server_socket.accept()  # Accept a client connection
        window["-STATUS-"].update(f"Client connected from {addr}", text_color="green")  # Update status
        window["-LED-"].update(text_color="green")  # Turn LED green on connection

        iteration_count = 0  # Initialize iteration count

        while True:
            event, _ = window.read(timeout=1000)  # Read events from the window with a timeout
            if event in (sg.WINDOW_CLOSED, "-EXIT-"):  # Handle window close or exit button
                break

            current_time = time.strftime("%H:%M:%S", time.localtime())  # Get current time
            window["-TIME-"].update(current_time)  # Update time display

            try:
                data = client_socket.recv(1024).decode('utf-8')  # Receive data from the client
                if not data:
                    break  # Exit loop if client disconnected

                parsed_data = json.loads(data)  # Parse the received JSON data

                # Update GUI with received data
                window["-ITER_COUNT-"].update(parsed_data.get("Iteration", "N/A"))
                window["-CORE_TEMP-"].update(f"{parsed_data.get('Core_Temperature', 'N/A')} °C")
                window["-GPU_TEMP-"].update(f"{parsed_data.get('GPU_Temperature', 'N/A')} °C")
                window["-CLOCK_SPEED-"].update(f"{parsed_data.get('Clock_Speed', 'N/A')} MHz")
                window["-VOLTAGE-"].update(f"{parsed_data.get('Voltage', 'N/A')} V")
                window["-MEM_FREE-"].update(f"{parsed_data.get('Memory_Free', 'N/A')} MB")

                # Toggle LED color for visual feedback
                if led_on:
                    window["-LED-"].update(text_color="red")  # Change LED to red
                else:
                    window["-LED-"].update(text_color="green")  # Change LED to green
                led_on = not led_on  # Toggle LED state

                # Check for completion of iterations
                if int(parsed_data.get("Iteration", 0)) >= 50:
                    sg.popup("50 iterations complete. Server exiting.")  # Notify user and exit
                    break

            except json.JSONDecodeError:
                window["-STATUS-"].update("Error: Invalid JSON received", text_color="red")  # Update status on JSON decode error
            except Exception as e:
                window["-STATUS-"].update(f"Error: {e}", text_color="red")  # Update status on other errors

    finally:
        if client_socket:  # Ensure the client socket is closed
            client_socket.close()
        server_socket.close()  # Close the server socket
        window.close()  # Close the GUI window

if __name__ == "__main__":
    main()  # Run the main function to start the server application