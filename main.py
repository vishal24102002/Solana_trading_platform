from telethon.errors import InviteHashInvalidError, ChatIdInvalidError
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from solana.rpc.api import Client as SyncClient
from jupiter_python_sdk.jupiter import Jupiter
from solana.rpc.types import TokenAccountOpts
from solana.rpc.async_api import AsyncClient
from telethon import TelegramClient, events
from PIL import Image, ImageTk, ImageDraw
from solders.signature import Signature
from solanatracker import SolanaTracker
from solana.publickey import PublicKey
from solders.keypair import Keypair
from typing import List, Dict, Any
from customtkinter import CTkImage
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import matplotlib.pyplot as plt
from typing import List, Tuple
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk
from io import BytesIO
import threading
import requests
import asyncio
import sqlite3
import time
import json
import os

load_dotenv()

wallet_address = os.getenv("wallet_address")
TELEGRAM_BOT_TOKEN = os.getenv("") #create a new bot using botfather from telegram and paste the bot code here
TELEGRAM_USER_ID = os.getenv("") #get from userinfobot on telegram
solana_endpoint=os.getenv("solana_endpoint")
token_mint_data = {}
api_id = os.getenv("api_id") #add your telegram api id here get the id and hash from me.telegram.org
api_hash = os.getenv("api_hash") 
CHAT_IDENTIFIER = os.getenv('CHAT_IDENTIFIER') #write the  telegram invite link or the username of channel or chatid here

