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
# Script: download_pup.py
#
# Author: Sarah Keefe
# Contributors: Austin McCullough, Rick Herrick
# Date Updated: 11/18/2020
#
# Written using python version 3.6
#
# Purpose: Go through a CSV of PUP IDs and download all files for that PUP one at a time.
#================================================================
#
#================================================================
# Usage:
# python download_pup.py <site> <destination_dir> -c <pup_ids.csv> -u <alias> -p <secret>
#================================================================
#
#================================================================
# Required Inputs: 
#
# <pup_ids.csv> : a csv of PUP IDs you want to download. The script expects the following columns:
#     PUP_ID (e.g. CNDA_E12345_PUPTIMECOURSE_2017101912345). 
#     - Must be the PUP ID that begins with the accession number (begins with CNDA_ or DCA_ or CENTRAL_, etc).
# <site> : the site to download from: https://cnda.wustl.edu
# <destination_dir> : the output directory to download to
# - u <alias>: Replace <alias> with the token next to the text "alias:" found on https://cnda.wustl.edu/data/services/tokens/issue
# - p <secret>: Replace <secret> with the token next to the text "secret:" found on https://cnda.wustl.edu/data/services/tokens/issue
#
# Choose one of these flags to read from a CSV of PUP IDs, or specify a single PUP ID:
# -c filename.csv or 
# --csv filename.csv to read from a CSV of PUP IDs with no header row (specify filename.csv)
# -i pup_id or --id pup_id to download for a single PUP ID (specify pup_id)
#
# Output:
# Organizes the files into the following folder structure: 
# destination_dir/${session_label}/${pup_id}/DATA/pet_proc
# destination_dir/${session_label}/${pup_id}/SNAPSHOTS
# destination_dir/${session_label}/${pup_id}/LOG
#
# If the --create-logs flag is included:
# Creates a log file at `download_pup_${timestamp}.log` - contains all output from the script.
# Creates a log file at `download_freesurfer_catalog_${timestamp}.log` - contains PUPs from your original list, 
#     specifying which resources were downloaded successfully, and which failed to download.
#================================================================
#
#
#
#================================================================
# Include any of these optional flags to only download particular file types, or include no flags to download the entire
# set of files:
#
# Include the --create-logs flag to create log files that show the script output and specify which files have been
# skipped.
#
# --download-4dfp: Download 4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)
# --download-dat: Download .dat files
# --download-info: Download .info files
# --download-logs: Download all log files, in both the LOG folder and DATA folder
# --download-lst: Download .lst files
# --download-mgz: Download .mgz files
# --download-moco: Download .moco files
# --download-nii: Download .nii files
# --download-params: Download .params files
# --download-snaps: Download snapshot files (all files in the SNAPSHOTS folder)
# --download-sub: Download .sub files
# --download-suvr: Download suvr files
# --download-tac: Download tac files
# --download-tb: Download .tb files
# --download-txt: Download .txt files
# --download-no-ext: Download files with no extension
# --download-SUVR4dfp: Download SUVR.4dfp and SUVR_g8.4dfp files
# --download-T10014dfp: Download T1001.4dfp file
# --download-PETFOV: Download PETFOV.4dfp files
# --download-RSFMask: Download RSFMask.4dfp files
# --download-wmparc: Download all files containing "wmparc" in the name
#================================================================
#
#
#================================================================
# Note:
# The script will prompt you for a username and password, unless you include both of these optional flags 
# to specify a username and password (alias and secret token from site/data/services/tokens/issue):
# -u username or --user username to include username/alias
# -p password or --password password to include password/secret
#================================================================

# Start script
#================================================================

# parse arguments to the script
parser = argparse.ArgumentParser(description='Download all PUP files for a given assessor ID.')
parser.add_argument('-c', '--csv', help="csv filename containing a list of assessor IDs, with a header row")
parser.add_argument('site', help="Which site to download from, example https://cnda.wustl.edu (full site url)")
parser.add_argument('destination', help="Which folder to download to, example /data/nil-bluearc/etc/etc/etc")
parser.add_argument('-u', '--user', required=False, help="Site username/alias, from site/data/services/tokens/issue")
parser.add_argument('-p', '--password', required=False,
                    help="Site password/secret, from site/data/services/tokens/issue")
parser.add_argument('-i', '--id', help="ID of a single PUP to download (instead of from a csv)")
parser.add_argument('--create-logs', help="Create log files of this download, showing which files have been downloaded",
                    action="store_true")
parser.add_argument('--download-4dfp', help="Download 4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)",
                    action="store_true")
parser.add_argument('--download-dat', help="Download .dat files", action="store_true")
parser.add_argument('--download-info', help="Download .info files", action="store_true")
parser.add_argument('--download-logs', help="Download all log files, in both the LOG folder and DATA folder",
                    action="store_true")
