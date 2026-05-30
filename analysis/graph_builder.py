import os
import networkx as nx
from pyvis.network import Network
from datetime import datetime  # <-- Tambahkan import ini

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


def build_graph(df):
    G = nx.Graph()

    for _, row in df.iterrows():
        source = row['Source']
        destination = row['Destination']
        price = float(row['Price'])
        duration = convert_duration_to_minutes(row['Duration'])
        
        # Cegah durasi 0 agar Dijkstra tidak error
        if duration <= 0:
            duration = 1 

        # LOGIKA BARU: Cek apakah rute ini sudah ada di dalam graf
        if G.has_edge(source, destination):
            # Ambil data harga dan durasi yang sudah tersimpan sebelumnya
            old_price = G[source][destination]['price']
            old_duration = G[source][destination]['duration']
            
            # Bandingkan! Simpan yang paling murah (price) dan paling cepat (duration)
            best_price = min(old_price, price)
            best_duration = min(old_duration, duration)
            
            # Update rute dengan nilai terbaik
            G[source][destination]['price'] = best_price
            G[source][destination]['duration'] = best_duration
            G[source][destination]['title'] = f"Best Price: ₹{best_price:,.0f} <br> Best Duration: {best_duration} mins"
            
        else:
            # Jika rute belum ada, buat garis baru
            G.add_edge(
                source,
                destination,
                price=price,
                duration=duration,
                title=f"Best Price: ₹{price:,.0f} <br> Best Duration: {duration} mins"
            )

    return G


def generate_network_html(G):
    # KUNCI PERBAIKAN: Tambahkan cdn_resources='remote'
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#111827",  
        font_color="white",
        select_menu=True,
        filter_menu=True,
        cdn_resources='remote' 
    )
    
    degrees = dict(G.degree())
    
    for node in G.nodes():
        node_size = (degrees.get(node, 0) * 2) + 10 
        hover_text = f"City: {node}<br>Total Routes: {degrees.get(node, 0)}"
        
        net.add_node(
            node, 
            label=node, 
            title=hover_text, 
            size=node_size,
            color="#06b6d4" 
        )
        
    for source, target, data in G.edges(data=True):
        net.add_edge(
            source, 
            target, 
            title=data.get('title', ''),
            color="#374151" 
        )

    net.repulsion(
        node_distance=200, 
        central_gravity=0.1, 
        spring_length=150, 
        spring_strength=0.05, 
        damping=0.9
    )

    # Memastikan folder 'static/graphs' ada sebelum file disimpan
    os.makedirs("static/graphs", exist_ok=True)
    
    # Menyimpan file HTML
    net.save_graph("static/graphs/network.html")