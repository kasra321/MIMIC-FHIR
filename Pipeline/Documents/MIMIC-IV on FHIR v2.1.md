---
title: "MIMIC-IV on FHIR v2.1"
source: "https://physionet.org/content/mimic-iv-fhir/2.1/fhir/#files-panel"
author:
  - "[[Alex Bennett]]"
  - "[[Joshua Wiedekopf]]"
  - "[[Hannes Ulrich]]"
  - "[[Philip van Damme]]"
  - "[[Piotr Szul]]"
  - "[[John Grimes]]"
  - "[[Alistair Johnson]]"
published: 2001-11-12
created: 2025-12-16
description: "MIMIC-IV and MIMIC-IV-ED data mapped into FHIR resources."
tags:
  - "clippings"
---
Database Credentialed Access

## MIMIC-IV on FHIR

**, , , , , ,**

Published: Nov. 12, 2024. Version: 2.1

---

## Abstract

Fast Healthcare Interoperability Resources (FHIR) has emerged as a robust standard for healthcare data exchange. To explore the use of FHIR for the process of data harmonization, we converted the Medical Information Mart for Intensive Care IV (MIMIC-IV) and MIMIC-IV Emergency Department (MIMIC-IV-ED) databases into FHIR. We extended base FHIR to encode information in MIMIC-IV and aimed to retain the data in FHIR with minimal additional processing, aligning to US Core v4.0.0 where possible. A total of 24 profiles were created for MIMIC-IV data, and an additional 6 profiles were created for MIMIC-IV-ED data. Code systems and value sets were created from MIMIC terminology. We hope MIMIC-IV in FHIR provides a useful restructuring of the data to support applications around data harmonization, interoperability, and other areas of research.

---

## Background

The FHIR standard provides a framework for structuring health data and supporting data exchange amongst disparate systems and vendors. Documentation for FHIR is richly detailed and openly available \[1\]. Briefly, FHIR consists of a set of resources which describe the most commonly encountered entities in healthcare. As local contexts are expected to deviate from the global standard, FHIR introduces a mechanism called "profiling". Profiles are modifications of the base FHIR resources intended for use in a local context, such as a hospital system or primary care clinic. These profiles allow for the flexibility to capture data as exchanged in the local system, while still enabling standardization as a majority of fields present in each resource will be consistent with the global standard (the base resource). FHIR also provides significant detail around all aspects of information exchange, and has a large ecosystem of tooling particularly around data exchange.

As a part of broader federal efforts to promote health information technology and interoperability, the Office of the National Coordinator for Health Information Technology (ONC) created the United States Core Data for Interoperability (USCDI) standard. The USCDI standard is a set of health data classes and data elements that are essential for nationwide, interoperable health information exchange. Although no specific exchange format is mandated, the ONC promotes the use of FHIR to exchange information according to the USCDI standard. To support FHIR based exchange of data adhering to USCDI by health systems, a set of Implementation Guides were created, commonly referred to as US Core. The US Core Implementation Guide provides extensive detail on how to format and exchange data which adheres to the USCDI standard. As a result, US Core has become a common extension of FHIR used by health systems across the US for interoperability. The latest version is available online \[2\].

Although FHIR is broadly used by health systems world wide, there remains a paucity of health system derived data publicly available in FHIR. Prominent publicly available datasets include MIMIC-IV, a relational database corresponding to over 60,000 patients and MIMIC-IV-ED, an extension of MIMIC-IV including data from emergency department patients \[3, 4\]. MIMIC-IV has gained traction in the community due to its transparent mechanism of data access, reasonably large sample size, and authentic capture of a real-world electronic health record database. A substantial portion of MIMIC-III and MIMIC-IV has already been translated into FHIR to assist in research and development in the German FHIR context \[5, 6\]. The MIMIC-IV-ED FHIR resources presented here have been shown to improve the quality of the dataset with respect to Findable, Accessible, Interoperable, Reusable (FAIR) criteria \[13\].

MIMIC-IV-on-FHIR, this PhysioNet project, aims to translate MIMIC-IV into FHIR, preserve the MIMIC-IV structure and information, and provide an easily accessible FHIR dataset for use in research and development.

---

## Methods

MIMIC-IV-on-FHIR aims to restructure MIMIC-IV in the FHIR format with as little information loss in translation as possible. FHIR stores healthcare information in resources, encoded as either JavaScript Object Notation (JSON), eXtended Markup Language (XML), or otherwise. Thus the mapping process involved mapping each record within MIMIC-IV relational database tables to FHIR resources. We chose JSON as the serialization format. The mapping process involved five steps:

1. Terminology Generation. Capturing the MIMIC-IV terminology in FHIR was needed to retain the rich context MIMIC provides. We did not attempt to map any MIMIC-IV concepts to standard ontologies. However we generate new codes using only standard ontologies where necessary, such as the use of a SNOMED-CT code to indicate the existence of triage at an emergency center for MIMIC-IV-ED patients. FHIR stores terminology in two resources: CodeSystems and ValueSets. CodeSystems are the source for codes and ValueSets are use-case specific and combinations of CodeSystems. Codes were pulled from the MIMIC-IV tables and then converted to CodeSystems and ValueSets. Once created, the ValueSets are bound to data elements in resources. These bindings are utilized by the FHIR server to validate proper codes are assigned to resource data elements.
1. Implementation Guide Creation. To provide a reproducible FHIR format for MIMIC, an implementation guide (IG) was made \[7, 8\]. A FHIR IG is a collection of FHIR profiles and terminology aiming to achieve a task within a specific domain. The creation of FHIR IGs additionally allows for publication of a website where users can explore the resources in detail. The MIMIC implementation guide includes 22 profiles, 64 terminology resources, and 2 extensions. Where possible MIMIC profiles were aligned with the US Core R4 profiles, but they do not explicitly inherit from US Core \[2\].
1. Mapping. The goal for mapping was to have as complete a picture of MIMIC-IV in FHIR. Each column in MIMIC-IV was investigated to identify potential mappings from MIMIC-IV columns to FHIR resource elements. Data from the MIMIC-IV tables were mapped to FHIR elements, and Structured Query Language (SQL) code was written to export the mapped data as JSON serialized FHIR resources. The final MIMIC-IV column to FHIR element mappings can be found in the MIMIC implementation guide. For MIMIC-IV columns without direct mappings into FHIR, extensions were made to house the information. After mapping into FHIR, the resources may be validated against the MIMIC implementation guide, as the native SQL tooling does not guarantee conformance of the exported data.
1. Validation. A FHIR server was used to validate the mapped MIMIC data. Validation is a useful exercise for locating issues in terminology binding, inter-resource referencing, or improper element mappings. The FHIR validation effectively provides unit testing for the correctness of the MIMIC to FHIR mappings completed.
1. Export. We chose ndjson as the format for distribution of the dataset. Exporting the validated mimic-fhir resources to ndjson required two main steps. First, the bulk export functionality of FHIR servers was leveraged to export all the resources. Second, the exported resources were then written to the ndjson format. At this stage the exported njdsons represent the full picture of MIMIC-IV-on-FHIR. We compressed the ndjson files using gzip to reduce the file size.

Note that although steps 4 and 5 are important for ensuring adherence of the data to the publicized implementation guide, it is also possible to directly export MIMIC-IV on FHIR from the source database into ndjson after it has been completely mapped in step 3.

---

## Data Description

MIMIC-IV-on-FHIR is a collection of FHIR profiles, each of which is used to house data transformed from MIMIC-IV and MIMIC-IV-ED databases. The base FHIR resources used include `Condition`, `Encounter`, `Medication`, `MedicationAdministration`, `MedicationDispense`, `MedicationRequest`, `Observation`, `Organization`, `Patient`, and `Procedure`. As we aimed to reproduce the data within FHIR without modification, we did not perform terminology mapping. As a result, new profiles were necessary in order to bind the original terminology present in the MIMIC-IV and MIMIC-IV-ED databases.

Table 1 provides an overview of all profiles created, the original MIMIC-IV or MIMIC-IV-ED tables used to source the data, and profile specific notes. After Table 1, we describe each profile in turn, highlighting (1) the base FHIR resource it inherits from, (2) relevant terminologies which were bound in the profile, and (3) other important attributes of the profiles.

*Table 1. Approximate mapping of MIMIC-IV tables with FHIR resources.*