def create_telegram_frame(parent, initial_chat_identifier=CHAT_IDENTIFIER):
    """
    Creates a customtkinter frame for Telegram channel/group display with live message updates.
    Supports usernames, chat IDs, or invite links.

    Args:
        root: Parent customtkinter widget (required for scheduling GUI updates)
        initial_chat_identifier (str): Telegram username, chat ID, or invite link, defaults to CHAT_IDENTIFIER

    Returns:
        ctk.CTkFrame: Frame containing channel name label, input field, button, and chat frame
    """
    # Set up appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Main frame to hold all UI elements
    main_frame = ctk.CTkFrame(master=parent)

    # Channel name label
    channel_label = ctk.CTkLabel(
        main_frame,
        text="Enter a username, chat ID, or invite link below" if not initial_chat_identifier else "Loading chat...",
        font=("Arial", 20, "bold")
    )
    channel_label.pack(pady=10)

    # Entry field for chat identifier
    identifier_entry = ctk.CTkEntry(
        main_frame,
        placeholder_text="Enter @username, chat ID, or t.me link",
        width=300
    )
    identifier_entry.pack(pady=5)
    if initial_chat_identifier:
        identifier_entry.insert(0, initial_chat_identifier)

    # Button to load chat
    load_button = ctk.CTkButton(
        main_frame,
        text="Load Chat",
        command=lambda: load_chat(identifier_entry.get())
    )
    load_button.pack(pady=5)

    # Scrollable frame for chats
    chat_frame = ctk.CTkScrollableFrame(main_frame)
    chat_frame.pack(fill="both", expand=True)

    # Set to store message IDs
    message_ids = set()

    # Initialize Telegram client
    client = TelegramClient('session_name', api_id, api_hash)

    def safe_gui_update(callback):
        """Schedule a GUI update in the main thread."""
        try:
            if app.winfo_exists():
                app.after(0, callback)
        except:
            pass  # Silently handle errors

    def display_message(message):
        """Helper function to display a single message."""
        if message.id in message_ids:
            return
        message_ids.add(message.id)

        def update_gui():
            if not main_frame.winfo_exists():
                return
            message_frame = ctk.CTkFrame(chat_frame,width=175, fg_color="#2b2b2b")
            message_frame.pack(fill="x", padx=5, pady=5)
            message_frame.pack_propagate(True)

            sender = "Unknown"
            if message.sender:
                print(message.sender)
                try:
                    sender = message.sender.first_name
                except:
                    sender = message.sender.username or "Anonymous"
            timestamp = message.date.strftime("%Y-%m-%d %I:%M %p")
            sender_time = f"{sender} • {timestamp}"
            sender_label = ctk.CTkLabel(
                message_frame,
                text=sender_time,
                font=("Arial", 12, "bold"),
                text_color="#a0a0a0"
            )
            sender_label.pack(anchor="w", padx=10, pady=2)

            message_text = message.text or "No text content"
            message_label = ctk.CTkLabel(
                message_frame,
                text=message_text,
                font=("Arial", 14),
                wraplength=250,
                justify="left"
            )
            message_label.pack(anchor="w", padx=10, pady=2)

        safe_gui_update(update_gui)

    async def setup_chat(identifier):
        """Set up chat and message handlers for the given identifier."""
        if not identifier:
            safe_gui_update(lambda: channel_label.configure(text="Please enter a username, chat ID, or invite link"))
            return

        try:
            await client.start()
            # Handle different types of identifiers
            if identifier.startswith('t.me/') or identifier.startswith('https://t.me/'):
                chat = await client.get_entity(identifier)
            elif identifier.startswith('@'):
                chat = await client.get_entity(identifier)
            elif identifier.startswith('-') and identifier.lstrip('-').isdigit():
                chat = await client.get_entity(int(identifier))
            else:
                safe_gui_update(lambda: channel_label.configure(text="Invalid format. Use @username, chat ID, or t.me link"))
                return

            def update_gui():
                if not main_frame.winfo_exists():
                    return
                channel_label.configure(text=chat.title)
                # Clear previous messages
                for widget in chat_frame.winfo_children():
                    widget.destroy()
                message_ids.clear()

            safe_gui_update(update_gui)

            # Fetch initial messages
            async for message in client.iter_messages(chat, limit=20):
                display_message(message)

            # Set up event handler for new messages
            @client.on(events.NewMessage(chats=chat))
            async def handler(event):
                display_message(event.message)

        except InviteHashInvalidError:
            safe_gui_update(lambda: channel_label.configure(text="Invalid invite link. Please check and try again."))
        except ChatIdInvalidError:
            safe_gui_update(lambda: channel_label.configure(text="Invalid chat ID. Please check and try again."))
        except Exception as e:
            safe_gui_update(lambda: channel_label.configure(text=f"Error: {str(e)}"))

    def run_client(identifier):
        """Run the Telegram client in a separate thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(setup_chat(identifier))
            loop.run_until_complete(client.disconnect())  # Ensure clean disconnection
        except:
            safe_gui_update(lambda: channel_label.configure(text="Client error. Please try again."))

    def load_chat(identifier):
        """Start a new thread to load the chat with the given identifier."""
        # Avoid starting a new thread if one is already running
        if hasattr(load_chat, 'thread') and load_chat.thread.is_alive():
            safe_gui_update(lambda: channel_label.configure(text="Please wait, chat is loading..."))
            return

        # Create a new thread
        thread = threading.Thread(target=run_client, args=(identifier,), daemon=True)
        load_chat.thread = thread  # Store thread to check status
        thread.start()

    # If an identifier is provided, load it immediately
    if initial_chat_identifier:
        load_chat(initial_chat_identifier)

    return main_frame

def get_token_name_price(contractor: str):
    """
    Fetch token name, price, price in SOL, and symbol for a given contractor address.
    Uses cached data if available, otherwise makes an API call.

    Args:
        contractor (str): The token's contractor address.

    Returns:
        list: [name, price_usd, price_in_sol, symbol]
    """
    # Check if data is already in cache
    if contractor in token_mint_data:
        return token_mint_data[contractor]

    # If not in cache, fetch from API
    url = f"https://crimson-ancient-market.solana-mainnet.quiknode.pro/7b1dfa5a6af169b6c5bv4i1s4h6aala362be45238935b5/addon/912/networks/solana/tokens/{contractor}"
    print("api_called")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        summary = data.get('summary', {})
        name = data.get("name", "Unknown")
        price = summary.get("price_usd", 0.0)
        price_in_sol = data.get("data", {}).get("priceSol", 0.0)
        symbol = data.get("symbol", "Unknown")
        price_changes = {
            '24hr': summary.get('24h',{}).get('last_price_usd_change', 0.0),  # 24h change not provided in sample data
            '6hr': summary.get('6h', {}).get('last_price_usd_change', 0.0),
            '1hr': summary.get('1h', {}).get('last_price_usd_change', 0.0),
            '30min': summary.get('30m', {}).get('last_price_usd_change', 0.0),
            '15min': summary.get('15m', {}).get('last_price_usd_change', 0.0),
            '5min': summary.get('5m', {}).get('last_price_usd_change', 0.0),
            '1min': summary.get('1m', {}).get('last_price_usd_change', 0.0)
        }

        # Store in cache
        token_mint_data[contractor] = [name, price, price_in_sol, symbol,price_changes]
        return token_mint_data[contractor]

    except Exception as e:
        print(f"Error fetching token data for {contractor}: {str(e)}")
        # Return default values if API call fails
        default_response = ["Unknown", 0.0, 0.0, "Unknown"]
        token_mint_data[contractor] = default_response
        return default_response

def create_circular_image_frame(parent, image_url, size=50, command=None):
    parent_fg_color = parent.cget("fg_color") if parent.cget("fg_color") else "transparent"
    frame = ttk.Frame(parent, width=size, height=size)
    frame.configure(style="Transparent.TFrame")

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image = image.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        circular_image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circular_image.paste(image, (0, 0), mask)
        frame.photo = ImageTk.PhotoImage(circular_image)
        image_label = ttk.Label(frame, image=frame.photo, background=parent_fg_color[1], style="Transparent.TLabel")
        image_label.place(relx=0.5, rely=0.5, anchor="center")
    except Exception as e:
        print(f"Error loading image from URL: {str(e)}")
        image_label = ttk.Label(frame, text="No Image", background="gray", foreground="white", style="Transparent.TLabel")
        image_label.place(relx=0.5, rely=0.5, anchor="center")

    def on_click(event):
        if command:
            command()

    frame.bind("<Button-1>", on_click)
    image_label.bind("<Button-1>", on_click)

    return frame

def load_token_list() -> Dict[str, Dict[str, str]]:
    """
    Load Solana token list from a public source.
    Returns a dictionary mapping mint addresses to token names and symbols.
    """
    try:
        url = "https://token.jup.ag/all"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        token_list = response.json()
        token_map = {
            "7fZYHRFgq1k1W6yHH1hf6VepQHQzGS3yNjuLgCmGpump": {"name": "GRUG", "symbol": "GRUG","url":"https://ipfs.io/ipfs/QmYye4cmhdXaNsnHkzDDGVvbWaJnZrkPj9iPsc5quwkGB1"},
            "fRfKGCriduzDwSudCwpL7ySCEiboNuryhZDVJtr1a1C": {"name": "Dupe", "symbol": "DUPE","url":"https://ipfs.io/ipfs/bafkreiaobt2ookhhoslvvard6oyjc6fw4askhg232yh22aqcgdddhrbcdy"},
            "A7S4UkbpAXSVfG196Qvr8TMvpvx3Lz2Q4X2RecuApump": {"name": "Hood Mr Beast", "symbol": "MRLEAST","url":"https://ipfs.io/ipfs/QmY7VJWPYcg4iGTzhQZYejW2BRpa2Kcpg42W8xi3nGW2md"}
        }
        for token in token_list:
            mint_address = token["address"]
            token_map[mint_address] = {
                "name": token['name'],
                "symbol": token['symbol'],
                "url":token.get('logoURI',"none")
            }
        return token_map
    except Exception as e:
        print(f"Error loading token list: {str(e)}")
        return {}

def get_phantom_wallet_tokens() -> List[Dict[str, Any]]:
    """
    Fetch token names and balances from a Phantom wallet on the Solana blockchain.

    Args:
        solana_endpoint (str): Solana RPC endpoint URL
    """
    try:
        # Initialize Solana client
        client = SyncClient(solana_endpoint)

        # Validate wallet address
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
        except ValueError as e:
            print(f"Invalid wallet address: {str(e)}")
            return []

        # Get SOL balance
        try:
            sol_balance_response = client.get_balance(wallet_pubkey)
            sol_balance = sol_balance_response.value / 1_000_000_000  # Convert lamports to SOL
        except Exception as e:
            print(f"Error fetching SOL balance: {str(e)}")
            sol_balance = 0.0

        # Load token list for name mapping
        token_map = load_token_list()

        # Get all token accounts owned by the wallet
        try:
            token_accounts_response = client.get_token_accounts_by_owner(
                wallet_pubkey,
                TokenAccountOpts(program_id= Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VlQa5hDsAilv"))
            )
            token_accounts = token_accounts_response.value
        except Exception as e:
            token_accounts = []

        token_list = [{"name": "Solana", "symbol": "SOL", "balance": sol_balance,"mint_address":"So11111111111111111111111111111111111111112","url":"https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png"}]

        # Iterate through token accounts
        for account in token_accounts:
            try:
                # Get token account info
                account_data_response = client.get_token_account_balance(account.pubkey)
                balance = float(account_data_response.value.ui_amount_string)

                # Get token mint address
                account_info_response = client.get_account_info(account.pubkey)
                if account_info_response.value is None or not account_info_response.value.data:
                    continue
                mint_address = Pubkey.from_bytes(account_info_response.value.data[0:32])
                mint_str = str(mint_address)


                # Get token name and symbol from token map
                token_info = token_map.get(mint_str, {"name": "unknown", "symbol": "unknown","url":None})
                token_list.append({
                    "name": token_info["name"],
                    "symbol": token_info["symbol"],
                    "balance": balance,
                    "mint_address": mint_str,
                    "url":token_info["url"]
                })
            except Exception as e:
                print(f"Error processing token account {account.pubkey}: {str(e)}")
                continue

        return token_list

    except Exception as e:
        print(f"Error fetching wallet data: {str(e)}")
        return []

# Function to create a SQLite database and table to store the private key
def create_db():
    conn = sqlite3.connect('wallets.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        private_key TEXT
    )''')
    conn.commit()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_name TEXT NOT NULL,
            contract_address_in TEXT NOT NULL,
            contract_address_out TEXT NOT NULL,
            buying_price REAL NOT NULL,
            number_of_tokens REAL NOT NULL,
            date_of_buying TEXT NOT NULL,
            type TEXT NOT NULL,
            Transaction_link TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Function to check if the private key is already stored in the database
def get_private_key_from_db():
    conn = sqlite3.connect('wallets.db')
    cursor = conn.cursor()
    cursor.execute("SELECT private_key FROM wallet ORDER BY id DESC LIMIT 1")
    private_key = cursor.fetchone()
    conn.close()
    return private_key[0] if private_key else None

# Function to store the private key in the database
def store_private_key_in_db(private_key):
    conn = sqlite3.connect('wallets.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO wallet (private_key) VALUES (?)", (private_key,))
    conn.commit()
    conn.close()

# Function to prompt the user for the private key
def ask_for_private_key():
    global app
    def save_private_key():
        private_key = entry_private_key.get()
        if private_key:
            store_private_key_in_db(private_key)
            top.destroy()  # Close the prompt window
        else:
            print("Private key cannot be empty")

    # Create a new top-level window to ask for the private key
    top = ctk.CTkToplevel(app)
    top.title("Enter Wallet Private Key")
    top.geometry("400x200")

    label_private_key = ctk.CTkLabel(top, text="Enter your Wallet Private Key:")
    label_private_key.pack(pady=10)

    entry_private_key = ctk.CTkEntry(top, show="*")  # Hide text for private key entry
    entry_private_key.pack(pady=10)

    button_save = ctk.CTkButton(top, text="Save", command=save_private_key)
    button_save.pack(pady=10)

    top.mainloop()

# Function to get the private key for future use
def get_wallet_private_key():
    private_key = get_private_key_from_db()
    if private_key:
        return private_key
    else:
        ask_for_private_key()
        return get_wallet_private_key()  # Try fetching again after user input


# Async function to fetch Jupiter quote
async def fetch_jupiter_quote():
    # Check if the private key exists in the database or prompt the user to enter it
    wallet_private_key = get_wallet_private_key()

    # Use `wallet_private_key` wherever required in your app for authentication or transactions

    try:
        client = AsyncClient(solana_endpoint)
        keypair = Keypair.from_base58_string(wallet_private_key)  # Replace with your actual key
        jupiter = Jupiter(client, keypair)

        quote = await jupiter.quote("So11111111111111111111111111111111111111112",  # SOL
                                    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                                    1_000_000)  # 1 SOL in lamports

        await client.close()
    except Exception as e:
        print("Jupiter quote fetch error:", e)

# Wrapper for GUI button
def run_jupiter_quote():
    threading.Thread(target=asyncio.run(fetch_jupiter_quote()))

def connect_wallet_and_display():
    for widget in subframe2.winfo_children():
        widget.destroy()

    main_label = ctk.CTkLabel(subframe2, text="Wallet info",font=("Helvetica", 16, "bold"))
    main_label.pack(anchor="center",side="top",pady=10)
    subframe2_1 = ctk.CTkScrollableFrame(subframe2, fg_color="transparent", width=450, height=400,scrollbar_fg_color="transparent",scrollbar_button_color="gray21")
    subframe2_1.pack()

    # Show loading animation
    loading_widget = loading_icon(subframe2_1)

    def fetch_tokens():
        try:
            tokens = get_phantom_wallet_tokens(solana_endpoint)

            # Update the GUI on the main thread
            subframe2_1.after(0, lambda: display_tokens(tokens, loading_widget, subframe2_1))

        except Exception as e:
            subframe2_1.after(0, lambda: show_error_message(e, loading_widget, subframe2_1))

    # Run token fetching in background thread
    threading.Thread(target=fetch_tokens, daemon=True).start()


def display_tokens(tokens, loading_widget, parent_frame):
    if loading_widget:
        loading_widget.destroy()

    for idx, token in enumerate(tokens):
        Token_frame = ctk.CTkFrame(parent_frame, width=400)
        Token_frame.pack(pady=10)
        Token_frame.pack_propagate(True)

        def on_click(event, token=token):
            for widget in temp_price_ch.winfo_children():
                widget.destroy()
            entry_coin_name.delete(0, "end")
            entry_coin_name.insert(0, token["name"])

            entry_current_price.delete(0, "end")

            entry_contract.delete(0, "end")
            entry_contract.insert(0, token['mint_address'])

            frame=create_price_change_frame(subframe0_1,token['mint_address'])
            frame.grid(row=0,column=1,padx=10,pady=10,sticky="nsew")

            # Setup price graph and get thread
            price_thread = setup_price_graph(
                temp_price_ch,
                token['mint_address'],
                "https://api.raydium.io/v2/main/price",
                120,
                 60 * 60,
                 token_name=token["name"]
            )

            entry_buy_price.delete(0, "end")
            entry_buy_price.insert(0, "1.71")

            try:
                fetch_coin_data()
            except:
                pass

            entry_total_tokens.configure(state="normal")

            entry_total_tokens.delete(0,"end")
            entry_total_tokens.insert(0,token['balance'])

        Token_frame.bind("<Button-1>", on_click)

        if token.get("url")!="none":
            logo_frame = create_circular_image_frame(
                parent=Token_frame,
                image_url=token["url"],
                size=50,
                command=lambda t=token: show_token_details(t)
            )
            logo_frame.grid(row=0, column=0, rowspan=2, padx=5)

        token_name_label = ctk.CTkLabel(Token_frame, text=token["name"])
        token_name_label.grid(row=0, column=2)

        token_bal_label = ctk.CTkLabel(Token_frame, text=token['balance'],font=("Helvetica", 16,"bold"))
        token_bal_label.grid(row=0, column=4, padx=5)

        if "mint_address" in token:
            token_mintadd_label = ctk.CTkLabel(Token_frame, text=token['mint_address'])
            token_mintadd_label.grid(row=1, column=1, columnspan=4, padx=10)


def show_error_message(error, loading_widget, parent_frame):
    if loading_widget:
        loading_widget.destroy()
    error_label = ctk.CTkLabel(parent_frame, text=f"Error: {str(error)}", text_color="red")
    error_label.pack(pady=10)

def loading_icon(parent_frame, gif_path="C:/Users/Admin/Downloads/Animation - 1746945699452.gif"):
    try:
        if not os.path.exists(gif_path):
            return None

        loading_image = Image.open(gif_path)
        frames = []
        try:
            frame_count = 0
            while True:
                frame = loading_image.copy()
                frame = frame.resize((150, 150), Image.LANCZOS)  # 100x100 for visibility
                frames.append(ctk.CTkImage(light_image=frame, dark_image=frame, size=(150, 150)))
                frame_count += 1
                loading_image.seek(loading_image.tell() + 1)
        except EOFError:
            print(f"Extracted {frame_count} frames from GIF")

        if not frames:
            # Fallback: Display a static red square
            fallback_image = Image.new("RGB", (150, 150), color="red")
            fallback_ctk_image = ctk.CTkImage(light_image=fallback_image, dark_image=fallback_image, size=(150, 150))
            loading_label = ctk.CTkLabel(
                parent_frame,
                image=fallback_ctk_image,
                text="GIF Failed",
                fg_color="transparent"
            )
            loading_label.pack(expand=True,anchor="center")
            return loading_label
        loading_label = ctk.CTkLabel(
            parent_frame,
            image=frames[0],
            text="",
            fg_color="transparent"
        )
        loading_label.pack(expand=True,fill="y",anchor="center")
        parent_frame.update()  # Force initial render
        # Animation function
        def animate(index=0):
            if loading_label.winfo_exists() and frames:
                loading_label.configure(image=frames[index])
                parent_frame.update_idletasks()
                index = (index + 1) % len(frames)
                loading_label.after_id = parent_frame.after(25, animate, index)
        animate()
        # Store frames to prevent garbage collection
        loading_label.frames = frames
        return loading_label
    except Exception as e:
        # Fallback: Display a static red square
        fallback_image = Image.new("RGB", (100, 100), color="red")
        fallback_ctk_image = ctk.CTkImage(light_image=fallback_image, dark_image=fallback_image, size=(100, 100))
        loading_label = ctk.CTkLabel(
            parent_frame,
            image=fallback_ctk_image,
            text="GIF Error",
            fg_color="transparent"
        )
        loading_label.pack(pady=10, padx=10, anchor="center")
        return loading_label

# Function to fetch data from Birdeye API
def fetch_coin_data():
    contract = entry_contract.get().strip()
    try:
        token_dat=get_token_name_price(contract)
        entry_coin_name.delete(0, "end")
        entry_coin_name.insert(0, token_dat[0])
        entry_sol_price.delete(0, "end")
        entry_sol_price.insert(0, f"{token_dat[2]:.8f}")
        entry_current_price.delete(0, "end")
        entry_current_price.insert(0, f"{token_dat[1]:.8f}")
        # if (trigger_invested_type.get()=="default"):
        #     entry_investment.delete(0, "end")
        #     entry_investment.insert(0, f"100")
    except Exception as e:
        print("Error fetching coin data:", e)

async def perform_token_swap(
    private_key: str,
    input_mint: str,
    output_mint: str,
    amount: float,
    slippage: float = 30,
    priority_fee: float = 0.00005
):
    """
    Perform a token swap using SolanaTracker.
    Args:
        private_key (str): Base58-encoded private key.
        input_mint (str): Mint address of input token.
        output_mint (str): Mint address of output token.
        amount (float): Amount of input token to swap.
        slippage (float): Allowed slippage in percent (default is 30).
        priority_fee (float): Priority fee in SOL (default is 0.00005).

    Returns:
        str: Transaction ID of the swap.
    """
    live_data_out=get_token_name_price(contractor=output_mint)
    live_data_in=get_token_name_price(contractor=input_mint)
    start_time = time.time()
    keypair = Keypair.from_base58_string(private_key)
    solana_tracker = SolanaTracker(keypair, "https://rpc.solanatracker.io/public?advancedTx=true")

    try:
        swap_response = await solana_tracker.get_swap_instructions(
                input_mint,
                output_mint,
                amount,
                slippage,
                str(keypair.pubkey()),
                priority_fee,
            )

        custom_options = {
            "send_options": {"skip_preflight": True, "max_retries": 5},
            "confirmation_retries": 50,
            "confirmation_retry_timeout": 1000,
            "last_valid_block_height_buffer": 200,
            "commitment": "processed",
            "resend_interval": 1500,
            "confirmation_check_interval": 100,
            "skip_confirmation_check": False,
        }

        send_time = time.time()
        txid = await solana_tracker.perform_swap(swap_response, options=custom_options)
        end_time = time.time()

        if not txid:
            return

        print("✅ Transaction ID:", txid)
        print("🔗 View on Solscan:", f"https://solscan.io/tx/{txid}")

        suclabel = ctk.CTkLabel(subframe3_1, text="✅ Sucessfully completed !!!", font=("Helvetica", 16, "bold"),
                                text_color="green")
        suclabel.grid(row=8, column=1, columnspan=2)

        solana_client = SyncClient(solana_endpoint)
        tx_signature = Signature.from_string(txid)
        tx_data = solana_client.get_transaction(tx_signature, encoding="jsonParsed", max_supported_transaction_version=0)

        if not tx_data.value:
            suclabel=ctk.CTkLabel(subframe3_1,text=f"❌ No transaction found for ID: {txid} ",font=("Helvetica", 16,"bold"),text_color="red")
            suclabel.grid(row=8,column=1,columnspan=2)
            return None

        no_of_tokens = (live_data_in[1] * amount) / live_data_out[1]
        update_token_purchase(live_data_out[0], input_mint, output_mint, float(live_data_out[1]), f"{no_of_tokens:.20f}",f"https://solscan.io/tx/{txid}")
        contractor_man_buy_Entry_in.delete(0,"end")
        contractor_man_buy_Entry.delete(0,"end")
        return f"https://solscan.io/tx/{txid}"

    except Exception as e:
        suclabel=ctk.CTkLabel(subframe3_1,text=f"❌ Failed {e} !!!",font=("Helvetica", 16,"bold"),text_color="red")
        suclabel.grid(row=8,column=1,columnspan=2)
        return None

def get_buying_price(contractor: str) -> float:
    """
    Fetch the buying price for a token with the given contract_address_out.

    Args:
        contractor (str): The contract address to match against contract_address_out.

    Returns:
        float: The buying price, or 0.0 if not found or an error occurs.
    """
    try:
        conn = sqlite3.connect('wallets.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT buying_price
            FROM token_purchases
            WHERE contract_address_out = ?
        """, (contractor,))
        result = cursor.fetchone()
        conn.close()

        return float(result[0]) if result else 0.0
    except Exception as e:
        print(f"Error fetching buying price for {contractor}: {str(e)}")
        return 0.0