parser.add_argument('--download-lst', help="Download .lst files", action="store_true")
parser.add_argument('--download-mgz', help="Download .mgz files", action="store_true")
parser.add_argument('--download-moco', help="Download .moco files", action="store_true")
parser.add_argument('--download-nii', help="Download .nii files", action="store_true")
parser.add_argument('--download-params', help="Download .params files", action="store_true")
parser.add_argument('--download-snaps', help="Download snapshot files (all files in the SNAPSHOTS folder)",
                    action="store_true")
parser.add_argument('--download-sub', help="Download .sub files", action="store_true")
parser.add_argument('--download-suvr', help="Download suvr files", action="store_true")
parser.add_argument('--download-tac', help="Download tac files", action="store_true")
parser.add_argument('--download-tb', help="Download .tb files", action="store_true")
parser.add_argument('--download-txt', help="Download .txt files", action="store_true")
parser.add_argument('--download-no-ext', help="Download files with no extension", action="store_true")
parser.add_argument('--download-SUVR4dfp',
                    help="Download SUVR .4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)",
                    action="store_true")
parser.add_argument('--download-T10014dfp', help="Download T1001.4dfp files", action="store_true")
parser.add_argument('--download-PETFOV',
                    help="Download PETFOV .4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)",
                    action="store_true")
parser.add_argument('--download-RSFMask',
                    help="Download RSFMask .4dfp files (.4dfp.hdr, .4dfp.ifh, .4dfp.img, .4dfp.img.rec)",
                    action="store_true")
parser.add_argument('--download-wmparc',
                    help="Download all wmparc-related files (wmparc001.4dfp, wmparc.nii, wmparc.mgz)",
                    action="store_true")
args = parser.parse_args()

sessions_csv = args.csv
pup_id_to_download = args.id
site = args.site
user = args.user
if user is None:
    user = raw_input("Enter your username for " + site + ": ")
password = args.password
if password is None:
    password = getpass.getpass("Enter your password for " + site + ": ")
destination = args.destination
create_logs = args.create_logs
download_4dfp = args.download_4dfp
download_dat = args.download_dat
download_info = args.download_info
download_logs = args.download_logs
download_lst = args.download_lst
download_mgz = args.download_mgz
download_moco = args.download_moco
download_nii = args.download_nii
download_params = args.download_params
download_snaps = args.download_snaps
download_sub = args.download_sub
download_suvr = args.download_suvr
download_tac = args.download_tac
download_tb = args.download_tb
download_txt = args.download_txt
download_no_ext = args.download_no_ext
download_SUVR4dfp = args.download_SUVR4dfp
download_T10014dfp = args.download_T10014dfp
download_PETFOV = args.download_PETFOV
download_RSFMask = args.download_RSFMask
download_wmparc = args.download_wmparc

download_all = False

# if no flags are set, download everything
if not download_4dfp and not download_dat and not download_info and not download_logs and not download_lst and not \
        download_mgz and not download_moco and not download_nii and not download_params and not download_snaps and not \
        download_sub and not download_suvr and not download_tac and not download_tb and not download_txt and not \
        download_SUVR4dfp and not download_T10014dfp and not download_PETFOV and not download_RSFMask and not \
        download_no_ext and not download_wmparc:
    download_all = True

# get timestamp for log file
timestamp_log_base = str(calendar.timegm(datetime.datetime.now().timetuple()))

# create a log file to write to
if create_logs:
    log_file = open('download_pup_' + timestamp_log_base + '.log', 'w')
    log_file_catalog = open('download_pup_catalog_' + timestamp_log_base + '.csv', 'w')
    log_file_catalog.write("Session ID,Session Label,PUP ID,Download Information\n")
else:
    log_file = None
    log_file_catalog = None

session = requests.Session()
credentials = (user, password)
headers = {"Content-Type": "application/json"}
#parameters = {"format": "json"}
parameters = {}
auth_url = site + "/data/JSESSION"


# Close the XNAT connection
def close_xnat_session():
    try:
        closed = session.delete(auth_url)
        closed.raise_for_status()
    except requests.exceptions.HTTPError as logout_error:
        print("An error occurred trying to close XNAT user session. HTTP Status " + str(logout_error))
    else:
        print("XNAT user session has been closed.")


