#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Mise à jour : 30/12/2015

# Contient les classes utilisés dans le cadre de l'assignation des structures 
# secondaires, pour le projet BDD

# Accès aux données :
# 
#   Accès à la séquence de structures secondaires PROSS d'une structure donnée:
#           seq = structure.pross_assignation.ss_sequence
#   Accès au troisième angle psi
#           seq = structure.pross_assignation.angles[2][1]

class PDB_structure:
    """
        Structure tridimensionnelle d'une protéine définie par son identifiant 
        PDB, pouvant faire l'objet d'assignation de structures secondaires
    """
    def __init__(self, pdb_id, chain):
        # Constructeur prenant en entrée l'identifiant PDB et la chaine
        self.pdb_id = pdb_id
        self.chain = chain
        
        # Initialement, aucune assignation n'est faite
        self.segno_assignation = None
        self.pross_assignation = None
        self.dssp_assignation = None
        self.dssppii_assignation = None
    
    # L'ajout de données d'assignation est effectué par les fonctions
    # appropriées
    def add_segno_assignation(self, assignation):
        self.segno_assignation = assignation
    
    def add_pross_assignation(self, assignation):
        self.pross_assignation = assignation
        
    def add_dssp_assignation(self, assignation):
        self.dssp_assignation = assignation
        
    def add_dssppii_assignation(self, assignation):
        self.dssppii_assignation = assignation
        
class Assignation:
    """
        Contient les données d'assignation de structure secondaire telles 
        qu'extraites à partir des sorties des algorithmes.
        Ces données correspondent à la séquence en structures secondaires et 
        à l'ensemble des angles phi et psi, normalisés quel que soit
        l'algorithme utilisé pour l'assignation (PROSS, DSSP...)
    """
    def __init__(self, method, ss_sequence, angles):
        # method : chaine de caractères correspondant à l'algorithme utilisé
        # pour l'assignation des structures secondaires
        # Possibilités : SEGNO, PROSS, DSSP, DSSPPII
        # ex : "PROSS"
        self.method = method
        
        # ss_sequence : Chaîne de caractère correspondant à la séquence des 
        # structures secondaires 
        # ex : "hhHHHEEEpp"
        self.ss_sequence = ss_sequence
        
        # angles : Liste de tuples des angles phi et psi tel que (phi, psi)
        # ex : [(40, 20), (30, 40)]
        self.angles = angles
        
if __name__ == "__main__":
    # Création d'une structure PDB
    ex_pdb_id = "4RUN"
    new_structure = PDB_structure(ex_pdb_id)
    
    # Création d'une nouvelle assignation PROSS
    ex_ss_sequence = 'hhHHHEEEpp'
    ex_angles = [(40, 20), (30, 40)]
    new_pross_assignation = Assignation('PROSS', ex_ss_sequence, ex_angles)
    
    # Ajout de l'assignation à la structure
    new_structure.add_pross_assignation(new_pross_assignation)
    
    # Affichage de la séquence en structures secondaires
    print new_structure.pross_assignation.ss_sequence
