
import streamlit as st
from visualizador import ProteinVisualizer
from Bio.PDB import PDBParser
from Bio.PDB import MMCIFParser
import os
import tempfile

st.set_page_config(page_title="Visualizador de proteínas - Bioinformática", page_icon=":microscope:")

st.title(":microscope: Visualizador de proteínas - Bioinformática")
st.write("Sube el archivo **CIF o PDB** para visualizar su estructura molecular.")

# File uploader to handle both PDB and CIF files
uploaded_file = st.file_uploader("Sube el archivo PDB o CIF", type=["pdb", "cif"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]
    file_data = uploaded_file.read().decode("utf-8")

    st.subheader(":dna: Visualización 3D:")

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
    st.write("Movimiento: Control + Click izquierdo")
    st.write("Utiliza el menu para cambiar la representación molecular.")

    st.subheader(":page_facing_up: Vista previa del archivo:")
    st.code("\n".join(file_data.split("\n")[:30]))
    
    st.sidebar.subheader('Información de la proteína')
    
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    # Create a temporary directory and save the uploaded file
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f'Analizado y guardado con éxito: {uploaded_file.name}')

        # Parse PDB file if extension is .pdb
        if file_extension == '.pdb':
            pdb_parser = PDBParser()
            try:
                structure = pdb_parser.get_structure('protein', file_path)
                st.sidebar.write(f"Numero de modelos: {len(structure)}")
                for model in structure:
                    st.sidebar.write(f"  Model ID: {model.id}, Numero de cadenas: {len(model)}")
                    for chain in model:
                        st.write(f"    Chain ID: {chain.id}, Numero de residuos: {len(chain)}")

            except Exception as e:
                st.error(f"Error: {e}")

        # Parse CIF file if extension is .cif
        elif file_extension == '.cif':
            cif_parser = MMCIFParser()
            try:
                structure_cif = cif_parser.get_structure('protein_cif', file_path)
                st.sidebar.write(f"Number of models: {len(structure_cif)}")
                for model in structure_cif:
                    st.sidebar.write(f"  Model ID: {model.id}, Numero de cadenas: {len(model)}")
                    for chain in model:
                        st.sidebar.write(f"    Chain ID: {chain.id}, Numero de residuos: {len(chain)}")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Por favor vuelva a ingresar el archivo. Tiene que ser del tipo PBD y CIF.")
else:
    st.write("""
        Realizado por Diana Mariella Villarreal Lopez & Jose Eduardo Mungaray Martinez
    """)

        