# Pull the session label for the given session ID from XNAT using the XNAT API
def get_session_label(assessor_id, session_id):
    # log that we are checking for the session
    print(assessor_id + ": Pulling session label for session " + session_id + ".")
    if create_logs:
        log_file.write(assessor_id + ": Pulling session label for session " + session_id + ".\n")

    # Pull session label using XNAT API
    sess_label_url = site + '/data/experiments?ID=' + session_id + '&columns=label&format=csv'
    print(assessor_id + ": Checking session info at URL: " + sess_label_url)
    if create_logs:
        log_file.write(assessor_id + ": Checking session info at URL:  " + sess_label_url + "\n")
    try:
        response = session.get(sess_label_url, params=parameters, headers=headers)
        if response.encoding is None:
            response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.exceptions.HTTPError as session_infopull_error:
        if session_infopull_error.response.status_code == 404:
            # No session found with this id
            print(assessor_id + ": Session ID " + session_id + " does not exist or can't be found.")
            if create_logs:
                log_file.write(assessor_id + ": Session " + session_id + " does not exist or can't be found.\n")
                log_file_catalog.write(session_id + ",,,Parent session not found\n")
            return None
        else:
            print(assessor_id + ": Error code " + str(session_infopull_error.response.status_code) + " when pulling session info for session " + session_id + ".")
            if create_logs:
                log_file.write(assessor_id + ": Error code " + str(session_infopull_error.response.status_code) + " when pulling session info for session " + session_id + ".\n")
                log_file_catalog.write(session_id + ",,,Parent session error code" + str(session_infopull_error.response.status_code) + "\n")
            return None
    else:
        session_label = None
        # Get the session label from the JSON result
        label_csv_contents = response.iter_lines(decode_unicode=True)
        label_info_reader = csv.reader(label_csv_contents, delimiter=",")
        for info_row in label_info_reader:
            if info_row[0] != "ID":
                session_label = info_row[1]
        return session_label


# Download a file to folder_path/filename from a requests response
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


# extract files from a zip file based on the flags sent to the script
def extract_requested_files(zip_file_path, resource_folder_path, resource_name):
    pupzip = zipfile.ZipFile(zip_file_path) 
    for subfile in pupzip.namelist():

        subfilename = pupzip.getinfo(subfile).filename

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
        elif len(subfilename_split) > 1 and '4dfp' in subfilename_split[1] and download_4dfp:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'dat' and download_dat:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'info' and download_info:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'log' and download_logs:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'lst' and download_lst:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'mgz' and download_mgz:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'moco' and download_moco:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'nii' and download_nii:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'params' and download_params:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'sub' and download_sub:
            download_this_file = True
        elif (len(subfilename_split) > 1) and (subfilename_split[1] == 'suvr') and download_suvr:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'tac' and download_tac:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'tb' and download_tb:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[1] == 'txt' and download_txt:
            download_this_file = True
        elif len(subfilename_split) == 1 and download_no_ext:
            download_this_file = True
        elif len(subfilename_split) > 1 and 'SUVR' in subfilename_split[0] and '4dfp' in subfilename_split[1] and download_SUVR4dfp:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[0] == 'T1001' and '4dfp' in subfilename_split[1] and \
                download_T10014dfp:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[0] == 'petfov' and '4dfp' in subfilename_split[1] and download_PETFOV:
            download_this_file = True
        elif len(subfilename_split) > 1 and subfilename_split[0] == 'RSFMask' and '4dfp' in subfilename_split[1] and \
                download_RSFMask:
            download_this_file = True
        elif len(subfilename_split) > 1 and ('wmparc' in subfilename_split[0]) and download_wmparc:
            download_this_file = True

        if download_this_file:
            # extract the file
            print("Extracting file: " + subfilename)
            pupzip.extract(subfilename, resource_folder_path)

            # get the folder name after resources/DATA/files (or whatever the resource name is)
            new_file_base_arr=subfilename.split("resources/" + resource_name + "/files/",1)
            new_file_base=new_file_base_arr[1]

            # get the new file basename and cut the filename off the end of it
            # need to create this directory before we can move the downloaded file to it
            new_file_location = ""
            if (new_file_base.count('/') > 0):
                new_file_location = new_file_base.rsplit("/",1)[0]

            if not os.path.exists(os.path.join(resource_folder_path,new_file_location)):
                os.makedirs(os.path.join(resource_folder_path,new_file_location))

            print("Moving file " + new_file_base + " from zipfile subdirectory into main resource directory.")
            shutil.move(os.path.join(resource_folder_path,subfilename),os.path.join(resource_folder_path,new_file_location))

            # Get the first foldername in the resource folder path - this folder structure is now empty so we can remove it.
            first_folder_path_arr=subfilename.split("/",1)
            first_folder_path=first_folder_path_arr[0]            
            shutil.rmtree(os.path.join(resource_folder_path,first_folder_path))


