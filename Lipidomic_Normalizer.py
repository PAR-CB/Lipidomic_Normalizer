import xml.etree.ElementTree as ET
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
from pprint import pprint
from tqdm import tqdm
import zipfile
import re
import numpy as np
import csv
from collections import defaultdict

# DEPENDENCY FOLDERS
data_path = os.path.join(os.path.dirname(__name__), 'AppData/DatosExcel', 'LipidClasses.xlsx')

## Functions
# Common
# Function for moving files to groups via metadata:
# zip creation from data folder included here
def movefilestogroups(classsamples):
    datafiles=os.listdir() # obtiene una lista de archivos inicial
    for i in range(len(classsamples)): # Para todas las clases en classsamples
        target_folder = classsamples[i][0] # primero busca la carpeta objetivo
        os.makedirs(target_folder, mode=0o777, exist_ok=True) # crea la carpeta objetivo
        for j in range(len(classsamples[i][1])): # para todos los archivos en cada clase
            for files in datafiles: # para los archivos en el listado inicial
                    if classsamples[i][1][j] in files and '_parsed' not in files:
                        # si el nombre del archivo coincide con el nombre del "archivo de la clase"
                        source_path = os.path.join('.',files) # escoge la carpeta inicial
                        target_path = os.path.join('.',target_folder,files) # escoge la carpeta destino
                        if os.path.exists(source_path): # si existe carpeta inicial
                            os.replace(source_path,target_path) # mueve el fichero a la carpeta destino
    parsedpattern=r".*(_parsed\.csv)$" # los archivos que contengan *_parsed.csv
    parsedfiles=[] # se guardarán en una lista
    for datafilename in os.listdir('./'): # mira todos los archivos en la carpeta actual
        if re.search(parsedpattern, datafilename): # busca que tengan *_parsed.csv
            parsedfiles.append(datafilename) # guarda su ruta en la lista.
    os.makedirs('parsed', mode=0o777, exist_ok=True) # crea la carpeta "parsed"
    for parseddata in parsedfiles:# para poder meter 
        sourceppath = os.path.join('.',parseddata) # específicamente 
        targetppath = os.path.join('.','parsed',parseddata) # sólo los archivos
        os.replace(sourceppath,targetppath) # parsed, dado que son un "residuo" de CEF.
    # Zips the folder structure without 'parsed'
    # Crea un nombre de un fichero zip
    zipfilename=tk.simpledialog.askstring(title='Info',prompt='Escribe el nombre del fichero *.zip al que se\n\
                                               guardarán los *.csv para MetaboAnalyst.',initialvalue='trial')
    if zipfilename: # Si existe el zip
        zipfilename = f"{zipfilename}.zip" if not zipfilename.endswith('.zip') else zipfilename
        # le añade el *.zip
        # Todo el with siguiente crea un zip de la estructura de carpetas, sin la carpeta parsed.
        with zipfile.ZipFile(zipfilename,'w',zipfile.ZIP_DEFLATED) as zipf:
            for root,dirs,files in os.walk('./'):
                dirs[:] = [d for d in dirs if d != 'parsed']
                if root != './':
                    for file in files:
                        file_path =os.path.join(root,file)
                        # Save the path relative to the src_directory for cleaner structure in zip
                        zipf.write(file_path, os.path.relpath(file_path, './'))
    return
# Functions for control selections and close window in tkinter:
def select_option(option):
    global selection
    selection = option # checks selection
    root.quit()
    root.destroy()  # This will exit the tkinter main loop

# XLSX Module (Omics)
# No functions yet
## Module Selection
root = tk.Tk()
root.withdraw()
tk.messagebox.showinfo(title='Lipidomic_Normalizer', message=f"Este programa transforma un fichero *.xlsx (Excel creado según 'PlantillaLipidomica_ACompletar.xlsx') a formato apto para MetaboAnalyst y Mass Profiler Professional, realizando una normalización por familias de lípidos durante el proceso.\n")

