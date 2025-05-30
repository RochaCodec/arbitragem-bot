import requests
import time
import telegram

# === CONFIGURAÇÕES ===
TOKEN_TELEGRAM = "7935292906:AAH_F4Git3WJAbRdDY_15jIXbPVoQN4MExY"  # Substitua pelo seu token
ID_CHAT_TELEGRAM = "5479717766"   # Substitua pelo seu ID de chat
PARES = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
LIMIAR_LUCRO = 0.5  # Porcentagem mínima de lucro para alertar
INTERVALO = 10  # Tempo entre verificações, em segundos

# === SETUP TELEGRAM ===
bot = telegram.Bot(token=TOKEN_TELEGRAM)

def enviar_alerta(msg):
    try:
        bot.send_message(chat_id=ID_CHAT_TELEGRAM, text=msg)
    except Exception as e:
        print(f"Erro ao enviar alerta para o Telegram: {e}")

def obter_precos_mexc(par):
    try:
        r = requests.get(
            f"https://api.mexc.com/api/v3/ticker/bookTicker?symbol={par}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        data = r.json()
        return float(data["bidPrice"]), float(data["askPrice"])
    except Exception as e:
        print(f"❌ Erro ao obter dados de {par} na MEXC: {e}")
        return None, None

def obter_precos_kucoin(par):
    try:
        r = requests.get(
            f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={par}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        data = r.json()["data"]
        return float(data["bestBid"]), float(data["bestAsk"])
    except Exception as e:
        print(f"❌ Erro ao obter dados de {par} na KuCoin: {e}")
        return None, None

def verificar_arbitragem(par):
    mexc_bid, mexc_ask = obter_precos_mexc(par)
    kucoin_bid, kucoin_ask = obter_precos_kucoin(par)

    if None in [mexc_bid, mexc_ask, kucoin_bid, kucoin_ask]:
        return

    oportunidades = []

    # Estratégia 1: Comprar na MEXC, vender na KuCoin
    lucro1 = (kucoin_bid - mexc_ask) / mexc_ask * 100
    if lucro1 >= LIMIAR_LUCRO:
        oportunidades.append(f"💰 Arbitragem: COMPRE na MEXC e VENDA na KuCoin — {par} | Lucro: {lucro1:.2f}%")

    # Estratégia 2: Comprar na KuCoin, vender na MEXC
    lucro2 = (mexc_bid - kucoin_ask) / kucoin_ask * 100
    if lucro2 >= LIMIAR_LUCRO:
        oportunidades.append(f"💰 Arbitragem: COMPRE na KuCoin e VENDA na MEXC — {par} | Lucro: {lucro2:.2f}%")

    for op in oportunidades:
        print(op)
        enviar_alerta(op)

# === LOOP PRINCIPAL ===
print("🚀 Bot de Arbitragem Bidirecional iniciado...")
while True:
    for par in PARES:
        verificar_arbitragem(par)
    time.sleep(INTERVALO)

