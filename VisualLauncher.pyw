import tkinter as tk
from tkinter import *
import os
import threading
import glob
from PIL import Image, ImageTk
from pathlib import Path
import requests
import time
import keyboard

start_index = 0

def toggle(button):
        if button.config('bg') == "red":
            print('ok')
        elif button.config('bg') == "green":
            print('ok2')

def open_settings():
        settings = tk.Toplevel()
        # title = tk.Label(settings, text=title, bg="black", fg="white", font=('Poppins', 14), anchor='nw', wraplength=450)
        settings.geometry("855x400")
        settings.overrideredirect(True)
        settings.config(bg="black")
        # title.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # description = tk.Label(settings, text=description, bg="black", fg="white", font=('Poppins', 14), anchor='nw', wraplength=450)
        # description.pack(side="top", fill="both", expand=True, padx=10)

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the window position to the bottom-right corner
        settings.geometry(f"+{screen_width - 400}+{screen_height - 148}")
        # settings.attributes('-topmost', True)  # Keep the window at the top

        center_window(settings)

def close_window():
    root.destroy()

def on_drag(event):
    x = root.winfo_pointerx() - root._offsetx
    y = root.winfo_pointery() - root._offsety
    root.geometry(f"+{x}+{y}")

def on_start_drag(event):
    root._offsetx = event.x
    root._offsety = event.y

def create_notification(title, description):
        notif = tk.Toplevel()
        title = tk.Label(notif, text=title, bg="black", fg="white", font=('Poppins', 14), anchor='nw', wraplength=450)
        notif.geometry("400x100")
        notif.overrideredirect(True)
        notif.config(bg="black")
        title.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        description = tk.Label(notif, text=description, bg="black", fg="white", font=('Poppins', 14), anchor='nw', wraplength=450)
        description.pack(side="top", fill="both", expand=True, padx=10)

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the window position to the bottom-right corner
        notif.geometry(f"+{screen_width - 400}+{screen_height - 148}")
        notif.attributes('-topmost', True)  # Keep the window at the top
        notif.after(5000, lambda: notif.destroy())

def get_app_id(game_name, button):
    # Make a request to the Steam API to get the app ID from the game name
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v0002/')
    if response.status_code == 200:
        data = response.json()
        app_list = data['applist']['apps']
        for app in app_list:
            if app['name'] == game_name:
                app_id = app['appid']
                download_game_icon(app_id, button)
                break

def download_game_icon(app_id, button):
    # Read the first line from the steamPath.txt file
    with open("./Config/steamPath.txt", "r") as file:
        steam_path = Path(file.readline().strip())
    
    game_icon_path = steam_path / 'appcache/librarycache' / f'{app_id}_library_600x900.jpg'
    if game_icon_path.exists():
        img = Image.open(game_icon_path)
        resized_img = img.resize((180, 280), Image.ANTIALIAS)
        game_icon = ImageTk.PhotoImage(resized_img)
        button.configure(image=game_icon, compound='center', text=" ")
        button.image = game_icon  # Keep a reference to prevent garbage collection

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def hide_me(event):
    event.pack_forget()

def show_me(event):
    event.pack()

def launch(gameName):
    foundGame = False
    print(gameName)
    for file in glob.iglob(gameName + '/**/*.exe', recursive=True):
        foundGame = True
        os.startfile(file)
        print(file)
        # break  # Stop after launching the first executable file
    
    if not foundGame:
        print("No executable files found in", gameName)

def create_rounded_button(parent, text):
    file = open("./Config/steamPath.txt", "r")
    lines = file.readline()
    games = os.path.join(lines.strip(), "steamapps/common/")
    file.close()

    img = Image.open("./Resources/game_button.png")  # Load the button background image
    rounded_img = ImageTk.PhotoImage(img)

    button = Button(parent, text=text, command=lambda gameName=games + text: launch(gameName), image=rounded_img, compound='center', font=('Poppins', 14), fg="white", bd=0, bg='black', highlightthickness=0, wraplength=180)
    button.image = rounded_img  # Keep a reference to the image to prevent garbage collection
    button.config(width=180, height=280)  # Set button size

    return button

def shift_cards(direction):
    global start_index
    if direction == 'right':
        start_index = min(start_index + 4, len(cards) - 4)
    else:
        start_index = max(start_index - 4, 0)

    update_layout()

def add_shift_buttons(root):
    right_button = Button(root, text='>', command=lambda: shift_cards('right'))
    left_button = Button(root, text='<', command=lambda: shift_cards('left'))

    right_button.place(x=830, y=190)
    left_button.place(x=10, y=190)

    return right_button, left_button