root.quit()
# starts logic
# Load Lipid Classes from LipidAnnotator
# Only this Excel 'LipidClasses.xlsx' is needed. The template is given but must be modified first.
# FLAG FOR REMEMBERING THIS IS ONLY LIPIDOMICS (FOR NOW)
#LipidData=pd.read_excel('./AppData/DatosExcel/LipidClasses.xlsx')
LipidData=pd.read_excel('./AppData/DatosExcel/LipidClasses.xlsx')
tk.messagebox.showinfo(title='Lipidomic_Normalizer', message='Escoge que fichero Excel (xlsx) creado a partir de\n\
                        la "PlantillaLipidomica_ACompletar.xslx" quiere abrir.')
tk.messagebox.showwarning(title='Advertencia', message='Se recomienda que las muestras presenten nombres únicos para su diferenciación.\n\
                            Se recomienda la revisión y eliminación con Mass Profinder de los compuestos con nombre duplicado\n\
                            para el correcto funcionamiento de MetaboAnalyst.\n\
                            Pueden ser de varios tipos:\n\
                            - Doble extracción (misma m/z y misma TR): se eliminaría.\n\
                            - Distintos aductos (m/z similar, distinta TR): se eliminaría aducto menos relevante.\n\
                            - Isomería (caso excepcional masas y TR similares): se tendrían en cuenta los dos pero con subíndices distintos.\n\
                            En esta versión, todos los duplicados se tratarán como compuestos distintos. \n\
                            Hay que tener cuidado con que los nombres de los lípidos coincidan con el código en el fichero AppData/DatosExcel/LipidClasses.xlsx')
xlsxfile=filedialog.askopenfilename(
    title='Select data.xlsx file.',
    filetypes=[("Data.xlsx Files", "*.xlsx"), ("All Files", "*.*")]
)
# Load Metadata, gets the sample names and the labels
META=pd.read_excel(xlsxfile,sheet_name="Metadata")
samplenames=META['Sample']
labels=META['Label']
# Load Raw Data, gets the matrix ordered by RT
RAW=pd.read_excel(xlsxfile,sheet_name="Datos crudos")
RAW.sort_values(by=['RT'])
# Load Pattern data, gets all the other data frames
addedconcentrations=pd.read_excel(xlsxfile,sheet_name="Concentraciones añadidas")
controlconcentrations=pd.read_excel(xlsxfile,sheet_name="Concentraciones patrones")
foundpattern=pd.read_excel(xlsxfile,sheet_name="Patrones Obtenidos")
prenormareas=pd.read_excel(xlsxfile,sheet_name="Áreas a normalizar")
# Concentraciones Patrones: Calculates it from the original data and correlates with handwritten
foundconc=[]
for j in range(len(addedconcentrations['ISDs'])):
    for i in foundpattern['ISDs']:
        if i in addedconcentrations.iloc[j,0]:
            foundconc.append([i,addedconcentrations.iloc[j,1].item(),addedconcentrations.iloc[j,2].item()])
notordconcentrations = pd.DataFrame(addedconcentrations,columns =['ISDs','[] µg/mL','[]muestra µg/mL'])
concentrations = notordconcentrations.set_index('ISDs').reindex(foundpattern['ISDs']).reset_index()
if concentrations.equals(controlconcentrations):
    tk.messagebox.showinfo(title='Info', message='ISDs "Patrones obtenidos"\n\
                        coinciden con "Concentraciones añadidas"')
else:
    tk.messagebox.showerror(title='Error', message='ISDs "Patrones obtenidos"\n\
                        NO coinciden con "Concentraciones añadidas". Se ha seleccionado "Concentraciones patrones"')
    concentrations = controlconcentrations
# Continue
samplenames=pd.Series(samplenames) # checks name
prenormfloat=prenormareas.iloc[:,1:].astype(np.float64) # saves it as float
# Creation of rawisds:
patternname=foundpattern['ISDs']
RTpattern=foundpattern['RT']
assoc_conc=concentrations['[]muestra µg/mL']
for i in range(0,len(patternname)):
    prenormfloat.iloc[:,i]=prenormfloat.iloc[:,i]/assoc_conc[i]
        # area directly normalized by dividing by associated concentration. Normalization one
        # It is supposed it is given in order
