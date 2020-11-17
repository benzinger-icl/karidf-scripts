#!/bin/env python

#================================================================
# Required python packages:
import argparse
import calendar
import csv
import datetime
import getpass
import os
import time
import zipfile
import shutil
import requests
#================================================================

#================================================================
# Script: download_freesurfer.py
#
# Author: Sarah Keefe
# Contributors: Austin McCullough, Rick Herrick
# Date Updated: 11/16/2020
#
# Written using python version 3
#
# Purpose: Go through a CSV of FreeSurfer IDs and download all files or specific files for that Freesurfer one at a time.
#================================================================
#
#================================================================
# Usage:  
# python download_freesurfer.py site destination_dir -c fs_ids.csv -u <alias> -p <secret>
#================================================================

#================================================================
# Required inputs:
# <fs_ids.csv> : a csv of FreeSurfer IDs you want to download with following columns with no header row:
# 		Freesurfer ID (e.g. CNDA_E12345_freesurfer_2017101912345). 
#		Must be the FS ID that begins with the accession number (begins with CNDA_).
# <site> : the site to download from: https://cnda.wustl.edu
# <destination_dir> : the output directory for the downloaded FreeSurfers.
# - u <alias>: Replace <alias> with the token next to the text "alias:" found on https://cnda.wustl.edu/data/services/tokens/issue
# - p <secret>: Replace <secret> with the token next to the text "secret:" found on https://cnda.wustl.edu/data/services/tokens/issue

# Output:
# The files will be organized into the following structure:
# ${fs_id}/DATA/atlas (if FS 5.1 or 5.0)
# ${fs_id}/DATA/label
# ${fs_id}/DATA/mri
# ${fs_id}/DATA/scripts
# ${fs_id}/DATA/stats
# ${fs_id}/DATA/surf
# ${fs_id}/DATA/touch
# ${fs_id}/DATA/tmp
# ${fs_id}/SNAPSHOTS
# ${fs_id}/LOG
#
# Creates a log file at `download_fs.log` - contains all output from the script.
# Creates a log file at `to_download_manually_fs.log` - contains a list of all FS IDs that could not be found.
# Creates a log file at `to_download_manually_fs_files.log` - contains a list of all files that could not be downloaded 
# and their FS IDs (in the format fs_id, filename).
#================================================================
#
#
#================================================================
# Include any of these optional flags to only download particular filetypes, or 
# include no flags to download the entire set of files:
#
# --download-annot Download .annot files
# --download-area Download .area files
# --download-avg_curv Download .avg_curv files
# --download-bak Download .bak files
# --download-cmd Download .cmd files
# --download-crv Download .crv files
# --download-csurfdir Download .csurfdir files
# --download-ctab Download .ctab files
# --download-curv Download .curv files
# --download-dat Download .dat files
# --download-defect_borders Download .defect_borders files
# --download-defect_chull Download .defect_chull files
# --download-defect_labels Download .defect_labels files
# --download-done Download .done files
# --download-env Download .env files
# --download-H Download .H files
# --download-inflated Download .inflated files
# --download-jacobian_white Download .jacobian_white files
# --download-K Download .K files
# --download-label Download .label files
# --download-local-copy Download .local-copy files
# --download-log Download all log files, in both the LOG folder and DATA folder
# --download-lta Download .lta files
# --download-mgh Download .mgh files
# --download-mgz Download .mgz files
# --download-m3z Download .mgz files
# --download-mid Download .mid files
# --download-nofix Download .nofix files
# --download-old Download .old files
# --download-orig Download .orig files
# --download-pial Download .pial files
# --download-reg Download .reg files
# --download-smoothwm Download .smoothwm files
# --download-snaps Download snapshot files (all files in the SNAPSHOTS folder)
# --download-sphere Download .sphere files
# --download-stats Download stats files
# --download-sulc Download sulc files
# --download-thickness Download .thickness files
# --download-touch Download .touch files
# --download-txt Download .txt files
# --download-volume Download .volume files
# --download-white Download .white files
# --download-xdebug_mris_calc Download .xdebug_mris_calc files
# --download-xfm Download .xfm files
#================================================================

