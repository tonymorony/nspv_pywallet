#!/usr/bin/env python3

from tkinter import ttk
import ttkthemes as tkT
import tkinter as tk
from tkinter import PhotoImage
from lib import nspvwallet
import sys
import subprocess
import time


# daemon initialization
try:
    ac_name = sys.argv[1]
    rpc_proxy = nspvwallet.def_credentials(ac_name)
except IndexError:
    print("Please use chain ticker as first start argument. For example: ./main.py KMD")
    sys.exit()

# checking if daemon connected
connect_attempts_counter = 0
while True:
    if connect_attempts_counter < 5:
        connect_attempts_counter += 1
        try:
            get_info_output = rpc_proxy.nspv_getinfo()
            print("nspv_getinfo")
            print(get_info_output)
            if "nSPV" in get_info_output and get_info_output["nSPV"] == "superlite":
                print(sys.argv[1] + " daemon is running. Welcome to nSPV pywallet!")
                break
            else:
                print("Please restart " + sys.argv[1] + " daemon in nSPV client mode (-nSPV=1 param)")
                sys.exit()
        except Exception as e:
            print(e)
            print(sys.argv[1] +" daemon is not started! Lets try to start")
            # TODO: have to parse json with params
            if sys.argv[1] == "KMD":
                subprocess.call(['./komodod', '-nSPV=1', '-connect=23.254.165.16', '-listen=0', '-daemon'])
                time.sleep(1)
            elif sys.argv[1] == "ILN":
                subprocess.call(['./komodod', '-ac_name=ILN', '-ac_supply=10000000000', '-ac_cc=2', '-nSPV=1',
                                 '-connect=5.9.102.210', '-listen=0', '-daemon'])
                time.sleep(1)
            else:
                print("I don't know params for this chain. Exiting")
                sys.exit()
    else:
        print("daemon for " + sys.argv[1] + " not started and can't start it. Exiting.")
        sys.exit()

# main window
root = tkT.ThemedTk(theme="equilux", background=True)  # overall darker theme
root.title("nSPV pywallet")
root.resizable(False, False)
root.iconbitmap('lib/kmd.ico')  # ICO still showing square edges
style = ttk.Style()
style.map("TButton", background=[('pressed', 'darkslategray4')]) # greenish color on button press

# KMD Logo (Could be clearer)
img = PhotoImage(file='lib/KMD_Horiz_Dark.png').subsample(3,3)
lbl_img = ttk.Label(root, image=img)

# Tabbed Notebook
nb = ttk.Notebook(root)
tab1 = ttk.Frame(nb)
tab2 = ttk.Frame(nb)
nb.add(tab1, text='Interaction Info')
nb.add(tab2, text='New Wallet Info')
nb.grid(row=3, column=0, rowspan=3, columnspan=2, sticky='NEWS', padx=(10,10), pady=(5,5))


# widgets creation
wallet_create_messages = tk.Text(tab1, height=5, width=80, padx=15, bg='darkslategray4')
wallet_interact_messages = tk.Text(tab2, height=5, width=80, padx=15, bg='darkslategray4')


get_new_address_button = ttk.Button(root, text="Get new address")
nspv_login_button = ttk.Button(root, text="Login")
nspv_logout_button = ttk.Button(root, text="Logout")
refresh_button = ttk.Button(root, text="Refresh")

wif_input = ttk.Entry(root, width=50)
nspv_login_text = ttk.Label(root, text="Input wif to login:")
nspv_spend_text = ttk.Label(root, text="Send to address:")
amount_text = ttk.Label(root, text="Amount:")
amount_input = ttk.Entry(root, width=50)
nspv_spend_button = ttk.Button(root, text="Send")
address_input = ttk.Entry(root, width=50)
current_address_text = ttk.Label(root, text="Address: please login first!")
current_balance_text = ttk.Label(root, text="Balance: please login first!")
logout_timer_text = ttk.Label(root, text="Logout in: please login first!")