<table><thead><tr><th><p><strong>MIMIC Schema</strong></p></th><th><p><strong>Table source for data</strong></p></th><th><p><strong>New FHIR Profile</strong></p></th><th><p><strong>Notes</strong></p></th></tr></thead><tbody><tr><td colspan="1" rowspan="3"><p>hosp</p><p>(patient tracking)</p></td><td><p><em>patients</em></p></td><td><p><u>MimicPatient</u></p></td><td><p>Patient birthdate was estimated by taking the anchor_age and subtracting the transfers.intime.</p></td></tr><tr><td><p><em>admissions</em></p></td><td><p><u>MimicEncounter</u></p></td><td></td></tr><tr><td><p><em>transfers</em></p></td><td><p><u>MimicEncounter</u></p><p><u>MimicLocation</u></p></td><td><p>Care units are translated to Location resources. These are referenced in the main Encounter</p></td></tr><tr><td colspan="1" rowspan="7"><p>hosp</p></td><td><p><em>diagnoses_icd</em>, <em>d_icd_diagnoses</em></p></td><td><p><u>MimicCondition</u></p></td><td></td></tr><tr><td><p><em>procedures_icd</em>, <em>d_icd_procedures</em></p></td><td><p><u>MimicProcedure</u></p></td><td></td></tr><tr><td><p><em>labevents</em>, <em>d_labitems</em></p></td><td><p><u>MimicObservationLabevents</u><br><u>MimicSpecimen</u></p></td><td><p>LOINC was not used. Terminology consists of the original itemid values.</p></td></tr><tr><td><p><em>microbiologyevents</em></p></td><td><p><u>MimicObservationMicroTest</u><br><u>MimicObservationMicroOrg</u><br><u>MimicObservationMicroSusc</u><br><u>MimicSpecimen</u></p></td><td><p>Microbiology data had to be divided into three separate resources to be represented in FHIR. There is a parent-child relationship going from Test-&gt;Org-&gt;Susc.</p></td></tr><tr><td><p><em>prescriptions</em>, <em>poe</em></p></td><td><p><u>MimicMedicationRequest</u></p></td><td><p>Prescriptions was the primary source for medication requests, but poe was used if a request was made but no linking pharmacy_id was present, such as for large volumes of fluid.</p></td></tr><tr><td><p><em>pharmacy</em></p></td><td><p><u>MimicMedicationDispense</u></p></td><td></td></tr><tr><td><p><em>emar</em>, <em>emar_detail</em></p></td><td><p><u>MimicMedicationAdministration</u></p></td><td><p>The medication referenced are primarily drug names and formulary drug codes. We did not use NDC as there are missing values.</p></td></tr><tr><td colspan="1" rowspan="6"><p>icu</p></td><td><p><em>icustays</em></p></td><td><p><u>MimicEncounterICU</u></p></td><td><p>All ICU profiles point to the this profile, which references back to the original hospital admission encounter.</p></td></tr><tr><td><p><em>procedureevents</em></p></td><td><p><u>MimicProcedureICU</u></p></td><td></td></tr><tr><td><p><em>inputevents</em></p></td><td><p><u>MimicMedicationAdministrationICU</u></p></td><td></td></tr><tr><td><p><em>chartevents</em></p></td><td><p><u>MimicObservationChartevents</u></p></td><td></td></tr><tr><td><p><em>datetimeevents</em></p></td><td><p><u>MimicObservationDatetimevents</u></p></td><td></td></tr><tr><td><p><em>outputevents</em></p></td><td><p><u>MimicObservationOutputevents</u></p></td><td></td></tr><tr><td colspan="1" rowspan="7"><p>ed</p></td><td><p><em>edstays</em></p></td><td><p><u>MimicEncounterED</u></p></td><td><p>All ED profiles point to the this profile, which references to the subsequent hospital admission encounter if the individual was later hospitalized.</p></td></tr><tr><td><p><em>diagnosis</em></p></td><td><p><u>MimicConditionED</u></p></td><td></td></tr><tr><td><p><em>medrecon</em></p></td><td><p><u>MimicMedicationStatementED</u></p></td><td></td></tr><tr><td><p><em>pyxis</em></p></td><td><p><u>MimicMedicationDispenseED</u></p></td><td></td></tr><tr><td><p><em>triage</em></p></td><td><p><u>MimicProcedureED</u></p></td><td><p>The existence of an emergency department triage event is considered a procedure.</p></td></tr><tr><td><p><em>vitalsign</em>, <em>triage</em></p></td><td><p><u>MimicObservationED</u></p></td><td><p>Pain and heart rhythm documentation.</p></td></tr><tr><td><p><em>vitalsign</em>, <em>triage</em></p></td><td><p><u>MimicObservationVitalSignsED</u></p></td><td><p>Vital sign documentation.</p></td></tr></tbody></table>

### Patient and Organization Resources

#### MimicOrganization

An `Organization` resource records any institutions or organization associated with healthcare services.

A single `MimicOrganization` resource was created for all of MIMIC-IV as the Beth Israel Deaconess Medical Center is the organization for all stays in the database.

#### MimicLocation

The Location resource records any physical location where services are delivered in relation to the hospital.

Each unique care unit found in transfers was translated into a `MimicLocation` resource. In total, there are 41 Location resources created for each of the care units. When a patient is transferred to one of these care units, the location element of their Encounter resource will contain a reference to one of the 41 `MimicLocation` resources.

#### MimicPatient

The `Patient` resource records the demographic information for a patient associated with an organization.

The *patients* table joined with the admissions and transfers tables mapped to the `MimicPatient` profile. Several assumptions were made to assist in the mapping to the `Patient` resource. First, the birthdate was calculated since only an anchor\_age is given for patients. The intime column of the *transfers* table was used as a base for the birthdate calculation versus using the admittime column of the *admissions* table, since the admittime column is only available for hospitalized patients (i.e. it excludes ED only stays). Second, the birthsex extension element uses the gender column from MIMIC-IV as there is no specific documentation of birth sex available. Finally, the `MimicPatient` name element is derived from the subject\_id column of the *patients* table following format of “Patient\_”.

