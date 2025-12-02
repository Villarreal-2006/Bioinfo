
import streamlit as st
from visualizador import ProteinVisualizer
import re

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

    # Generate HTML visualization using ProteinVisualizer class
    visualizer = ProteinVisualizer(file_data, file_extension)
    html_content = visualizer.generate_visualization(style=style)
    st.components.v1.html(html_content, height=700, width=900, scrolling=True)

    # Controls Section
    st.subheader(":gear: Controles:")
    st.write("Rotar: Click derecho")
    st.write("Zoom: Shift + Click derecho o Scroll")
    st.write("Movimiento: Control + Click derecho")
    st.write("Utiliza el menu para cambiar la representación molecular.")
    st.write("Opcion de incluir los átomos de hidrogeno en la visualización.")

    # Display file preview
    st.subheader(":page_facing_up: Vista previa del archivo:")
    st.code("\n".join(file_data.split("\n")[:20]))

else:
    st.subheader(":card_index_dividers: Información de la proteína")
    protein_info = {
        'Título/Descripción': 'No disponible', 
        'Nombre de la molécula': 'No disponible', 
        'Clasificación/Palabras clave': 'No disponible', 
        'Método experimental': 'No disponible',
        'Organismo': 'No disponible'
    }
    if file_extension == 'pdb':
        title=re.search(r"^TITLE\s+(.+)", file_data, re.MULTILINE)
        if title_match:
            protein_info["Título/Descripción"] = title_match.group(1).strip()
        else:
            header_match = re.search(r"^HEADER\s+(.+)", file_data, re.MULTILINE)
            if header_match:
                protein_info["Título/Descripción"] = header_match.group(1).strip()

        compnd_lines = re.findall(r"^COMPND\s+\d+\s*(.+)", file_data, re.MULTILINE)
        if compnd_lines:
            full_compnd_text = " ".join(compnd_lines)
            molecule_match = re.search(r"MOLECULE:\s*([^;]+)", full_compnd_text, re.IGNORECASE)
            if molecule_match:
                protein_info["Nombre de la Molécula"] = molecule_match.group(1).strip()
            elif "PROTEIN" in full_compnd_text.upper():
                protein_info["Nombre de la Molécula"] = "Proteína"

        keywds_match = re.search(r"^KEYWDS\s+(.+)", file_data, re.MULTILINE)
        if keywds_match:
            protein_info["Clasificación/Palabras Clave"] = keywds_match.group(1).strip()

        expdta_match = re.search(r"^EXPDTA\s+(.+)", file_data, re.MULTILINE)
        if expdta_match:
            protein_info["Método Experimental"] = expdta_match.group(1).strip()

        source_org_scientific_match = re.search(r"ORGANISM_SCIENTIFIC:\s*([^;\n]+)", file_data, re.MULTILINE)
        if source_org_scientific_match:
            protein_info["Organismo"] = source_org_scientific_match.group(1).strip()
        else:
            source_lines = re.findall(r"^SOURCE\s+\d+\s*(.+)", file_data, re.MULTILINE)
            if source_lines:
                full_source_text = " ".join(source_lines)
                organism_match = re.search(r"ORGANISM:\s*([^;\n]+)", full_source_text, re.IGNORECASE)
                if organism_match:
                    protein_info["Organismo"] = organism_match.group(1).strip()
                else:
                    if len(source_lines[0].split()) > 1:
                        protein_info["Organismo"] = source_lines[0].split(';')[0].strip()

    elif file_extension == "cif":
        def get_cif_value(data, tag):
            match_multi = re.search(rf"^{tag}\n;\n(.+?)\n;\n", data, re.DOTALL | re.MULTILINE)
            if match_multi:
                return match_multi.group(1).strip()
            match_single = re.search(rf"^{tag}\s+['\"]?([^'\"\n]+)['\"]?", data, re.MULTILINE)
            if match_single:
                return match_single.group(1).strip()
            return "No disponible"

        protein_info["Título/Descripción"] = get_cif_value(file_data, "_struct.title")
        protein_info["Nombre de la Molécula"] = get_cif_value(file_data, "_entity.pdbx_description")
        protein_info["Clasificación/Palabras Clave"] = get_cif_value(file_data, "_struct_keywords.pdbx_keywords")
        protein_info["Método Experimental"] = get_cif_value(file_data, "_exptl.method")

        organism_scientific_nat = get_cif_value(file_data, "_entity_src_nat.organism_scientific")
        organism_scientific_gen = get_cif_value(file_data, "_entity_src_gen.organism_scientific")

        if organism_scientific_nat != "No disponible":
            protein_info["Organismo"] = organism_scientific_nat
        elif organism_scientific_gen != "No disponible":
            protein_info["Organismo"] = organism_scientific_gen

    for key, value in protein_info.items():
        st.write(f"**{key}:** {value}")
        