#================================================================
# Note:
# The script will prompt you for a username and password, unless you include both of these optional flags 
# to specify a username and password (alias and secret token from site/data/services/tokens/issue):
# -u username or --user username to include username/alias
# -p password or --password password to include password/secret
#================================================================

#Start Script
#================================================================
# parse arguments to the script
parser = argparse.ArgumentParser(description='Download all FS files for a given assessor ID.')
parser.add_argument('-c', '--csv', help="csv filename containing a list of assessor IDs, with a header row")
parser.add_argument('site', help="Which site to download from, example https://cnda.wustl.edu (full site url)")
parser.add_argument('destination', help="Which folder to download to, example /data/nil-bluearc/etc/etc/etc")
parser.add_argument('-u', '--user', required=False, help="Site username/alias, from site/data/services/tokens/issue")
parser.add_argument('-p', '--password', required=False,
                    help="Site password/secret, from site/data/services/tokens/issue")
parser.add_argument('-i', '--id', help="ID of a single FS to download (instead of from a csv)")
parser.add_argument('--create-logs', help="Create log files of this download, showing which files have been downloaded",
                    action="store_true")
parser.add_argument('--download-annot',help="Download .annot files", action="store_true")
parser.add_argument('--download-area',help="Download .area files", action="store_true")
parser.add_argument('--download-avg_curv',help="Download .avg_curv files", action="store_true")
parser.add_argument('--download-bak',help="Download .bak files", action="store_true")
parser.add_argument('--download-cmd',help="Download .cmd files", action="store_true")
parser.add_argument('--download-crv',help="Download .crv files", action="store_true")
parser.add_argument('--download-csurfdir',help="Download .csurfdir files", action="store_true")
parser.add_argument('--download-ctab',help="Download .ctab files", action="store_true")
parser.add_argument('--download-curv',help="Download .curv files", action="store_true")
parser.add_argument('--download-dat',help="Download .dat files", action="store_true")
parser.add_argument('--download-defect_borders',help="Download .defect_borders files", action="store_true")
parser.add_argument('--download-defect_chull',help="Download .defect_chull files", action="store_true")
parser.add_argument('--download-defect_labels',help="Download .defect_labels files", action="store_true")
parser.add_argument('--download-done',help="Download .done files", action="store_true")
parser.add_argument('--download-env',help="Download .env files", action="store_true")
parser.add_argument('--download-H',help="Download .H files", action="store_true")
parser.add_argument('--download-inflated',help="Download .inflated files", action="store_true")
parser.add_argument('--download-jacobian_white',help="Download .jacobian_white files", action="store_true")
parser.add_argument('--download-K',help="Download .K files", action="store_true")
parser.add_argument('--download-label',help="Download .label files", action="store_true")
parser.add_argument('--download-local-copy',help="Download .local-copy files", action="store_true")
parser.add_argument('--download-logs',help="Download all log files, in both the LOG folder and DATA folder", action="store_true")
parser.add_argument('--download-lta',help="Download .lta files", action="store_true")
parser.add_argument('--download-mgh',help="Download .mgh files", action="store_true")
parser.add_argument('--download-mgz',help="Download .mgz files", action="store_true")
parser.add_argument('--download-m3z',help="Download .mgz files", action="store_true")
parser.add_argument('--download-mid',help="Download .mid files", action="store_true")
parser.add_argument('--download-nofix',help="Download .nofix files", action="store_true")
parser.add_argument('--download-old',help="Download .old files", action="store_true")
parser.add_argument('--download-orig',help="Download .orig files", action="store_true")
parser.add_argument('--download-pial',help="Download .pial files", action="store_true")
parser.add_argument('--download-reg',help="Download .reg files", action="store_true")
parser.add_argument('--download-smoothwm',help="Download .smoothwm files", action="store_true")
parser.add_argument('--download-snaps',help="Download snapshot files (all files in the SNAPSHOTS folder)", action="store_true")
parser.add_argument('--download-sphere',help="Download .sphere files", action="store_true")
parser.add_argument('--download-stats',help="Download stats files", action="store_true")
parser.add_argument('--download-sulc',help="Download sulc files", action="store_true")
parser.add_argument('--download-thickness',help="Download .thickness files", action="store_true")
parser.add_argument('--download-touch',help="Download .touch files", action="store_true")
parser.add_argument('--download-txt',help="Download .txt files", action="store_true")
parser.add_argument('--download-volume',help="Download .volume files", action="store_true")
parser.add_argument('--download-white',help="Download .white files", action="store_true")
parser.add_argument('--download-xdebug_mris_calc',help="Download .xdebug_mris_calc files", action="store_true")
parser.add_argument('--download-xfm',help="Download .xfm files", action="store_true")
args = parser.parse_args()