#### MimicEncounter and MimicEncounterED

The `Encounter` resource records the full span of a hospital stay, including admission, stay, and discharge. Although both inpatient and outpatient encounters can be referenced using the `Encounter` resource, only inpatient encounters exist in MIMIC-IV v2.2. Data from the *admissions* and *icustays* tables were mapped to the `MimicEncounter` profile. `MimicEncounter` contains custom terminology bindings for admission class, admission type, admission source and discharge disposition. The primary information mapped from admissions was the admission start and stop time along with the context for the admission. Additional information is supplied for the encounter from the *transfers* table in the form of `Location` resources. The `Location` resources track the movement of the patient throughout their encounter, i.e. each inter-ward transfer in the *transfers* table will result in a new reference to a `Location` resource. The `MimicEncounterED` profile is similar and contains information for stays within the ED.

### Specimen Related Observation Profiles

#### MimicObservationLabevents

A standard way to map lab observations was created by US Core with their profile `USCoreLaboratoryResultObservationProfile`. The US core profile was used as reference but not as a parent resource for `MimicObservatoinLabevents` as we chose to not modify terminology present in MIMIC, and the US Core profiles have strict terminology bindings. `MimicObservationLabevents` contains terminology bindings for lab codes and interpretation plus an extension for lab priority. Rows from the *labevents* table were mapped to `MimicObservationLabevents` resources, and these resources primarily capture the item code, resulting value, interpretation, and timing for labs.

#### MimicObservationMicroTest, MimicObservationMicroOrg, and MimicObservationMicroSusc

We found that microbiology observations were too complex to map to a single resource in FHIR. We chose to map a single microbiology observation into three resources covering the test, organisms detected, and susceptibility results. Three `Observation` profiles were generated: `MimicObservationMicroTest`, `MimicObservationMicroOrg`, and `MimicObservationMicroSusc`.

`MimicObservationMicroTest` captures the test information documented in the *microbiologyevents* table. Test codes, timing and comments are delineated in the profile. If a microbiology test is associated with the growth of an organism, references to `MimicObservationMicroOrg` resources are created. There are a significant number of tests with no reference to an organism, and these tests are stored with their result pulled from the comments. Alternatively, tests with no organism growth would not have an associated organism.

`MimicObservationMicroOrg` captures the organism information from the *microbiologyevents* table including MIMIC-IV specific organism codes and their descriptions. If the organisms were tested for susceptibility to antibiotics, references to child `MimicObservationMicroSusc` resources were created. Additionally, all `MimicObservationMicroOrg` resources will have a reference to the "parent" `MimicObservationMicroTest` resource.

`MimicObservationMicroSusc` captures the susceptibility results from the *microbiologyevents* table including MIMIC-IV specific terminology codes for antibiotics, their descriptive name, and interpretation of the susceptibility. An extension was also added to `MimicObservationMicroSusc` to house the dilution values for susceptibility testing.

#### MimicSpecimen

Microbiology and laboratory tests are conducted on samples derived from the individual, and these samples are referred to as specimens. In FHIR, the `Specimen` resource records information about a material sample, and the `MimicSpecimen` profile is based on this resource. The `MimicSpecimen` profile captures the specimen information from both the *microbiologyevents* and *labevents* tables in MIMIC-IV. Notably attributes of this profile include the type of fluid and a unique identifier for the specimen, which is distinct for microbiology and laboratory tests.

### Medication Profiles

#### MimicMedication

In FHIR, the `Medication` resource records medications and drugs available in healthcare settings. As MIMIC-IV does not have a single data table for medications, the relevant information was acquired from seven sources.

1. Formulary drug codes are pulled from the *prescriptions*  table and the *emar\_detail* table.
1. National Drug Codes (NDC) were sourced from the *prescriptions* table
1. Generic Sequence Numbers (GSN) were sourced from the *prescriptions* table
1. Generic medication names were sourced from drug and medication columns of the *prescriptions*  table as well as the medication column of the *emar* table
1. Intravenous (IV) specific events were extracted from the *poe* table when order\_type is set to IV therapy or total parenteral nutrition.
1. ICU medications were sourced from the *d\_items* table
1. Medication mixes were pulled from *prescriptions*. Medication mixes are sets of medications which are grouped together as they are typically dispensed together by the pharmacy. Medication mixes reference their component medications using an ingredients attribute. Medication mixes were included as only one Medication reference is allowed for a  MedicationRequest resource (i.e. a prescription) even though multiple medications can be requested together in MIMIC-IV.

The medication sources are included in `MimicMedication` using terminology bindings for the medication codes. All medication codes found in MIMIC-IV were bound to a single `ValueSet` resource, which combined together the `CodeSystem` resources derived from each of the seven above listed sources.

