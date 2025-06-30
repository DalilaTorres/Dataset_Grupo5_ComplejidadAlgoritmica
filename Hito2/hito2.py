import json
import math
import random
import sys
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt


def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en metros entre dos puntos geográficos."""
    R = 6_371_000 
    dlat, dlon = map(math.radians, [lat2 - lat1, lon2 - lon1])
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def cargar_grafo(path_json: Path):
    """Carga los datos de un archivo JSON y construye un grafo con NetworkX."""
    datos = json.load(path_json.open(encoding="utf-8"))["elements"]
    nodos = {e["id"]: e for e in datos if e["type"] == "node"}
    ways = [e for e in datos if e["type"] == "way" and
            "highway" in e.get("tags", {})]

    G = nx.Graph()
    for nid, n in nodos.items():
        G.add_node(nid, lat=n["lat"], lon=n["lon"], tipo="transito")

    for w in ways:
        seq = w["nodes"]
        for u, v in zip(seq[:-1], seq[1:]):
            if u in G and v in G and not G.has_edge(u, v):
                n1, n2 = nodos[u], nodos[v]
                dist = haversine(n1["lat"], n1["lon"], n2["lat"], n2["lon"])
                G.add_edge(u, v, length=dist)
    return G


def subgrafo_aleatorio(G: nx.Graph, n=1500):
    """Crea un subgrafo con 'n' nodos aleatorios si el grafo es muy grande."""
    return G if G.number_of_nodes() <= n else G.subgraph(
        random.sample(list(G.nodes), n)).copy()


def layout_seguro(G):
    """Intenta calcular la disposición de los nodos con diferentes algoritmos."""
    try:
        import scipy  # noqa: F401
        return nx.spring_layout(G, seed=42, k=0.6)
    except (ModuleNotFoundError, ImportError):
        try:
            return nx.kamada_kawai_layout(G)
        except (ModuleNotFoundError, ImportError):
            return nx.random_layout(G)



def dibujar_ruta_con_etiquetas(G, ruta, titulo):
    """
    Dibuja ÚNICAMENTE los nodos y aristas de la ruta encontrada,
    mostrando sus etiquetas (IDs) para un análisis detallado.
    """
    
    ruta_subgraph = G.subgraph(ruta)

    
    pos_ruta = nx.spring_layout(ruta_subgraph, seed=42)

    
    fig, ax = plt.subplots(figsize=(10, 8))

    
    nx.draw_networkx_nodes(ruta_subgraph, pos_ruta, node_color="#cccccc", node_size=2500, ax=ax)
    nx.draw_networkx_edges(ruta_subgraph, pos_ruta, width=2.0, edge_color="#999999", style='dashed', ax=ax)
    nx.draw_networkx_labels(ruta_subgraph, pos_ruta, font_size=10, font_color="black", ax=ax)

   
    nx.draw_networkx_nodes(ruta_subgraph, pos_ruta, nodelist=[ruta[0]], node_color="#1f78b4", node_size=3000, ax=ax)
    nx.draw_networkx_nodes(ruta_subgraph, pos_ruta, nodelist=[ruta[-1]], node_color="#33a02c", node_size=3000, ax=ax)
    
    
    labels_inicio_fin = {n: n for n in [ruta[0], ruta[-1]]}
    nx.draw_networkx_labels(ruta_subgraph, pos_ruta, labels=labels_inicio_fin, font_size=10, font_color="white", ax=ax)

    ax.set_title(titulo, fontsize=16)
    plt.margins(0.1, 0.1)
    fig.tight_layout()
    return fig



def main():
    """Función principal para ejecutar el script desde la terminal."""
    print("Este es un módulo de ayuda para la aplicación Streamlit.")
    print("Para usar la interfaz gráfica, ejecuta: streamlit run app_gui.py")

if __name__ == "__main__":
    main()