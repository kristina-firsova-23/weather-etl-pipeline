import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timezone, timedelta
import os
import traceback

def run_etl():
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(BASE_DIR, 'data', 'weather_data.db')
        
        print(f"📂 База данных: {db_path}")
        
        # Часовой пояс Камчатки (UTC+12)
        KAMCHATKA_TZ = timezone(timedelta(hours=12))
        now_kamchatka = datetime.now(KAMCHATKA_TZ)
        today_kamchatka = now_kamchatka.date()
        
        print(f"🕐 Текущее время на Камчатке: {now_kamchatka.strftime('%Y-%m-%d %H:%M:%S')}")
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 53.045,
            "longitude": 158.650,
            "hourly": ["temperature_2m", "relativehumidity_2m", "pressure_msl"],
            "timezone": "Asia/Kamchatka",  # Явно указываем часовой пояс
            "forecast_days": 2
        }
        
        print("🌐 Запрос к API...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("📊 Обработка данных...")
        df = pd.DataFrame(data['hourly'])
        
        if df.empty:
            print("❌ Нет данных от API")
            return
        
        df.rename(columns={
            'time': 'время',
            'temperature_2m': 'температура_с',
            'relativehumidity_2m': 'влажность_процент',
            'pressure_msl': 'давление_гпа'
        }, inplace=True)
        
        # Преобразование типов
        df['температура_с'] = pd.to_numeric(df['температура_с'], errors='coerce')
        df['влажность_процент'] = pd.to_numeric(df['влажность_процент'], errors='coerce')
        df['давление_гпа'] = pd.to_numeric(df['давление_гпа'], errors='coerce')
        
        # Удаляем строки с пустыми значениями
        before_len = len(df)
        df = df.dropna(subset=['температура_с', 'влажность_процент'])
        print(f"🧹 Удалено {before_len - len(df)} строк")
        
        # Конвертируем время в локальное (Камчатка)
        df['время_utc'] = pd.to_datetime(df['время'])
        df['время_камчатка'] = df['время_utc'] + timedelta(hours=12)
        df['дата_камчатка'] = df['время_камчатка'].dt.date
        
        # Определяем день относительно Камчатки
        df['день'] = df['дата_камчатка'].apply(lambda x: 'сегодня' if x == today_kamchatka else 'завтра')
        
        # Оставляем нужные колонки
        df['время'] = df['время_камчатка'].dt.strftime('%H:00')
        
        df['ощущаемая_температура'] = df['температура_с'] - (df['влажность_процент']/100) * 0.3
        df['дата_загрузки'] = now_kamchatka.strftime("%Y-%m-%d %H:%M:%S")
        
        # Сохранение
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Выбираем только нужные колонки для сохранения
        output_df = df[['время', 'температура_с', 'влажность_процент', 'давление_гпа', 
                        'ощущаемая_температура', 'день', 'дата_загрузки']]
        
        output_df.to_sql('weather_petropavlovsk', con=engine, if_exists='replace', index=False)
        
        today_count = len(output_df[output_df['день'] == 'сегодня'])
        tomorrow_count = len(output_df[output_df['день'] == 'завтра'])
        
        print(f"✅ Успешно! Загружено {len(output_df)} записей")
        print(f"   📅 Сегодня: {today_count}")
        print(f"   📅 Завтра: {tomorrow_count}")
        
        # Покажем пример данных
        print("\n📋 Пример данных (первые 3 строки):")
        print(output_df[['время', 'температура_с', 'день']].head(3))
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_etl()