# find Center of screen (needs testing on different screens
def center():
    windowWidth = root.winfo_reqwidth()
    windowHeight = root.winfo_reqheight()
    positionRight = int(root.winfo_screenwidth() / 4 - windowWidth / 4)
    positionDown = int(root.winfo_screenheight() / 3 - windowHeight / 1)
    root.geometry("+{}+{}".format(positionRight, positionDown))

# buttons bindings
def get_new_address(event):
    new_address_info = rpc_proxy.getnewaddress()
    print("getnewaddress")
    print(new_address_info)
    new_address_info_string = "wif: " + new_address_info["wif"] + "\n" \
                              + "address: " + new_address_info["address"] + "\n" \
                              + "pubkey: " + new_address_info["pubkey"] + "\n"
    wallet_create_messages.replace('1.0', '100.0', new_address_info_string)


def nspv_login(event):
    login_info = rpc_proxy.nspv_login(wif_input.get())
    print("nspv_login " + wif_input.get())
    print(login_info)
    wallet_interact_messages.replace('1.0', '100.0', login_info)
    current_address_text["text"] = "Address: " + login_info["address"]
    listunspent_output = rpc_proxy.nspv_listunspent(login_info["address"])
    print(listunspent_output)
    if "error" in listunspent_output and listunspent_output["error"] == "no utxos result":
        current_balance_text["text"] = "Balance: 0 " + ac_name
    else:
        if len(listunspent_output["utxos"]) < 10:
            for utxo in listunspent_output["utxos"]:
                print(utxo)
                rpc_proxy.nspv_txproof(utxo["txid"], str(utxo["height"]))
        current_balance_text["text"] = "Balance: " + str(listunspent_output["balance"]) + " " + ac_name
    logout_timer_text["text"] = "Logout in: " + str(rpc_proxy.nspv_getinfo()["wifexpires"]) + " seconds"


def nspv_logout(event):
    logout_info = rpc_proxy.nspv_logout()
    print("nspv_logout")
    print(logout_info)
    wallet_interact_messages.replace('1.0', '100.0', logout_info)
    current_address_text["text"] = "Address: please login first!"
    current_balance_text["text"] = "Balance: please login first!"
    logout_timer_text["text"] = "Logout in: please login first!"


def nspv_send_tx(event):
    nspv_spend_output = rpc_proxy.nspv_spend(str(address_input.get()), str(amount_input.get()))
    print("nspv_spend " + str(address_input.get() + " "  + str(amount_input.get())))
    print(nspv_spend_output)
    if "vout" in nspv_spend_output:
        confirmation_popup(nspv_spend_output)
    else:
        wallet_interact_messages.replace('1.0', '100.0', nspv_spend_output)


def refresh(event):
    current_address = current_address_text["text"][-34:]
    listunspent_output = rpc_proxy.nspv_listunspent(current_address)
    print("nspv_listunspent " + current_address)
    print(listunspent_output)
    nspv_getinfo_output = rpc_proxy.nspv_getinfo()
    print("nspv_getinfo")
    print(nspv_getinfo_output)
    if "wifexpires" in nspv_getinfo_output:
        logout_timer_text["text"] = "Logout in: " + str(rpc_proxy.nspv_getinfo()["wifexpires"]) + " seconds"
        if "error" in listunspent_output and listunspent_output["error"] == "no utxos result":
            current_balance_text["text"] = "Balance: 0 " + ac_name
        else:
            try:
                current_balance_text["text"] = "Balance: " + str(listunspent_output["balance"]) + " " + ac_name
            except KeyError:
                current_balance_text["text"] = "Balance: 0 " + ac_name
    else:
        current_address_text["text"] = "Address: please login first!"
        current_balance_text["text"] = "Balance: please login first!"
        logout_timer_text["text"] = "Logout in: please login first!"


def confirm_broadcasting(spend_output, popup_window):
    try:
        nspv_broadcast_output = rpc_proxy.nspv_broadcast(spend_output["hex"])
        print("nspv_broadcast " + spend_output["hex"])
        print(nspv_broadcast_output)
        wallet_interact_messages.replace('1.0', '100.0', nspv_broadcast_output)
    except Exception as e:
        wallet_interact_messages.replace('1.0', '100.0', spend_output)
    finally:
        refresh("test")
        popup_window.destroy()