#### MimicMedicationAdministration

The `MedicationAdminstration` resource records any administration of medication in a healthcare setting. The two main MIMIC-IV documented sources for administration come from *emar* and *inputevents*. Each of these tables were mapped to a custom profile derived from the base R4 fhir profiles.

Information documented in the *emar* and *emar\_detail* tables was mapped to the `MimicMedicationAdministration` profile. `MimicMedicationAdministration` contains terminology bindings for medication site, medication method, and medication route. The primary information is pulled from each row in the *emar\_detail* table, with the *emar* table supplying the medication reference only when it is not available in product\_code column of the *emar\_detail* table.

#### MimicMedicationAdministrationICU

The *inputevents* table was mapped to `MimicMedicationAdministrationICU`. `MimicMedicationAdministrationICU` contains terminology bindings for category ICU and medication method ICU. The ICU medication administration resources will be smaller than emar medication administrations since less detailed information is available in MIMIC-IV.

#### MimicMedicationDispense

The `MedicationDispense` resource records the supply of medication to a patient. Medications in MIMIC-IV are primarily dispensed by the pharmacy. The *pharmacy* table was mapped to `MimicMedicationDispense`, with terminology bindings for medication route and medication frequency. The `MimicMedicationDispense` is linked back to `MimicMedicationRequest` through the element authorizingPrescription.

#### MimicMedicationDispenseED

The *pyxis* table was mapped to `MimicMedicationDispenseED` profile. `MimicMedicationDispenseED` contains terminology bindings for GSN medication codes and medication dispensation timing.

#### MimicMedicationRequest

The `MedicationRequest` resource records orders for medication and the administration instructions for the medication. The resource only accepts a single `Medication` resource, which means the majority of referenced medication will be medication mixes coming from the *prescriptions* table. There were two sources for `MimicMedicationRequest`: the *prescriptions* table and the *poe* table. Information from the *prescriptions* table was supplemented by the *pharmacy* table to populate missing dosage information.

The *poe* table maps orders to `MimicMedicationRequest` when events documented in the *emar* table do not have a related pharmacy\_id. This scenario is typically for IV or TPN events occurring in the hospital when a direct prescription may not have been written but the medication was ordered.

#### MimicMedicationStatementED

The `MedicationStatement` resource documents stated history of medication information. For ED derived data, this corresponds to the medicine reconciliation data present in the *medrecon* table. The `MimicMedicationStatementED` thus provides a profile for reported medication use by individuals in the ED.

### Charted Observation Profiles

#### MimicObservationChartevents, MimicObservationDatetimeevents, and MimicObservationOutputevents

The `Observation` resource records any measurements made about a patient. The *chartevents*, *datetimeevents*, and *outputevents* tables are all measurement tables for ICU events. Each table maps to a mimic observation profile, based on the base `Observation` resource. The mimic profiles are of a similar format but with different terminology bindings based on the source table.

The *chartevents* table is mapped to the `MimicObservationChartevents` profile. `MimicObservationChartevents` enforces terminology bindings for the observation code and category. Chartevents captures the majority of documented information from the ICU, thus the primary information mapped was the timing, item code and the result of the item. Additional columns were mapped to capture reference ranges and observation category.

The *datetimeevents* table is mapped to the `MimicObservationDatetimeevents` profile. `MimicObservationDatetimeevents` enforces terminology bindings for observation code and category. Information in the *datetimeevents* table follows a datetime format, thus the primary information mapped were the datetime value and the item code.

The *outputevents* table is mapped to the `MimicObservationOutputevents` profile. `MimicObservationOutputevents` enforces terminology bindings for observation code and category. The *outputevents* table holds information on the patients’ bodily outputs, thus the primary information mapped were item codes for these events and the resulting value.

#### MimicProcedureICU

The *procedureevents* table is mapped to the `MimicProcedureICU` profile. `MimicProcedureICU` enforces terminology bindings for the procedure code, body site and category. The primary information mapped from the *procedureevents* table includes timing, procedure codes, status and the procedure location.

#### MimicObservationED

Observations made in the emergency department around pain and heart rhythm were documented within the `MimicObservationED` resource, which inherited from the base `Observation` resource.

#### MimicObservationVitalSignsED

Vital signs, including heart rate, respiratory rate, temperature, and oxygen saturation, were mapped to the `MimicObservationVitalSignsED` profile. These observations are made either on triage or during routine monitoring of individuals in the emergency department.

### Billing Resources

#### MimicCondition and MimicConditionED

The `Condition` resource records conditions, diagnoses, and problems. For the `MimicCondition` profile, the *diagnoses\_icd* table was the primary source of information, including terminology bindings for the diagnosis code and condition category. The `MimicConditionED` profile contains billed ICD diagnoses from the end of an individual's ED stay.

