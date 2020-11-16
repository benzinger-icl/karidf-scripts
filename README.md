# karidf-scripts
## Overview

This repository contains scripts to download raw imaging scans, freesurfer files, and PUP files from an XNAT platform (i.e. CNDA). These scripts are specifically designed for the collaborators who have access to the KARI Master Data Freeze project on the CNDA.
  

 


# Download raw imaging scans:
## Instructions:
1. Download the karidf-scripts repository.

2. In the downloads_scans_by_type directory, update the scans_to_download.csv with the list of MR or PET sessions/visits you would like to download imaging scans from.
- Use the MR/PET Accession # [Typically starts with "CNDA_"]
- Do not include a header.

Example of csv: 
||
|-------------|
| CNDA_E71543 |
| CNDA_E1594  |
| CNDA_E2240  |
| CNDA_E1112  |

2. In the downloads_scans_by_type directory, update the scans_types.csv with all the scan names you need to download.  There are several scan  names listed for T1, T2, DTI, etc. scans so you will need to pull this information from the list of sessions you are interested in.
- You can combine various scan types together in one list (i.e. T1, FLAIR, DTI, etc)
- Copy the scan name exactly as written in the MR/PET session [spaces and all]
- Do not include a header.
- Note in example below there are multiple scan names for the T1.

Example of csv: 
||
|-------------|
| SAG 3D FSPGR |
| MPRAGE GRAPPA2  |
| AX T1  |
| FLAIR  |
| DTI  |

Once the two csv files are updated, you are now ready to run the script.


3. Open the terminal and change your directory to the download_scans folder.

```
cd /path/to/download_scans
```


4. Run the download_scans_by_scan_type.sh script:

General usage:
```
./download_scans_by_scan_type.sh <input_file.csv> <scan_type_list.csv> <directory_name> <xnat_username> <site>
```
<input_file.csv> - A Unix formatted, comma-separated file containing the following columns: Experiment ID
<scan_type_list.csv> - A csv with each row containing one scan type you want to download.
<directory_name> - A directory path (relative or absolute) to save the scan files to
<xnat_username> - Your username used for accessing data on the given site (you will be prompted for your password before downloading)
<site> - the full path to the xnat site you are using, ie. https://cnda.wustl.edu
  
  
Specifically, for the KARI Master Data Freeze CNDA project, use the yntax below but change cnda_username to your current cnda username.

```
./download_scans_by_scan_type.sh scans_to_download.csv scan_types.csv out_dir cnda_username https://cnda.wustl.edu/
```


## Script Output Description

The output directory will be organized as follow:
${OUTPUTDIR}/${EXPERIMENT_LABEL}/${SCAN_NAME}/


A log file will be created named, downloading_log_XXX.log,  that contains the list of scans downloaded.