def add_card(parent, text1):
    text = text1
    card = create_rounded_button(card_container, text1)
    cards.append(card)
    update_layout()
    if len(cards) >= 4:
        add_shift_buttons(root)
    # Start a thread to get the app ID and download the game icon
    threading.Thread(target=get_app_id, args=(text1, card)).start()

def update_layout():
    global start_index
    for card in cards:
        card.grid_forget()

    end_index = min(start_index + 4, len(cards))
    for i in range(start_index, end_index):
        row = (i - start_index) // columns
        column = (i - start_index) % columns
        cards[i].grid(row=row, column=column, padx=5, pady=5)

def search_steamapps():
    global found_steamapps

    for root1, dirs, files in os.walk(path):
        for name in dirs:
            if name.startswith("steamapps"):
                print(os.path.join(root1, name))
                file = open("Config/steamPath.txt", "a")
                file.write(root1)
                file.close()
                found_steamapps = True  # Set flag to True once directory is found
                show_me(found)
                notFound.destroy()
                break  # Break inner loop when directory is found
    
        if found_steamapps:  # Check flag to determine whether to end the loop
            show_me(found)
            notFound.destroy
            break # Break outer loop if directory is found
        else:
            hide_me(notFound)
            hide_me(found)
    
    #root.after(5000, search_steamapps)  # Check again after 5 seconds

def run_search():
    if os.stat("./Config/steamPath.txt").st_size == 0:
        search_thread = threading.Thread(target=search_steamapps)
        search_thread.daemon = True  # Daemonize the thread to stop when the main program stops
        search_thread.start()
    else:
        found.destroy()
        notFound.destroy()

        file = open("./Config/steamPath.txt", "r")
        lines = file.readline()
        games = lines + "/steamapps/common"

        for i in os.listdir(games):
            add_card(card_container, i)

root = tk.Tk()

root.title('Visual Launcher')

# Set window attributes
root.configure(bg='black')
root.resizable(False, False)
root.overrideredirect(True)  # Remove window borders

# Load a transparent image with rounded corners as the background
img = PhotoImage(file='./Resources/rounded_corners.png')  # Replace 'rounded_corners.png' with your image path
background_label = Label(root, image=img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Place the image to cover the whole window

close_button = Button(root, text="X", command=close_window)
close_button.pack(side=TOP)
close_button.place(x = 0)

nameLabel = Label(root, text="Visual Launcher", bg="black", fg="white", font=('Poppins', 14))
nameLabel.config(width=200)
nameLabel.place(relx=.5, rely=.5, anchor="center")
nameLabel.after(1, lambda: nameLabel.destroy())

root.after(1, lambda: root.geometry('855x400'))
root.after(1, lambda: center_window(root))

vL = Label(root, text="Visual Launcher", bg="black", fg="white", font=('Poppins', 14))
vL.config(padx=100)
vL.after(1, lambda: show_me(vL))

settingsIcon = PhotoImage(file=r"./Resources/settings_button.png")

settingsBtn = Button(root, text=" ", image=settingsIcon, bg="black", highlightthickness=0, bd=0, command=lambda: open_settings())
settingsBtn.pack(side=TOP)
settingsBtn.place(x = 828)

horizontal = Frame(root, bg="white", height=2, width=1000)
horizontal.place(x=0, y=30)
horizontal.after(1, lambda: show_me(horizontal))

hide_me(vL)
hide_me(horizontal)
center_window(root)

card_container = Frame(root)
card_container.place(x=50, y=70)
card_container.config(bg="black")

cards = []
columns = 4

found = Label(root, text="We found your steam installation. Please restart Visual Launcher.", bg="black", fg="white", font=('Poppins', 14), wraplength=700)
notFound = Label(root, text="We're detecting your steam installation paths. This might take some minutes, don't close this window.", bg="black", fg="white", font=('Poppins', 14), wraplength=700)

hide_thread = threading.Thread(target=hide_me(found))
hide_thread.daemon = True  # Daemonize the thread to stop when the main program stops
hide_thread.start()

hide_thread2 = threading.Thread(target=hide_me(notFound))
hide_thread2.daemon = True  # Daemonize the thread to stop when the main program stops
hide_thread2.start()

found.place(relx=.5, rely=.5, anchor="center")
found.config(pady=150)
notFound.place(relx=.5, rely=.5, anchor="center")

path = "D:/"
found_steamapps = False  # Flag to control loop termination

notif = threading.Thread(create_notification("Loading your games", "We're currently loading your games."))
notif.daemon = True  # Daemonize the thread to stop when the main program stops
notif.start()

# root.attributes('-topmost', True)  # Keep the window at the top

run_search()  # Start the search on a separate thread

# Binding events for window dragging
root.bind("<ButtonPress-1>", on_start_drag)
root.bind("<B1-Motion>", on_drag)

root.mainloop()