#### MimicProcedure and MimicProcedureED

The `Procedure` resource records an action that is performed on a patient. The *procedures\_icd* table was the primary source of data for the `MimicProcedure` profile, with terminology bindings created for the ICD codes present. As the act of triage of a patient is a procedure, we created the `MimicProcedureED` to capture ED procedures, with the only ED procedure currently present being provision of triage to the individual.

---

## Usage Notes

Data files are distributed as compressed NDJSON files with the extension `ndjson.gz`. Each line of each `ndjson.gz` file is a valid FHIR resource serialized as a JSON.

An open source repository, MIMIC-FHIR, was created to store the code needed to generate and use the mimic-fhir resources \[9\]. The repository allows for community discussion and collaboration on mimic-fhir. A static version of the code for building the MIMIC-IV-on-FHIR dataset has been archived by Zenodo \[10\].

The mimic-fhir NDJSON's can be taken and loaded into any FHIR server. A jupyter notebook was developed to walk through the loading and usage of the mimic-fhir resources with the Pathling FHIR server \[11, 12\]. Pathling was used to demo the mimic-fhir resources due to its simple ndjson loading and optimized analytic operations.

An implementation guide with detailed information about the profiles created for the FHIR formatted dataset is provided online \[8\]. The code for generating the implementation guide is available in the open-source mimic-profiles repository \[7\].

---

## Release Notes

### Version 2.1

The current release of MIMIC-IV on FHIR is v2.1. This is a bug-fix release which corrects a number of issues across the dataset encountered during FHIR validation. This version sources data from MIMIC-IV v2.2 \[3\] and MIMIC-IV-ED v2.2 \[4\].

#### Validation fixes

