# Vireonix Trading Platform

## Overview

The Vireonix Trading Platform is a Python-based application designed for trading tokens on the Solana blockchain. It provides a graphical user interface (GUI) built with CustomTkinter, integrates with the Solana blockchain for wallet management and token swaps, and supports real-time Telegram notifications for trading updates. The application also includes features for tracking token prices, calculating profits, and performing manual or automated trades.

Key features include:
- Fetching token balances from a Solana wallet (e.g., Phantom wallet).
- Displaying live token price graphs using Matplotlib.
- Performing token swaps via SolanaTracker.
- Sending Telegram notifications with Twilio calls for price alerts.
- Storing transaction history in a SQLite database.
- Supporting automated profit calculation and selling triggers.

## Prerequisites

- **Operating System**: Windows (tested on Windows with PyCharm)
- **Python Version**: Python 3.8 or higher
- **PyCharm**: Recommended IDE for running and debugging the project
- **Solana Wallet**: A Solana wallet (e.g., Phantom) with a private key and address
- **Telegram Account**: A Telegram bot token and channel ID for notifications
- **Twilio Account**: For sending phone call notifications (optional)

## Dependencies

The project relies on several Python libraries. Install them using the following command in PyCharm's terminal or your command prompt:

```bash
pip install customtkinter matplotlib pillow requests solana solders jupiter-python-sdk sqlite3 telethon twilio solanatracker python-dotenv
```

### Required Libraries
- `customtkinter`: For building the GUI.
- `matplotlib`: For plotting live token price graphs.
- `pillow`: For image processing (e.g., displaying token logos).
- `requests`: For making HTTP requests to APIs.
- `solana` and `solders`: For interacting with the Solana blockchain.
- `jupiter-python-sdk`: For fetching token swap quotes on Solana.
- `sqlite3`: For storing wallet and transaction data (built into Python).
- `telethon`: For Telegram integration.
- `twilio`: For sending phone call notifications.
- `solanatracker`: For performing token swaps on Solana.
- `python-dotenv`: For loading environment variables from a `.env` file.

## Setup Instructions

### 1. Clone the Repository
Clone or download this project to your local machine.

```bash
git clone <repository-url>
cd vireonix-trading-platform
```

### 2. Create a `.env` File
In the project root directory, create a file named `.env` and add the following environment variables. Replace the placeholder values with your actual credentials:

```
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_telegram_channel_id
WALLET_PRIVATE_KEY=your_wallet_private_key
WALLET_ADDRESS=your_wallet_address
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
CHAT_IDENTIFIER=your_telegram_chat_identifier
```

