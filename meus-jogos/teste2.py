import yfinance as yf
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import winsound
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta

class LiveTradingMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Trading em Tempo Real - NVIDIA (NVDA)")
        self.root.geometry("1100x800")
        self.root.minsize(1000, 750)
        self.root.configure(bg='#f5f5f5')
        
        # Control variables
        self.running = False
        self.final_balance = 0
        self.initial_balance = 0
        self.prices = []
        self.times = []
        self.events = []
        self.current_price = 0
        self.owned_shares = 0
        self.buy_price = 0
        self.portfolio_value = 0
        self.total_profit = 0
        self.trading_active = True  # Trading flag
        self.downtrend_detected = False  # Downtrend flag
        
        # Setup styles
        self.setup_styles()
        
        # Create interface
        self.create_widgets()
        
        # Setup chart
        self.setup_chart()
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.map('Green.TButton', foreground=[('active', 'white')], background=[('active', '#4CAF50')])
        self.style.map('Red.TButton', foreground=[('active', 'white')], background=[('active', '#F44336')])
        self.style.map('Blue.TButton', foreground=[('active', 'white')], background=[('active', '#2196F3')])
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame (controls)
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        
        # Right frame (chart)
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Asset configuration
        config_frame = ttk.LabelFrame(left_frame, text="Configurações do Ativo (NVDA)", padding=(15, 10))
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="Ticker: NVDA (NVIDIA)").pack(anchor='w')
        self.ticker_entry = ttk.Entry(config_frame, state='disabled')
        self.ticker_entry.pack(fill=tk.X, pady=2)
        self.ticker_entry.insert(0, "NVDA")
        
        # Account settings
        account_frame = ttk.LabelFrame(left_frame, text="Configurações da Conta", padding=(15, 10))
        account_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(account_frame, text="Saldo Inicial (USD $):").pack(anchor='w')
        self.balance_entry = ttk.Entry(account_frame)
        self.balance_entry.pack(fill=tk.X, pady=2)
        self.balance_entry.insert(0, "10000")
        
        ttk.Label(account_frame, text="Quantidade por operação:").pack(anchor='w')
        self.shares_entry = ttk.Entry(account_frame)
        self.shares_entry.pack(fill=tk.X, pady=2)
        self.shares_entry.insert(0, "1")
        
        # Risk management
        risk_frame = ttk.LabelFrame(left_frame, text="Gerenciamento de Risco", padding=(15, 10))
        risk_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(risk_frame, text="Take Profit (%):").pack(anchor='w')
        self.tp_entry = ttk.Entry(risk_frame)
        self.tp_entry.pack(fill=tk.X, pady=2)
        self.tp_entry.insert(0, "5")
        
        ttk.Label(risk_frame, text="Stop Loss (%):").pack(anchor='w')
        self.sl_entry = ttk.Entry(risk_frame)
        self.sl_entry.pack(fill=tk.X, pady=2)
        self.sl_entry.insert(0, "3")
        
        ttk.Label(risk_frame, text="Limite de Queda (%):").pack(anchor='w')
        self.downtrend_entry = ttk.Entry(risk_frame)
        self.downtrend_entry.pack(fill=tk.X, pady=2)
        self.downtrend_entry.insert(0, "5")  # Stop trading if price drops 5% in 5 minutes
        
        # Control buttons
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(
            control_frame, 
            text="▶ Iniciar Monitoramento", 
            style='Green.TButton',
            command=self.start_monitoring
        )
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.stop_btn = ttk.Button(
            control_frame, 
            text="⏹ Parar Monitoramento", 
            style='Red.TButton',
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        # Force buy/sell button
        ttk.Button(
            control_frame, 
            text="🔁 Ativar/Desativar Trading", 
            style='Blue.TButton',
            command=self.toggle_trading
        ).pack(fill=tk.X, pady=2)
        
        # Real-time info
        info_frame = ttk.LabelFrame(left_frame, text="Informações em Tempo Real", padding=(15, 10))
        info_frame.pack(fill=tk.X, pady=5)
        
        self.price_var = tk.StringVar(value="Preço: $ 0.00")
        ttk.Label(info_frame, textvariable=self.price_var, font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        self.balance_var = tk.StringVar(value="Saldo: $ 0.00")
        ttk.Label(info_frame, textvariable=self.balance_var).pack(anchor='w')
        
        self.shares_var = tk.StringVar(value="Ações: 0")
        ttk.Label(info_frame, textvariable=self.shares_var).pack(anchor='w')
        
        self.profit_var = tk.StringVar(value="Lucro: $ 0.00 (0.00%)")
        ttk.Label(info_frame, textvariable=self.profit_var).pack(anchor='w')
        
        self.status_var = tk.StringVar(value="Pronto para iniciar")
        ttk.Label(info_frame, textvariable=self.status_var, foreground='#666666').pack(anchor='w')
        
        self.trading_var = tk.StringVar(value="Trading: INATIVO")
        ttk.Label(info_frame, textvariable=self.trading_var, foreground='red').pack(anchor='w')
        
        # Chart
        self.fig, self.ax = plt.subplots(figsize=(10, 6), dpi=100)
        self.fig.patch.set_facecolor('#f5f5f5')
        self.ax.set_facecolor('#f5f5f5')
        
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Chart tooltip
        self.tooltip = self.ax.annotate("", xy=(0,0), xytext=(10,10), 
                                       textcoords="offset points",
                                       bbox=dict(boxstyle="round", fc="w"),
                                       arrowprops=dict(arrowstyle="->"))
        self.tooltip.set_visible(False)
        self.chart_canvas.mpl_connect("motion_notify_event", self.hover)
    
    def setup_chart(self):
        self.ax.clear()
        self.ax.set_title("Gráfico de Preços em Tempo Real - NVIDIA (NVDA)", fontsize=12, pad=20)
        self.ax.set_xlabel("Tempo", fontsize=10)
        self.ax.set_ylabel("Preço ($)", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Price line
        self.price_line, = self.ax.plot([], [], label="Preço", color="#1f77b4", linewidth=2, alpha=0.8)
        
        # Buy/sell zones
        self.buy_zone = self.ax.axhspan(0, 0, color='green', alpha=0.1, visible=False)
        self.sell_zone = self.ax.axhspan(0, 0, color='red', alpha=0.1, visible=False)
        
        # Event markers
        self.events_markers = []
        
        self.ax.legend(loc='upper left', fontsize=8)
        self.chart_canvas.draw()
    
    def hover(self, event):
        if event.inaxes == self.ax:
            # Find closest point
            if len(self.times) > 0 and len(self.prices) > 0:
                x, y = event.xdata, event.ydata
                idx = min(np.searchsorted(self.times, x), len(self.times)-1)
                price = self.prices[idx]
                time_str = datetime.fromtimestamp(self.times[idx]).strftime('%H:%M:%S')
                
                # Check for events at this point
                event_text = ""
                for event_time, event_desc, _ in self.events:
                    if abs(event_time - self.times[idx]) < 30:  # +/- 30 seconds
                        event_text = f"\nEvento: {event_desc}"
                        break
                
                self.tooltip.xy = (self.times[idx], price)
                self.tooltip.set_text(f"Horário: {time_str}\nPreço: $ {price:.2f}{event_text}")
                self.tooltip.set_visible(True)
        else:
            self.tooltip.set_visible(False)
        
        self.chart_canvas.draw_idle()
    
    def play_sound(self, sound_type):
        try:
            if sound_type == "buy":
                winsound.Beep(1000, 300)
            elif sound_type == "sell":
                winsound.Beep(500, 300)
            elif sound_type == "alert":
                winsound.Beep(400, 500)
        except:
            pass
    
    def get_live_price(self, ticker):
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1d", interval="1m")
            if not hist.empty:
                return round(hist["Close"][-1], 2), hist.index[-1].timestamp()
        except Exception as e:
            self.status_var.set(f"Erro ao obter preço: {str(e)}")
        return None, None
    
    def check_downtrend(self):
        """Check for significant price drop in recent prices"""
        if len(self.prices) < 5:  # Need at least 5 data points
            return False
        
        try:
            downtrend_threshold = float(self.downtrend_entry.get()) / 100
        except ValueError:
            return False
        
        # Get last 5 prices (last 5 minutes)
        recent_prices = self.prices[-5:]
        initial_price = recent_prices[0]
        current_price = recent_prices[-1]
        
        # Calculate percentage change
        change = (current_price - initial_price) / initial_price
        
        # If drop exceeds threshold
        if change < -downtrend_threshold:
            return True
        
        return False
    
    def toggle_trading(self):
        self.trading_active = not self.trading_active
        if self.trading_active:
            self.trading_var.set("Trading: ATIVO")
            self.trading_var.configure(foreground='green')
            self.downtrend_detected = False
            self.status_var.set("Trading reativado pelo usuário")
        else:
            self.trading_var.set("Trading: INATIVO")
            self.trading_var.configure(foreground='red')
            self.status_var.set("Trading desativado pelo usuário")
    
    def start_monitoring(self):
        if self.running:
            return
        
        # Reset variables
        self.prices = []
        self.times = []
        self.events = []
        self.running = True
        self.trading_active = True
        self.downtrend_detected = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.trading_var.set("Trading: ATIVO")
        self.trading_var.configure(foreground='green')
        
        # Get settings
        ticker = "NVDA"  # Fixed ticker for NVIDIA
        try:
            self.initial_balance = float(self.balance_entry.get())
            shares_per_trade = float(self.shares_entry.get())
            take_profit = float(self.tp_entry.get()) / 100
            stop_loss = float(self.sl_entry.get()) / 100
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos em todos os campos.")
            self.stop_monitoring()
            return
        
        self.current_balance = self.initial_balance
        self.owned_shares = 0
        self.buy_price = 0
        self.total_profit = 0
        
        # Update UI
        self.update_info()
        self.setup_chart()
        self.status_var.set("Monitoramento iniciado - obtendo dados em tempo real...")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.run_monitoring, 
                                                args=(ticker, shares_per_trade, take_profit, stop_loss),
                                                daemon=True)
        self.monitoring_thread.start()
    
    def run_monitoring(self, ticker, shares_per_trade, take_profit, stop_loss):
        while self.running:
            # Get new price
            new_price, timestamp = self.get_live_price(ticker)
            
            if new_price is not None and timestamp is not None:
                self.current_price = new_price
                self.times.append(timestamp)
                self.prices.append(new_price)
                
                # Update info
                self.update_info()
                self.update_chart()
                
                # Check for downtrend
                if not self.downtrend_detected and self.check_downtrend():
                    self.downtrend_detected = True
                    self.trading_active = False
                    self.trading_var.set("Trading: INATIVO (queda detectada)")
                    self.trading_var.configure(foreground='red')
                    self.status_var.set(f"ALERTA: Queda acentuada detectada - Trading desativado")
                    self.play_sound("alert")
                
                # Trading logic (only if trading is active)
                if self.trading_active:
                    if self.owned_shares == 0 and self.current_balance >= new_price * shares_per_trade:
                        # Buy
                        self.owned_shares = shares_per_trade
                        self.buy_price = new_price
                        self.current_balance -= new_price * shares_per_trade
                        
                        # Record event
                        self.events.append((timestamp, "COMPRA", new_price))
                        self.status_var.set(f"COMPRA: {shares_per_trade} ações a $ {new_price:.2f}")
                        self.play_sound("buy")
                    
                    elif self.owned_shares > 0:
                        current_value = new_price * self.owned_shares
                        profit_percent = (new_price - self.buy_price) / self.buy_price
                        
                        # Check take profit or stop loss
                        if profit_percent >= take_profit or profit_percent <= -stop_loss:
                            # Sell
                            self.current_balance += current_value
                            profit = current_value - (self.buy_price * self.owned_shares)
                            self.total_profit += profit
                            self.owned_shares = 0
                            
                            # Record event
                            result = "TP" if profit_percent >= take_profit else "SL"
                            self.events.append((timestamp, f"VENDA ({result})", new_price))
                            self.status_var.set(f"VENDA ({result}): {shares_per_trade} ações a $ {new_price:.2f}")
                            self.play_sound("sell")
            
            time.sleep(60)  # Update every minute (to avoid API overload)
        
        # Finalize monitoring
        if self.owned_shares > 0:
            final_value = self.current_price * self.owned_shares
            self.current_balance += final_value
            profit = final_value - (self.buy_price * self.owned_shares)
            self.total_profit += profit
            self.owned_shares = 0
            self.events.append((self.times[-1], "LIQUIDAÇÃO FINAL", self.current_price))
        
        self.final_balance = self.current_balance
        self.show_results()
    
    def update_info(self):
        self.price_var.set(f"Preço: $ {self.current_price:.2f}")
        self.balance_var.set(f"Saldo: $ {self.current_balance:.2f}")
        self.shares_var.set(f"Ações: {self.owned_shares}")
        
        if self.owned_shares > 0:
            current_value = self.current_price * self.owned_shares
            profit = current_value - (self.buy_price * self.owned_shares)
            profit_percent = (profit / (self.buy_price * self.owned_shares)) * 100
            color = "green" if profit >= 0 else "red"
            self.profit_var.set(f"Lucro: $ {profit:.2f} ({profit_percent:.2f}%)")
        else:
            total_profit_percent = (self.total_profit / self.initial_balance) * 100 if self.initial_balance > 0 else 0
            color = "green" if self.total_profit >= 0 else "red"
            self.profit_var.set(f"Lucro Total: $ {self.total_profit:.2f} ({total_profit_percent:.2f}%)")
        
        # Update profit color
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget("textvariable") == self.profit_var:
                widget.config(foreground=color)
    
    def update_chart(self):
        if not self.prices or not self.times:
            return
        
        self.ax.clear()
        
        # Convert timestamps to datetime for better display
        times_dt = [datetime.fromtimestamp(t) for t in self.times]
        
        # Plot price line
        self.price_line, = self.ax.plot(times_dt, self.prices, 
                                      label=f"{self.ticker_entry.get()}", 
                                      color="#1f77b4", linewidth=2, alpha=0.8)
        
        # Add buy/sell zones
        if self.owned_shares > 0:
            buy_zone = self.ax.axhspan(self.buy_price * 0.99, self.buy_price * 1.01, 
                                      color='green', alpha=0.1, label='Preço de Compra')
            
            # TP/SL lines
            tp_price = self.buy_price * (1 + float(self.tp_entry.get())/100)
            sl_price = self.buy_price * (1 - float(self.sl_entry.get())/100)
            
            self.ax.axhline(tp_price, color='green', linestyle='--', alpha=0.5, label='Take Profit')
            self.ax.axhline(sl_price, color='red', linestyle='--', alpha=0.5, label='Stop Loss')
        
        # Add event markers
        for event_time, event_desc, factor in self.events:
            idx = min(np.searchsorted(self.times, event_time), len(self.times)-1)
            event_price = self.prices[idx]
            event_time_dt = datetime.fromtimestamp(event_time)
            
            if event_desc.startswith("COMPRA"):
                color = 'blue'
                marker = '^'
            elif event_desc.startswith("VENDA"):
                color = 'purple'
                marker = 'v'
            else:
                color = 'gray'
                marker = 'o'
            
            self.ax.scatter(event_time_dt, event_price, color=color, marker=marker, s=100, 
                           label=event_desc if event_desc not in ["COMPRA", "VENDA (TP)", "VENDA (SL)", "LIQUIDAÇÃO FINAL"] else None)
            
            # Add text for important events
            if event_desc in ["COMPRA", "VENDA (TP)", "VENDA (SL)", "LIQUIDAÇÃO FINAL"]:
                self.ax.annotate(event_desc, xy=(event_time_dt, event_price),
                                xytext=(10, 20 if "COMPRA" in event_desc else -30),
                                textcoords='offset points',
                                arrowprops=dict(arrowstyle="->"),
                                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8))
        
        # Chart settings
        self.ax.set_title(f"Monitoramento em Tempo Real - NVIDIA (NVDA)", fontsize=12, pad=20)
        self.ax.set_xlabel("Horário", fontsize=10)
        self.ax.set_ylabel("Preço ($)", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Format x-axis to show time
        self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
        
        # Improve legend
        handles, labels = self.ax.get_legend_handles_labels()
        if handles:  # Only add legend if there are items
            self.ax.legend(handles, labels, loc='upper left', fontsize=8)
        
        self.chart_canvas.draw()
    
    def stop_monitoring(self):
        self.running = False
        self.status_var.set("Monitoramento finalizando...")
    
    def show_results(self):
        profit = self.final_balance - self.initial_balance
        profit_percent = (profit / self.initial_balance) * 100
        
        if profit >= 0:
            result = "LUCRO"
            emoji = "✅"
            color = "#4CAF50"
        else:
            result = "PREJUÍZO"
            emoji = "❌"
            color = "#F44336"
        
        start_time = datetime.fromtimestamp(self.times[0]) if self.times else None
        end_time = datetime.fromtimestamp(self.times[-1]) if self.times else None
        duration = str(end_time - start_time).split(".")[0] if start_time and end_time else "0:00:00"
        
        message = (
            f"{emoji} Resultado: {result}\n\n"
            f"📈 Ativo: NVIDIA (NVDA)\n"
            f"⏱ Duração: {duration}\n"
            f"🕒 Início: {start_time.strftime('%H:%M:%S') if start_time else 'N/A'}\n"
            f"🕒 Fim: {end_time.strftime('%H:%M:%S') if end_time else 'N/A'}\n\n"
            f"💰 Saldo Inicial: $ {self.initial_balance:.2f}\n"
            f"💵 Saldo Final: $ {self.final_balance:.2f}\n"
            f"📊 {result}: $ {abs(profit):.2f} ({profit_percent:.2f}%)\n\n"
            f"🔢 Operações realizadas: {len([e for e in self.events if e[1].startswith('VENDA')])}\n"
            f"{'⚠️ Trading desativado por queda acentuada' if self.downtrend_detected else ''}"
        )
        
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultado do Monitoramento - NVIDIA")
        result_window.geometry("450x400")
        
        ttk.Label(result_window, text=message, font=('Segoe UI', 10), 
                 justify=tk.LEFT, foreground=color).pack(padx=20, pady=20)
        
        ttk.Button(result_window, text="Fechar", command=result_window.destroy).pack(pady=10)
        
        # Update buttons
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveTradingMonitor(root)
    root.mainloop()