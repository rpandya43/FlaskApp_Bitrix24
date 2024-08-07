import tkinter as tk
from tkinter import ttk
import requests
import webbrowser
from urllib.parse import unquote  # Import the unquote function from urllib.parse

def send_post_request():
    # Get the ID from the entry widget
    user_id = id_entry.get()

    # URL and parameters
    url = "http://178.79.147.177:9852/trigger-script"
    params = {
        "event": "ONCRMLEADADD",
        "data[FIELDS][ID]": user_id,
        "ts": 1706799761,
        "auth[domain]": "rtech.bitrix24.com",
        "auth[client_endpoint]": "https://rtech.bitrix24.com/rest/",
        "auth[server_endpoint]": "https://oauth.bitrix.info/rest/",
        "auth[member_id]": "43615c91b71c9d18bd172435af4bc425",
        "auth[application_token]": "gt77z8s8bewt9brhn01ks7tjm6rlkny1"
    }

    # Send POST request
    response = requests.post(url, data=params)

    # Parse the response JSON
    response_json = response.json()

    # Display response
    result_label.config(text=f"Response: {response_json['message']}")

    # If a link is received in the response, enable the button to open it
    if 'stored_data' in response_json:
        open_link_button.config(state=tk.NORMAL)
        link = response_json['stored_data']

        # Decode the URL-encoded link
        decoded_link = unquote(link)

        # Update the link label to display the decoded link
        link_label.config(text=f"Received Link: {decoded_link}")

        # Store the decoded link as an attribute of the button
        open_link_button.link = decoded_link
    else:
        open_link_button.config(state=tk.DISABLED)
        link_label.config(text="Received Link: N/A")

def open_link():
    # Open the link stored in the button's attribute
    webbrowser.open(open_link_button.link)

# Create the main window
app = tk.Tk()
app.title("POST Request Sender")
app.geometry("400x250")  # Set the initial window size

# Create a style object
style = ttk.Style()

# Configure the style for buttons
style.configure("TButton", font=("Arial", 12), background="#007bff", foreground="white", padding=10, borderwidth=0)
style.map("TButton", background=[("active", "#0056b3")])

# Create and place ID entry widget
id_label = tk.Label(app, text="Enter ID:")
id_label.pack(pady=10)
id_entry = tk.Entry(app)
id_entry.pack(pady=10)

# Create and place send button
send_button = ttk.Button(app, text="Send POST Request", command=send_post_request)
send_button.pack(pady=20)

# Create and place label for displaying response
result_label = tk.Label(app, text="")
result_label.pack()

# Create and place label for displaying received link
link_label = tk.Label(app, text="Received Link: N/A")
link_label.pack()

# Create and place button to open received link
open_link_button = ttk.Button(app, text="Open Received Link", command=open_link, state=tk.DISABLED)
open_link_button.pack(pady=10)

# Run the application
app.mainloop()
