# Table of Contents
- [KARI data freeze scripts overview](#kari-data-freeze-scripts-overview)
- [Downloading MR and PET scan files](#downloading-mr-and-pet-scan-files)




# KARI data freeze scripts overview
This repository contains scripts to download Knight Alzheimer Research Institute (KARI) raw imaging scans, freesurfer files, and PUP files from the XNAT platform, CNDA. These scripts are specifically designed for the collaborators who have access to the KARI Master Data Freeze project on the CNDA.



# Downloading MR and PET scan files

## download_scans/download_scans_by_scan_type.sh 

This script downloads scans of a specified type and organizes the files. 

<br>

**General Usage:**
```
./download_scans_by_scan_type.sh <input_file.csv> <scan_type_list.csv> <directory_name> <xnat_username> <site>
```

<br>

**Required inputs:**

`<input_file.csv>` - A Unix formatted, comma-separated file containing a column for experiment_id (e.g. CNDA_E12345) without a header.

`<scan_type>` - The scan type of the scan you want to download. (e.g. T1w, angio, bold, fieldmap, FLAIR). For example, there are several scan names listed for T1 scans (i.e. MPRAGE, SAG T1 MPRAGE, Accelerated Sagittal MPRAGE, etc).  This scan names vary depending on the list of sessions. You can also enter multiple scan types in the file. (e.g. T2w,swi,bold). Without this argument, all scans for the given experiment_id will be downloaded.

`<directory_name>` - A directory path (relative or absolute) to save the scan files to. If this directory doesn't exist when you run the script, it will be created automatically.

`<xnat_username>` - Your XNAT username (you will be prompted for your password before downloading) or the 

`<site>` - the XNAT website url ( https://cnda.wustl.edu/ )
  
 <br>
 
**Example Usage**

1. Create a csv containing experiment_id without a header.

Example:

|<!-- -->   |
|-------------|
| CNDA_E71543 |
| CNDA_E1594  |
| CNDA_E2240  |
| CNDA_E1112  |

2. Create a csv containing scan types/names without a header.

Example:

||
|-------------|
| SAG 3D FSPGR |
| MPRAGE GRAPPA2  |
| AX T1  |
| FLAIR  |
| DTI  |

3. Run download_scans_by_scan_type.sh script

The command below is an example of downloading data from the KARI Master Data Freeze CNDA project 
where out_dir is your output directory path and cnda_username is your own cnda username.
```
./download_scans_by_scan_type.sh scans_to_download.csv scan_types.csv out_dir cnda_username https://cnda.wustl.edu/
```
<br>

**Script output**

This script organizes the files into folders like this:

```
directory_name/experiment_id/scan_type/
```

A log file will be created named, downloading_log_XXX.log,  that contains the list of scans downloaded.






## Download raw imaging scans:
### Instructions:
1. Download the karidf-scripts repository.

2. In the downloads_scans_by_type directory, update the scans_to_download.csv with the list of MR or PET sessions/visits you would like to download imaging scans from.
- Use the MR/PET Accession # (Typically starts with "CNDA_")
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
- Copy the scan name exactly as written in the MR/PET session (spaces and all)
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
  



### Script Output Description

The output directory will be organized as follow:
${OUTPUTDIR}/${EXPERIMENT_LABEL}/${SCAN_NAME}/


A log file will be created named, downloading_log_XXX.log,  that contains the list of scans downloaded.




## Download FreeSurfer files:
### Instructions:
1. Download python 2.7 (script written under this version)
https://www.python.org/downloads/

2. Make sure the following python packages are installed:
- sys
- json
- argparse
- datetime
- csv
- os
- base64
- shutil
- requests
- time
- urllib2
- getpass
- calendar
- urllib

3. Download the karidf-scripts repository.

4. In the download_freesurfer directory, update the download_freesurfer_list.csv with the FreeSurfer IDs you want to download.
- Must be the FS ID that begins with the accession number (begins with CNDA_).
- Do not include a header.

Example of csv: 
||
|-------------|
| CNDA_E12345_freesurfer_2017101912345 |
| CNDA_E57844_freesurfer_2019102112345  |
| CNDA_E19495_freesurfer_2018112212345  |


5. Open the terminal and change your directory to the download_freesurfer folder.

```
cd /path/to/download_freesurfer
```


6. Run the download_freesurfer.sh script:

General usage:
```
python download_freesurfer.py <fs_ids.csv> <site> <destination_dir> -u <alias> -p <secret>
```
<fs_ids.csv> : a csv of FreeSurfer IDs you want to download with following columns with no header row: Freesurfer ID (e.g. CNDA_E12345_freesurfer_2017101912345). 
- Must be the FS ID that begins with the accession number (begins with CNDA_).
<site> : the site to download from: https://cnda.wustl.edu
<destination_dir> : the output directory for the downloaded FreeSurfers.
<alias>: Replace <alias> with the token next to the text "alias:" found on https://cnda.wustl.edu/data/services/tokens/issue
<secret>: Replace <secret> with the token next to the text "secret:" found on https://cnda.wustl.edu/data/services/tokens/issue

### Script Output Description
The files will be organized into the following structure:
${fs_id}/DATA/atlas (if FS 5.1 or 5.0)
${fs_id}/DATA/label
${fs_id}/DATA/mri
${fs_id}/DATA/scripts
${fs_id}/DATA/stats
${fs_id}/DATA/surf
${fs_id}/DATA/touch
${fs_id}/DATA/tmp
${fs_id}/SNAPSHOTS
${fs_id}/LOG

Creates a log file at `download_fs.log` - contains all output from the script.
Creates a log file at `to_download_manually_fs.log` - contains a list of all FS IDs that could not be found.
Creates a log file at `to_download_manually_fs_files.log` - contains a list of all files that could not be downloaded and their FS IDs (in the format fs_id, filename).

## Download PUP files:
### Instructions:
1. Download python 2.7 (script written under this version)
https://www.python.org/downloads/

2. Make sure the following python packages are installed:
- argparse
- datetime
- csv
- requests
- time
- calendar
- getpass
- os

3. Download the karidf-scripts repository.

4. In the download_pup directory, update the download_pup_list.csv with the PUP IDs you want to download.
- Must be the PUP ID that begins with the accession number (begins with CNDA_).
- Do not include a header.

Example of csv: 
||
|-------------|
| CNDA_E12345_PUPTIMECOURSE_2017101912345 |
| CNDA_E57844_PUPTIMECOURSE_2019102112345  |
| CNDA_E19495_PUPTIMECOURSE_2018112212345  |


5. Open the terminal and change your directory to the download_pup folder.

```
cd /path/to/download_pup
```


6. Run the download_pup.sh script:

General usage:
```
python download_pup.py <site> <destination_dir> -c <pup_ids.csv> -u <alias> -p <secret>

```
<pup_ids.csv> : a csv of PUP IDs you want to download. The script expects the following columns: PUP_ID (e.g. CNDA_E12345_PUPTIMECOURSE_2017101912345). 
     - Must be the PUP ID that begins with the accession number (begins with CNDA_ or DCA_ or CENTRAL_, etc).
<site> : the site to download from: https://cnda.wustl.edu
<destination_dir> : the output directory to download to
- u <alias>: Replace <alias> with the token next to the text "alias:" found on https://cnda.wustl.edu/data/services/tokens/issue
- p <secret>: Replace <secret> with the token next to the text "secret:" found on https://cnda.wustl.edu/data/services/tokens/issue

Choose one of these flags to read from a CSV of PUP IDs, or specify a single PUP ID:
-c filename.csv or 
--csv filename.csv to read from a CSV of PUP IDs with no header row (specify filename.csv) or
-i pup_id or --id pup_id to download for a single PUP ID (specify pup_id)

7. Add on optional flags
Include any of these optional flags to only download particular file types, or include no flags to download the entire set of files:

Include the --create-logs flag to create log files that show the script output and specify which files have been skipped.

--download-4dfp: Download 4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)
--download-dat: Download .dat files
--download-info: Download .info files
--download-logs: Download all log files, in both the LOG folder and DATA folder
--download-lst: Download .lst files
--download-mgz: Download .mgz files
--download-moco: Download .moco files
--download-nii: Download .nii files
--download-params: Download .params files
--download-snaps: Download snapshot files (all files in the SNAPSHOTS folder)
--download-sub: Download .sub files
--download-suvr: Download suvr files
--download-tac: Download tac files
--download-tb: Download .tb files
--download-txt: Download .txt files
--download-no-ext: Download files with no extension
--download-SUVR4dfp: Download SUVR.4dfp and SUVR_g8.4dfp files
--download-T10014dfp: Download T1001.4dfp file
--download-PETFOV: Download PETFOV.4dfp files
--download-RSFMask: Download RSFMask.4dfp files
--download-wmparc: Download all files containing "wmparc" in the name


### Script Output Description
Organizes the files into the following folder structure: 
${pup_id}/DATA
${pup_id}/SNAPSHOTS
${pup_id}/LOG

If the --create-logs flag is included:
Creates a log file at `download_pup.log` - contains all output from the script.
Creates a log file at `to_download_manually_pup.log` - contains a list of all PUP IDs that could not be found.
Creates a log file at `to_download_manually_pup_files.log` - contains a list of all files that could not be downloaded and their PUP IDs (in the format pup_id, filename).
