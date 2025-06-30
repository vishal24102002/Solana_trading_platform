# 💱 Solana Trading Platform

A simple crypto trading simulation platform built using Flask and Python, powered by real-time price data from CoinGecko and historical data from MongoDB.

---

## 📸 Demo

(/sol_tracker.jpg)

---

## ⚙️ Features

- 🔁 Real-time Solana price fetching via CoinGecko API
- 🧮 Buy/Sell simulation with balance and holdings tracking
- 🧾 Transaction history and P&L computation
- 🧠 MongoDB integration for persistent trade data
- 🌐 Flask-based web interface (or CLI interface depending on how it's run)

---

## 🧰 Tech Stack

- 🐍 Python 3
- ⚙️ Flask
- 🍃 MongoDB (via PyMongo)
- 🌐 CoinGecko API
- 🧾 HTML/CSS (basic frontend)

---

## 🏁 Getting Started

### 🔧 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/vishal24102002/Solana_trading_platform.git
   cd Solana_trading_platform
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:

   Create a `.env` file in the root directory:
   ```env
   MONGO_URI=mongodb://localhost:27017/
   DATABASE_NAME=solana_trader
   ```

5. Start the Flask app:
   ```bash
   python app.py
   ```

---

## ⚠️ Note on Database Usage

> ⚠️ Important:  
This project uses **MongoDB** for data persistence. Ensure MongoDB is installed and running locally (`localhost:27017`) or update the connection string to use **MongoDB Atlas** or another cloud service.

---

## 📦 Example Trade Flow

1. View live Solana price.
2. Buy/Sell based on your balance.
3. Transactions are logged and stored in MongoDB.
4. Track portfolio and profit/loss across sessions.

---

## 🧪 Testing

If you'd like to test the transaction logic:

- Run the app
- Make mock trades
- Inspect the `trades` collection in MongoDB via a GUI like [MongoDB Compass](https://www.mongodb.com/products/compass)

---

## 📄 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for more information.

---

## 🙋‍♂️ Contributing

Contributions are welcome!  
Feel free to fork the repository and submit a pull request.  
For major changes, please open an issue first to discuss what you'd like to change.

---

## 🔗 API Reference

- [CoinGecko API](https://www.coingecko.com/en/api)

---

[![View on GitHub](https://img.shields.io/badge/View_on-GitHub-24292e?style=for-the-badge&logo=github)](https://github.com/vishal24102002/Solana_trading_platform)


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