sessions_csv = args.csv
fs_id_to_download = args.id
site = args.site
user = args.user
if user is None:
    user = raw_input("Enter your username for " + site + ": ")
password = args.password
if password is None:
    password = getpass.getpass("Enter your password for " + site + ": ")
destination = args.destination
create_logs = args.create_logs
download_annot = args.download_annot
download_area = args.download_area
download_avg_curv = args.download_avg_curv
download_bak = args.download_bak
download_cmd = args.download_cmd
download_crv = args.download_crv
download_csurfdir = args.download_csurfdir
download_ctab = args.download_ctab
download_curv = args.download_curv
download_dat = args.download_dat
download_defect_borders = args.download_defect_borders
download_defect_chull = args.download_defect_chull
download_defect_labels = args.download_defect_labels
download_done = args.download_done
download_env = args.download_env
download_H = args.download_H
download_inflated = args.download_inflated
download_jacobian_white = args.download_jacobian_white
download_K = args.download_K
download_local_copy = args.download_local_copy
download_logs = args.download_logs
download_label = args.download_label
download_lta = args.download_lta
download_m3z = args.download_m3z
download_mgh = args.download_mgh
download_mgz = args.download_mgz
download_mid = args.download_mid
download_nofix = args.download_nofix
download_old = args.download_old
download_orig = args.download_orig
download_pial = args.download_pial
download_reg = args.download_reg
download_smoothwm = args.download_smoothwm
download_sphere = args.download_sphere
download_stats = args.download_stats
download_sulc = args.download_sulc
download_thickness = args.download_thickness
download_touch = args.download_touch
download_txt = args.download_txt
download_volume = args.download_volume
download_white = args.download_white
download_xdebug_mris_calc = args.download_xdebug_mris_calc
download_xfm = args.download_xfm
download_snaps = args.download_snaps

download_all = False

# if no flags are set, download everything
if not download_annot and not download_area and not download_avg_curv and not download_bak and not download_cmd and not download_crv and not download_csurfdir and not download_ctab and not download_curv and not download_dat and not download_defect_borders and not download_defect_chull and not download_defect_labels and not download_done and not download_env and not download_H and not download_inflated and not download_jacobian_white and not download_K and not download_label and not download_local_copy and not download_logs and not download_lta and not download_m3z and not download_mgh and not download_mgz and not download_mid and not download_nofix and not download_old and not download_orig and not download_pial and not download_reg and not download_smoothwm and not download_sphere and not download_stats and not download_sulc and not download_thickness and not download_touch and not download_txt and not download_volume and not download_white and not download_xdebug_mris_calc and not download_xfm and not download_snaps:
    download_all = True

# get timestamp for log file
timestamp_log_base = str(calendar.timegm(datetime.datetime.now().timetuple()))

# create a log file to write to
if create_logs:
    log_file = open('download_fs_log_' + timestamp_log_base + '.log', 'w')
    log_file_missing_fs = open('not_downloaded_fs_resources_' + timestamp_log_base + '.log', 'w')
