import pandas as pd
from datetime import datetime

# Fungsi membaca format waktu durasi (sama dengan di graph_builder agar aman)
def convert_duration_to_minutes(duration_str):
    duration_str = str(duration_str).strip()
    
    # 1. Membaca format waktu dari Excel
    try:
        t = datetime.strptime(duration_str, "%I:%M:%S %p")
        hours = t.hour
        
        # BUG FIX: Excel membungkus durasi 24 jam+ menjadi "12:XX AM" (0 Jam)
        # Jika Python membaca 0 jam, kita kembalikan ke 24 jam!
        if hours == 0 and "AM" in duration_str:
            hours = 24
            
        return (hours * 60) + t.minute
    except ValueError:
        pass
        
    # 2. Format lama (jika datanya aman berbentuk "2h 30m" atau angka)
    duration_str = duration_str.lower()
    if duration_str.replace('.', '', 1).isdigit():
        return int(float(duration_str))
        
    hours = 0
    minutes = 0
    if 'h' in duration_str:
        try:
            hours = int(duration_str.split('h')[0].strip())
        except: pass
    if 'm' in duration_str:
        try:
            minutes_part = duration_str.split('h')[-1].replace('m', '').strip()
            if minutes_part: minutes = int(minutes_part)
        except: pass
            
    return (hours * 60) + minutes


def analyze_ticket_prices(df):
    # 1. Metrik Dasar
    avg_price = round(df['Price'].mean(), 2)
    min_price = round(df['Price'].min(), 2)
    max_price = round(df['Price'].max(), 2)

    # 2. Rata-rata Maskapai
    airline_avg = (
        df.groupby('Airline')['Price']
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )

    # 3. Rata-rata Berdasarkan Jumlah Transit
    stops_avg_raw = df.groupby('Total_Stops')['Price'].mean().round(2).to_dict()
    # Mengurutkan kategori transit agar rapi di grafik
    stop_order = ['non-stop', '1 stop', '2 stops', '3 stops', '4 stops']
    stops_avg = {}
    for stop in stop_order:
        if stop in stops_avg_raw:
            stops_avg[stop] = stops_avg_raw[stop]
    for k, v in stops_avg_raw.items(): # Masukkan sisanya jika ada
        if k not in stops_avg: stops_avg[k] = v

    # 4. Data Scatter Plot (Durasi vs Harga)
    df_copy = df.copy()
    df_copy['Duration_Mins'] = df_copy['Duration'].apply(convert_duration_to_minutes)
    
    # Ambil sampel acak maksimal 1000 data agar browser pengguna tidak lag/ngehang saat merender titik
    sample_df = df_copy.sample(n=min(1000, len(df_copy)), random_state=42)
    
    scatter_data = [
        {"x": int(row['Duration_Mins']), "y": float(row['Price'])} 
        for _, row in sample_df.iterrows() 
        if int(row['Duration_Mins']) > 0
    ]

    return {
        "avg_price": avg_price,
        "min_price": min_price,
        "max_price": max_price,
        "airline_avg": airline_avg.to_dict(),
        "stops_avg": stops_avg,
        "scatter_data": scatter_data
    }