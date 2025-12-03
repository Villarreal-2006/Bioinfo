
import streamlit as st
from visualizador import ProteinVisualizer

st.set_page_config(page_title="Visualizador de proteínas - Bioinformática", page_icon=":microscope:")

st.title(":microscope: Visualizador de proteínas - Bioinformática")
st.write("Sube el archivo **CIF o PDB** para visualizar su estructura molecular.")

# File uploader to handle both PDB and CIF files
uploaded_file = st.file_uploader("Sube el archivo PDB o CIF", type=["pdb", "cif"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]
    file_data = uploaded_file.read().decode("utf-8")

    # 3D Molecular Visualization
    st.subheader(":dna: Visualización 3D:")

    # Dropdown for visualization style
    style_options = ["Cartoon", "Stick", "Sphere"]
    style = st.radio(
        label="Visualization",
        options=style_options,
        index=0,
        horizontal=True
    )

    visualizer = ProteinVisualizer(file_data, file_extension)
    html_content = visualizer.generate_visualization(style=style)
    st.components.v1.html(html_content, height=700, width=900, scrolling=True)

    st.subheader(":gear: Controles:")
    st.write("Rotar: Click izquierdo")
    st.write("Zoom: Shift + Click derecho o Scroll")
    st.write("Movimiento: Control + Click derecho")
    st.write("Utiliza el menu para cambiar la representación molecular.")

    st.subheader(":page_facing_up: Vista previa del archivo:")
    st.code("\n".join(file_data.split("\n")[:20]))
else:
    st.write("""
        Realizado por Diana Mariella Villarreal Lopez & Jose Eduardo Mungaray Martinez
    """)

        
