import yfinance as yf
import time
import json
import threading
from winotify import Notification, audio
import os

def clear_screen():
    # 'nt' is Windows, 'posix' is Mac/Linux
    os.system('cls' if os.name == 'nt' else 'clear')

# --- JSON PERSISTENCE LOGIC ---

def load_stocks():
    """Helper to load stocks from the JSON file."""
    try:
        with open('stocks.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('stocks.json', 'w') as f:
            json.dump([], f)
        return []

def save_stocks(stock_list):
    """Helper to save the current stock list to the JSON file."""
    with open('stocks.json', 'w') as f:
        json.dump(stock_list, f, indent=4)

# Initialize global list
ticker_markers = load_stocks()

# --- FUNCTIONS ---

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
        global ticker_markers
        ticker_markers = data
        print(f"\n[+] Successfully added {symbol}.")

def track_stocks():
    # Get the target price once at the start of the thread
    try:
        target = float(input("\nAlert when price is ABOVE: $"))
    except ValueError:
        print("[!] Invalid number. Monitoring canceled.")
        return

    print(f"\n[Monitoring Started for target: ${target:0.2f}]")
    print("Ticker | Current Price | Status")
    print("-" * 35)
    
    while True:
        stocks_to_check = load_stocks() 
        
        for stock in stocks_to_check:
            try:
                dat = yf.Ticker(stock)
                
                hist = dat.history(period="1d", interval="1m")
                
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    
                    print(f"{stock:6} | ${price:9.2f} | Checked")
                    
                    margin = 0.0075 * target
                    #check if price is within 0.75% of the target price
                    if target - margin <= price <= target + margin:
                        notify(
                            f"{stock} Alert!", 
                            f"Current: ${price:9.2f} | Target: ${target:9.2f}"
                        )

                else:
                    print(f"{stock:6} | Error: No data found.")
                
            except Exception as e:
                if '404' in str(e):
                    print(f"{stock:6} | Error: Ticker not found.")
                else:
                    pass

        # Wait 60 seconds before the next check
        time.sleep(60)

def get_price_targets(stock):
    try: 
        dat = yf.Ticker(stock)
        targets = dat.analyst_price_targets
        if not targets:
            print(f"No analyst data found for {stock}.")
            return

        print(f"\n--- Analyst Targets for {stock} ---")
        for key, value in targets.items():
            # Formatting keys for alignment
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

def main():
    clear_screen()
    print("="*40)
    print("   STOCK ALERT SYSTEM - DASHBOARD")
    print("="*40)
    print("1. Add a stock to monitor")
    print("2. Start Monitoring (Background)")
    print("3. View Analyst Info")
    print("4. Show Current Watchlist")
    print("5. Exit")
    print("-" * 40)
    
    choice = input("Select an option (1-5): ")

    if choice == '1':
        add_stock()
        input("\nPress Enter to return to menu...")
        
    elif choice == '2':
        if not ticker_markers:
            print("\n[!] Watchlist is empty. Add a stock first.")
        else:
            # We don't want to start multiple threads for the same thing
            stock_thread = threading.Thread(target=track_stocks, daemon=True)
            stock_thread.start()
            print("\n[!] Background monitoring active.")
        input("\nPress Enter to return to menu...")

    elif choice == '3':
        tick = input("Enter Ticker: ").upper()
        get_price_targets(tick)
        input("\nPress Enter to continue...")

    elif choice == '4':
        show_stocks()
        input("\nPress Enter to continue...")

    elif choice == '5':
        print("Closing application...")
        exit()

    else:
        print("\n[!] Invalid choice.")
        time.sleep(1)

# --- ENTRY POINT ---
if __name__ == "__main__":
    while True:
        main()