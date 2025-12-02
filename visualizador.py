# -*- coding: utf-8 -*-
import py3Dmol

class ProteinVisualizer:
    def __init__(self, file_data: str, file_extension: str):
        self.file_data = file_data
        self.file_extension = file_extension.lower()

    def _add_model(self, view: py3Dmol.view) -> None:
        if self.file_extension == "pdb":
            view.addModel(self.file_data, "pdb")
        elif self.file_extension == "cif":
            view.addModel(self.file_data, "cif")
        else:
            raise ValueError("Formato de archivo incorrecto. Solo ingrese archivos de tipos PDB y CIF.")

    def generate_visualization(self, style: str = "cartoon") -> str:
        view = py3Dmol.view(width=800, height=600)
        self._add_model(view)
        if style.lower() == "cartoon":
            view.setStyle({"cartoon": {"color": "spectrum"}})
        elif style.lower() == "stick":
            view.setStyle({"stick": {}})
        elif style.lower() == "sphere":
            view.setStyle({"sphere": {}})
        else:
            raise ValueError(f"Estilo sin soporte: {style}. Escoga 'cartoon', 'stick', or 'sphere'.")
        view.zoomTo(1.5)
        return view._make_html()
