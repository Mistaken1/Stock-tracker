import yfinance as yf
import time
import json
import threading
from winotify import Notification, audio
import os

monitoring = False
monitor_thread = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_stocks():
    try:
        with open('stocks.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('stocks.json', 'w') as f:
            json.dump([], f)
        return []

def save_stocks(stock_list):
    with open('stocks.json', 'w') as f:
        json.dump(stock_list, f, indent=4)

def notify(title, message):
    toast = Notification(
        app_id="Stock Alert",
        title=title,
        msg=message,
        duration='short',
    )
    toast.set_audio(audio.Reminder, loop=False)
    toast.show()

def add_stock():
    data = load_stocks()
    symbol = input("What ticker would you like to monitor? ").upper().strip()

    if symbol in data:
        print(f"\n[!] {symbol} is already in your watchlist.")
    else:
        data.append(symbol)
        save_stocks(data)
        print(f"\n[+] Successfully added {symbol}.")

def track_stocks(targets):
    """Runs in a background thread. Receives pre-collected targets dict."""
    global monitoring

    print(f"\n[Monitoring Started for {len(targets)} stocks]")

    while monitoring:
        stocks_to_check = list(targets.keys())

        for stock in stocks_to_check:
            if not monitoring:
                break

            try:
                dat = yf.Ticker(stock)
                hist = dat.history(period="1d", interval="1m")

                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    print(f"{stock:6} | ${price:9.2f} | Checked")

                    margin = 0.06 # cents margin for notification
                    if targets[stock] - margin <= price <= targets[stock] + margin:
                        notify(
                            f"{stock} Alert!",
                            f"Current: ${price:9.2f} | Target: ${targets[stock]:9.2f}"
                        )
                else:
                    print(f"{stock:6} | Error: No data found.")

            except Exception as e:
                print(f"{stock:6} | Error: {e}")

        # Wait 60 seconds between sweeps, checking for stop signal
        for _ in range(60):
            if not monitoring:
                break
            time.sleep(1)

    print("\n[!] Background monitoring thread stopped.")

def get_price_targets(stock):
    try:
        dat = yf.Ticker(stock)
        targets = dat.analyst_price_targets
        if not targets:
            print(f"No analyst data found for {stock}.")
            return

        print(f"\n--- Analyst Targets for {stock} ---")
        for key, value in targets.items():
            print(f"{key:10}: ${value:.2f}")

    except Exception as e:
        print(f"Error fetching data: {e}")

def show_stocks():
    data = load_stocks()
    if data:
        print("\n--- Current Watchlist ---")
        for i, stock in enumerate(data, 1):
            print(f"{i}. {stock}")
    else:
        print("\n[!] Your watchlist is empty.")

def start_monitoring():
    """Collect all targets first (blocking), then launch the thread."""
    global monitoring, monitor_thread

    stock_list = load_stocks()
    if not stock_list:
        print("\n[!] Watchlist is empty. Add stocks first.")
        return

    targets = {}
    print()
    try:
        for stock in stock_list:
            target_input = input(f"Enter target price for {stock}: $").strip()
            targets[stock] = float(target_input)
    except ValueError:
        print("[!] Invalid number entered. Monitoring canceled.")
        return

    # All input collected — now start the thread
    monitoring = True
    monitor_thread = threading.Thread(target=track_stocks, args=(targets,), daemon=True)
    monitor_thread.start()

def stop_monitoring():
    global monitoring
    confirm = input("\nStop monitoring? (Y/N): ").strip().upper()
    if confirm == 'Y':
        monitoring = False
        print("[!] Stopping monitor...")
        time.sleep(2)

def main():
    global monitoring, monitor_thread
    clear_screen()
    print("=" * 40)
    print("    STOCK MONITOR - DASHBOARD")
    print("=" * 40)
    print(f"STATUS: {'[RUNNING]' if monitoring else '[IDLE]'}")
    print("-" * 40)
    print("1. Add a stock to monitor")
    print("2. Toggle Monitoring")
    print("3. View Analyst Info")
    print("4. Show Current Watchlist")
    print("5. Exit")
    print("-" * 40)

    choice = input("Select an option (1-5): ").strip()

    if choice == '1':
        add_stock()
        input("\nPress Enter to return...")

    elif choice == '2':
        if not monitoring:
            start_monitoring()          # blocks until all targets are entered
            input("\nMonitoring started. Press Enter to return...")
        else:
            stop_monitoring()

    elif choice == '3':
        tick = input("Enter Ticker: ").upper().strip()
        get_price_targets(tick)
        input("\nPress Enter to continue...")

    elif choice == '4':
        show_stocks()
        input("\nPress Enter to continue...")

    elif choice == '5':
        monitoring = False
        print("Goodbye!")
        exit()

    else:
        print("[!] Invalid option.")
        time.sleep(1)

if __name__ == "__main__":
    while True:
        main()