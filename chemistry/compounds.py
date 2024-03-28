from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import Descriptors #ES
import requests
from rdkit.Chem import AllChem, Descriptors
from rdkit.DataStructs.cDataStructs import ExplicitBitVect

from typing import List

SUBSTRUCTURE_FP_SIZE = 2048

EXAMPLE_COMPOUNDS = [
    # smiles, substructure fingerprint
    "CCC(Cl)C(N)C1=CC=CC=C1",
    "CCC(Cl)C(F)C1=CC=CC=C1",
    "CCC(Cl)C(F)C1CCCCC1",
    "CCC(Cl)C(N)C1CCCCC1",
    "CCC(F)C(Cl)CC",
    "CCC(F)C(N)CC",
    "CCC(Cl)C(N)C1CCC2CCCCC2C1",
]
def smiles_to_svg(smiles: str, width: int = 400, height: int = 400) -> bytes:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise RuntimeError("Invalid SMILES")

    Chem.rdCoordGen.AddCoords(mol)
    drawer = Chem.Draw.rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText().encode()

def get_substructure_fingerprint(mol):
    fp = ExplicitBitVect(SUBSTRUCTURE_FP_SIZE, True)
    return fp

def get_highlighted_image(target_smiles: str, query_smiles: str, width: int = 400, height: int = 400):
    target_mol = Chem.MolFromSmiles(target_smiles)
    query_mol = Chem.MolFromSmiles(query_smiles)
    match = target_mol.GetSubstructMatch(query_mol)

    Chem.rdCoordGen.AddCoords(target_mol)
    Chem.rdCoordGen.AddCoords(query_mol)

    drawer = Chem.Draw.rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.DrawMolecule(target_mol, highlightAtoms=match)
    drawer.FinishDrawing()
    return drawer.GetDrawingText().encode()

def get_molecule_info(match):
    print(match)
    print("get_molecule_info")

    mol = Chem.MolFromSmiles(match)
    if match is None or mol is None:
        return {
            'Name': 'Invalid',
            'NumAtoms': None,
            'MolecularWeight': None,
            'LogP': None,
            'HBD': None,
            'HBA': None,
            'PSA': None,
        }

    
    num_atoms = mol.GetNumAtoms()
    molecular_weight = round(Descriptors.MolWt(mol),2)
    logp = round(Descriptors.MolLogP(mol), 2)
    hbd = round(Descriptors.NumHDonors(mol), 2)
    hba = round(Descriptors.NumHAcceptors(mol), 2)
    psa = round(AllChem.CalcLabuteASA(mol, includeHs=True, force=False), 2)

    return {
        'NumAtoms': num_atoms,
        'MolecularWeight': molecular_weight,
        'LogP': logp,
        'HBD': hbd,
        'HBA': hba,
        'PSA': psa,
    }


def search_compounds(query_smiles: str, compound_list: List[str] = EXAMPLE_COMPOUNDS) -> List[dict]:
    query_mol = Chem.MolFromSmiles(query_smiles)
    if query_mol is None:
        raise RuntimeError("Invalid query SMILES")

    compounds = [Chem.MolFromSmiles(s) for s in compound_list]
    matches = []
    res = []
    
    for m in compounds:
        if m is None:
            matches.append([])
        else:
            matches.append(m.GetSubstructMatch(query_mol))

    print(matches)
    return matches

query_smiles = "CC"
results = search_compounds(query_smiles)

# for idx, result in enumerate(results):
#     print(f"\nCompound {idx + 1}:\n")
#     print(f"SMILES: {result['Name']}")
#     print(f"Number of Atoms: {result['NumAtoms']}")
#     print(f"Molecular Weight: {result['MolecularWeight']}")
#     print(f"logP: {result['LogP']}")
#     print(f"Number of Hydrogen Bond Donors: {result['HBD']}")
#     print(f"Number of Hydrogen Bond Acceptors: {result['HBA']}")
#     print(f"Molecular Polar Surface Area: {result['PSA']}")