# download the contents of an XNAT resource folder for a given assessor
# A resource folder is named "DATA", "LOG", or "SNAPSHOTS"
def download_resource_contents(dl_expt, dl_assessor, folder_path, filename, resource_name):
    # log that we are checking for the session
    print(assessor_id + ": Checking for session " + dl_assessor + " folder " + resource_name + ".")
    if create_logs:
        log_file.write(assessor_id + ": Checking for session " + dl_assessor + " folder " + resource_name + ".\n")

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
            print("resource type " + resource_name + "for PUP ID " + dl_assessor + " does not exist or can't be found.")
            if create_logs:
                log_file.write("PUP " + dl_assessor + " resource " + resource_name + " does not exist or can't be found.\n")
            return files_download_error.response.status_code
        else:
            print("Error code " + str(files_download_error.response.status_code) + " when searching for PUP " + dl_assessor + ".")
            if create_logs:
                log_file.write("Error code " + str(files_download_error.response.status_code) + " when searching for PUP " + dl_assessor + ".\n")
            return files_download_error.response.status_code
    else:
        download_file(folder_path, filename, response, 8192)
        return response.status_code


# Download a single PUP based on a given assessor ID
# Pulls the experiment ID for the main session from the assessor
# Determines which resource to download from based on the flags sent to the main script
def download_one_pup(assessor_id):

    # split up the PUP ID to get the PET accession number (experiment_id)
    experiment_id_arr = assessor_id.split("_PUPTIMECOURSE_")

    experiment_id = experiment_id_arr[0]

    print(assessor_id + ": Got experiment ID: " + experiment_id + ".")
    if create_logs:
        log_file.write(assessor_id + ": Got experiment ID: " + experiment_id + ". \n")

    session_label = get_session_label(assessor_id, experiment_id)
    if session_label is not None:
        # download each folder
        # send it the log files too
        resource_list = []
        if download_snaps or download_all:
            resource_list.append("SNAPSHOTS")
        if download_logs or download_all:
            resource_list.append("LOG")
        if download_all or download_4dfp or download_dat or download_info or download_logs or download_lst \
                or download_mgz or download_moco or download_nii or download_params or download_sub or \
                download_suvr or download_tac or download_tb or download_txt or download_SUVR4dfp or \
                download_T10014dfp or download_PETFOV or download_RSFMask or download_no_ext or download_wmparc:
            resource_list.append("DATA")

        if not os.path.exists(destination):
            os.makedirs(destination)

        for resource_name in resource_list:
            folder_path = os.path.join(destination, session_label, assessor_id)
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
                if create_logs:
                    log_file.write(assessor_id + ": Successfully unzipped zip file for resource " + resource_name + ".\n")
                    log_file_catalog.write(experiment_id + "," + session_label + "," + assessor_id + ",Files from " + resource_name + " resource downloaded successfully.\n")
            elif (str(download_result_code) != "200"):
                print(assessor_id + ": Error code " + str(download_result_code) + " when attempting to download PUP " + assessor_id + " resource " + resource_name + ".")
                if create_logs:
                    log_file.write(assessor_id + ": Error code " + str(download_result_code) + " for resource " + resource_name + ".\n")
                    log_file_catalog.write(experiment_id + "," + session_label + "," + assessor_id + ",Error code " + str(download_result_code) + " for resource " + resource_name + ".\n")
            else:
                print(assessor_id + ": Downloaded an invalid zip file for PUP " + assessor_id + ", resource " + resource_name + ".")
                if create_logs:
                    log_file.write(assessor_id + ": Downloaded an invalid zip file " + zip_filename + " for resource " + resource_name + ".\n")
                    log_file_catalog.write(experiment_id + "," + session_label + "," + assessor_id + ",Got invalid zip file for resource " + resource_name + ".\n")
    else:
        print("Problem pulling label for Session ID " + experiment_id + " (PUP ID " + assessor_id + ")")
        if create_logs:
            log_file.write(assessor_id + ": Problem pulling label for Session ID " + experiment_id + ".\n")
            log_file_catalog.write(experiment_id + ",," + assessor_id + ",Could not pull Session Label from Session ID.\n")

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
        if pup_id_to_download is None and sessions_csv is not None:
            # open the csv file and go through it
            with open(sessions_csv, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')

                for row in csv_reader:
                    # get the assessor ID from the row data
                    assessor_id = row[0]

                    if create_logs:
                        log_file.write("Getting started with PUP " + assessor_id + ".\n")

                    # download the single Freesurfer based on assessor ID
                    download_one_pup(assessor_id)

                    if create_logs:
                        log_file.write("Done with PUP " + assessor_id + ".\n")

        elif pup_id_to_download is not None and sessions_csv is None:
            assessor_id = pup_id_to_download

            if create_logs:
                log_file.write("Getting started with PUP " + assessor_id + ".\n")

            # download the single Freesurfer based on assessor ID
            download_one_pup(assessor_id)

            if create_logs:
                log_file.write("Done with PUP " + assessor_id + ".\n")
        else:
            print("You must include either a csv of PUP ids to download, or specify a single PUP ID using the --id flag.")
        close_xnat_session()
        print("Download PUP script is completed.")
        if create_logs:
            print('See download_pup_catalog_' + timestamp_log_base + '.csv for a list of the PUP resources that were downloaded.')
    break