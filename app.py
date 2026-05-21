from flask import Flask, render_template_string, jsonify
import pandas as pd
import sqlite3
import plotly.express as px
import os
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Погода в Петропавловске-Камчатском</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <meta http-equiv="refresh" content="300"> <!-- автообновление каждые 5 минут -->
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f4f8; }
        h1 { color: #2c3e50; text-align: center; }
        h2 { color: #34495e; margin-top: 30px; }
        .chart { margin: 20px auto; max-width: 1000px; }
        .stats { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            max-width: 600px; 
            margin: 20px auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stats p { margin: 10px 0; font-size: 18px; }
        .last-update { text-align: center; color: #7f8c8d; margin-top: 30px; }
    </style>
</head>
<body>
    <h1>🌤️ Погода в Петропавловске-Камчатском</h1>
    
    <div class="stats">
        <h2>📊 Статистика за сегодня</h2>
        <p>🌡️ Максимальная температура: <strong>{{ max_temp }}°C</strong></p>
        <p>❄️ Минимальная температура: <strong>{{ min_temp }}°C</strong></p>
        <p>💧 Средняя влажность: <strong>{{ avg_humidity }}%</strong></p>
        <p>📈 Среднее давление: <strong>{{ avg_pressure }} гПа</strong></p>
    </div>
    
    <div class="stats">
        <h2>📅 Прогноз на завтра</h2>
        <p>🌡️ Максимальная температура: <strong>{{ tomorrow_max_temp }}°C</strong></p>
        <p>❄️ Минимальная температура: <strong>{{ tomorrow_min_temp }}°C</strong></p>
        <p>💧 Средняя влажность: <strong>{{ tomorrow_avg_humidity }}%</strong></p>
    </div>
    
    <div class="chart">{{ graph_temp | safe }}</div>
    <div class="chart">{{ graph_humidity | safe }}</div>
    <div class="chart">{{ graph_comparison | safe }}</div>
    
    <div class="last-update">
        Последнее обновление: {{ last_update }}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    db_path = 'data/weather_data.db'
    
    if not os.path.exists(db_path):
        return render_template_string('''
        <html><body><h1>⚠️ База данных не найдена</h1>
        <p>Запустите DAG в Airflow: <a href="http://localhost:8080">localhost:8080</a></p>
        </body></html>
        ''')
    
    conn = sqlite3.connect(db_path)
    
    # Проверяем, есть ли таблица с городами или старая
    try:
        df = pd.read_sql_query("SELECT * FROM weather_comparison", conn)
    except:
        df = pd.read_sql_query("SELECT * FROM weather_petropavlovsk", conn)
        df['город'] = 'Петропавловск-Камчатский'
    
    conn.close()
    
    # Фильтрация по дням (если есть колонка день)
    if 'день' in df.columns:
        today_df = df[df['день'] == 'сегодня']
        tomorrow_df = df[df['день'] == 'завтра']
    else:
        today_df = df
        tomorrow_df = pd.DataFrame()  # пустой DataFrame
    
    # Статистика сегодня
    max_temp = today_df['температура_с'].max()
    min_temp = today_df['температура_с'].min()
    avg_humidity = round(today_df['влажность_процент'].mean(), 1)
    avg_pressure = round(today_df['давление_гпа'].mean(), 1)
    
    # Прогноз на завтра
    if not tomorrow_df.empty:
        tomorrow_max_temp = tomorrow_df['температура_с'].max()
        tomorrow_min_temp = tomorrow_df['температура_с'].min()
        tomorrow_avg_humidity = round(tomorrow_df['влажность_процент'].mean(), 1)
    else:
        tomorrow_max_temp = tomorrow_min_temp = "Нет данных"
        tomorrow_avg_humidity = "Нет данных"
    
    # График температуры
    fig_temp = px.line(today_df, x='время', y='температура_с', 
                        title='🌡️ Температура в течение дня',
                        labels={'температура_с': 'Температура (°C)', 'время': 'Время'},
                        markers=True)
    
    # График влажности
    fig_humidity = px.bar(today_df, x='время', y='влажность_процент',
                           title='💧 Влажность воздуха',
                           labels={'влажность_процент': 'Влажность (%)', 'время': 'Время'},
                           color='влажность_процент',
                           color_continuous_scale='Blues')
    
    # График сравнения городов (если есть данные)
    if 'город' in df.columns and len(df['город'].unique()) > 1:
        fig_comparison = px.line(df, x='время', y='температура_с', color='город',
                                  title='🌍 Сравнение температуры по городам',
                                  labels={'температура_с': 'Температура (°C)', 'время': 'Время'})
        graph_comparison_html = fig_comparison.to_html(full_html=False)
    else:
        graph_comparison_html = "<p style='text-align:center'>Добавьте другие города в ETL-скрипт для сравнения</p>"
    
    return render_template_string(HTML_TEMPLATE,
                                   graph_temp=fig_temp.to_html(full_html=False),
                                   graph_humidity=fig_humidity.to_html(full_html=False),
                                   graph_comparison=graph_comparison_html,
                                   max_temp=round(max_temp, 1),
                                   min_temp=round(min_temp, 1),
                                   avg_humidity=avg_humidity,
                                   avg_pressure=avg_pressure,
                                   tomorrow_max_temp=tomorrow_max_temp if isinstance(tomorrow_max_temp, str) else round(tomorrow_max_temp, 1),
                                   tomorrow_min_temp=tomorrow_min_temp if isinstance(tomorrow_min_temp, str) else round(tomorrow_min_temp, 1),
                                   tomorrow_avg_humidity=tomorrow_avg_humidity,
                                   last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False для production
