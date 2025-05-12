# Lipidomic Normalizer

These are the main scripts. You can either use them directly or you can bundle them into executables via auto-py-to-exe,
adding the *AppData folders* as *Additional files* and calling *-contents-directory* **AppData**.
---
The script was developed in Python 3.11.9 and executed in a Windows 11 Pro 64 bits system.

The following libraries have been used:
-	xml.etree.ElementTree (version 1.3.0)
-	pandas (version 2.2.2)
-	os 
-	tkinter (Tcl/Tk) (version 8.6.12)
-	pprint (version 3.13.1)
-	tqdm (version 4.66.5)
-	zipfile 
-	re (version 2.2.1)
-	numpy (version 2.0.1)
-	csv (version 1.0)
-	collections (version)

The program converts input data obtained through Mass Profinder into suitable formats for its statistical analysis in the open software platform MetaboAnalyst and for the proprietary software of Agilent, Mass Profiler Professional.

For this lipidomics study, the input data are written into a special Excel file due to the amount of initial conditions required for the normalization, which would be explained further on. 

Moreover, it is supported by a second Excel file, “LipidClasses.xlsx” that shows all the possible lipid names detected by LipidAnnotator, software previously used to obtain the lipid database of the analysed samples. This Excel is used as name control to maintain the coherence between the reading and conversion of data, achieving coincidences between internal standard lipids and sample lipids.  

“Template.xlsx” is ordered by sheets similarly to how is a work imported to Mass Profinder. Considering the Python script structure, is it not possible to change the sheet nor the columns header names. All the lipids that appear in the Excel must follow the format indicated by “LipidClasses.xlsx”.

- Metadata: This table identifies the samples differentiated by the group they belong to. In this way, the parameter is identified with its associated values. A sample with the same associated value is treated as a replicate of the group, and a group of replicates is considered as a condition to the parameter.
  - Needs Sample and Label headers, and at least 3 samples for each group (except quality control groups QC or blanks BLANK).
- Datos crudos: This table is the data obtained directly from Mass Profinder, exported as a *.csv “Normal” file. 
  - Compound name, Formula, Mass, RT, CAS ID: Not modifiable column headers.
  -	Features (Rows) and Samples (Columns).
- Concentraciones añadidas: It has the information related to the internal standard used for the lipidomics analysis.
  -	ISDs, [ ] µg/mL, [ ]muestra µg/mL : Not modifiable column headers.
  - Internal Standard Compounds as rows.
-	Patrones obtenidos: For all the “concentraciones añadidas” added concentrations of the sheet before, only some of them have actually appeared in the measurings of the “Datos Crudos”, which are the ones used as standards.
  -	ISDs, RT, Standard desv, RSD: Not modifiable column headers.
  -	Measured Internal Standard Compounds as rows.
-	Concentraciones patrones: Starting from the “Patrones obtenidos”, the internal standards, only the concentrations of those internal standards can be chosen from “Concentraciones añadidas”. It is “hand-written” in the sheet as data control, with the same columns as the “Concentraciones añadidas” Sheet. 
-	Áreas a normalizar: One of the reasons an Excel file is used as the input format is that specific measured intensities are needed for each standard in each sample, which implies a separate measurement in addition to the “Datos Crudos”. 
  -	Muesrea (Muestra real): Not modifiable header of the samples column. Here the samples maintain the bulk name, with the *.d format extension, of Agilent data.
  - Table with the intensities of each standard (column) for each sample: To identify each standard, the initials from “LipidClasses.xlsx” are followed as *InternalStandardCode*. “Area *InternalStandardCode*” must be written as header.
 	
This method entails a MetaboAnalyst problem, not bothered by Mass Profiler Professional data. MetaboAnalyst shows errors when there are duplicates inside the lipids listed in “Datos Crudos”. These duplicates may appear due to:
-	Double extraction (same m/z and same RT): it would be erased.
-	Different adducts (similar m/z, different RT): The less relevant adduct would be erased.
-	Isomers (exceptional case of similar m/Z and RT): Both must be taken into account, but with different.

To resolve this, the code checks if there are duplicates and if positive, those are differentiated with numeric subindexes.

The objective of the code is to transform *.xlsx input data into *.csv files for both MetaboAnalyst and Mass Profiler Professional, conducting the data standardization in between.

These standardizations are doubled, one from the concentrations and areas of the internal standards and then these standardized areas are used as the raw data (“Datos crudos”) standards based on the lipid families of those obtained internal standards. For those compounds that do not enter into any obtained internal standard lipid family, the standard would be chosen as the lipid whose retention time is similar (the difference between retention times is minimal). Focusing on this part of the script:

1.	Data input: Following the script instructions, the data are uploaded as the format of “Template.xslx” and then are read with “pandas” library. 
2.	Lipid families are coded from the obtained internal standards. 
3.	First standardization is obtained divided each “internal standard per sample” area by the concentration associated with each internal standard. 
4.	A numerical matrix from the raw data is obtained and ordered by retention time. This numeric matrix would be standardized to give the final result. It is also obtained a list of lipids ordered by this retention time.
5.	Ordered lipid list is compared with the obtained internal standards list in order to assign to each lipid its respective internal normalization standard. If the lipid doesn’t belong to any of the lipid families found, the internal standard that minimises the difference between retention times of each compounds. 
6.	Final standardization result would be a table like the initial one from “Datos crudos”, but with the standardized areas correspondingly, furthermore it is followed by the conversion to MetaboAnalyst and Mass Profiler Professional format.


