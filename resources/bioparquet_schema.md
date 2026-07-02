# bioparquet schema

One row = one data asset. 18 top-level components (**bold**); indented rows are nested subfields.

| Field | Type | Description | Format | Access query |
| --- | --- | --- | --- | --- |
| **`description`** | `string` | Description of the data asset | Text | Free text |
| **`authors`** | `list<struct>` | Information about the authors | Name; Affiliation, ORCID | Author name, ORCID, CRediT, Organization name, ROR |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`orcid` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`credit_roles` | `list<string>` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`organization_name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`ror` | `string` |  |  |  |
| **`organizations`** | `list<struct>` | Information about the organization | Name URL, ROR | Name, ROR |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`url` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`ror` | `string` |  |  |  |
| **`publications`** | `list<struct>` | Information on the related publication | Text (Title), Publication year, DOI (Journal) | DOI |
| &nbsp;&nbsp;&nbsp;&nbsp;`title` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`year` | `int16` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`doi` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`journal` | `string` |  |  |  |
| **`license`** | `struct` | Information about the data asset's license | Creative Commons with the version and URL | CC version, URL |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`url` | `string` |  |  |  |
| **`release_date`** | `timestamp[us, tz=UTC]` | The release date of the data | ISO 8601 format (including time/time zone) | Release date, range search |
| **`acquisition_methods`** | `list<struct>` | The method used to acquire the data | FBbi, EDAM Bioimaging Ontology term and ID | FBbi or EDAM Bioimaging Ontology ID, term |
| &nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| **`specimens`** | `list<struct>` | The biological specimen or model system imaged (cell line, primary culture, tissue, organoid, ...) | CLO, CL, BTO, or OBI term and ID; anatomical location (UBERON/RadLex); genotype; treatments (ChEBI/PubChem) | Specimen ID, type, anatomical location, treatment |
| &nbsp;&nbsp;&nbsp;&nbsp;`specimen_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`specimen_type` | `struct` | The kind of biological material imaged (cell line, cell type, tissue, organoid, ...) |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`anatomical_location` | `struct` | The anatomical site in the organism the specimen was taken from |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`genotype` | `string` | Genetic modifications defining the specimen (reporter, tag, knock-in/out, edits) |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`treatments` | `list<struct>` | Compounds applied to the specimen as a treatment/perturbation |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`protocol_doi` | `string` | DOI of the protocol describing how the specimen was prepared |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`additional_metadata` | `arrow.json` |  |  |  |
| **`organisms`** | `list<struct>` | Information about the organism studied | NCBI Taxonomy term and ID, BioSample (geographic location) | NCBI Taxonomy ID, term |
| &nbsp;&nbsp;&nbsp;&nbsp;`organism_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`ncbi_taxon_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`genotype` | `string` | The organism's genetic background (strain, alleles, reporter/tagged/knocked-out genes, edits) |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`geographic_location` | `string` | The place on Earth (e.g. country/region, per BioSample) where the organism was collected |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`pathology_disease` | `list<struct>` | Pathology/disease affecting the organism |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`additional_metadata` | `arrow.json` |  |  |  |
| **`channels`** | `list<struct>` | Information about the channels (probe and target) | Ontology term and ID for the probe (with RRID) and the target | Probe ID/term/RRID, Target ID/term |
| &nbsp;&nbsp;&nbsp;&nbsp;`probe` | `struct` | The label/reagent applied or expressed |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`rrid` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`target` | `struct` | The biological molecule or structure detected; a gene/transcript (Ensembl/NCBI Gene) when imaging gene expression |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| **`instrument`** | `struct` | Information about the instrument used | Compliant with 4DN-BINA-OME-QUAREP (NBO-Q) standards, PIDInst | Instrument name, ID |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`description` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`additional_metadata` | `arrow.json` |  |  |  |
| **`axes`** | `list<struct>` | Information about data dimensions, including pixel/voxel size and time interval | Compliant with OME-Zarr axes info. (T, C, Z, Y, X); pixel/voxel size and time interval stored with units | Dimension specification, Pixel/voxel size, Time interval |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`type` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`size` | `int64` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`spacing` | `double` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`unit` | `string` |  |  |  |
| **`study`** | `struct` | The study this data asset belongs to | Accession ID, DOI | Accession ID, DOI |
| &nbsp;&nbsp;&nbsp;&nbsp;`accession_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`doi` | `string` |  |  |  |
| **`data_asset_id`** | `string` | Unique ID for the data asset | Accession ID | Accession ID |
| **`phenotype`** | `list<struct>` | Phenotypic data related to the analysis | Cell Morphology Phenotype Ontology, MPO, or HPO | Phenotype ID, term |
| &nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| **`anatomical_location`** | `list<struct>` | The anatomical region depicted by the data asset | UBERON, RadLex Ontology | UBERON ID, term |
| &nbsp;&nbsp;&nbsp;&nbsp;`ontology_source` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_id` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`term_label` | `string` |  |  |  |
| **`processing`** | `list<struct>` | Software/workflow that produced this data asset | Name, URL (e.g. source repo or release), RRID, version | Name, RRID |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`url` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`rrid` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`version` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`additional_metadata` | `arrow.json` |  |  |  |
| **`derived_data`** | `list<struct>` | Data assets derived from this one (each describes its own processing) | Name, DOI (Zenodo, Figshare), Data asset ID | Name, DOI |
| &nbsp;&nbsp;&nbsp;&nbsp;`name` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`doi` | `string` |  |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`data_asset_id` | `string` |  |  |  |
