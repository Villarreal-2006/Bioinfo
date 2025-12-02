
import streamlit as st
from visualizador import ProteinVisualizer

st.set_page_config(page_title="Prot-View | A BioApps Tool", page_icon=":microscope:")

st.title(":microscope: ProtView | A BioApps Tool")
st.write("Upload a **CIF or PDB file** to visualize its molecular structure.")

# File uploader to handle both PDB and CIF files
uploaded_file = st.file_uploader("Upload a PDB or CIF file", type=["pdb", "cif"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]
    file_data = uploaded_file.read().decode("utf-8")

    # 3D Molecular Visualization
    st.subheader(":dna: 3D Molecular Visualization:")

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
    st.subheader(":gear: Controls:")
    st.write("Rotate: Left Click")
    st.write("Zoom: Shift + Left Click or Scroll")
    st.write("Move: Control + Left Click")
    st.write("Use the dropdown menu to change the molecular representation.")
    st.write("Check the box to include hydrogen atoms in the visualization.")

    # Display file preview
    st.subheader(":page_facing_up: File Preview:")
    st.code("\n".join(file_data.split("\n")[:20]))  # Show first 20 lines

else:
    st.subheader(":grey_question: What are those files?")
    st.write("""
        Prot-View can work with both formats and gives the option to convert the data between them.
        \n
        The most recent data format to handle 3D protein data is
        the Macromolecular Crystallographic Information File (.cif).
        Another very common file extension is the Protein Data Bank file (.pdb).
    """)