else:
    log_file = None
    log_file_missing_fs = None

session = requests.Session()
credentials = (user, password)
headers = {"Content-Type": "application/json"}
#parameters = {"format": "json"}
parameters = {}
auth_url = site + "/data/JSESSION"


def close_xnat_session():
    # Close the XNAT connection
    try:
        closed = session.delete(auth_url)
        closed.raise_for_status()
    except requests.exceptions.HTTPError as logout_error:
        print("An error occurred trying to close XNAT user session. HTTP Status " + str(logout_error))
    else:
        print("XNAT user session has been closed.")

def download_file(folder_path, filename, response, block_sz):
    # from https://stackoverflow.com/a/22776
    # download file in chunks in case it is too large
    f = open(os.path.join(folder_path, filename), 'wb')
    if "content-length" in response.headers:
        file_size = int(response.headers["Content-Length"])
    else:
        file_size = 1

    print("Downloading: %s Bytes: %s" % (filename, file_size))

    file_size_dl = 0

    for incoming in response.iter_content(chunk_size=block_sz):
        file_size_dl += len(incoming)
        f.write(incoming)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print(status)

    f.close()


def extract_requested_files(zip_file_path, resource_folder_path, resource_name):
    fszip = zipfile.ZipFile(zip_file_path) 
    for subfile in fszip.namelist():

        subfilename = fszip.getinfo(subfile).filename

        subfilename_split = subfilename.split(".")
        #print(subfilename_split[0])
        #print(subfilename_split[1])

        download_this_file = False

        if download_all:
            # download all if none of the specific download flags are specified
            download_this_file = True
        elif download_logs and resource_name == "LOG":
            download_this_file = True
        elif download_snaps and resource_name == "SNAPSHOTS":
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'annot' and download_annot:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'area' and download_area:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'avg_curv' and download_avg_curv:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'bak' and download_bak:
            download_this_file = True             
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'cmd' and download_cmd:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'crv' and download_crv:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'csurfdir' and download_csurfdir:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'ctab' and download_ctab:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'curv' and download_curv:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'dat' and download_dat:
            download_this_file = True             
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'defect_borders' and download_defect_borders:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'defect_chull' and download_defect_chull:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'defect_labels' and download_defect_labels:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'env' and download_env:
            download_this_file = True                         
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'H' and download_H:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'inflated' and download_inflated:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'jacobian_white' and download_jacobian_white:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'K' and download_K:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'label' and download_label:
            download_this_file = True                         
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'local-copy' and download_local_copy:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'log' and download_logs:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'lta' and download_lta:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'm3z' and download_m3z:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'mgh' and download_mgh:
            download_this_file = True                         
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'mgz' and download_mgz:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'mid' and download_mid:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'nofix' and download_nofix:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'old' and download_old:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'orig' and download_orig:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'pial' and download_pial:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'reg' and download_reg:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'smoothwm' and download_smoothwm:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'sphere' and download_sphere:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'stats' and download_stats:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'sulc' and download_sulc:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'thickness' and download_thickness:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'touch' and download_touch:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'txt' and download_txt:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'volume' and download_volume:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'white' and download_white:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'xdebug_mris_calc' and download_xdebug_mris_calc:
            download_this_file = True 
        elif len(subfilename_split) > 1 and subfilename_split[-1] == 'xfm' and download_xfm:
            download_this_file = True                                                                                 

        if download_this_file:
            # extract the file
            print("Extracting file: " + subfilename)
            fszip.extract(subfilename, resource_folder_path)

            # get the folder name after resources/DATA/files (or whatever the resource name is)
            new_file_base_arr=subfilename.split("resources/" + resource_name + "/files/",1)
            new_file_base=new_file_base_arr[1]

            # get the new file basename and cut the filename off the end of it
            # need to create this directory before we can move the downloaded file to it
            new_file_location=new_file_base.rsplit("/",1)[0]
            print(os.path.join(resource_folder_path,new_file_location))
            if not os.path.exists(os.path.join(resource_folder_path,new_file_location)):
                #print("making directory: " + os.path.join(resource_folder_path,new_file_location))
                os.makedirs(os.path.join(resource_folder_path,new_file_location))

            #print(os.path.join(resource_folder_path,subfilename))
            #print(os.path.join(resource_folder_path,new_file_base))
            print("Moving file " + new_file_base + " from zipfile subdirectory into main resource directory.")
            shutil.move(os.path.join(resource_folder_path,subfilename),os.path.join(resource_folder_path,new_file_base))

            # Get the first foldername in the resource folder path - this folder structure is now empty so we can remove it.
            first_folder_path_arr=subfilename.split("/",1)
            first_folder_path=first_folder_path_arr[0]            
            shutil.rmtree(os.path.join(resource_folder_path,first_folder_path))