isdstable=[]
prenormfloatT=pd.DataFrame(prenormfloat.T) # save new table
indexlist=pd.Series(list(range(len(patternname)))) # save indexes
patternindex=list(range(len(patternname))) # save pattern list
prenormrenamed=prenormfloatT.rename(columns=samplenames) # renamed the columns
prenormrenamed.index=list(range(len(patternname))) # index the pattern
isdstable=pd.concat([patternname,RTpattern,prenormrenamed],axis=1) # creates the table

## File coding ##
# Adds info to foundpattern, concentrations and isds
# to identify the lipid families better:
#expression = fr'(?!\B\w)({re.escape(LipidData['Short'][j])})(?!\B\w)')
#expression = fr'\b({re.escape(LipidData['Short'][j])})\b'
Codes = []
for i in range(len(foundpattern['ISDs'])):
    for j in range(len(LipidData['Short'])):
        Lipidj=LipidData['Short'][j] # lipid ID info
        expression = fr'\b({re.escape(Lipidj)})\b' # checks for the lipid ID pattern
        #re.findall(expression, foundpattern['ISDs'][i])
        if re.search(expression, str(foundpattern['ISDs'][i])) is not None:
            Codes.append(LipidData['Short'][j]) # gets the pattern

patternscoded=foundpattern.copy()
patternscoded.insert(1,'Codes',Codes,allow_duplicates=True) # inserts the codes in patterns

concentrationscoded=concentrations.copy()
concentrationscoded.insert(1,'Codes',Codes,allow_duplicates=True) # inserts the codes in concentrations

isdscoded=isdstable.copy()
isdscoded.insert(1,'Codes',Codes,allow_duplicates=True) # inserts the codes in isds table
## Calculus start ##
normareaslist=list(isdscoded.iloc[:,3:].keys()) # gets the numerical of normareas from isdscoded

expression=[]
#expression = fr'\b({re.escape(LipidData['Short'][j])})\b'
for patrones in range(len(isdscoded['Codes'])):
    codepatron=patternscoded['Codes'][patrones]
    expression.append(fr'\b({re.escape(codepatron)})\b') # gets the lipid expression

RAWMAT=[]
for muestras in range(5,len(RAW.iloc[0,:])):
    RAWMAT.append([])
    for lipidos in range(len(RAW.iloc[:,0])):
        RAWMAT[muestras-5].append(RAW.iloc[lipidos,muestras]) # append the raw values, the important data only

RAWMAT=tuple(RAWMAT)

patternguide=[]
# Genera patternguide como referencia de qué patrón utilizar para cada lípido
# Obtiene la diferencia de tiempo mínima como control
for lipidos in range(len(RAWMAT[0])):
    sampletime=RAW['RT']
    difftime=[]
    difftimelist=[]
    for patrones in range(len(isdscoded['Codes'])):
        difftime.append(abs(isdscoded['RT'][patrones]-sampletime))
        difftimelist.append(difftime[patrones][lipidos])
    minimaldiff=min(list(difftimelist))
    indexmindiff=difftimelist.index(min(difftimelist))
    patternguide.append(indexmindiff)

for lipidos in range(len(RAWMAT[0])):
    for patrones in range(len(isdscoded['Codes'])): # comprueba que está en la lista de patrones
        if  re.search(expression[patrones], RAW.iloc[lipidos,0]) is not None:
            patternguide[lipidos]=patrones
        else:
            continue

normalizer=[] # normaliza según el patrón indicado
for lipidos in range(len(RAWMAT[0])):
    normalizer.append([])
    for muestras in range(5,len(RAW.keys())):
                normalizer[lipidos].append(isdscoded.iloc[patternguide[lipidos],muestras-2])

# Obtain RAWNorm: Los datos se traspusieron cuando se obtuvieron
# (se rellenaron de forma transpuesta), así que otra vez traspuesta
RAWNorm=np.transpose(np.array(RAWMAT))/np.array(normalizer)

