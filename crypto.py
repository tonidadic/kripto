import requests
import argparse
import os
import pandas as pd
import pandas_datareader 
import plotly.graph_objects as graph_objects 
from bitcoinrpc.authproxy import AuthServiceProxy 
from datetime import datetime, timedelta
from tkinter import * 
from PIL import ImageTk, Image 


def ParseCmdArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpcBasicAuth', action="store", dest='rpcBasicAuth', default=None)
    parser.add_argument('--rpcUrl', action="store", dest='rpcUrl', default=None)
    parser.add_argument('--useSsl', action="store", dest='useSsl', default=False)

    args = parser.parse_args()
    if(args.rpcBasicAuth == None or args.rpcBasicAuth == "" or len(args.rpcBasicAuth.split(":")) != 2):
        raise Exception("RPC basic auth not configured properly! Please use format --rpcBasicAuth='username:password'.")
    if(args.rpcUrl == None or args.rpcUrl == "" or "@" in args.rpcUrl or "http://" in args.rpcUrl or "https://" in args.rpcUrl):
        raise Exception("RPC URL not configured properly! Please use format --rpcUrl='example.com'.")
    return args


def InitializeMenus(root, frame, connection, configuration):
    menu = Menu(root)
    root.config(menu=menu)
    priceSubMenu = Menu(menu)

    menu.add_cascade(label="Bitcoin Price",  menu=priceSubMenu)
    priceSubMenu.add_command(label="Bitcoin Current price", command=lambda: CurrentPrice(frame, configuration))
    priceSubMenu.add_command(label="Bitcoin Price graph", command=lambda: ShowPriceGraph(configuration))
    

def InitializeMainWindow(connection, configuration):
    if(connection == None or configuration == None):
        return
    root = Tk()
    root.update_idletasks()
    root.state('iconic')
    root.title("Crypto")
    width = configuration["window"]["width"] if configuration["window"]["width"] != None else 800
    height = configuration["window"]["width"] if configuration["window"]["width"] != None else 600
    InitializeMenus(root, Frame(root, width=width, height=height), connection, configuration)
    root.geometry("%dx%d" % (width, height))
    return root


if __name__ == "__main__":
    args = ParseCmdArguments()
    ssl = False
    if(args.useSsl != None and args.useSsl == True):
        ssl = True
    rpcUrl = "%s://%s@%s"%("https" if ssl else "http", args.rpcBasicAuth.replace("'",""), args.rpcUrl.replace("'",""))
    connection = AuthServiceProxy(rpcUrl)
    rootDirectoryPath = os.path.dirname(__file__)
    configuration = {
        "rootDirectoryPath": rootDirectoryPath,
        "fonts": {
            "h1": ("aerial", 18, "bold"),
            "h2": ("aerial", 16, "bold"),
            "h3": ("aerial", 14, "normal")
        },
        "colors":{
            "primary": "#007bff",
            "secondary": "#17a2b8"
        },
        "window": {
            "height": 600,
            "width": 800
        }
    }

    rootScreen = InitializeMainWindow(connection, configuration)

    rootScreen.mainloop()