- `SOLANA_RPC_URL`: Solana RPC endpoint (default: `https://api.mainnet-beta.solana.com`).
- `TELEGRAM_BOT_TOKEN`: Token for your Telegram bot (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).
- `TELEGRAM_CHANNEL_ID`: Your Telegram channel ID (e.g., `@MyTradingChannel` or `-1001234567890`).
- `WALLET_PRIVATE_KEY`: Your Solana wallet private key (base58-encoded, keep it secure).
- `WALLET_ADDRESS`: Your Solana wallet address (e.g., `9maR6hnACsxEVgbyjk7oBwft61jtQjKu4ZY1fuARo1CD`).
- `TELEGRAM_API_ID`: Your Telegram API ID (obtained from https://my.telegram.org).
- `TELEGRAM_API_HASH`: Your Telegram API hash (obtained from https://my.telegram.org).
- `CHAT_IDENTIFIER`: Telegram chat identifier (e.g., `https://t.me/NiggaHelpline`, `@username`, or chat ID).

**Security Note**: Never share your `.env` file publicly, as it contains sensitive information. Add `.env` to your `.gitignore` file to prevent it from being tracked by Git.

### 3. Install Dependencies
Open the project in PyCharm and run the following command in the PyCharm terminal to install the required libraries:

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` file, you can create one with the dependencies listed above, or install them individually as shown in the **Dependencies** section.

### 4. Configure PyCharm
- Open the project in PyCharm.
- Set up a Python interpreter if not already configured:
  - Go to **File > Settings > Project > Python Interpreter**.
  - Click the gear icon, then **Add Interpreter**, and select your Python installation or a virtual environment.
- Ensure the `.env` file is in the project root directory and loaded correctly (the script uses `python-dotenv` to load it).

### 5. Run the Application
- Open `main.py` in PyCharm.
- Click the green "Run" button or press `Shift + F10` to run the script.
- The application window will open, displaying the Vireonix Trading Platform GUI.

If any required environment variables are missing, the script will raise a `ValueError` with a message indicating the missing variable. Check your `.env` file and ensure all variables are set correctly.

## Usage

### Main Interface
- **Sidebar**:
  - **Settings**: Currently a placeholder button (⚙️).
  - **Automation Checkbox**: Enable to start automatic profit calculation and selling triggers.
  - **Trigger Dropdown**: Set auto-selling triggers (e.g., "50% at 2.5x & 50% at 4.5x").
  - **Telegram Call Options**: Select a multiplier for Telegram notifications (e.g., "2x").
  - **Send Telegram Call**: Manually send a Telegram notification and Twilio call based on current token prices.

- **Buy Panel (Subframe 1)**:
  - Enter token details (Coin Name, Contract Address, etc.).
  - Click **Fetch Coin Info** to retrieve token price data.
  - Displays token details like buying price, current price in SOL/USDT, and total tokens.

- **Wallet Info (Subframe 2)**:
  - Click **Connect Wallet Using Private Key** to fetch and display tokens in your Solana wallet.
  - Shows token names, balances, and mint addresses.
  - Click a token to populate the Buy Panel with its details and display a price change graph.

- **Manual Buy/Sell (Subframe 3)**:
  - Enter contractor addresses for the input and output tokens.
  - Check "I want to swap tokens to get SOL Token" to sell tokens for SOL.
  - Click **Buy** or **Sell** to perform a token swap using SolanaTracker.

- **Price Graph (Subframe 4)**:
  - Displays a live price graph for the selected token, updated every 2 minutes for 1 hour.
  - Green lines indicate price increases, red for decreases, white for no change.

- **Telegram Frame (Subframe 5)**:
  - Displays live messages from the specified Telegram chat.
  - Enter a new chat identifier (username, chat ID, or invite link) and click **Load Chat** to switch chats.

### Database
- The application uses a SQLite database (`wallets.db`) to store:
  - Your wallet private key (entered via the GUI prompt or loaded from `.env`).
  - Token purchase history (token name, contract addresses, buying price, number of tokens, transaction link, etc.).

### Automation
- Enable the **Automation** checkbox to start profit calculation.
- The script checks token profits every 5 minutes and sends a Telegram notification if the profit exceeds twice the buying price.

## Troubleshooting

- **Missing Environment Variables**:
  - If you see a `ValueError: Missing required environment variable: <variable>`, check your `.env` file for the missing variable.
  - Ensure variable names match exactly (case-sensitive) and there are no extra spaces or quotes.

- **Telegram Errors**:
  - **Invalid Chat ID/Link**: Verify the `CHAT_IDENTIFIER` in your `.env` file.
  - **API ID/Hash Issues**: Ensure `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` are correct (get them from https://my.telegram.org).

- **Solana Connection Issues**:
  - Verify that `SOLANA_RPC_URL` is correct and accessible.
  - Check your internet connection and Solana network status.

- **GUI Not Loading**:
  - Ensure all dependencies are installed.
  - Run the script in PyCharm’s debug mode (`Shift + F9`) to identify errors.

- **Token Swap Fails**:
  - Ensure your wallet has sufficient funds for the swap and priority fees.
  - Check the contractor addresses for accuracy.

## Security Notes
- **Private Key**: Store your wallet private key securely in the `.env` file or database. Never hardcode it in the script.
- **Environment Variables**: Do not commit your `.env` file to version control. Add it to `.gitignore`.
- **Twilio Credentials**: The current script hardcodes Twilio credentials in `send_telegram_call`. For better security, add them to the `.env` file as `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`, and update the function to use `os.getenv()`.

## Contributing
Feel free to submit issues or pull requests to improve the project. Focus areas for improvement include:
- Adding support for more blockchains.
- Enhancing the GUI with additional features (e.g., portfolio tracking).
- Improving error handling and user feedback.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