- Generates code systems and value set resources from the mimic database (fhir\_trm schema).
- Removed unnecessary code systems and value sets.
- Added emar\_detail.product\_unit and emar\_detail.dose\_given\_unit as sources for the cs\_unit code system.
- Fixed display names for cs-diagnosis-icd9, cs-diagnosis-icd10, and cs-medication-etc code systems.
- Corrected whitespace in pharmacy.frequency (ensured compliance with coding whitespace rules).
- Updated dosageInstruction.timing in fhir\_medication\_dispense.sql (ensured inclusion of code or repeat elements).
- Handled blank medication in medication\_dispense generation (Treated blank medications as NULL values).
- Produced NULL for blank lab\_VALUE in fhir\_observation\_labevents.sql
- Handled blank dose\_given\_unit in fhir\_medication\_administration.sql
- Corrected display name for LOINC code: 2708-6 in fhir\_observation\_vitalsigns.sql
- Changed extraction of quantity from pharmacy.fill\_quantity, improving extraction logic for numerical values and units.
- Handled NULL values in BP vital signs observations (Ensured compliance with \[http://hl7.org/fhir/StructureDefinition/bp|4.0.\](http://hl7.org/fhir/StructureDefinition/bp|4.0%60.)).
- Changed JSON export format to 'csv', fixing backslash escaping issues.
- Added null value checks, prevented creation of empty objects in fhir\_medication\_administration.sql and fhir\_specimen.sql.
- Removed array wrapping for medicationCodeableConcept (fhir\_medication\_request).
- Renamed mimic-lab-priority to lab-priority (udated extension URL in fhir\_observation\_labevents).
- Fixed unit codes for respiratory and heart rate (fhir\_observation\_vitalsigns).
- Removed leading whitespace from display names (map\_race\_omb.sql).
- Added 'emar\_detail.product\_unit' and 'emar\_detail.dose\_given\_unit' as source sources for cs\_unit code system to fix: Unknown code 'TPN Bag' in the CodeSystem ' [http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-units](http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-units) ' version '2.2.0', eg: ": {"dose": {"code": "TPN Bag", "unit": "TPN Bag", ) in MedicationAdministation.
- Aligned coding display names in fhir resources with the display names in the code system for cs-diagnosis-icd9, cs-diagnosis-icd10 and cs-medication-etc to fix 'Wrong Display Name XXX' errors, e.g: Wrong Display Name 'Acne Therapy Systemic - Tetracycline antibiotic' for [http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-etc#00005953](http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-etc#00005953). Valid display is 'Acne Therapy Systemic - Tetracyclines' (en) (for the language(s) '--')

### Version 1.0

The first release of MIMIC-IV on FHIR was v1.0. This release used data from MIMIC-IV v2.2 \[3\] and MIMIC-IV-ED v2.2 \[4\].

---

## Ethics

MIMIC-IV on FHIR was created using publicly available deidentified data.

---

## Acknowledgements

The authors would like to thank those behind MIMIC-IV for making the data available and the FHIR community for support in answering questions. This work was supported by the Canadian Institutes of Health Research funding reference number 470397.

---

## Conflicts of Interest

None to declare.

---

## References

1. HL7 FHIR Documentation. [https://www.hl7.org/fhir/](https://www.hl7.org/fhir/) \[Accessed: 30 January 2024\]
2. US Core HL7 FHIR Implementation Guide. [https://www.hl7.org/fhir/us/core/](https://www.hl7.org/fhir/us/core/) \[Accessed: 6 June 2022\]
3. Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV (version 2.2). PhysioNet. [https://doi.org/10.13026/6mm1-ek67.](https://doi.org/10.13026/6mm1-ek67.)
4. Johnson, A., Bulgarelli, L., Pollard, T., Celi, L. A., Mark, R., & Horng, S. (2023). MIMIC-IV-ED (version 2.2). PhysioNet. [https://doi.org/10.13026/5ntk-km72.](https://doi.org/10.13026/5ntk-km72.)
5. Ververs, S., Ulrich, H., Kock, A.-K., & Ingenerf, J. (2018). Konvertierung von MIMIC-III-Daten zu FHIR. Jahrestagung Der Deutschen Gesellschaft Für Medizinische Informatik, Biometrie Und Epidemiologie E.V. (GDMS). [https://doi.org/10.3205/18gmds018](https://doi.org/10.3205/18gmds018)
6. Ulrich, H., Behrend, P., Wiedekopf, J., Drenkhahn, C., Kock-Schoppenhauer, A.-K., & Ingenerf, J. (2021). Hands on the Medical Informatics Initiative Core Data Set — lessons learned from converting the mimic-IV. Studies in Health Technology and Informatics. [https://doi.org/10.3233/shti210549](https://doi.org/10.3233/shti210549)
7. mimic-profiles on GitHub. [https://github.com/kind-lab/mimic-profiles](https://github.com/kind-lab/mimic-profiles) \[Accessed: 2 Jan 2024\]
8. MIMIC Implementation Guide. [https://kind-lab.github.io/mimic-fhir/](https://kind-lab.github.io/mimic-fhir/) \[Accessed: 2 Jan 2024\]
9. MIMIC-IV-on-FHIR Code on GitHub. [https://github.com/kind-lab/mimic-fhir](https://github.com/kind-lab/mimic-fhir) \[Accessed: 28 Oct 2024\]
10. Bennett AM; Johnson AJ. (2022). kind-lab/mimic-fhir: MIMIC-IV-on-FHIR v2.1.0 (v2.1.0). Zenodo. [https://doi.org/10.5281/zenodo.14003175](https://doi.org/10.5281/zenodo.14003175)
11. MIMIC-FHIR Tutorial. [https://github.com/kind-lab/mimic-fhir/blob/main/tutorial/mimic-fhir-tutorial-pathling.ipynb](https://github.com/kind-lab/mimic-fhir/blob/main/tutorial/mimic-fhir-tutorial-pathling.ipynb) \[Accessed: 6 June 2022\]
12. Pathling: Advanced FHIR Analytics Server. [https://pathling.csiro.au/](https://pathling.csiro.au/) \[Accessed: 6 June 2022\]
13. Van Damme P, Löbe M, Benis N, De Keizer NF, Cornet R. Assessing the use of HL7 FHIR for implementing the FAIR guiding principles: a case study of the MIMIC-IV Emergency Department module. JAMIA open. 2024 Apr 1;7(1):ooae002.

---

##### Parent Projects

MIMIC-IV on FHIR was derived from:
- [MIMIC-IV v2.2](https://physionet.org/content/mimiciv/2.2/)
- [MIMIC-IV-ED v2.2](https://physionet.org/content/mimic-iv-ed/2.2/)
Please cite them when using this project.

##### Access

**Access Policy:**  
Only credentialed users who sign the DUA can access the files.

**License (for files):**  
[PhysioNet Credentialed Health Data License 1.5.0](https://physionet.org/content/mimic-iv-fhir/view-license/2.1/)

**Data Use Agreement:**  
[PhysioNet Credentialed Health Data Use Agreement 1.5.0](https://physionet.org/content/mimic-iv-fhir/view-dua/2.1/)

**Required training:**  
[CITI Data or Specimens Only Research](https://physionet.org/content/mimic-iv-fhir/view-required-training/2.1/#1)

##### Discovery

**DOI (version 2.1):**  
[https://doi.org/10.13026/rrj1-ny66](https://doi.org/10.13026/rrj1-ny66)

**DOI (latest version):**  
[https://doi.org/10.13026/9hhp-ps57](https://doi.org/10.13026/9hhp-ps57)

**Topics:**  
[mimic-iv](https://physionet.org/content/?topic=mimic-iv) [fhir](https://physionet.org/content/?topic=fhir) [electronic health record](https://physionet.org/content/?topic=electronic+health+record) [us core](https://physionet.org/content/?topic=us+core) [fast healthcare interoperability resources](https://physionet.org/content/?topic=fast+healthcare+interoperability+resources) [mimic](https://physionet.org/content/?topic=mimic)

**Project Website:**  
[https://mimic.mit.edu/fhir/](https://mimic.mit.edu/fhir/)

##### Corresponding Author

Alistair Johnson  
Massachusetts Institute of Technology.  
[aewj@mit.edu](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/)

##### Versions

- [1.0](https://physionet.org/content/mimic-iv-fhir/1.0/)
- [2.1](https://physionet.org/content/mimic-iv-fhir/2.1/)

## Files

Total uncompressed size: 29.2 GB.

##### Access the files

- [Download the ZIP file](https://physionet.org/content/mimic-iv-fhir/get-zip/2.1/) (29.2 GB)
- Download the files using your terminal:
	```
	wget -r -N -c -np --user kafzali --ask-password https://physionet.org/files/mimic-iv-fhir/2.1/
	```

| Name | Size | Modified |
| --- | --- | --- |
| [Parent Directory](https://physionet.org/content/mimic-iv-fhir/2.1/#files-panel) |  |  |
| [MimicCondition.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicCondition.ndjson.gz) | 235.7 MB | 2024-10-28 |
| [MimicConditionED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicConditionED.ndjson.gz) | 56.5 MB | 2024-10-28 |
| [MimicEncounter.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicEncounter.ndjson.gz) | 52.8 MB | 2024-10-28 |
| [MimicEncounterED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicEncounterED.ndjson.gz) | 32.8 MB | 2024-10-28 |
| [MimicEncounterICU.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicEncounterICU.ndjson.gz) | 7.2 MB | 2024-10-28 |
| [MimicLocation.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicLocation.ndjson.gz) | 1.7 KB | 2024-10-28 |
| [MimicMedication.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedication.ndjson.gz) | 1.0 MB | 2024-10-28 |
| [MimicMedicationAdministration.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationAdministration.ndjson.gz) | 1.2 GB | 2024-10-28 |
| [MimicMedicationAdministrationICU.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationAdministrationICU.ndjson.gz) | 506.7 MB | 2024-10-28 |
| [MimicMedicationDispense.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationDispense.ndjson.gz) | 902.8 MB | 2024-10-28 |
| [MimicMedicationDispenseED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationDispenseED.ndjson.gz) | 73.1 MB | 2024-10-28 |
| [MimicMedicationMix.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationMix.ndjson.gz) | 604.2 KB | 2024-10-28 |
| [MimicMedicationRequest.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationRequest.ndjson.gz) | 1.1 GB | 2024-10-28 |
| [MimicMedicationStatementED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicMedicationStatementED.ndjson.gz) | 156.9 MB | 2024-10-28 |
| [MimicObservationChartevents.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationChartevents.ndjson.gz) | 14.9 GB | 2024-10-28 |
| [MimicObservationDatetimeevents.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationDatetimeevents.ndjson.gz) | 259.0 MB | 2024-10-28 |
| [MimicObservationED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationED.ndjson.gz) | 226.1 MB | 2024-10-28 |
| [MimicObservationLabevents.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationLabevents.ndjson.gz) | 8.0 GB | 2024-10-28 |
| [MimicObservationMicroOrg.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationMicroOrg.ndjson.gz) | 46.7 MB | 2024-10-28 |
| [MimicObservationMicroSusc.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationMicroSusc.ndjson.gz) | 52.4 MB | 2024-10-28 |
| [MimicObservationMicroTest.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationMicroTest.ndjson.gz) | 175.4 MB | 2024-10-28 |
| [MimicObservationOutputevents.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationOutputevents.ndjson.gz) | 163.9 MB | 2024-10-28 |
| [MimicObservationVitalSignsED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicObservationVitalSignsED.ndjson.gz) | 446.0 MB | 2024-10-28 |
| [MimicOrganization.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicOrganization.ndjson.gz) | 345 B | 2024-10-28 |
| [MimicPatient.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicPatient.ndjson.gz) | 14.9 MB | 2024-10-28 |
| [MimicProcedure.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicProcedure.ndjson.gz) | 40.9 MB | 2024-10-28 |
| [MimicProcedureED.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicProcedureED.ndjson.gz) | 77.0 MB | 2024-10-28 |
| [MimicProcedureICU.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicProcedureICU.ndjson.gz) | 34.8 MB | 2024-10-28 |
| [MimicSpecimen.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicSpecimen.ndjson.gz) | 68.6 MB | 2024-10-28 |
| [MimicSpecimenLab.ndjson.gz](https://physionet.org/content/mimic-iv-fhir/2.1/fhir/MimicSpecimenLab.ndjson.gz) | 486.8 MB | 2024-10-28 |