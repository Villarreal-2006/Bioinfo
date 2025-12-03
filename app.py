
import requests
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
import io
import streamlit as st
from visualizador import ProteinVisualizer
import re
import json

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

    st.subheader(":card_index_dividers: Información de la proteína")
    protein_info = {
        'Título/Descripción': 'No disponible', 
        'Nombre de la molécula': 'No disponible', 
        'Clasificación/Palabras clave': 'No disponible', 
        'Método experimental': 'No disponible',
        'Organismo': 'No disponible'
    }
    if file_extension == 'pdb':
        pdb_id_match = re.search(r'HEADER\s+.*?\s+([A-Z0-9]{4})', file_data)
        pdb_id = None
        if pdb_id_match:
            pdb_id = pdb_id_match.group(1)
            st.write(f"Detected PDB ID: {pdb_id}") # For debugging

        if pdb_id:
            api_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
            try:
                response = requests.get(api_url)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                # Extract information and update dictionary
                protein_info['Título/Descripción'] = data.get('rcsb_entry_container_identifiers', {}).get('entry_title', 'No disponible')

                # Molecule Name - trying to get from entity_macromolecule or reference_entity_identifiers
                molecule_name = 'No disponible'
                if 'entity_macromolecule' in data and len(data['entity_macromolecule']) > 0:
                    molecule_name = data['entity_macromolecule'][0].get('chem_comp_name', 'No disponible')
                elif 'rcsb_entry_container_identifiers' in data and 'reference_entity_identifiers' in data['rcsb_entry_container_identifiers'] and len(data['rcsb_entry_container_identifiers']['reference_entity_identifiers']) > 0:
                    molecule_name = data['rcsb_entry_container_identifiers']['reference_entity_identifiers'][0].get('chem_comp_name', 'No disponible')
                protein_info['Nombre de la molécula'] = molecule_name

                protein_info['Clasificación/Palabras clave'] = ', '.join(data.get('rcsb_entry_info', {}).get('keywords', ['No disponible']))
                protein_info['Método experimental'] = data.get('exptl', [{}])[0].get('method', 'No disponible')

                # Organism - trying to get from organism_scientific or organism_common
                organism = 'No disponible'
                if 'entity' in data and len(data['entity']) > 0 and 'rcsb_macromolecular_info' in data['entity'][0]:
                    organism = data['entity'][0]['rcsb_macromolecular_info'].get('organism_scientific', data['entity'][0]['rcsb_macromolecular_info'].get('organism_common', 'No disponible'))
                protein_info['Organismo'] = organism

            except requests.exceptions.RequestException as e:
                st.warning(f"Error fetching PDB info from API: {e}")
            except json.JSONDecodeError:
                st.warning("Error decoding JSON from PDB API response.")
            except IndexError: # Catch errors for list indexing if data structure is unexpected
                st.warning("Unexpected data structure from PDB API response (IndexError).")
            except KeyError: # Catch errors for dictionary key access if data structure is unexpected
                st.warning("Unexpected data structure from PDB API response (KeyError).")

        # Fallback to regex-based parsing if API failed or no PDB ID was found
        if protein_info['Título/Descripción'] == 'No disponible':
            protein_info['Título/Descripción'] = get_pdb_regex_info(file_data, r"TITLE\s*(.*)")

        if protein_info['Nombre de la molécula'] == 'No disponible':
            molecule_name_regex = get_pdb_regex_info(file_data, r"COMPND.*?MOL_ID:\s*\d+;\s*MOLECULE:\s*(.*?)(?:;\s*|\n)")
            if molecule_name_regex == 'No disponible': # Simpler fallback if the first regex doesn't work
                molecule_name_regex = get_pdb_regex_info(file_data, r"COMPND\s*(.*?)")
            protein_info['Nombre de la molécula'] = molecule_name_regex

        if protein_info['Clasificación/Palabras clave'] == 'No disponible':
            protein_info['Clasificación/Palabras clave'] = get_pdb_regex_info(file_data, r"KEYWDS\s*(.*)")

        if protein_info['Método experimental'] == 'No disponible':
            protein_info['Método experimental'] = get_pdb_regex_info(file_data, r"EXPTL\s*METHOD\s*:\s*(.*)")

        if protein_info['Organismo'] == 'No disponible':
            organism_scientific_regex = get_pdb_regex_info(file_data, r"SOURCE.*?ORGANISM_SCIENTIFIC:\s*(.*?)(?:;\s*|\n)")
            if organism_scientific_regex == 'No disponible':
                organism_scientific_regex = get_pdb_regex_info(file_data, r"SOURCE.*?ORGANISM:\s*(.*?)(?:;\s*|\n)")
            protein_info['Organismo'] = organism_scientific_regex
    elif file_extension == "cif":
        try:
            # Use io.StringIO to parse the string data
            cif_io = io.StringIO(file_data)
            cif_dict_data = MMCIF2Dict(cif_io)

            # Populate protein_info using the helper function
            protein_info['Título/Descripción'] = get_cif_value(cif_dict_data, '_entry.title')
            
            # Molecule name - often found in _entity.pdbx_description or _entity_poly.pdbx_entity_type
            # MMCIF2Dict structure can be tricky, often a list of dictionaries if multiple entries
            molecule_names = []
            if '_entity.pdbx_description' in cif_dict_data:
                # This is usually a list of descriptions for each entity
                molecule_names.extend(get_cif_value(cif_dict_data, '_entity.pdbx_description').split(', '))
            protein_info['Nombre de la molécula'] = ', '.join(list(set(molecule_names))) if molecule_names else 'No disponible'

            protein_info['Clasificación/Palabras clave'] = get_cif_value(cif_dict_data, '_struct_keywords.pdbx_keywords')
            if protein_info['Clasificación/Palabras clave'] == 'No disponible':
                protein_info['Clasificación/Palabras clave'] = get_cif_value(cif_dict_data, '_entry.descr_gen') # Fallback

            protein_info['Método experimental'] = get_cif_value(cif_dict_data, '_exptl.method')

            # Organism - typically found in _entity_src_gen or _entity_src_nat
            organism_scientific = get_cif_value(cif_dict_data, '_entity_src_gen.pdbx_organism_scientific')
            if organism_scientific == 'No disponible':
                organism_scientific = get_cif_value(cif_dict_data, '_entity_src_nat.pdbx_organism_scientific')
            protein_info['Organismo'] = organism_scientific

        except Exception as e:
            st.warning(f"Error parsing CIF file with Bio.PDB: {e}")

    # Display protein information (after potential API update or CIF parsing)
    for key, value in protein_info.items():
        st.write(f"**{key}**: {value}")

else:
    st.subheader("Proyecto final - Bioinformática")
    st.write("""
        Realizado por Diana Mariella Villarreal Lopez & Jose Eduardo Mungaray Martinez
    """)
        
