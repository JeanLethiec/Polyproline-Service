CREATE DATABASE IF NOT EXISTS bdd_m2;
use bdd_m2;

DROP TABLE IF EXISTS AA;
DROP TABLE IF EXISTS SS_Assign;
DROP TABLE IF EXISTS PDB;

CREATE TABLE PDB (
    PDB_ID VARCHAR(4),
    chain CHAR(1),
    PDB_header TEXT,
    amino_seq TEXT,
    seq_size SMALLINT,
    resol FLOAT,
    CONSTRAINT pk_PDB PRIMARY KEY (PDB_ID, chain)
);

CREATE TABLE SS_Assign (
    PDB_ID VARCHAR(4),
    chain CHAR(1),
    struct_sec TEXT,
    date_creation TIMESTAMP,
    method VARCHAR(10),
    CONSTRAINT pk_ssassign PRIMARY KEY (PDB_ID, chain, method)
);

ALTER TABLE SS_Assign ADD CONSTRAINT fk_ssassign_pdb1 FOREIGN KEY (PDB_ID, chain) REFERENCES PDB(PDB_ID, chain);

CREATE TABLE AA (
    PDB_ID VARCHAR(4),
    chain CHAR(1),
    method VARCHAR(10),
    num_aa TINYINT,
    struct_seq CHAR(1),
    phi FLOAT,
    psi FLOAT,
    CONSTRAINT pk_ssassign PRIMARY KEY (PDB_ID, chain, method, num_aa)
);

ALTER TABLE AA ADD CONSTRAINT fk_aa_ssassign FOREIGN KEY (PDB_ID, chain, method) REFERENCES SS_Assign(PDB_ID, chain, method);
