__version__ = "1.0.0"

import threading
import time
from datetime import datetime

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


HEADERS = {"User-Agent": "Mozilla/5.0"}
SYMBOLS = {"1570": "1570.T", "1360": "1360.T"}


def get_prices(symbol):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbol}?interval=5m&range=1d"
    )

    last_error = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                last_error = "通信結果 429（アクセス制限）"
                if attempt < 2:
                    time.sleep(10)
                    continue
                raise RuntimeError(last_error)
            if r.status_code != 200:
                raise RuntimeError(f"通信結果 {r.status_code}")

            data = r.json()
            result = data["chart"]["result"][0]
            closes = result["indicators"]["quote"][0]["close"]
            prices = [float(x) for x in closes if x is not None]

            if len(prices) < 20:
                raise RuntimeError("5分足データが20本未満です")

            return prices
        except Exception as e:
            last_error = str(e)
            if attempt < 2:
                time.sleep(3)
            else:
                raise RuntimeError(last_error)


def sma(values, period):
    return sum(values[-period:]) / period


def ema(values, period):
    values = values[-period * 4:]
    k = 2 / (period + 1)
    value = values[0]
    for price in values[1:]:
        value = price * k + value * (1 - k)
    return value


def rsi(values, period=14):
    if len(values) < period + 1:
        return 50.0
    recent = values[-(period + 1):]
    gains, losses = [], []
    for i in range(1, len(recent)):
        diff = recent[i] - recent[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def analyze(values):
    current = values[-1]
    sma20 = sma(values, 20)
    ema5 = ema(values, 5)
    ema20 = ema(values, 20)
    rsi14 = rsi(values, 14)

    score = 0
    if current > sma20:
        score += 1
    if ema5 > ema20:
        score += 2
    else:
        score -= 2

    if 45 <= rsi14 < 70:
        score += 1
    elif rsi14 >= 70:
        score -= 1
    elif rsi14 <= 30:
        score += 1

    changes = [
        abs(values[i] - values[i - 1])
        for i in range(max(1, len(values) - 10), len(values))
    ]
    volatility = sum(changes) / max(1, len(changes))
    risk = volatility * 2

    return {
        "current": current,
        "sma20": sma20,
        "ema5": ema5,
        "ema20": ema20,
        "rsi": rsi14,
        "score": score,
        "trend": "上昇" if ema5 > ema20 else "下降",
        "stop": current - risk,
        "target": current + risk * 2,
    }


def fmt(x):
    return f"{x:.2f}"


class StockApp(App):
    title = "1570 / 1360 株価分析"

    def build(self):
        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8,
        )

        self.status = Label(
            text="起動中…",
            font_size=16,
            size_hint_y=None,
            height=42,
        )
        root.add_widget(self.status)

        self.result = Label(
            text="データ取得中…",
            font_size=17,
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        self.result.bind(texture_size=self.result.setter("size"))

        scroll = ScrollView()
        scroll.add_widget(self.result)
        root.add_widget(scroll)

        btn = Button(
            text="今すぐ更新",
            font_size=20,
            size_hint_y=None,
            height=60,
        )
        btn.bind(on_press=lambda _: self.start_update())
        root.add_widget(btn)

        Clock.schedule_once(lambda dt: self.start_update(), 0.5)
        Clock.schedule_interval(lambda dt: self.start_update(), 300)

        return root

    def start_update(self):
        if getattr(self, "_busy", False):
            return
        self._busy = True
        self.status.text = "更新中…"
        threading.Thread(target=self.update_data, daemon=True).start()

    def update_data(self):
        try:
            p1570 = get_prices(SYMBOLS["1570"])
            time.sleep(3)
            p1360 = get_prices(SYMBOLS["1360"])

            a = analyze(p1570)
            b = analyze(p1360)

            if a["score"] >= 2 and a["score"] > b["score"] and a["rsi"] < 70:
                overall = "1570 BUY候補"
            elif b["score"] >= 2 and b["score"] > a["score"] and b["rsi"] < 70:
                overall = "1360 BUY候補"
            else:
                overall = "HOLD"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            text = (
                "【総合判定】\n"
                f"{overall}\n\n"
                "━━━━━━━━━━━━━━\n"
                "1570 日経レバ\n"
                "━━━━━━━━━━━━━━\n"
                f"現在値 : {fmt(a['current'])}\n"
                f"SMA20  : {fmt(a['sma20'])}\n"
                f"EMA5   : {fmt(a['ema5'])}\n"
                f"EMA20  : {fmt(a['ema20'])}\n"
                f"トレンド : {a['trend']}\n"
                f"RSI14  : {fmt(a['rsi'])}\n"
                f"スコア : {a['score']}\n"
                f"エントリー目安 : {fmt(a['current'])}\n"
                f"損切り目安     : {fmt(a['stop'])}\n"
                f"利確目安       : {fmt(a['target'])}\n"
                "R/R : 2.0\n\n"
                "━━━━━━━━━━━━━━\n"
                "1360 日経平均ベア2倍\n"
                "━━━━━━━━━━━━━━\n"
                f"現在値 : {fmt(b['current'])}\n"
                f"SMA20  : {fmt(b['sma20'])}\n"
                f"EMA5   : {fmt(b['ema5'])}\n"
                f"EMA20  : {fmt(b['ema20'])}\n"
                f"トレンド : {b['trend']}\n"
                f"RSI14  : {fmt(b['rsi'])}\n"
                f"スコア : {b['score']}\n"
                f"エントリー目安 : {fmt(b['current'])}\n"
                f"損切り目安     : {fmt(b['stop'])}\n"
                f"利確目安       : {fmt(b['target'])}\n"
                "R/R : 2.0\n\n"
                "━━━━━━━━━━━━━━\n"
                f"最終更新 : {now}\n"
                "自動更新 : 5分\n"
                "自動注文 : なし\n"
                "※分析値は売買を保証するものではありません。"
            )

            Clock.schedule_once(lambda dt, t=text: self.show(t, "更新完了"))

        except Exception as e:
            msg = (
                "データ取得失敗\n\n"
                f"{e}\n\n"
                "5分後の自動更新、または「今すぐ更新」で再試行します。"
            )
            Clock.schedule_once(lambda dt, t=msg: self.show(t, "更新失敗"))
        finally:
            self._busy = False

    def show(self, text, status):
        self.result.text = text
        self.status.text = status


if __name__ == "__main__":
    StockApp().run()
