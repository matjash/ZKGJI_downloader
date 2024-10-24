# -*- coding: utf-8 -*-

"""
Matjaž Mori, 
ZUM d.o.o.
24.10.2024


***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import ( QgsVectorLayer,
                        QgsWkbTypes,
                       QgsProcessingAlgorithm,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterFile)
from qgis import processing

import subprocess
import shutil
import json

def install_package(package_name):
    try:
        __import__(package_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} is not installed. Installing...")
        subprocess.check_call(['python', '-m', 'pip', 'install', package_name])
        print(f"{package_name} has been installed.")

# List of required packages
required_packages = ['requests',  'sqlalchemy', 'geoalchemy2']

for package in required_packages:
    install_package(package)

# Now you can import the rest of your packages
import requests
import zipfile
import tempfile
import os
import re
from datetime import datetime
import re



class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.



    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'zkgji_prenesi'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Paketni prenos katastra GJI')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
       

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
 

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("""V izbrano mapo prenese Zbirni kataster gospodarske javne infrastrukture iz spletne strani https://ipi.eprostor.gov.si. Posamezne tematike združi v skupne sloje točk, linij in poligonov.
                       Vir podatkov: Geodetska uprava Republike Slovenije. """)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(QgsProcessingParameterFile('out_folder', 'Shrani sloje v mapo...', behavior=QgsProcessingParameterFile.Folder, defaultValue='D:\\'))


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # User Input Variables

        urls_to_download = {
            'CESTE': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/221/file?filterParam=DRZAVA&filterValue=1',
            'ZELEZNICE': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/222/file?filterParam=DRZAVA&filterValue=1',
            'LETALISCA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/235/file?filterParam=DRZAVA&filterValue=1',
            'PRISTANISCA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/234/file?filterParam=DRZAVA&filterValue=1',
            'ZICNICE': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/233/file?filterParam=DRZAVA&filterValue=1',
            'ELEKTRIKA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/232/file?filterParam=DRZAVA&filterValue=1',
            'PLIN': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/231/file?filterParam=DRZAVA&filterValue=1',
            'TOPLOTNA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/230/file?filterParam=DRZAVA&filterValue=1',
            'NAFTA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/229/file?filterParam=DRZAVA&filterValue=1',        
            'VODOVOD': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/228/file?filterParam=DRZAVA&filterValue=1',
            'KANALIZACIJA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/227/file?filterParam=DRZAVA&filterValue=1',
            'ODPADKI': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/226/file?filterParam=DRZAVA&filterValue=1',
            'VODNA_INFRASTRUKTURA': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/225/file?filterParam=DRZAVA&filterValue=1',
            'OBJEKTI_ZA_OPAZOVANJE': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/224/file?filterParam=DRZAVA&filterValue=1',
            'EKEKTRONSKE_KOMUNIKACIJE': 'https://ipi.eprostor.gov.si/jgp-service-api/display-views/groups/301/composite-products/223/file?filterParam=DRZAVA&filterValue=1'

        }  # Dictionary of URLs to download zip files
            
      
        self.lines_layers = []
        self.points_layers = []
        self.polygons_layers = []
        
    
 
      

        def download_file(key, url, folder_path):
            try:
                # First request to get the JSON response
                response = requests.get(url)
                response.raise_for_status()  # Raises an error for bad responses
                
                # Parse the JSON response
                json_data = response.json()
                download_url = json_data.get('url')  # Extract the actual download URL
                
                if not download_url:
                    feedback.pushInfo("No download URL found in the response.")
                    return None
                
                # Second request to download the file
                file_response = requests.get(download_url, stream=True)
                file_response.raise_for_status()  # Check for errors in file download
                feedback.pushInfo(f"Downloaded: {download_url}")
                # Determine filename from the download URL or use a default name
                file_name = key + '.zip'
                
                file_path = os.path.join(folder_path, file_name)

                with open(file_path, 'wb') as file:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        file.write(chunk)

                feedback.pushInfo(f"Downloaded: {file_path}")
                return file_path

            except requests.exceptions.HTTPError as e:
                feedback.pushInfo(f"HTTP Error: {e}")
            except Exception as e:
                feedback.pushInfo(f"Error downloading file: {e}")



        def process_zip_file(zip_path,temp_out_folder_path):
            success = True
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                for file in os.listdir(temp_dir):
                    if file.endswith('.gpkg'):
                        gpkg_dest_path = os.path.join(temp_out_folder_path, file)
                        gpkg_path = os.path.join(temp_dir, file)
                        shutil.copy(gpkg_path, gpkg_dest_path)
                        process_gpkg_file(gpkg_dest_path)
            return success


        def process_gpkg_file(gpkg_path):
            layer_name = extract_layer_name_from_filepath(gpkg_path)
            
            vlayer = QgsVectorLayer(gpkg_path, layer_name, "ogr")
            if not vlayer.isValid():
                feedback.pushInfo(f"Failed to load layer from {gpkg_path}")
                return False
            else:
                geom_type = vlayer.geometryType()
                if geom_type == QgsWkbTypes.PointGeometry: 
                    self.points_layers.append(gpkg_path)
                 
                elif geom_type == QgsWkbTypes.LineGeometry:
                    self.lines_layers.append(gpkg_path)
                   
                elif geom_type == QgsWkbTypes.PolygonGeometry:
                    self.polygons_layers.append(gpkg_path)
                 
                else:
                    feedback.pushInfo(f"Layer type not detected: {gpkg_path}")


        def extract_layer_name_from_filepath(file_path):
            # Regular expression pattern to extract layer name
            # This pattern assumes the layer name ends just before a sequence of 8 digits (representing the date)
            filename= os.path.basename(file_path)
            pattern = r'KGI_SLO_GJI_(.*?)_\d{8}\.'
            match = re.search(pattern, filename)
          
            if match:
                # Extract and return the layer name
                return match.group(1)
            else:
                # Return None or an appropriate default if no match is found
                return None

        def merge_layers(list, out_layer):
            processing.run("native:mergevectorlayers", {
                'LAYERS':list,
                'CRS':QgsCoordinateReferenceSystem('EPSG:3794'),
                'OUTPUT':out_layer})
       
        def extract_and_format_date(zip_file_name):
            today_date = datetime.now().strftime('%Y%m%d')
            try:
                date_match = re.search(r'(\d{8})\.zip$', zip_file_name)
                if date_match:
                    date_str = date_match.group(1)
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    feedback.pushInfo(f"File date: {date_obj.strftime('%d.%m.%Y')}")
                    return date_obj.strftime('%Y%m%d')
                else:
                    return today_date
            except ValueError:
                feedback.pushInfo(f"Invalid date format in file name: {zip_file_name}")
                return today_date
                
        

        def main():
            with tempfile.TemporaryDirectory() as temp_folder_path:
                # Download files to the temporary folder
                total_d = 100.0 / len(urls_to_download.items()) if len(urls_to_download.items()) else 0
                for current, (key, url) in enumerate(urls_to_download.items()):
                    feedback.pushInfo(f"Downloading file from {url}")
                    download_file(key, url, temp_folder_path)
                    feedback.setProgress(int(current * total_d))
                    if feedback.isCanceled():
                        break
                # Process downloaded files
                total_c = 100.0 / len(os.listdir(temp_folder_path)) if urls_to_download.items() else 0
                for current, zip_file in enumerate(os.listdir(temp_folder_path)):
                    if feedback.isCanceled():
                        break
                    if zip_file.endswith('.zip'):
                        data_date = extract_and_format_date(zip_file)
                        zip_file_path = os.path.join(temp_folder_path, zip_file)
                        feedback.pushInfo(f"Processing file: {zip_file_path}")
                        process_zip_file(zip_file_path,temp_folder_path)
                    feedback.setProgress(int(current * total_c))
                
                out_layer_lines = parameters['out_folder']   + '\\zkgji_linije_' + data_date + '.gpkg'
                out_layer_points = parameters['out_folder']   + '\\zkgji_tocke_' +  data_date + '.gpkg'
                out_layer_poly = parameters['out_folder']   + '\\zkgji_poligoni_' + data_date + '.gpkg'



                merge_layers(self.lines_layers, out_layer_lines)
                merge_layers(self.points_layers, out_layer_points)
                merge_layers(self.polygons_layers, out_layer_poly)
                    
        main()
        
 
        return {}
