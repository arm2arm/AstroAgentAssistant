VO & data-publishing: practical notes for Hermes skills

This reference file collects the practical guidance, placeholders, and CI checklist that the agent used when adding the "VO, data publishing, and registries" subsection to the paper. It is intentionally concise and aimed at future sessions that need to produce VO-compliant publications from DRPs.

Key standards to cite (placeholders in paper):
- IVOA VOTable specification (serialization for tabular data) [cite exact URL/DOI when available]
- IVOA ObsCore (minimal observation metadata model) [cite exact URL/DOI when available]
- IVOA TAP / ADQL (Table Access Protocol and query language) [cite exact URL/DOI when available]
- DataCite metadata schema (mapping CITATION.cff → DataCite) [cite exact URL]
- Zenodo deposit API / guide (how to mint DOIs) [cite exact URL]

Tasks a Hermes skill should perform (concise):
- Validate VOTable output: check types, units, UCDs. Use astropy.io.votable or VO libraries for validation.
- Generate ObsCore metadata: target, time/spatial coverage, publisher ID, access URL, and file format.
- Produce service descriptors and example ADQL queries if exposing TAP endpoints.
- Assemble a landing-page metadata bundle (CITATION.cff, DataCite metadata file, README, .fair-metadata/provenance.yaml) ready for archive deposit.
- Automate Zenodo or institutional archive deposit via API (scripted step), attach provenance (git commit, container digest, CI run id) to DOI landing page/metadata.

CI checklist (to run on PRs and release builds):
- VOTable schema validation using astropy/pyvo validators.
- ObsCore metadata completeness checks (required fields present).
- DataCite metadata completeness (title, creators, publisher, publicationYear, resourceType, identifier).
- Verify that CITATION.cff exists and maps to DataCite fields.
- Confirm DOI/landing page contains provenance links (git commit, container digest, CI job id).

Placeholders & provenance
- Placeholders left in paper: [IVOA VOTable spec — add citation], [ObsCore spec — add citation], [DataCite / Zenodo — add citation].
- When exact URLs are available, add BibTeX entries to references.bib and replace placeholders in main.tex.

Implementation notes & libs
- Python: astropy.io.votable, pyvo, datacite-python-client, requests for Zenodo API.
- Example command: python scripts/validate_votable.py path/to/catalog.xml

References in this file are intentionally lightweight: when live web access is available replace placeholders with canonical spec links and short descriptive quotes.