def confirmation_popup(spend_output):
    popup = ttk.Tk()
    popup.wm_title("Please confirm your transaction")
    label = ttk.Label(popup, text="You're about to spend: " + str(spend_output["vout"][0]["value"]) + " " + ac_name)
    label2 = ttk.Label(popup, text="Destination address: " + str(spend_output["vout"][0]["scriptPubKey"]["addresses"][0]))
    label3 = ttk.Label(popup, text="Input txid: " + str(spend_output["vin"][0]["txid"]))
    if spend_output["retcodes"][0] == 0:
        label4 = ttk.Label(popup, text="Input notarized")
    else:
        label4 = ttk.Label(popup, text="Input NOT notarized")
    label5 = ttk.Label(popup, text="Tx fee: 0.0001 " + ac_name)
    label6 = ttk.Label(popup, text="Rewards: " + str(spend_output["rewards"]) + " " + ac_name)
    label.pack(side="top", fill="x", pady=10)
    label2.pack(side="top", fill="x", pady=10)
    label3.pack(side="top", fill="x", pady=10)
    label4.pack(side="top", fill="x", pady=10)
    label5.pack(side="top", fill="x", pady=10)
    label6.pack(side="top", fill="x", pady=10)
    button1 = ttk.Button(popup, text="Confirm", command=lambda: confirm_broadcasting(spend_output, popup))
    button2 = ttk.Button(popup, text="Cancel", command=popup.destroy)
    button1.pack()
    button2.pack()
    popup.mainloop()


def custom_paste(event):
    try:
        event.widget.delete("sel.first", "sel.last")
    except:
        pass
    event.widget.insert("insert", event.widget.clipboard_get())
    return "break"


get_new_address_button.bind('<Button-1>', get_new_address)
nspv_login_button.bind('<Button-1>', nspv_login)
nspv_spend_button.bind('<Button-1>', nspv_send_tx)
nspv_logout_button.bind('<Button-1>', nspv_logout)
refresh_button.bind('<Button-1>', refresh)
amount_input.bind("<<Paste>>", custom_paste)
wif_input.bind("<<Paste>>", custom_paste)
address_input.bind("<<Paste>>", custom_paste)

# widgets drawing
lbl_img.grid(row=0, sticky='e', padx=(10,10), pady=(10,0))
get_new_address_button.grid(row=0, sticky='nws', padx=(10,10), pady=(10,0))
wallet_create_messages.grid(row=1, sticky='nesw', padx=(10,10), pady=(10,0))
nspv_login_text.grid(row=2, sticky='w', pady=(15,0), padx=(10,10))
wif_input.grid(row=2, sticky='w', pady=(15,0), padx=(160,10))
nspv_login_button.grid(row=2, sticky='e', pady=(15,0), padx=(160,10))
wallet_interact_messages.grid(row=4, sticky='nesw', padx=(10,10), pady=(10,0))
current_address_text.grid(row=6, sticky='w', pady=(15,0), padx=(10,10))
current_balance_text.grid(row=7, sticky='w', pady=(15,0), padx=(10,10))
refresh_button.grid(row=7, column=0, sticky='w', pady=(15,0), padx=(630,10))
nspv_logout_button.grid(row=8, column=0, sticky='w', pady=(15,0), padx=(630,10))
logout_timer_text.grid(row=8, sticky='w', pady=(15,0), padx=(10,10))
nspv_logout_button.grid(row=8, column=0, sticky='w', pady=(15,0), padx=(630,10))
nspv_spend_text.grid(row=9, sticky='w', pady=(15,0), padx=(10,10))
address_input.grid(row=9, sticky='w', pady=(15,0), padx=(160,10))
amount_text.grid(row=10, sticky='w', pady=(15,0), padx=(10,10))
amount_input.grid(row=10, sticky='w', pady=(15,0), padx=(160,10))
nspv_spend_button.grid(row=11, sticky='W', pady=(5,10), padx=(160,10))


# lets go
center()
root.mainloop()