def calculate_profit():
    client=SyncClient(solana_endpoint)
    wallet_pubkey = Pubkey.from_string(wallet_address)
    while True:
        token_accounts_response = client.get_token_accounts_by_owner(
            wallet_pubkey,
            TokenAccountOpts(program_id= Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
        )
        token_accounts = token_accounts_response.value
        # Iterate through token accounts
        for account in token_accounts:
            # Get token account info
            account_data_response = client.get_token_account_balance(account.pubkey)
            # Get token mint address
            account_info_response = client.get_account_info(account.pubkey)
            mint_address = Pubkey.from_bytes(account_info_response.value.data[0:32])
            mint_str = str(mint_address)
            try:
                del token_mint_data[mint_str]
            except:
                pass
            buying_price=get_buying_price(mint_str)
            current_price=get_token_name_price(mint_str)[1]
            num_tokens= float(account_data_response.value.ui_amount_string)
            profit=num_tokens * (current_price - buying_price)
            print(profit)
            if profit>=2*buying_price:
                send_telegram_call(buying_price,get_token_name_price(mint_str)[1],get_token_name_price(mint_str)[0])
        time.sleep(300)

def star_profit_checker():
    if checkox_automation.get():
        threading.Thread(target=calculate_profit).start()

def update_token_purchase(
    token_name: str,
    contract_address_in: str,
    contract_address_out: str,
    new_buying_price: float,
    new_number_of_tokens: float,
    transaction_link: str,
    date_of_buying: str = None
):
    """
    Update or insert a record in the token_purchases table based on contract_address_out.
    Updates buying_price using the weighted average formula, combines transaction links,
    and updates total tokens and date.

    Args:
        token_name (str): Name of the token.
        contract_address_in (str): Input mint address.
        contract_address_out (str): Output mint address (used to check for existing data).
        new_buying_price (float): Buying price of the new tokens.
        new_number_of_tokens (float): Number of new tokens purchased.
        transaction_link (str): New transaction link (e.g., Solscan URL).
        type_of_transaction (str): Type of transaction ('Buy' or 'Sell').
        date_of_buying (str, optional): Date of the transaction. Defaults to current time.
    """
    if checkbox_var.get():
        type_of_transaction="Sell"
    else:
        type_of_transaction="Buy"
    if date_of_buying is None:
        date_of_buying = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect("wallets.db")
        cursor = conn.cursor()

        # Check if data exists for contract_address_out
        cursor.execute("""
            SELECT number_of_tokens, buying_price, Transaction_link
            FROM token_purchases
            WHERE contract_address_out = ?
        """, (contract_address_out,))
        existing_data = cursor.fetchone()

        if existing_data:
            # Existing data found: update the record
            old_number_of_tokens, old_buying_price, old_transaction_link = existing_data

            # Calculate total tokens
            total_tokens = old_number_of_tokens + new_number_of_tokens

            # Calculate new buying price using the formula
            if total_tokens > 0:  # Avoid division by zero
                new_buying_price_calculated = (
                    (old_number_of_tokens * old_buying_price) +
                    (new_number_of_tokens * new_buying_price)
                ) / total_tokens
            else:
                new_buying_price_calculated = new_buying_price

            # Combine transaction links
            combined_transaction_links = (
                f"{old_transaction_link},{transaction_link}"
                if old_transaction_link
                else transaction_link
            )

            # Update the record
            cursor.execute("""
                UPDATE token_purchases
                SET token_name = ?,
                    contract_address_in = ?,
                    buying_price = ?,
                    number_of_tokens = ?,
                    date_of_buying = ?,
                    type = ?,
                    Transaction_link = ?
                WHERE contract_address_out = ?
            """, (
                token_name,
                contract_address_in,
                new_buying_price_calculated,
                total_tokens,
                date_of_buying,
                type_of_transaction,
                combined_transaction_links,
                contract_address_out
            ))
            print(f"Updated record for contract_address_out: {contract_address_out}")

        else:
            # No existing data: insert a new record
            cursor.execute("""
                INSERT INTO token_purchases (
                    token_name,
                    contract_address_in,
                    contract_address_out,
                    buying_price,
                    number_of_tokens,
                    date_of_buying,
                    type,
                    Transaction_link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                token_name,
                contract_address_in,
                contract_address_out,
                new_buying_price,
                new_number_of_tokens,
                date_of_buying,
                type_of_transaction,
                transaction_link
            ))
            print(f"Inserted new record for contract_address_out: {contract_address_out}")

        conn.commit()

    except Exception as e:
        print(f"Error updating token_purchases table: {str(e)}")
    finally:
        conn.close()

def create_price_change_frame(parent,contractor: str) -> ctk.CTkFrame:

    """
    Create a CustomTkinter frame to display price changes for a token.

    Args:
        parent: The parent widget (e.g., subframe3).
        contractor (str): The token's contractor address.

    Returns:
        ctk.CTkFrame: The frame containing price change labels.
    """
    # Create frame
    price_frame = ctk.CTkFrame(parent, fg_color="gray20", corner_radius=10)

    # Title
    title_label = ctk.CTkLabel(
        price_frame,
        text="Price Change (USD)",
        font=("Helvetica", 16, "bold")
    )
    title_label.grid(row=0,column=0,columnspan=2,pady=5)

    # Fetch price changes
    try:
        price_changes = get_token_name_price(contractor)[4]
    except:
        pass
    # Time periods and their labels
    time_periods = [
        ('24hr', '24 Hours'),
        ('6hr','6 Hours'),
        ('1hr', '1 Hour'),
        ('30min', '30 Minutes'),
        ('15min', '15 Minutes'),
        ('5min', '5 Minutes'),
        ('1min', '1 Minute')
    ]

    # Display each time period
    for i,(period_key, period_label) in enumerate(time_periods):
        change = price_changes.get(period_key, 0.0)

        # Color based on positive/negative change
        text_color = "green" if change >= 0 else "red"
        sign = "+" if change >= 0 else ""

        # Create label for this period
        time_label=ctk.CTkLabel(price_frame,text=period_label,font=("Helvetica", 14,"bold"))
        time_label.grid(row=i+1,column=0, padx=10,pady=5)
        change_label = ctk.CTkLabel(
            price_frame,
            text=f": {sign}{change:.5f} USD",
            font=("Helvetica", 14),
            text_color=text_color
        )
        change_label.grid(row=i+1, column=1, padx=10,pady=5)

    return price_frame


create_db()
# UI Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")
app = ctk.CTk()
app.geometry("1400x800")
app.title("Vireonix Trading Platform")
# Sidebar
frame_sidebar = ctk.CTkFrame(app, width=450)
frame_sidebar.pack(side="left", fill="y")
setting_but=ctk.CTkButton(frame_sidebar,text="Setting   ⚙️",)
setting_but.pack(padx=10,pady=35)

checkbox_auto_var = ctk.BooleanVar(value=False)
checkox_automation=ctk.CTkCheckBox(frame_sidebar,variable=checkbox_auto_var,text="Automation",command=star_profit_checker)
checkox_automation.pack(side="bottom",padx=10,pady=15)

# Main Frame
frame_main = ctk.CTkFrame(app)
frame_main.pack(side="left", fill="both", expand=True)
frame_main.grid_rowconfigure((0, 1), weight=1)
frame_main.grid_columnconfigure((0, 1), weight=1)
subframe0 = ctk.CTkFrame(frame_main)
subframe0.grid(row=0, column=0,columnspan=2, sticky="nsew", padx=10, pady=10)

subframe0_1 = ctk.CTkFrame(subframe0)
subframe0_1.pack(expand=True)

# Subframe1 for Buy Panel
subframe1 = ctk.CTkFrame(subframe0_1,fg_color="transparent")
subframe1.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")
# Grid-based Input Fields
labels = [
    ("Coin Name:", "entry_coin_name"),
    ("Contract Address:", "entry_contract"),
    ("Buying Price:", "entry_buy_price"),
    ("Current Price in SOL:", "entry_sol_price"),
    ("Current Price in USDT:", "entry_current_price"),
    ("Total Tokens:", "entry_total_tokens"),
    # ("Return %:", "entry_return_percent")
]

entries = {}
for idx, (label_text, var_name) in enumerate(labels):
    label = ctk.CTkLabel(subframe1, text=label_text)
    label.grid(row=idx, column=0, padx=5, pady=5, sticky="e")
    state = "normal" if "Tokens" not in label_text and "Return" not in label_text else "readonly"
    entry = ctk.CTkEntry(subframe1, state=state)
    entry.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
    globals()[var_name] = entry

#investment default
# investment_label=ctk.CTkLabel(subframe1,text="Current investment:")
# investment_label.grid(row=len(labels)+1, column=0, padx=5, pady=5, sticky="e")
# trigger_invested_type = ctk.StringVar(value="Set invested price Trigger")
# invested=ctk.CTkOptionMenu(subframe1, variable=trigger_invested_type,width=200,
#                                      values=["SOL", "$", "default"])
# invested.grid(row=len(labels)+1, column=1, padx=5, pady=5, sticky="w")
#
# label = ctk.CTkLabel(subframe1, text="Investment label")
# label.grid(row=len(labels)+2, column=0, padx=5, pady=5, sticky="e")
#
# entry_inv = ctk.CTkEntry(subframe1, state="normal")
# entry_inv.grid(row=len(labels)+2, column=1, padx=5, pady=5, sticky="w")
# globals()["entry_investment"] = entry_inv
frame_sidebar1=ctk.CTkFrame(frame_sidebar)
frame_sidebar1.pack(anchor="center",expand=True)
# Trigger Dropdown
trigger_label = ctk.CTkLabel(frame_sidebar1, text="Set auto selling Trigger:")
trigger_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

trigger_var = ctk.StringVar(value="Set Trigger")
trigger_dropdown = ctk.CTkOptionMenu(frame_sidebar1, variable=trigger_var,width=200,
                                     values=["50% at 2.5x & 50% at 4.5x", "50% at 2.5x & 50% at 6.5x", "50% at 5x & 50% at 10x", "Custom"])
trigger_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky="w")

# Telegram Call Options Dropdown
call_label = ctk.CTkLabel(frame_sidebar1, text="Telegram Call Options:")
call_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

call_var = ctk.StringVar(value="Select Option")
call_dropdown = ctk.CTkOptionMenu(frame_sidebar1, variable=call_var,
                                  values=["2x", "3x", "4x", "6x", "8x", "10x"])
call_dropdown.grid(row=3, column=0, padx=5, pady=5, sticky="w")

# Fetch Button
fetch_btn = ctk.CTkButton(subframe1, text="Fetch Coin Info", command=fetch_coin_data)
fetch_btn.grid(row=len(labels)+4, column=1, columnspan=2, pady=5)

# Telegram Notify with Twilio Call
def send_telegram_call(buying_price,current_price,token_name):
    print("Telegram call triggered")

    try:
        buy_price = float(buying_price)
        current_price = float(current_price)
        trigger = trigger_var.get()

        if "x" in trigger:
            multiplier = float(trigger.replace("x", ""))
            target_price = buy_price * multiplier
            if current_price >= target_price:
                message = f"Token {token_name} has hit {multiplier}x!\nCurrent Price: {current_price}"
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {"chat_id": TELEGRAM_USER_ID, "text": message}
                response = requests.post(url, data=data)

                if response.status_code == 200:
                    print("Telegram message sent!")
                else:
                    print("Failed to send Telegram message.")
                account_sid = 'ACcv2i3schfa0r1mea4de6125f782eafb3b48091b'
                auth_token = '9sFHDaVRDmUA4NWZKFNC4WLM4ZYFD5'
                client = Client(account_sid, auth_token)

                call = client.calls.create(
                    to='+91 8882083822',  # Replace with your number
                    from_='+1 208 418 0548',  # Twilio number
                    twiml='<Response><Say>Your coin has reached your targeted price rage you can now sell it.</Say></Response>'
                )
                print("Call initiated successfully")
        else:
            print("Please select a valid trigger.")
    except Exception as e:
        print("Error sending call:", e)

send_btn = ctk.CTkButton(frame_sidebar1, text="Send Telegram Call", command=send_telegram_call)
send_btn.grid(row=4, column=0, columnspan=2,padx=10 ,pady=20)

subframe2 = ctk.CTkFrame(frame_main)
subframe2.grid(row=0, column=2,sticky="nsew", padx=10, pady=10)

connect_wallet_button=ctk.CTkButton(subframe2,text="Connect wallet using private key" ,command=connect_wallet_and_display)
connect_wallet_button.pack(expand=True)

subframe3=ctk.CTkFrame(frame_main)
subframe3.grid(row=1,column=0,sticky="nsew", padx=10, pady=10)

subframe3_1=ctk.CTkFrame(subframe3,fg_color="transparent")
subframe3_1.pack(expand=True,fill="y")

Label=ctk.CTkLabel(subframe3_1,text="Buy Manually",font=("Helvetica", 16, "bold"))
Label.grid(row=0,column=0,columnspan=3,padx=10,pady=10)

contractor_man_buy_Entry_in=ctk.CTkEntry(subframe3_1,placeholder_text="Contractor Address of the token used",width=250)
contractor_man_buy_Entry_in.grid(row=2,column=1,padx=10,pady=10)

contractor_man_buy_Entry=ctk.CTkEntry(subframe3_1,placeholder_text="Contractor Address of token to get",width=250)
contractor_man_buy_Entry.grid(row=3,column=1,padx=10,pady=10)

# Amount_label=ctk.CTkLabel(subframe3_1,text="$ 100",text_color="Green",font=("Helvetica", 16,))
# Amount_label.grid(row=4,column=1,padx=10,pady=10)

checkbox_var = ctk.BooleanVar(value=False)

def toggle_button():
    if checkbox_var.get():
        add_custom_tokens.grid(row=3,column=1)
        contractor_man_sell_button.grid(row=7,column=1,padx=10,pady=10) # Show button
        contractor_man_buy_button.grid_forget()
        contractor_man_buy_Entry.grid_forget()
    else:
        contractor_man_sell_button.grid_forget()
        contractor_man_buy_button.grid(row=6,column=1,padx=10,pady=10)
        contractor_man_buy_Entry.grid(row=3,column=1,padx=10,pady=10)

# Checkbox
checkbox = ctk.CTkCheckBox(subframe3_1, text="I want to swap tokens to get SOL Token",width=150, variable=checkbox_var, command=toggle_button)
checkbox.grid(row=5,column=1,columnspan=2,padx=10,pady=10)

add_custom_tokens=ctk.CTkEntry(subframe3_1,placeholder_text="tokens to send")

contractor_man_buy_button=ctk.CTkButton(subframe3_1,text="Buy",command=lambda:asyncio.run(perform_token_swap(get_wallet_private_key(),contractor_man_buy_Entry_in.get(),contractor_man_buy_Entry.get(),0.004)))
contractor_man_buy_button.grid(row=6,column=1,padx=10,pady=10)

contractor_man_sell_button=ctk.CTkButton(subframe3_1,text="Sell the selected token",command=lambda:asyncio.run(perform_token_swap(get_wallet_private_key(),contractor_man_buy_Entry_in.get(),"So11111111111111111111111111111111111111112",float(add_custom_tokens.get()))))
# contractor_man_buy_button.grid(row=4,column=1,padx=10,pady=10)

def setup_price_graph(
    graph_frame: ctk.CTkFrame,
    mint_address: str,
    raydium_price_api: str,
    poll_interval: int,
    duration: int,
    token_name=str
) -> threading.Thread:
    """
    Set up a live price graph in the provided CustomTkinter frame and return the thread.
    The graph updates at the specified poll interval with price data from the Raydium API.
    Green lines for price increases, red for decreases, white for no change.
    Uses a dark theme with white text and no grid.
    The thread stops if the graph frame is destroyed.

    Args:
        graph_frame: The CTkFrame to embed the graph in.
        mint_address: Solana token mint address.
        raydium_price_api: URL of the Raydium price API.
        poll_interval: Time between API polls (in seconds).
        duration: Total duration to collect data (in seconds).

    Returns:
        threading.Thread: The thread running the price collection.
    """
    # Local variables for this graph instance
    price_data: List[Tuple[float, float]] = []
    is_running = False
    fig = None
    ax = None
    canvas = None

    def fetch_price_data() -> float:
        """
        Fetch current price for the Solana token from the Raydium API.
        Returns price in USD or None if failed.
        """
        try:
            response = requests.get(raydium_price_api)
            response.raise_for_status()
            data = response.json()

            if mint_address not in data:
                return None

            return float(data[mint_address])
        except requests.RequestException:
            return None

    def collect_price_data():
        """Collect price data in a separate thread and update the plot."""
        nonlocal price_data, is_running
        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time and is_running:
            price = fetch_price_data()
            if price is not None:
                price_data.append((time.time(), price))
                update_plot()

            time.sleep(poll_interval)

    def update_plot():
        """Update the matplotlib plot with new price data, coloring slopes based on price change."""
        nonlocal price_data, ax, fig, canvas
        if not price_data:
            return

        ax.clear()
        timestamps = [datetime.fromtimestamp(ts) for ts, _ in price_data]
        prices = [price for _, price in price_data]

        # Plot line segments with color based on price change
        for i in range(1, len(price_data)):
            x_segment = [timestamps[i-1], timestamps[i]]
            y_segment = [prices[i-1], prices[i]]
            # Green for increase, red for decrease, white for no change
            if prices[i] > prices[i-1]:
                color = 'green'
            elif prices[i] < prices[i-1]:
                color = 'red'
            else:
                color = 'white'
            ax.plot(x_segment, y_segment, color=color, linewidth=2)

        ax.set_title(f"Token Price History {token_name}", color='white')
        ax.set_xlabel("Time", color='white')
        ax.set_ylabel("Price (USD)", color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        # Add dummy plots for legend
        ax.plot([], [], 'green', label='Price Increase')
        ax.plot([], [], 'red', label='Price Decrease')
        ax.plot([], [], 'white', label='No Change')
        ax.legend(labelcolor='white')
        ax.set_facecolor('#1c2526')  # Dark background
        fig.set_facecolor('#1c2526')  # Match figure background
        fig.autofmt_xdate(rotation=45)
        canvas.draw()

    def stop_price_collection():
        """Stop the price collection thread."""
        nonlocal is_running
        is_running = False

    # Setup plot with dark theme
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    ax.set_title(f"Token Price History (Mint: {mint_address[:8]}...)", color='white')
    ax.set_xlabel("Time", color='white')
    ax.set_ylabel("Price (USD)", color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_facecolor('#1c2526')  # Dark background
    fig.set_facecolor('#1c2526')  # Match figure background
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Start price collection thread
    is_running = True
    thread = threading.Thread(target=collect_price_data, daemon=True)
    thread.start()

    # Bind frame destruction to stop the thread
    graph_frame.bind("<Destroy>", lambda event: stop_price_collection())

    return thread

# Placeholder subframes for now
temp_price_ch = ctk.CTkFrame(frame_main)
temp_price_ch.grid(row=1, column=1,columnspan=2,sticky="nsew",padx=10, pady=10)

telegram_frame=ctk.CTkFrame(frame_main)
telegram_frame.grid(row=0,column=3,rowspan=2,sticky="nsew",padx=10,pady=10)

frame=create_telegram_frame(telegram_frame)
frame.pack(expand=True,fill="y")

app.mainloop()
