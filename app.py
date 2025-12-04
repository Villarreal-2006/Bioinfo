
import streamlit as st
from visualizador import ProteinVisualizer
from Bio.PDB import PDBParser
from Bio.PDB import MMCIFParser
from Bio.PDB import PDBList
import os
import tempfile
import shutil

st.set_page_config(page_title="Visualizador de proteínas - Bioinformática", page_icon=":microscope:")

st.title(":microscope: Visualizador de proteínas - Bioinformática")
st.write("Sube el archivo **CIF o PDB** para visualizar su estructura molecular, o introduce un ID de PDB.")

pdb_id_input = st.text_input("Ingresa un ID de PDB (ej. 1FAT, 2PLB):", "")
use_example = st.button("Ver ejemplo (1FAT)")

file_data = None
file_extension = None
file_name = None
pdb_id = '1FAT'

if use_example:
    pdb_id = "1FAT"
elif pdb_id_input:
    pdb_id = pdb_id_input.upper()

uploaded_file = st.file_uploader("O sube tu propio archivo:", type=["pdb", "cif"])

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_extension = uploaded_file.name.split('.')[-1]
    file_data = uploaded_file.read().decode("utf-8")
    st.success(f"Archivo subido: {file_name}")
elif pdb_id:
    pdb_list = PDBList()
    download_success = False
    temp_dir = tempfile.mkdtemp()
    try:
        st.info(f"Intentando descargar {pdb_id} en formato CIF...")
        downloaded_path = pdb_list.retrieve_pdb_file(pdb_id, pdir=temp_dir, file_format='mmcif')
        if downloaded_path and os.path.exists(downloaded_path):
            file_extension = 'cif'
            file_name = os.path.basename(downloaded_path)
            with open(downloaded_path, 'r') as f:
                file_data = f.read()
            download_success = True
            st.success(f"Descargado {file_name} exitosamente.")
        else:
            st.warning(f"No se encontró el archivo CIF descargado para {pdb_id}.")

    except Exception as e_cif:
        st.warning(f"Error al descargar CIF para {pdb_id}: {e_cif}")

    if not download_success:
        try:
            st.info(f"Intentando descargar {pdb_id} en formato PDB...")
            downloaded_path = pdb_list.retrieve_pdb_file(pdb_id, pdir=temp_dir, file_format='pdb')
            if downloaded_path and os.path.exists(downloaded_path):
                file_extension = 'pdb'
                file_name = os.path.basename(downloaded_path)
                with open(downloaded_path, 'r') as f:
                    file_data = f.read()
                download_success = True
                st.success(f"Descargado {file_name} exitosamente.")
            else:
                st.warning(f"No se encontró el archivo PDB descargado para {pdb_id}.")

        except Exception as e_pdb:
            st.error(f"Error al descargar PDB para {pdb_id}: {e_pdb}")

    shutil.rmtree(temp_dir)

    if not download_success:
        st.error(f"No se pudo descargar la proteína {pdb_id} en ningún formato. Por favor, verifica el ID o intenta subir un archivo.")
        file_data = None


if file_data is not None:
    st.subheader(f":dna: Visualización 3D: {file_name if file_name else 'Proteína Subida'} ")

    style_options = ["Cartoon", "Stick", "Sphere"]
    style = st.radio(
        label="Estilo de visualización:",
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

    st.sidebar.subheader(":page_facing_up: Vista previa del archivo:")
    st.sidebar.code("\n".join(file_data.split("\n")[:20]))

    st.subheader('Información de la proteína')
    with tempfile.TemporaryDirectory() as tmpdir:
        if file_name:
            temp_file_path = os.path.join(tmpdir, file_name)
        else:

            temp_file_path = os.path.join(tmpdir, f"temp_protein.{file_extension}")

        with open(temp_file_path, "w") as f:
            f.write(file_data)
        st.success(f'Analizando: {file_name if file_name else "archivo subido"}')

        if file_extension == 'pdb':
            pdb_parser = PDBParser()
            try:
                structure = pdb_parser.get_structure('protein', temp_file_path)
                st.write(f"Numero de modelos: {len(structure)}")
                for model in structure:
                    st.write(f"  Model ID: {model.id}, Numero de cadenas: {len(model)}")
                    for chain in model:
                        st.write(f"    Chain ID: {chain.id}, Numero de residuos: {len(chain)}")

            except Exception as e:
                st.error(f"Error al analizar el archivo PDB: {e}")

        elif file_extension == 'cif':
            cif_parser = MMCIFParser()
            try:
                structure_cif = cif_parser.get_structure('protein_cif', temp_file_path)
                st.write(f"Number of models: {len(structure_cif)}")
                for model in structure_cif:
                    st.write(f"  Model ID: {model.id}, Numero de cadenas: {len(model)}")
                    for chain in model:
                        st.write(f"    Chain ID: {chain.id}, Numero de residuos: {len(chain)}")

            except Exception as e:
                st.error(f"Error al analizar el archivo CIF: {e}")
        else:
            st.warning("Formato de archivo no soportado para análisis detallado (solo PDB y CIF).")
else:
    if not pdb_id and not pdb_id_input and uploaded_file is None:
        st.write("""
            Realizado por Diana Mariella Villarreal Lopez & Jose Eduardo Mungaray Martinez
        """)

        
