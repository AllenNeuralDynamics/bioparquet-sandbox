# foundingGIDE Metadata Fields

The founding Global Image Data Exchange (GIDE) bioimaging metadata
specification. This file is the canonical source for `bioparquet_schema.py`.

| Component | Description | Format | Access Query |
| --- | --- | --- | --- |
| Study Description | Description of the study | Text | Free text |
| Authors | Information about the authors | First name and Last name; Affiliation, ORCID | Author name, ORCID, CRediT, Organization name, ROR |
| Organization | Information about the organization | Name URL, ROR | Name, ROR |
| Publication | Information on the related publication | Text (Title), Publication year, DOI (Journal) | DOI |
| License | Information about the data asset's license | Creative Commons with the version and URL | CC version, URL |
| Release Date | The release date of the data | ISO 8601 format (including time/time zone) | Release date, range search |
| Imaging Method | The method used to obtain image data | FBbi, EDAM Bioimaging Ontology term and ID | FBbi or EDAM Bioimaging Ontology ID, term |
| Cell Line | Information about the cell line | Cell Line Ontology term and ID | CLO ID, term |
| Organism | Information about the organism studied | NCBI Taxonomy term and ID, BioSample (geographic location) | NCBI Taxonomy ID, term |
| Gene | Information about related genes | Ensembl Gene or NCBI Gene name or ID | Gene ID, name |
| Compound | Information about the compound | ChEBI or PubChem term and ID | Compound ID, term |
| Antibody | Information about the antibody used | FBbi or ChEBI term and ID, RRID | Antibody ID, term |
| Channel – Content | Content related to the channel | FBbi term and ID | Channel content ID, term |
| Channel – Biological Entity | Biological entities related to the channel | Experimental Factor Ontology term and UniProt ID | Biological entity ID, term |
| Instrument | Information about the instrument used | Compliant with 4DN-BINA-OME-QUAREP (NBO-Q) standards, PIDInst | Instrument name, ID |
| Dimension | Information about data dimensions | Compliant with OME-Zarr axes info. (T, C, Z, Y, X) | Dimension specification |
| Pixel/Voxel Size/Time resolution | Size of the pixels or voxels, Time interval | Pixel/Voxel size and time interval stored with units | Pixel/voxel size, Time interval |
| Study Unique ID | Unique ID for the study | Accession ID, DOI | Accession ID, DOI |
| Data Asset Unique ID | Unique ID for the data asset | Accession ID | Accession ID |
| Pathology/Disease (Biological Entity) | Pathology/Disease related to the biological entity | SNOMED-CT, DOID, ICD-11 or MONDO | Pathology/Disease ID, term |
| Phenotype (Analysis Data) | Phenotypic data related to the analysis | Cell Morphology Phenotype Ontology, MPO, or HPO | Phenotype ID, term |
| Organ | Information about anatomical entities | UBERON, RadLex Ontology | UBERON ID, term |
| Analyzed Data | Information about software, workflow, annotation data | GitHub URL (release), DOI (Zenodo, Figshare), RRID, Data asset ID | Name, DOI |
