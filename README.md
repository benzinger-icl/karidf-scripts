# Table of Contents
- [KARI data freeze scripts overview](#kari-data-freeze-scripts-overview)
- [Prerequisites - Please Read](#prerequisites---please-read)
  * [Python packages](#python-packages)
  * [XNAT Tokens](#xnat-tokens)
- [General instructions on running scripts](#general-instructions-on-running-scripts)
- [Downloading MR and PET scan files](#downloading-mr-and-pet-scan-files)
- [Downloading FreeSurfer files](#downloading-freesurfer-files)
- [Downloading PUP files](#downloading-pup-files)
- [Additional help with scripts?](#additional-help-with-scripts)

<br>
<br>

# KARI data freeze scripts overview
This repository contains scripts to download Knight Alzheimer Research Institute (KARI) raw imaging scans, freesurfer files, and PUP files from the XNAT platform, CNDA. These scripts are specifically designed for the collaborators who have access to the KARI Master Data Freeze project on the CNDA. All scripts were written using python 3.

<br>
<br>

# Prerequisites - Please Read
## Python packages

The python package, requests, is required to run any of the scripts in this repository.

To install, run the following command in your terminal:
```
python -m pip install requests
```

## XNAT Tokens
XNAT tokens are a secure way of authenticating your request so that XNAT can determine whether you are allowed to perform the action that you are requesting. The tokens expire in a short period of time. Do not share your token with anyone else.

1. Log in to CNDA ( https://cnda.wustl.edu)
2. Click on your username in the very top right navigation bar to go to your User Account page. 
3. Click on the "Manage Alias Tokens" tab. 
4. Click "Create Alias Token".
5. Click on the generated "Alias" link or the "view" button under the "Actions" column to view the full token
6. Copy the "alias" and "secret" strings and paste them into the following commands below when specified.

More detailed documentation can be found here: https://wiki.xnat.org/documentation/how-to-use-xnat/generating-an-alias-token-for-scripted-authentication

<br>
<br>

# Instructions on running these scripts

1. Download the script from this Github repository by clicking "Clone or download" and choose Download ZIP. This will download a zip file containing all the scripts in the repository and this README file.

2. Extract the .zip file onto your local computer and move the desired script (ex. download_freesurfer.py) into the folder you will be working from.

3. Download / create CSV files necessary to run scripts.

4. Move the csv file(s) into the same folder as the script.

5. If you are running a download script, create an empty directory in the same folder as your script and make a note of its name. This is the directory where your scan files will be downloaded to.

6. Go into your command line. On Windows you can use a terminal system like MobaXTerm. If you're using a Mac you can use Terminal. Make sure you are not running the script while logged in as the root user. Change directories to the folder your scripts and empty folder are in using the `cd` command.

<br>
<br>

# Downloading MR and PET scan files
**download_scans/download_scans_by_scan_type.sh**

This script downloads all or a specificed type of MR and PET. 

<br>

**General Usage:**
```
python3 download_scans.py <site> <destination_dir> -c <session_ids.csv> -t <requested_scan_types.csv> -u <alias> -p <secret>
```

<br>

**Required inputs:**

`<site>` - the XNAT website url ( https://cnda.wustl.edu/ )

`<destination_dir>` - A directory path (relative or absolute) to save the files to. If this directory doesn't exist when you run the script, it will be created automatically.

`<session_ids.csv>` - A Unix formatted, comma-separated file containing a column for MR and PET session IDs (e.g. CNDA_E12345) without a header.

`<requested_scan_types.csv>` - A Unix formatted, comma-separated file containing a column with scan type names (e.g. "MPRAGE" or "SAG T1 MPR") without a header.

`<alias>`: Obtain alias token using the instructions under "XNAT token"
  
`<secret>`: Obtain secret token using the instructions under "XNAT token"

 <br>
 
**Optional Flags**

Include the `-t <requested_scan_types.csv>` to download only scans that match your requested scan type list. Leave this option out to download all scans for each session in your `session_ids.csv` file.

Include the `--create-logs` flag to create output logs. Two logs will be created: one contains all output from the script, and the other will contain a catalog of the scans that were downloaded for each session.

If you only have one session you need to download scans for, you can use the `-i` or `--id` flag instead of including `-c <session_ids.csv>`. Specify it like this: `-i CNDA_E123456`

 <br>
 
**Example Usage**

1. Create a csv containing experiment_id/accession without a header.

session_ids.csv example:

||
|-------------|
| CNDA_E71543 |
| CNDA_E1594  |
| CNDA_E2240  |
| CNDA_E1112  |

2. Create a csv containing scan types/names without a header.

requested_scan_types.csv example:

||
|-------------|
| SAG 3D FSPGR |
| MPRAGE GRAPPA2  |
| AX T1  |
| FLAIR  |
| DTI  |

3. Run download_scans.py script

The command below is an example of downloading data from the KARI Master Data Freeze CNDA project 
where out_dir is your output directory path and ALIAS and SECRET below are replaced with the tokens you got from CNDA.
```
python3 download_scans.py https://cnda.wustl.edu out_dir -c scans_to_download.csv -t requested_scan_types.csv -u ALIAS -p SECRET
```
<br>

**Script output**

This script organizes the files into folders like this:

```
out_dir/session_label/scans/scan_id-scan_type
```

If the `--create-logs` flag is included when running the script, the following logs will be created:
- File `download_scans_${timestamp}.log`  that contains all output from the script.
- File `download_scans_catalog_${timestamp}.csv` - contains a list of all MR or PET Session IDs in your original list, the scans that were downloaded, and their final download status.

<br>
<br>

# Downloading FreeSurfer files
**download_freesurfer/download_freesurfer.py**

This script downloads all or a specific type of FreeSurfer files.

<br>

**General Usage:**
```
python download_freesurfer.py <site> <destination_dir> -c <fs_ids.csv> -u <alias> -p <secret>
```

<br>

**Required inputs:**

`<site>` - the XNAT website url ( https://cnda.wustl.edu/ )

`<destination_dir>` - A directory path (relative or absolute) to save the files to. If this directory doesn't exist when you run the script, it will be created automatically.

`<fs_ids.csv>` - A Unix formatted, comma-separated file containing a column for FreeSurfer IDs (FS_ID) (e.g. CNDA_E12345_freesurfer_2017101912345) without a header.

`<alias>`: Obtain alias token using the instructions under "XNAT token"
  
`<secret>`: Obtain secret token using the instructions under "XNAT token"

 <br>
 
**Optional Flags**

Include the `--create-logs` flag to create output logs. Two logs will be created: one contains all output from the script, and the other will contain a catalog of the Freesurfer resources that were downloaded.

If you only have one FreeSurfer you need to download files for, you can use the `-i` or `--id` flag instead of including `-c <fs_ids.csv>`. Specify it like this: `-i CNDA_E123456_freesurfer_01234567890`

Include any of the following optional flags to only download particular filetypes, or include no flags to download the entire set of files:

`--download-annot` Download .annot files

`--download-area` Download .area files

`--download-avg_curv` Download .avg_curv files

`--download-bak` Download .bak files

`--download-cmd` Download .cmd files

`--download-crv` Download .crv files

`--download-csurfdir` Download .csurfdir files

`--download-ctab` Download .ctab files

`--download-curv` Download .curv files

`--download-dat` Download .dat files

`--download-defect_borders` Download .defect_borders files

`--download-defect_chull` Download .defect_chull files

`--download-defect_labels` Download .defect_labels files

`--download-done` Download .done files

`--download-env` Download .env files

`--download-H` Download .H files

`--download-inflated` Download .inflated files

`--download-jacobian_white` Download .jacobian_white files

`--download-K` Download .K files

`--download-label` Download .label files

`--download-local-copy` Download .local-copy files

`--download-log` Download all log files, in both the LOG folder and DATA folder

`--download-lta` Download .lta files

`--download-mgh` Download .mgh files

`--download-mgz` Download .mgz files

`--download-m3z` Download .mgz files

`--download-mid` Download .mid files

`--download-nofix` Download .nofix files

`--download-old` Download .old files

`--download-orig` Download .orig files

`--download-pial` Download .pial files

`--download-reg` Download .reg files

`--download-smoothwm` Download .smoothwm files

`--download-snaps` Download snapshot files (all files in the SNAPSHOTS folder)

`--download-sphere` Download .sphere files

`--download-stats` Download stats files

`--download-sulc` Download sulc files

`--download-thickness` Download .thickness files

`--download-touch` Download .touch files

`--download-txt` Download .txt files

`--download-volume` Download .volume files

`--download-white` Download .white files

`--download-xdebug_mris_calc` Download .xdebug_mris_calc files

<br>
 
**Example Usage**

1. Create a csv containing FreeSurfer IDs (FS_ID) without a header.

download_freesurfer_list.csv example:

||
|-------------|
| CNDA_E12345_freesurfer_2017101912345 |
| CNDA_E57844_freesurfer_2019102112345  |
| CNDA_E19495_freesurfer_2018112212345  |

2. Run download_freesurfer.py script

The command below is an example of downloading all FreeSurfer files
where out_dir is your output directory path and ALIAS and SECRET are your alias and secret tokens.
```
python download_freesurfer.py https://cnda.wustl.edu out_dir -c download_freesurfer_list.csv -u ALIAS -p SECRET
```

The command below is an example of downloading the .pial and .mgz FreeSurfer files
where out_dir is your output directory path and ALIAS and SECRET are your alias and secret tokens.
```
python download_freesurfer.py https://cnda.wustl.edu out_dir -c download_freesurfer_list.csv -u ALIAS -p SECRET --download-mgz --download-pial
```

<br>

**Script output**

This script organizes the files into folders like this:

```
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/atlas (if FS 5.1 or 5.0)
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/label
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/mri
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/scripts
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/stats
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/surf
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/touch
out_dir/mr_session_label/fs_id/DATA/fs_id/mr_session_label/tmp
out_dir/mr_session_label/fs_id/SNAPSHOTS
out_dir/mr_session_label/fs_id/LOG
```

If the `--create-logs` flag is included when running the script, the following logs will be created:
- File `download_freesurfer_${timestamp}.log`  that contains all output from the script.
- File `download_freesurfer_catalog_${timestamp}.csv` - contains a list of all FreeSurfer IDs in your original list and their final download status.


<br>
<br>

# Downloading PUP files
**download_pup/download_pup.py**

This script downloads all or a specific type of PUP files.

<br>

**General Usage:**
```
python download_pup.py <site> <destination_dir> -c <pup_ids.csv> -u <alias> -p <secret>
```

<br>

**Required inputs:**

`<site>` - the XNAT website url ( https://cnda.wustl.edu/ )

`<destination_dir>` - A directory path (relative or absolute) to save the files to. If this directory doesn't exist when you run the script, it will be created automatically.

`<pup_ids.csv>` - A Unix formatted, comma-separated file containing a column for PUP IDs (PUP_ID) (e.g. CNDA_E12345_PUPTIMECOURSE_2017101912345) without a header.

`<alias>`: Obtain alias token using the instructions under "XNAT token"
  
`<secret>`: Obtain secret token using the instructions under "XNAT token"

 <br>
 
**Optional Flags**

Include the `--create-logs` flag to create output logs. Two logs will be created: one contains all output from the script, and the other will contain a catalog of the PUP resources that were downloaded.

If you only have one PUP you need to download files for, you can use the `-i` or `--id` flag instead of including `-c <pup_ids.csv>`. Specify it like this: `-i CNDA_E123456_PUPTIMECOURSE_01234567890`

Include any of the following optional flags to only download particular filetypes, or include no flags to download the entire set of files:

`--download-4dfp` Download 4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)

`--download-dat` Download .dat files

`--download-info` Download .info files

`--download-logs` Download all log files, in both the LOG folder and DATA folder

`--download-lst` Download .lst files

`--download-mgz` Download .mgz files

`--download-moco` Download .moco files

`--download-nii` Download .nii files

`--download-params` Download .params files

`--download-snaps` Download snapshot files (all files in the SNAPSHOTS folder)

`--download-sub` Download .sub files

`--download-suvr` Download suvr files

`--download-tac` Download tac files

`--download-tb` Download .tb files

`--download-txt` Download .txt files

`--download-no-ext` Download files with no extension

`--download-SUVR4dfp` Download SUVR.4dfp and SUVR_g8.4dfp files

`--download-T10014dfp` Download T1001.4dfp file

`--download-PETFOV` Download PETFOV.4dfp files

`--download-RSFMask` Download RSFMask.4dfp files

`--download-wmparc` Download all files containing "wmparc" in the name

<br>
 
**Example Usage**

1. Create a csv containing PUP IDs (PUP_ID) without a header.

download_pup_list.csv example:

||
|-------------|
| CNDA_E12345_PUPTIMECOURSE_2017101912345 |
| CNDA_E57844_PUPTIMECOURSE_2019102112345  |
| CNDA_E19495_PUPTIMECOURSE_2018112212345  |

2. Run download_pup.py script

The command below is an example of downloading all PUP files
where out_dir is your output directory path and ALIAS and SECRET are your alias and secret tokens.

**Note** PUP files can range from 1gb - 10 gb.

```
python download_pup.py https://cnda.wustl.edu out_dir -c download_pup_list.csv -u ALIAS -p SECRET
```

The command below is an example of downloading the .4dfp PUP files
where out_dir is your output directory path and ALIAS and SECRET are your alias and secret tokens.
```
python download_pup.py https://cnda.wustl.edu out_dir -c download_pup_list.csv -u ALIAS -p SECRET --download-4dfp
```

<br>

**Script output**

This script organizes the files into folders like this:

```
out_dir/pet_session_label/pup_id/DATA/pet_proc
out_dir/pet_session_label/pup_id/SNAPSHOTS
out_dir/pet_session_label/pup_id/LOG
```

If the `--create-logs` flag is included when running the script, the following logs will be created:
- File `download_pup_${timestamp}.log`  that contains all output from the script.
- File `download_pup_catalog_${timestamp}.csv` - contains a list of all PUP IDs in your original list and their final download status.

# Need additional help running these scripts?

If you have any questions regarding the scripts in this repository, find any issues running them, or wish to make improvements, feel free to open a Github issue above.