# more things for the csvs, gets the names
samplenameslist=list(samplenames) 
classorder=list(labels)
# names of lipids
lipidnames=list(RAW['Compound Name'])
RAWNormlist=RAWNorm.tolist()
datamatrix=pd.DataFrame(RAWNormlist)
datalipid=pd.DataFrame(lipidnames)
# MetaboAnalyst
lipidnames=list(RAW['Compound Name'])
RAWNormlist=RAWNorm.tolist()
# necessary for duplicates sanity check but not for the table (not for MPP)
Formulae=pd.DataFrame(list(RAW['Formula']))
masses=pd.DataFrame(list(RAW['Mass']))
retentionT=pd.DataFrame(list(RAW['RT']))

# duplicate workaround    
formulalist = list(RAW['Formula'])
masslist = list(RAW['Mass'])
RTlist = list(RAW['RT'])

# Dictionary to store the indexes of each name
name_indexes = defaultdict(list)

# Populate the dictionary with the indexes of each name
for index, name in enumerate(lipidnames):
    name_indexes[name].append(index)

# Filter for duplicates and extract their indexes
duplicates = {name: indexes for name, indexes in name_indexes.items() if len(indexes) > 1}
# if there are duplicates, adds new name
if duplicates != None:
    newlipidnames = lipidnames
    for i in duplicates.keys():
        for j in range(len(duplicates[i])):
            newlipidnames[duplicates[i][j]] = lipidnames[duplicates[i][j]]+f"__{j+1}"
else:
    newlipidnames = lipidnames

# continue
datalipid=pd.DataFrame(newlipidnames)
datametaboasc=pd.concat([datalipid,Formulae,masses,retentionT,datamatrix],axis=1)

datamatrix=pd.DataFrame(RAWNormlist)
datalipid=pd.DataFrame(newlipidnames)
datametaboa=pd.concat([datalipid,datamatrix],axis=1)
datametaboalist=datametaboa.values.tolist()
# WorkDir
tk.messagebox.showinfo(title='Info', message='Escoge el directorio donde quieres guardar los archivos.')
workdir=filedialog.askdirectory()
os.chdir(workdir)
# curation of data for elliminating doubles is BEFORE RECEIVING EXCEL
xlsx2csvfilename=tk.simpledialog.askstring(title='Info',prompt='Escribe el nombre del fichero *.csv al que se\n\
                                            guardarán los datos del Excel tanto para MetaboAnalyst como para Mass Profiler Pro.',initialvalue='trial')
with open(xlsx2csvfilename+'.csv', 'w', newline='') as csvfile:
    trialwriter = csv.writer(csvfile, delimiter=',',
                            quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    trialwriter.writerow(['Sample'] + samplenameslist)# first line= samples
    # Second line: sample labeling
    trialwriter.writerow(['Label'] + classorder)
    # Third line and after: lipid name + data
    trialwriter.writerows(datametaboalist) 
original_rows = [['Sample'] + samplenameslist,
                    ['Label'] + classorder] + datametaboalist
transposed_rows = list(zip(*original_rows))
with open(xlsx2csvfilename + '_transposed.csv', 'w', newline='') as csvfile:
    trialwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    trialwriter.writerows(transposed_rows)
# DATA NOT CURATED YET, for MPP
# Mass Profinder Pro
Formulae=pd.DataFrame(list(RAW['Formula']))
masses=pd.DataFrame(list(RAW['Mass']))
retentionT=pd.DataFrame(list(RAW['RT']))
casidydf=pd.DataFrame(list(RAW['CAS ID']))
datampp=pd.concat([datalipid,Formulae,masses,retentionT,casidydf,datamatrix],axis=1)
datampplist=datampp.values.tolist()
with open(xlsx2csvfilename+'_mpp.csv', 'w', newline='') as csvfile:
    trialwriter = csv.writer(csvfile, delimiter=',',
                            quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    trialwriter.writerow(['Compound Name']+ ['Formula'] + ['Mass'] + ['RT'] + ['CAS ID']+ samplenameslist)# first line = samples
    # Second line and after: lipid name + data
    trialwriter.writerows(datampplist)
tk.messagebox.showinfo(title='Info', message=f'Archivos {xlsx2csvfilename}.csv, {xlsx2csvfilename}_mpp.csv y {xlsx2csvfilename}_transposed.csv creados. Trabajo finalizado.')

