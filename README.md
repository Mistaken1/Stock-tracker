# Stock Alert System

A Python-based financial monitoring tool designed to track market trends and provide instant desktop feedback.

## Key Features
- **Real-time Market Data:** Utilizes the `yfinance` API to fetch live, up-to-date information directly from the stock market.
- **Instant Alerts:** Implements pushed notifications via `winotify` to ensure users receive immediate updates on their desktop.

## Technical Stack
- **Language:** Python
- **API:** Yahoo Finance (yfinance)
- **Notifications:** Winotify
- **Formatting:** Tabulate (for clean terminal output)

## Quick Start
1. Install dependencies:
   ```bash
   pip install yfinance winotify tabulate