Solana Trading Platform

## Overview

The Solana Trading Platform is a powerful tool designed for trading Wrapped SOL tokens. It provides real-time price monitoring, automated selling triggers, and manual buying options. A standout feature is the ability to connect to a Telegram channel to fetch live trading calls, helping users stay ahead in the fast-paced crypto market.

## Features

- **Real-Time Price Tracking**: Monitor the current price of Wrapped SOL in both SOL and USD, along with price changes over multiple timeframes (1 minute to 24 hours).
- **Automated Selling**: Set auto-selling triggers to execute trades based on predefined conditions.
- **Manual Buying**: Buy Wrapped SOL tokens manually with a user-friendly interface.
- **Telegram Integration**: Connect to a Telegram channel to fetch live trading calls and receive updates instantly.
- **Wallet Information**: View your total token balance and other wallet details.
- **Token Price History**: Visualize price trends with a built-in graph for better decision-making.

## Prerequisites

Before setting up the platform, ensure you have the following:

- Node.js (v16 or higher)
- npm (v7 or higher)
- A Solana wallet (e.g., Phantom or Sollet)
- A Telegram account and channel for fetching trading calls
- API keys for Solana blockchain access (e.g., via Solana's RPC nodes)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/solana-trading-platform.git
   cd solana-trading-platform
   ```

2. **Install Dependencies**

   ```bash
   npm install
   ```

3. **Configure Environment Variables**\
   Create a `.env` file in the root directory and add the following:

   ```
   SOLANA_RPC_URL=your_solana_rpc_url
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=your_telegram_channel_id
   WALLET_PRIVATE_KEY=your_wallet_private_key
   ```

4. **Run the Application**

   ```bash
   npm start
   ```

## Usage

1. **Launch the Platform**\
   Open the application in your browser (default: `http://localhost:3000`).

2. **Connect Your Wallet**\
   Use the "Wallet Info" section to connect your Solana wallet and view your balance.

3. **Set Up Telegram Integration**

   - Go to the "Telegram Call Options" section.
   - Enter your Telegram channel details and select the "Send Telegram Call" option to start fetching live calls.

4. **Monitor and Trade**

   - Check the "Token Price History" graph for price trends.
   - Use the "Set Auto-Selling Trigger" to automate trades.
   - Manually buy tokens using the "Buy Manually" section.

## Screenshots

\
*Main interface showing price tracking, wallet info, and Telegram integration.*

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For support or inquiries, reach out via:

- Email: yourname@example.com
- GitHub Issues: Open an Issue