import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


try:
    import hito2
except ImportError:
    st.error("Error crítico: No se pudo encontrar el archivo 'hito2.py'. Asegúrate de que esté en la misma carpeta que 'app_gui.py'.")
    st.stop()


st.set_page_config(layout="wide", page_title="Análisis de Red Vial")
st.title("OptiRuta Urbana🗺️")


if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_figure' not in st.session_state:
    st.session_state.last_figure = None


@st.cache_data
def cargar_datos_iniciales():
    archivo = Path("export2.json")
    if not archivo.is_file():
        return None, None
    
    G_completo = hito2.cargar_grafo(archivo)
    G_subgrafo = hito2.subgrafo_aleatorio(G_completo, 1500)
    
    componentes = list(nx.connected_components(G_subgrafo))
    if not componentes:
        return None, None
        
    componente_mas_grande = max(componentes, key=len)
    G_principal = G_subgrafo.subgraph(componente_mas_grande).copy()
    
    return G_principal


with st.spinner("Cargando y procesando el grafo... Esto puede tardar un momento."):
    G = cargar_datos_iniciales()

if G is None:
    st.error(f"Error al cargar los datos. Asegúrate de que 'export2.json' existe y es válido.")
    st.stop()

st.success(f"Grafo principal cargado y listo. Contiene {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
st.markdown("---")


st.sidebar.header("Algoritmos de Búsqueda")
analisis_elegido = st.sidebar.radio(
    "Selecciona un algoritmo:",
    ("Búsqueda por Recorrido (BFS)", "Búsqueda Voraz (informada por A*)"),
    key="algoritmo_radio"
)

st.sidebar.subheader("Parámetros de la Búsqueda")
nodos_disponibles = sorted(list(G.nodes))
origen = st.sidebar.selectbox("Nodo de Origen:", nodos_disponibles, index=0, key="origen_select")
destino = st.sidebar.selectbox("Nodo de Destino:", nodos_disponibles, index=len(nodos_disponibles) // 2, key="destino_select")

if st.sidebar.button("Encontrar Ruta", key="btn_buscar"):
    st.session_state.last_result = None
    st.session_state.last_figure = None

    if origen == destino:
        st.warning("El nodo de origen y destino no pueden ser el mismo.")
    else:
        with st.spinner(f"Buscando ruta con {analisis_elegido}..."):
            try:
                if analisis_elegido == "Búsqueda por Recorrido (BFS)":
                    ruta = nx.shortest_path(G, origen, destino)
                    distancia = sum(G[u][v]["length"] for u, v in zip(ruta[:-1], ruta[1:]))
                    st.session_state.last_result = {"tipo": "BFS", "ruta": ruta, "distancia": distancia}
                
                elif analisis_elegido == "Búsqueda Voraz (informada por A*)":
                    ruta = nx.astar_path(G, origen, destino,
                                         heuristic=lambda u, v: hito2.haversine(G.nodes[u]["lat"], G.nodes[u]["lon"], G.nodes[v]["lat"], G.nodes[v]["lon"]),
                                         weight="length")
                    distancia = sum(G[u][v]["length"] for u, v in zip(ruta[:-1], ruta[1:]))
                    st.session_state.last_result = {"tipo": "A*", "ruta": ruta, "distancia": distancia}
                
                
                fig = hito2.dibujar_ruta_con_etiquetas(G, st.session_state.last_result['ruta'], f"Detalle de la Ruta por {st.session_state.last_result['tipo']}")
                st.session_state.last_figure = fig

            except nx.NetworkXNoPath:
                st.session_state.last_result = {"error": "No se encontró una ruta entre los nodos seleccionados."}
            except Exception as e:
                st.session_state.last_result = {"error": f"Ocurrió un error inesperado: {e}"}


col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Resultados del Algoritmo")
    if st.session_state.last_result is None:
        st.info("Selecciona los parámetros y haz clic en 'Encontrar Ruta' para ver los resultados.")
    elif "error" in st.session_state.last_result:
        st.error(st.session_state.last_result["error"])
    else:
        resultado = st.session_state.last_result
        if resultado['tipo'] == 'BFS':
            st.markdown(f"✅ **Ruta BFS encontrada**")
            st.markdown(f"- **Número de 'saltos' (paradas):** `{len(resultado['ruta']) - 1}`")
            st.markdown(f"- **Distancia total (informativa):** `{resultado['distancia']:,.2f} metros`.")
        elif resultado['tipo'] == 'A*':
            st.markdown(f"✅ **Ruta Voraz (A*) encontrada**")
            st.markdown(f"- **Número de 'saltos' (paradas):** `{len(resultado['ruta']) - 1}`")
            st.markdown(f"- **Distancia total (optimizado):** `{resultado['distancia']:,.2f} metros`.")

with col2:
    st.subheader("Visualización del Grafo")
    if st.session_state.last_figure:
        st.pyplot(st.session_state.last_figure)
    else:
        st.info("Aquí se mostrará el grafo con la ruta resaltada después de la búsqueda.")