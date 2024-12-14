# TPRG 2131 Fall 202x Project 2
# Student Name : Mankaran Singh Chattha
# Student Id : 100944566
# submission Date : 13 December 2024
# This program is strictly my own work. Any material
# beyond course learning materials that is taken from
# the Web or other sources is properly cited, giving.
# credit to the original author(s)
import socket
import json
import time
import threading
import PySimpleGUI as sg

# Function to simulate data collection
def collect_data(iteration):
    return {
        "Iteration": iteration,
        "Core_Temperature": 50 + iteration % 10,  # Simulated core temperature
        "GPU_Temperature": 45 + iteration % 10,   # Simulated GPU temperature
        "Clock_Speed": 1200 + iteration % 100,     # Simulated clock speed
        "Voltage": 1.2 + (iteration % 5) * 0.01,   # Simulated voltage
        "Memory_Free": 800 + (iteration % 50)      # Simulated free memory
    }

# Function to send data to the server
def send_data(client_socket, window, stop_event):
    iteration = 0
    while iteration < 50 and not stop_event.is_set():  # Limit to 50 iterations or until stop event is set
        try:
            data = collect_data(iteration)  # Collect data
            client_socket.sendall(json.dumps(data).encode('utf-8'))  # Send data to server
            iteration += 1
            time.sleep(2)  # Wait for 2 seconds before sending the next data
        except (BrokenPipeError, ConnectionResetError):
            if window is not None:
                window.write_event_value('-DISCONNECT-', None)  # Trigger disconnect event on error
            break
        except Exception as e:
            if window is not None:
                window.write_event_value('-ERROR-', str(e))  # Trigger error event
            break

# Main function to create the GUI and manage socket connection
def main():
    # Define the layout of the GUI
    layout = [
        [sg.Text("Client Status:", font=("Helvetica", 12), text_color="white")],
        [sg.Text("Ready to Connect", size=(40, 1), key="-STATUS-", text_color="yellow")],
        [sg.Button("Connect", key="-CONNECT-", size=(10, 1))],
        [sg.Button("Exit", key="-EXIT-", size=(10, 1))]
    ]

    # Create the window
    window = sg.Window("Client Application", layout, finalize=True, background_color='black')

    client_socket = None  # Initialize client socket
    stop_event = threading.Event()  # Event to signal stopping the data sending thread

    while True:
        event, _ = window.read(timeout=100)  # Read events from the window
        if event in (sg.WINDOW_CLOSED, "-EXIT-"):  # Handle window close or exit button
            stop_event.set()  # Signal the thread to stop
            if client_socket:
                try:
                    client_socket.close()  # Close the socket
                    window["-STATUS-"].update("Disconnected", text_color="red")  # Update status
                except Exception as e:
                    window["-STATUS-"].update(f"Error closing socket: {e}", text_color="red")
            break

        if event == "-CONNECT-":  # Handle connect button
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket
                client_socket.settimeout(10)  # Set a timeout for connection attempt
                client_socket.connect(("127.0.0.1", 5000))  # Connect to the server
                client_socket.settimeout(None)  # Remove timeout after connection is established
                window["-STATUS-"].update("Connected", text_color="green")  # Update status
                
                stop_event.clear()  # Reset the stop event
                
                # Start a new thread to send data
                threading.Thread(target=send_data, args=(client_socket, window, stop_event), daemon=True).start()
            except socket.timeout:
                window["-STATUS-"].update("Connection timed out", text_color="red")  # Handle timeout
            except Exception as e:
                window["-STATUS-"].update(f"Error: {e}", text_color="red")  # Handle other exceptions

        if event == '-DISCONNECT-':  # Handle disconnect event
            window["-STATUS-"].update("Disconnected", text_color="red")
            if client_socket:
                client_socket.close()  # Close the socket
                client_socket = None

        if event == '-ERROR-':  # Handle error event
            error_message = _  # The error message is passed as the event data
            window["-STATUS-"].update(f"Error: {error_message}", text_color="red")  # Update status
            if client_socket:
                client_socket.close()  # Close the socket
                client_socket = None

    if client_socket:  # Ensure the socket is closed before exiting
        try:
            client_socket.close()  # Close the socket if it's still open
            window["-STATUS-"].update("Disconnected", text_color="red")  # Update status
        except Exception as e:
            window["-STATUS-"].update(f"Error closing socket: {e}", text_color="red")  # Handle closing error
    window.close()  # Close the GUI window

if __name__ == "__main__":
    main()  # Run the main function to start the application