import tkinter as tk
from tkinter import messagebox
import math
import json
import urllib.request


def fetch_currency_rates():
    """Fetch currency rates to TRY. Uses fallback rates if network fails."""
    url = "https://api.exchangerate.host/latest?base=TRY&symbols=USD,EUR"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.load(response)
            rates = data.get("rates", {})
            rates["TRY"] = 1.0
            rates["GOLD"] = 2000.0  # fallback for gold per gram
            return rates
    except Exception:
        return {
            "USD": 32.0,
            "EUR": 35.0,
            "TRY": 1.0,
            "GOLD": 2000.0,
        }


class InventoryTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finance Inventory Tracker")

        self.holdings = {"TRY": 0.0, "USD": 0.0, "EUR": 0.0, "GOLD": 0.0}
        self.rates = fetch_currency_rates()
        self.wedges = []

        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Asset:").grid(row=0, column=0)
        self.entry_asset = tk.Entry(control_frame)
        self.entry_asset.grid(row=0, column=1)

        tk.Label(control_frame, text="Amount:").grid(row=0, column=2)
        self.entry_amount = tk.Entry(control_frame)
        self.entry_amount.grid(row=0, column=3)

        tk.Button(control_frame, text="Add", command=self.add_asset).grid(row=0, column=4, padx=5)
        tk.Button(control_frame, text="Remove", command=self.remove_asset).grid(row=0, column=5, padx=5)

        self.label_total = tk.Label(self, text="Total: 0")
        self.label_total.pack(pady=10)

        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Motion>", self.on_motion)

        self.after(2000, self.update_rates)
        self.update_chart()

    def add_asset(self):
        asset = self.entry_asset.get().strip().upper()
        try:
            amount = float(self.entry_amount.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        if not asset:
            return
        self.holdings[asset] = self.holdings.get(asset, 0.0) + amount
        self.update_chart()

    def remove_asset(self):
        asset = self.entry_asset.get().strip().upper()
        try:
            amount = float(self.entry_amount.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        if asset in self.holdings:
            self.holdings[asset] -= amount
            if self.holdings[asset] <= 0:
                del self.holdings[asset]
        self.update_chart()

    def update_rates(self):
        self.rates = fetch_currency_rates()
        self.update_chart()
        self.after(2000, self.update_rates)

    def get_total_values(self):
        total_try = 0.0
        values = {}
        for asset, qty in self.holdings.items():
            rate = self.rates.get(asset, 1.0)
            value = qty * rate
            values[asset] = (qty, value)
            total_try += value
        return total_try, values

    def update_chart(self):
        total_try, values = self.get_total_values()
        self.label_total.config(text=f"Total (TRY): {total_try:.2f}")
        self.canvas.delete("all")
        self.wedges = []
        if total_try <= 0:
            return
        start = 0
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0", "#ffb3e6"]
        center = (200, 200)
        radius = 150
        idx = 0
        for asset, (qty, val) in values.items():
            extent = val / total_try * 360
            color = colors[idx % len(colors)]
            item = self.canvas.create_arc(
                center[0]-radius, center[1]-radius,
                center[0]+radius, center[1]+radius,
                start=start, extent=extent, fill=color, outline="white",
                tags=("wedge", asset)
            )
            self.wedges.append((item, asset, qty, val))
            start += extent
            idx += 1

    def on_motion(self, event):
        self.canvas.delete("tooltip")
        current = self.canvas.find_withtag("current")
        if current:
            for item, asset, qty, val in self.wedges:
                if item == current[0]:
                    text = f"{asset}: {qty} (\u2248 {val:.2f} TRY)"
                    self.canvas.create_text(200, 380, text=text, tags="tooltip")
                    break


if __name__ == "__main__":
    app = InventoryTracker()
    app.mainloop()
