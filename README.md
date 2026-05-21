# 🌤️ Weather ETL Pipeline — Петропавловск-Камчатский

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.7.1-green.svg)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Автоматизированный ETL-пайплайн для сбора, обработки и визуализации данных о погоде в Петропавловске-Камчатском. Данные собираются из открытого API Open-Meteo, обрабатываются с помощью Python, оркестрируются Apache Airflow и визуализируются через интерактивный веб-дашборд.

**Что делает проект:**
- ✅ Автоматически загружает почасовой прогноз погоды на сегодня и завтра
- ✅ Рассчитывает ощущаемую температуру на основе температуры и влажности
- ✅ Сохраняет данные в SQLite базу данных внутри Docker-контейнера
- ✅ Предоставляет интерактивные графики температуры и влажности
- ✅ Сравнивает погоду с другими городами (Москва, СПб, Владивосток)

---

## 🚀 Быстрый старт

### Предварительные требования

- **Docker Desktop** (Windows) — [скачать](https://www.docker.com/products/docker-desktop/)
- **Python 3.10+** (только для локального запуска веб-приложения)

### Установка и запуск (через Docker)

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/kristina-firsova-23/weather-etl-pipeline.git
   cd weather-etl-pipeline
