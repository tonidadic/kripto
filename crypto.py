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

# Parsiranje argumenata
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

# Kreiranje menu-a
def InitializeMenus(root, frame, connection, configuration):
    menu = Menu(root)
    root.config(menu=menu)
    priceSubMenu = Menu(menu)

    menu.add_cascade(label="Bitcoin Price",  menu=priceSubMenu)
    priceSubMenu.add_command(label="Bitcoin Current price", command=lambda: CurrentPrice(frame, configuration))
    priceSubMenu.add_command(label="Bitcoin Price graph", command=lambda: ShowPriceGraph(configuration))

    menu.add_cascade(label="Transaction list", command=lambda: Transactions(frame, connection, configuration))
    menu.add_cascade(label="Block information", command=lambda: BlockInfo(frame, configuration))
    
    Transactions(frame, connection, configuration)

# Kreiranje glavnog prozora
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

# Dodavanje slike/ikone ako postoji
def GetBitcoinIconPath(sourceDirectory):
    image = None
    bitcoinIconPath = os.path.join(sourceDirectory, "images", "bitcoin-icon.ico")
    if(os.path.isfile(bitcoinIconPath)):
        return bitcoinIconPath
    return image

def ClearFrame(frame):
    if(frame == None or type(frame) is not Frame):
        return
    for widget in frame.winfo_children():
        widget.destroy()

def ClearFramesDecorator(func):
    def inner(*args, **kwargs):
        ClearFrame(args[0], **kwargs)
        func(*args, **kwargs) 
    return inner

# Metoda za dohvat trenutne cijene BTC-a
@ClearFramesDecorator
def CurrentPrice(frame, configuration):
    if(frame == None):
        return
    frame.pack(fill="both", expand=1)
    url="https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,JPY,EUR&api_key=06efcda2677d688ac20177063ed6af2a3e341d19db249029ec66e7072c6f932c"
    response = requests.get(url).json()
    image = ImageTk.PhotoImage(Image.open(configuration["iconPath"]))
    label = Label(frame, image=ImageTk.PhotoImage(Image.open(configuration["iconPath"])))
    label.image = image
    label.place(x=380, y=250)
    Label(frame, text = "Bitcoin price", font = configuration["fonts"]["h1"]).pack(pady=20)
    Label(frame, text = str(response["USD"]) + "$", font = configuration["fonts"]["h2"]).pack(pady=10)
    Label(frame, text = "Time: " + datetime.now().strftime("%H:%M:%S"), font = configuration["fonts"]["h3"]).pack(pady=10)
    Button(frame, text = "Refresh!", pady=5, padx=10, command=lambda: CurrentPrice(frame, configuration), bg=configuration["colors"]["secondary"]).pack()

# Metoda za dohvat informacija o bloku
@ClearFramesDecorator
def BlockInfo(frame, configuration):
    if(frame == None):
        return
    frame.pack(fill="both", expand=1)
    best_block_hash = connection.getbestblockhash()
    info=connection.getblock(best_block_hash)
    Label(frame, text = "Best block hash", font = configuration["fonts"]["h1"]).pack(pady=20)
    Label(frame, text = 'Hash = ' + info['hash']+ '\n\nDifficulty = ' + str(info['difficulty'])+ '\nNonce = ' + str(info['nonce'])+ '\nConfirmations = ' + str(info['confirmations'])+ '\nVersion = ' + str(info['version']) + '\nMerkleroot = ' + str(info['merkleroot']) + '\n\nPreviousBlockHash = \n' + info['previousblockhash'], font = configuration["fonts"]["h3"]).pack()
    
# Metoda za dohvacanje i ispis transakcija iz mempool-a
@ClearFramesDecorator
def Transactions(frame, connection, configuration):
    if(frame == None):
        return
    frame.pack(fill="both", expand=1)
    Label(frame, text = "Transaction list:", font = configuration["fonts"]["h2"]).pack(pady=10)
    text = Text(frame, cursor="arrow")
    vsb = Scrollbar(frame, command=text.yview)
    text.configure(yscrollcommand=vsb.set)

    vsb.pack(side="right", fill="y")
    text.pack(side="left", fill="both", expand=True)

    transactions = connection.getrawmempool()
    buttons=[]
    vars=[]
    for i, trans in enumerate(transactions):
        var = IntVar(value=0)
        bg = configuration["colors"]["primary"] if i % 2 == 0 else configuration["colors"]["secondary"]
        b = Button(text, text=trans, pady=5, padx=300, command=lambda: GetTransactionInfo(connection, configuration), bg=bg)
        b.pack()
        text.window_create("end", window=b)
        text.insert("end", "\n")
        buttons.append(b)
        vars.append(var)
    text.configure(state="disabled")

# Metoda za dohvacanje i ispis detalja o transakciji
def GetTransactionInfo(connection, configuration):
    top= Toplevel()
    size=connection.getrawmempool()
    for i in size:
        txid = connection.getrawtransaction(i, True)
    Label(top, text= 'Transaction information:', font=configuration["fonts"]["h1"]).pack()
    Label(top, text= '\n\nHash = ' + txid['hash'] + '\nTxid = ' + str(txid['txid'])+ '\nSize = ' + str(txid['size']) + '\nVsize = ' + str(txid['vsize'])+ '\nWeight = ' + str(txid['weight']), font=configuration["fonts"]["h3"]).pack()

# Metoda za dohvacanje i prikaz grafa cijene BTC-a preko web browsera
def ShowPriceGraph(configuration):
    if(configuration == None):
        return
    CRYPTO = 'BTC'
    CURRENCY = 'USD'

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    last_year_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")

    start = pd.to_datetime(last_year_date)
    end = pd.to_datetime(current_date)

    crypto_data = pandas_datareader.get_data_yahoo(f'{CRYPTO}-{CURRENCY}', start, end)

    fig = graph_objects.Figure(
    data = [
        graph_objects.Scatter(
            x = crypto_data.index, 
            y = crypto_data.Close.rolling(window=1).mean(),
            mode = 'lines', 
            name = '20SMA',
            line = {'color': configuration["colors"]["primary"]}
        ),
        ]
    )

    fig.update_layout(
        title = f'The price graph for {CRYPTO}',
        xaxis_title = 'Date',
        yaxis_title = f'Price ({CURRENCY})',
        xaxis_rangeslider_visible = True
    )
    fig.update_yaxes(tickprefix='$')

    fig.show()

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
        "iconPath": GetBitcoinIconPath(rootDirectoryPath),
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

    if(configuration["iconPath"] != None):
        rootScreen.iconbitmap(configuration["iconPath"])

    rootScreen.mainloop()