def download_resource_contents(dl_expt, dl_assessor, folder_path, filename, resource_name):
    # log that we are checking for the session
    print("Checking for session " + dl_assessor + " folder " + resource_name + ".")
    if create_logs:
        log_file.write("Checking for session " + dl_assessor + " folder " + resource_name + ".\n")

    # Download all files for this folder
    resource_contents_url = site + '/data/experiments/' + dl_expt + '/assessors/' + dl_assessor + '/resources/' + resource_name + \
                       '/files?format=zip'
    print(dl_assessor + ": Downloading from files URL: " + resource_contents_url)
    if create_logs:
        log_file.write(dl_assessor + ": Downloading from files URL:  " + resource_contents_url + "\n")

    #print("Resource contents URL: " + resource_contents_url)

    try:
        response = session.get(resource_contents_url, params=parameters, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as files_download_error:
        if files_download_error.response.status_code == 404:
            # No session found with this id
            print(resource_name + " resource for FreeSurfer ID " + dl_assessor + " does not exist or can't be found.")
            if create_logs:
                log_file.write("FreeSurfer " + dl_assessor + " resource " + resource_name + " does not exist or can't be found.\n")
                log_file_missing_fs.write(dl_assessor + "," + resource_name + "\n")
            return files_download_error.response.status_code
        else:
            print("Error code " + str(files_download_error.response.status_code) + " when searching for FreeSurfer " + dl_assessor + " resource " + resource_name + ".")
            if create_logs:
                log_file.write("Error code " + str(files_download_error.response.status_code) + " when searching for FreeSurfer " + dl_assessor + " resource " + resource_name + ".\n")
                log_file_missing_fs.write(dl_assessor + "," + resource_name + "\n")
            return files_download_error.response.status_code
    else:
        download_file(folder_path, filename, response, 8192)
        return response.status_code


def download_one_fs(assessor_id):

    # split up the FreeSurfer ID to get the PET accession number (experiment_id)
    experiment_id_arr = assessor_id.split("_freesurfer_")

    experiment_id = experiment_id_arr[0]

    print(assessor_id + ": Got experiment ID: " + experiment_id + ".")
    if create_logs:
        log_file.write(assessor_id + ": Got experiment ID: " + experiment_id + ". \n")

    # download each folder
    # send it the log files too
    resource_list = []
    if download_snaps or download_all:
        resource_list.append("SNAPSHOTS")
    if download_logs or download_all:
        resource_list.append("LOG")
    if download_all or download_annot or download_area or download_avg_curv or download_bak or download_cmd or download_crv or download_csurfdir or download_ctab or download_curv or download_dat or download_defect_borders or download_defect_chull or download_defect_labels or download_done or download_env or download_H or download_inflated or download_jacobian_white or download_K or download_label or download_local_copy or download_logs or download_lta or download_m3z or download_mgh or download_mgz or download_mid or download_nofix or download_old or download_orig or download_pial or download_reg or download_smoothwm or download_sphere or download_stats or download_sulc or download_thickness or download_touch or download_txt or download_volume or download_white or download_xdebug_mris_calc or download_xfm:
        resource_list.append("DATA")

    if not os.path.exists(destination):
        os.makedirs(destination)

    for resource_name in resource_list:
        folder_path = os.path.join(destination, assessor_id)
        resource_folder_path = os.path.join(folder_path, resource_name)

        zip_filename = assessor_id + '_' + resource_name + '.zip'

        download_result_code = download_resource_contents(experiment_id, assessor_id, destination, zip_filename, resource_name)

        if (str(download_result_code) == "200") and zipfile.is_zipfile(os.path.join(destination, zip_filename)):
            print(assessor_id + ": Got valid zip file " + os.path.join(destination, zip_filename) + ". Continuing.")        
            if create_logs:
                log_file.write(assessor_id + ": Got valid zip file " + os.path.join(destination, zip_filename) + ". Continuing.\n")
            # Make the DATA/SNAPSHOTS/LOGS dir if it doesn't exist yet
            if not os.path.exists(resource_folder_path):
                os.makedirs(resource_folder_path)
            extract_requested_files(os.path.join(destination, zip_filename), resource_folder_path, resource_name)
            os.remove(os.path.join(destination, zip_filename))
        elif (str(download_result_code) != "200"):
            print(assessor_id + ": Error code " + str(download_result_code) + " when attempting to download FreeSurfer " + assessor_id + " resource " + resource_name + ".")
            if create_logs:
                log_file.write(assessor_id + ": Error code " + str(download_result_code) + " for resource " + resource_name + ".\n")
        else:
            print(assessor_id + ": Downloaded an invalid zip file for FreeSurfer " + assessor_id + ", resource " + resource_name + ".")
            if create_logs:
                log_file.write(assessor_id + ": Downloaded an invalid zip file " + zip_filename + " for resource " + resource_name + ".\n")


# start the main thing

# write a date/time row to the log because why not
print("Script started at " + str(datetime.datetime.now()))
if create_logs:
    log_file.write("Script started at " + str(datetime.datetime.now()) + "\n")

num_password_retries = 1

while num_password_retries <= 3:
    num_password_retries = num_password_retries + 1

    if user is None:
        user = raw_input("Enter your username for " + site + ": ")
    if password is None:
        password = getpass.getpass("Enter your password for " + site + ": ")

    print("Checking that provided username and password are valid for " + site + ".")

    try:
        auth = session.get(auth_url, headers=headers, auth=credentials)
    except requests.exceptions.HTTPError as auth_err:
        if auth_err == 401:
            # Could not authenticate!
            if num_password_retries < 3:
                print("Could not log in to " + str(site) + " with username " + str(
                    user) + " and the provided password. Please re-try your password or press Ctrl+C to exit.")
            else:
                print("Could not log in to " + str(site) + " with username " + str(user) + " and the provided "
                      "password. Please make sure you are using the right username and password for this site.")
        else:
            if num_password_retries < 3:
                print("Error code " + str(auth_err) + " when logging in to " + str(site) + " as username " + str(
                    user) + " using the provided password. Please re-try your password or press Ctrl+C to exit.")
            else:
                print("Error code " + str(auth_err) + " when logging in to " + str(site) + " as username " + str(user) +
                      " using the provided password. Please make sure you are using the right username and password for"
                      " this site.")
        password = None
        continue
    else:
        if fs_id_to_download is None and sessions_csv is not None:
            # open the csv file and go through it
            with open(sessions_csv, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')

                for row in csv_reader:
                    # get the row data
                    assessor_id = row[0]

                    download_one_fs(assessor_id)

        elif fs_id_to_download is not None and sessions_csv is None:
            assessor_id = fs_id_to_download

            download_one_fs(assessor_id) 
        else:
            print(
                "You must include either a csv of FreeSurfer ids to download, or specify a single FreeSurfer ID using the --id flag.")

        close_xnat_session()
    break