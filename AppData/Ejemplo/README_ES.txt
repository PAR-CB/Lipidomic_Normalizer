Cada carpeta contiene los datos ejemplo de entrada y salida:
- La carpeta 'Datos' contiene los datos ejemplo iniciales (la plantilla).
- La carpeta 'Clasificación' contiene la ejemplificación de los datos transformados a través del programa.
-La 'Template.xlsx' presenta varias hojas:
-- Se recomienda no cambiar el nombre a las hojas. Tampoco se recomienda cambiar el nombre de las cabeceras
de las columnas salvo si se especifica que son modificables.
---Metadata: Necesita de cabeceras 'Sample' y 'Label', y al menos 3 muestras por cada grupo (excepto grupos de control QC o blanco BLANK).
---Datos Crudos: Necesita de cabeceras 'Compound Name', 'Formula', 'Mass', 'RT'. Compuestos en Filas, Muestras en el resto de columnas.
---Concentraciones añadidas: Necesita de las cabeceras 'ISDs', '[] µg/mL' y '[]muestra µg/mL', con los 
compuestos del patrón interno en filas.
---Patrones obtenidos: Necesita de las cabeceras 'ISDs', 'RT', 'Standard desv', 'RSD', con los 
compuestos del patrón interno en filas.
---Concentraciones patrones: oncentraciones de aquellos compuestos del patrón interno medidos (se emplea como control de datos), con la misma información que 'Concentraciones añadidas' pero sólo con los compuestos del patrón interno que aparecen.
---Áreas a normalizar: Datos de las intensidades de los patrones observados para cada muestra. Necesita de
la columna 'Muesrea', con las muestras en sus filas. Las columnas restantes presentan las intensidades de cada compuesto patrón para cada muestra, con el nombre 'Area *CódigoPatrón*', siendo *CódigoPatrón* la clase de lípido dada por "LipidClasses.xlsx"