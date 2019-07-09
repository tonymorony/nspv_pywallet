#!/usr/bin/env python3

import tkinter as tk
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
            if "nSPV" in get_info_output and get_info_output["nSPV"] == "superlite":
                print(sys.argv[1] + " daemon is running. Welcome to nSPV pywallet!")
                break
            else:
                print("Please restart " + sys.argv[1] + " daemon in nSPV client mode (-nSPV=1 param)")
                sys.exit()
        except Exception as e:
            print(sys.argv[1] +" daemon is not started! Lets try to start")
            # TODO: probably need to add case for windows binary
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
root = tk.Tk()
root.title("nSPV pywallet")
root.geometry("720x680")
root.resizable(False, False)

# widgets creation
wallet_create_messages = tk.Text(root, height=4, width=70)
wallet_interact_messages = tk.Text(root, height=7, width=70)


get_new_address_button = tk.Button(root, text="Get new address")
nspv_login_button = tk.Button(root, text="Login")
nspv_logout_button = tk.Button(root, text="Logout")
refresh_button = tk.Button(root, text="Refresh")

wif_input = tk.Entry(root, width=50)
nspv_login_text = tk.Label(root, text="Input wif to login:")
nspv_spend_text = tk.Label(root, text="Send to address:")
amount_text = tk.Label(root, text="Amount:")
amount_input = tk.Entry(root, width=50)
nspv_spend_button = tk.Button(root, text="Send")
address_input = tk.Entry(root, width=50)
current_address_text = tk.Label(root, text="Address: please login first!")
current_balance_text = tk.Label(root, text="Balance: please login first!")
logout_timer_text = tk.Label(root, text="Logout in: please login first!")


# buttons bindings
def get_new_address(event):
    new_address_info = rpc_proxy.getnewaddress()
    new_address_info_string = "wif: " + new_address_info["wif"] + "\n" \
                              + "address: " + new_address_info["address"] + "\n" \
                              + "pubkey: " + new_address_info["pubkey"] + "\n"
    wallet_create_messages.replace('1.0', '100.0', new_address_info_string)


def nspv_login(event):
    login_info = rpc_proxy.nspv_login(wif_input.get())
    wallet_interact_messages.replace('1.0', '100.0', login_info)
    current_address_text["text"] = "Address: " + login_info["address"]
    listunspent_output = rpc_proxy.nspv_listunspent(login_info["address"])
    if "error" in listunspent_output and listunspent_output["error"] == "no utxos result":
        current_balance_text["text"] = "Balance: 0 " + ac_name
    else:
        current_balance_text["text"] = "Balance: " + str(listunspent_output["balance"]) + " " + ac_name
    logout_timer_text["text"] = "Logout in: " + str(rpc_proxy.nspv_getinfo()["wifexpires"]) + " seconds"


def nspv_logout(event):
    logout_info = rpc_proxy.nspv_logout()
    wallet_interact_messages.replace('1.0', '100.0', logout_info)
    current_address_text["text"] = "Address: please login first!"
    current_balance_text["text"] = "Balance: please login first!"
    logout_timer_text["text"] = "Logout in: please login first!"


def nspv_send_tx(event):
    nspv_spend_output = rpc_proxy.nspv_spend(str(address_input.get()), str(amount_input.get()))
    if "vout" in nspv_spend_output:
        confirmation_popup(nspv_spend_output)
    else:
        wallet_interact_messages.replace('1.0', '100.0', nspv_spend_output)


def refresh(event):
    current_address = current_address_text["text"][-34:]
    listunspent_output = rpc_proxy.nspv_listunspent(current_address)
    if "error" in listunspent_output and listunspent_output["error"] == "no utxos result":
        current_balance_text["text"] = "Balance: 0 " + ac_name
    else:
        current_balance_text["text"] = "Balance: " + str(listunspent_output["balance"]) + " " + ac_name
    logout_timer_text["text"] = "Logout in: " + str(rpc_proxy.nspv_getinfo()["wifexpires"]) + " seconds"


def confirm_broadcasting(spend_output, popup_window):
    try:
        nspv_broadcast_output = rpc_proxy.nspv_broadcast(spend_output["hex"])
        wallet_interact_messages.replace('1.0', '100.0', nspv_broadcast_output)
    except Exception as e:
        wallet_interact_messages.replace('1.0', '100.0', spend_output)
    finally:
        popup_window.destroy()


def confirmation_popup(spend_output):
    popup = tk.Tk()
    popup.wm_title("Please confirm your transaction")
    label = tk.Label(popup, text="You're about to spend: " + str(spend_output["vout"][0]["value"]) + " " + ac_name)
    label2 = tk.Label(popup, text="Destination address: " + str(spend_output["vout"][0]["scriptPubKey"]["addresses"][0]))
    label3 = tk.Label(popup, text="Input txid: " + str(spend_output["vin"][0]["txid"]))
    if spend_output["retcodes"][0] == 0:
        label4 = tk.Label(popup, text="Input notarized")
    else:
        label4 = tk.Label(popup, text="Input NOT notarized")
    label.pack(side="top", fill="x", pady=10)
    label2.pack(side="top", fill="x", pady=10)
    label3.pack(side="top", fill="x", pady=10)
    label4.pack(side="top", fill="x", pady=10)
    button1 = tk.Button(popup, text="Confirm", command=lambda: confirm_broadcasting(spend_output, popup))
    button2 = tk.Button(popup, text="Cancel", command=popup.destroy)
    button1.pack()
    button2.pack()
    popup.mainloop()


get_new_address_button.bind('<Button-1>', get_new_address)
nspv_login_button.bind('<Button-1>', nspv_login)
nspv_spend_button.bind('<Button-1>', nspv_send_tx)
nspv_logout_button.bind('<Button-1>', nspv_logout)
refresh_button.bind('<Button-1>', refresh)

# widgets drawing
get_new_address_button.grid(row=0, sticky='nesw', padx=(5,5), pady=(10,0))
wallet_create_messages.grid(row=1, sticky='nesw', padx=(5,5), pady=(10,0))
nspv_login_text.grid(row=2, sticky='w', pady=(15,0), padx=(5,5))
wif_input.grid(row=2, sticky='w', pady=(15,0), padx=(160,5))
nspv_login_button.grid(row=3, sticky='nesw', pady=(15,0), padx=(160,5))
wallet_interact_messages.grid(row=4, sticky='nesw', padx=(5,5), pady=(10,0))
current_address_text.grid(row=5, sticky='w', pady=(15,0), padx=(5,5))
current_balance_text.grid(row=6, sticky='w', pady=(15,0), padx=(5,5))
refresh_button.grid(row=6, column=0, sticky='w', pady=(15,0), padx=(630,5))
nspv_logout_button.grid(row=7, column=0, sticky='w', pady=(15,0), padx=(630,5))
logout_timer_text.grid(row=7, sticky='w', pady=(15,0), padx=(5,5))
nspv_logout_button.grid(row=7, column=0, sticky='w', pady=(15,0), padx=(630,5))
nspv_spend_text.grid(row=8, sticky='w', pady=(15,0), padx=(5,5))
address_input.grid(row=8, sticky='w', pady=(15,0), padx=(160,5))
amount_text.grid(row=9, sticky='w', pady=(15,0), padx=(5,5))
amount_input.grid(row=9, sticky='w', pady=(15,0), padx=(160,5))
nspv_spend_button.grid(row=10, sticky='nesw', pady=(15,0), padx=(160,5))


# lets go
root.mainloop()
