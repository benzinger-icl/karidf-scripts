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
# Script: download_scans.py
#
# Author: Sarah Keefe
# Contributors: Austin McCullough, Rick Herrick
# Date Updated: 11/18/2020
#
# Written using python version 3.6
#
# Purpose: Go through a CSV of XNAT Session IDs and download scans from those sessions based on other inputs to the script.
#================================================================
#
#================================================================
# Usage:
# python download_scans.py <site> <destination_dir> -c <session_ids.csv> -u <alias> -p <secret>
#================================================================
#
#================================================================
# Required Inputs: 
#
# -c <session_ids.csv> : a csv of XNAT Session IDs you want to download. The script expects the following columns:
#     - MR or PET Session ID (e.g. CNDA_E12345). Must be the session "accession number"
#     (begins with CNDA_ or DCA_ or CENTRAL_, etc).
# <site> : the site to download from: https://cnda.wustl.edu
# <destination_dir> : the output directory to download to
# -u <alias>: Replace <alias> with the token next to the text "alias:" found on https://cnda.wustl.edu/data/services/tokens/issue
# -p <secret>: Replace <secret> with the token next to the text "secret:" found on https://cnda.wustl.edu/data/services/tokens/issue
#
# Choose one of these flags to read from a CSV of Session IDs, or specify a single Session ID:
# -c filename.csv or --csv filename.csv to read from a CSV of Session IDs with no header row (specify filename.csv)
# -i session_id or --id session_id to download for a single Session ID (specify session_id)
#
# Include the -t flag to specify a CSV of specific XNAT scan type names to download:
# -t filename.csv or --type-list filename.csv to read from a CSV of scan types with no header row (specify filename.csv)
# If -t is not included, all scans for each session will be downloaded.
#
# Include the --create-logs flag to create log files that show the script output and specify which files have been
# skipped.
#
#
# Output:
# Organizes the files into the following folder structure: 
# destination_dir/session_label/scans/4-MPRAGE/resources/DICOM
#
# If the --create-logs flag is included:
# Creates a log file at `download_scans_timestamp.log` - contains all output from the script. 
# Creates a log file at `download_scans_catalog_timestamp.csv` - contains a catalog of which scans were downloaded. 
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
parser = argparse.ArgumentParser(description='Download scan files for a given session ID or list of session IDs. Allows the user to specify a single column list of scan types in order to download only those types.')
parser.add_argument('-c', '--csv', help="csv filename containing a list of session IDs (accession numbers), one per line")
parser.add_argument('-t', '--type-list', help="csv filename containing a list of scan type names, one per line")
parser.add_argument('site', help="Which site to download from, example https://cnda.wustl.edu (full site url)")
parser.add_argument('destination', help="Which folder to download to, example /data/nil-bluearc/etc/etc/etc")
parser.add_argument('-u', '--user', required=False, help="Site username/alias, from site/data/services/tokens/issue")
parser.add_argument('-p', '--password', required=False,
                    help="Site password/secret, from site/data/services/tokens/issue")
parser.add_argument('-i', '--id', help="ID of a single session to download (instead of from a csv)")
parser.add_argument('--create-logs', help="Create log files of this download, showing which files have been downloaded",
                    action="store_true")

args = parser.parse_args()

sessions_csv = args.csv
scan_type_list = args.type_list
session_id_to_download = args.id
site = args.site
user = args.user
if user is None:
    user = raw_input("Enter your username for " + site + ": ")
password = args.password
if password is None:
    password = getpass.getpass("Enter your password for " + site + ": ")
destination = args.destination
create_logs = args.create_logs

download_all = False

# if no scan type list was sent, download all scans
if scan_type_list is None:
    print("Downloading all scans.")
    download_all = True

# get timestamp for log file
timestamp_log_base = str(calendar.timegm(datetime.datetime.now().timetuple()))

# create a log file to write to
if create_logs:
    log_file = open('download_scans_' + timestamp_log_base + '.log', 'w')
    log_file_catalog = open('download_scans_catalog_' + timestamp_log_base + '.csv', 'w')
    log_file_catalog.write("Session ID,Session Label,Scan ID,Scan Type,Scan Series Description,Download Information\n")
else:
    log_file = None
    log_file_catalog = None

session = requests.Session()
credentials = (user, password)
headers = {"Content-Type": "application/json"}
#parameters = {"format": "json"}
parameters = {}
auth_url = site + "/data/JSESSION"


# Close the XNAT session after the script is completed
def close_xnat_session():
    # Close the XNAT connection
    try:
        closed = session.delete(auth_url)
        closed.raise_for_status()
    except requests.exceptions.HTTPError as logout_error:
        print("An error occurred trying to close XNAT user session. HTTP Status " + str(logout_error))
    else:
        print("XNAT user session has been closed.")


# Function to download a zip file in chunks
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

# if scan_id is ALL then go through the scan list response and log all the scans we got in the catalog log file.
# If scan_id is a single scan ID, then log the scan type and series desc info for just that scan.
def log_downloaded_scans(session_id, session_label, scan_id, scans_list_response):
    csv_contents = scans_list_response.iter_lines(decode_unicode=True)
    scanlist_reader = csv.reader(csv_contents, delimiter=",")
    for scan_result_row in scanlist_reader:
        found_image_scandata_id = scan_result_row[0]
        found_scan_id = scan_result_row[1]
        found_scan_type = scan_result_row[2]
        found_scan_series_desc = scan_result_row[6]
        if found_image_scandata_id != "xnat_imagescandata_id":
            if scan_id == "ALL":
                log_file.write("Session " + session_id + " scan " + found_scan_id + " was downloaded successfully.\n")
                log_file_catalog.write(session_id + "," + session_label + "," + found_scan_id + "," + found_scan_type + "," + found_scan_series_desc + ",Downloaded successfully\n")
            elif scan_id == found_scan_id:
                log_file.write("Session " + session_id + " scan " + scan_id + " was downloaded successfully.\n")
                log_file_catalog.write(session_id + "," + session_label + "," + found_scan_id + "," + found_scan_type + "," + found_scan_series_desc + ",Downloaded successfully\n")


# Unzip a downloaded scan zip file
def extract_scan_files(session_id, session_label, zip_file_path, session_folder_path, scan_id):
    print("Extracting zip file " + zip_file_path + " to location " + session_folder_path + ".")  
    scanzip = zipfile.ZipFile(zip_file_path)
    scanzip.extractall(session_folder_path)


# Download a single scan from XNAT using the XNAT API, or if scan_id is "ALL", download all scans
def download_scan_contents(session_id, session_label, scan_id, destination, zip_filename):
    # log that we are checking for the session
    print("Checking for session " + session_id + " scan " + scan_id + ".")
    if create_logs:
        log_file.write("Checking for session " + session_id + " scan " + scan_id + ".\n")

    # Download all files for this scan
    scan_url = site + '/data/experiments/' + session_id + '/scans/' + scan_id + '/files?format=zip'
    print(session_id + ": Downloading from scan URL: " + scan_url)
    if create_logs:
        log_file.write(session_id + ": Downloading from scan URL:  " + scan_url + "\n")
    try:
        response = session.get(scan_url, params=parameters, headers=headers)
        if response.encoding is None:
            response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.exceptions.HTTPError as scan_download_error:
        if scan_download_error.response.status_code == 404:
            # No session found with this id
            print("Scan ID " + scan_id + "for Session ID " + session_id + " does not exist or can't be found.")
            if create_logs:
                log_file.write("Session " + session_id + " scan " + scan_id + " does not exist or can't be found.\n")
                log_file_catalog.write(session_id + "," + session_label + "," + scan_id + ",,,Not found\n")
            return scan_download_error.response.status_code
        else:
            print("Error code " + str(scan_download_error.response.status_code) + " when searching for session " + session_id + ".")
            if create_logs:
                log_file.write("Error code " + str(scan_download_error.response.status_code) + " when searching for session " + session_id + ".\n")
                log_file_catalog.write(session_id + "," + session_label + "," + scan_id + ",,,Error code" + str(scan_download_error.response.status_code) + "\n")
            return scan_download_error.response.status_code
    else:
        download_file(destination, zip_filename, response, 8192)
        return response.status_code


# Pull the session label for the given session ID from XNAT using the XNAT API
def get_session_label(session_id):
    # log that we are checking for the session
    print("Pulling session label for session " + session_id + ".")
    if create_logs:
        log_file.write("Pulling session label for session " + session_id + ".\n")

    # Pull session label using XNAT API
    sess_label_url = site + '/data/experiments?ID=' + session_id + '&columns=label&format=csv'
    print(session_id + ": Checking session info at URL: " + sess_label_url)
    if create_logs:
        log_file.write(session_id + ": Checking session info at URL:  " + sess_label_url + "\n")
    try:
        response = session.get(sess_label_url, params=parameters, headers=headers)
        if response.encoding is None:
            response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.exceptions.HTTPError as session_infopull_error:
        if session_infopull_error.response.status_code == 404:
            # No session found with this id
            print("Session ID " + session_id + " does not exist or can't be found.")
            if create_logs:
                log_file.write("Session " + session_id + " does not exist or can't be found.\n")
                log_file_catalog.write(session_id + ",,,,,Not found\n")
            return None
        else:
            print("Error code " + str(session_infopull_error.response.status_code) + " when pulling session info for session " + session_id + ".")
            if create_logs:
                log_file.write("Error code " + str(session_infopull_error.response.status_code) + " when pulling session info for session " + session_id + ".\n")
                log_file_catalog.write(session_id + ",,,,,Error code" + str(session_infopull_error.response.status_code) + "\n")
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


# Run the single scan download process
# But if scan_id is "ALL", then "ALL" is sent to the XNAT API URL and all scans will 
#     be downloaded (using download_scan_contents())
# Also creates the destination directory if it does not already exist
def download_one_scan(session_id, session_label, scan_id, scans_list_response, destination):

    if not os.path.exists(destination):
        os.makedirs(destination)

    session_folder_path = destination

    zip_filename = session_id + '_' + scan_id + '.zip'

    # Download the scan (or ALL scans) to file zip_filename and get the result code to determine if the zip file is valid
    download_result_code = download_scan_contents(session_id, session_label, scan_id, destination, zip_filename)

    if (str(download_result_code) == "200") and zipfile.is_zipfile(os.path.join(destination, zip_filename)):
        print(session_id + ": Got valid zip file " + os.path.join(destination, zip_filename) + ". Continuing.")        
        if create_logs:
            log_file.write(session_id + ": Got valid zip file " + os.path.join(destination, zip_filename) + ". Continuing.\n")

        extract_scan_files(session_id, session_label, os.path.join(destination, zip_filename), session_folder_path, scan_id)

        # Log the results in the catalog
        if create_logs:
            log_downloaded_scans(session_id, session_label, scan_id, scans_list_response)
        # Remove the zip file
        os.remove(os.path.join(destination, zip_filename))
    elif (str(download_result_code) != "200"):
        print(session_id + ": Error code " + str(download_result_code) + " when attempting to download session " + session_id + " scan " + scan_id + ".")
        if create_logs:
            log_file.write(session_id + ": Error code " + str(download_result_code) + " for scan " + scan_id + ".\n")
            log_file_catalog.write(session_id + "," + session_label + "," + scan_id + ",,,Error code " + str(download_result_code) + "\n")
    else:
        print(session_id + ": Downloaded an invalid zip file for scan " + assessor_id + ", scan " + scan_id + ".")
        if create_logs:
            log_file.write(session_id + ": Downloaded an invalid zip file " + zip_filename + " for scan " + scan_id + ".\n")
            log_file_catalog.write(session_id + "," + session_label + "," + scan_id + ",,,Got invalid zip file\n")


# Take the response we got back from asking the session for the list of scan types it has
# Go through that list, and go through the provided list of scan types
# If any scans in the session scan list match the type in the provided scan type list,
# download that scan with "download_one_scan()"
def download_scans_from_list(session_id, session_label, scans_list_response, destination):
    csv_contents = scans_list_response.iter_lines(decode_unicode=True)
    scanlist_reader = csv.reader(csv_contents, delimiter=",")
    with open(scan_type_list) as scantypes_file:
        scantypes_reader = csv.reader(scantypes_file, delimiter=",")
        for scan_row in scanlist_reader:
            found_image_scandata_id = scan_row[0]
            found_scan_id = scan_row[1]
            found_scan_type = scan_row[2]
            found_scan_series_desc = scan_row[6]
            if found_image_scandata_id != "xnat_imagescandata_id":
                #print("Found scan in session scan list: " + found_scan_type + ", ID: " + found_scan_id)
                for scantype_row in scantypes_reader:
                    #print("Comparing with scan type from list: " + scantype_row[0])
                    if found_scan_type == scantype_row[0]:
                        print("Found scan type " + scantype_row[0] + " in scan list for session " + session_id + ". Attempting to download the scan (ID " + found_scan_id + ").")
                        if create_logs:
                            log_file.write(session_id + ": Found scan type " + scantype_row[0] + " (Scan ID " + found_scan_id + "). Attempting to download it.\n")
                        download_one_scan(session_id, session_label, found_scan_id, scans_list_response, destination)
            scantypes_file.seek(0)


# Use the session ID to pull the list of scans from XNAT
# Pull the list of scans and scan info in CSV format.
def pull_scans_list(session_id):
    # log that we are checking for the session
    print("Checking session " + session_id + " scan list.")
    if create_logs:
        log_file.write("Checking session " + session_id + " scan list.\n")

    # Download all files for this scan
    scan_list_url = site + '/data/experiments/' + session_id + '/scans?format=csv'
    print(session_id + ": Checking scan list at URL: " + scan_list_url)
    if create_logs:
        log_file.write(session_id + ": Checking scan list at URL:  " + scan_list_url + "\n")
    try:
        response = session.get(scan_list_url, params=parameters, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as scan_download_error:
        if scan_download_error.response.status_code == 404:
            # No session found with this id
            print("Session ID " + session_id + " does not exist or can't be found.")
            #if create_logs:
            #    log_file.write("Session " + session_id + " does not exist or can't be found.\n")
            #    log_file_catalog.write(session_id + ",,Not found\n")
            return scan_download_error.response
        else:
            print("Error code " + str(scan_download_error.response.status_code) + " when pulling scan list for session " + session_id + ".")
            #if create_logs:
            #    log_file.write("Error code " + str(scan_download_error.response.status_code) + " when pulling scan list for session " + session_id + ".\n")
            #    log_file_catalog.write(session_id + ",,Error code" + str(scan_download_error.response.status_code) + "\n")
            return scan_download_error.response
    else:
        #download_scans_from_list(folder_path, filename, response, 8192)
        return response


# Download scans to the destination based on whether we are downloading all scans or 
# whether a scan type list has been provided.
def download_requested_scans(session_id, destination):
    session_label = get_session_label(session_id)
    if session_label is not None:
        scans_list_response = pull_scans_list(session_id)
        if scans_list_response.status_code == 200:
            if download_all:
                download_one_scan(session_id, session_label, 'ALL', scans_list_response, destination)
            else:
                download_scans_from_list(session_id, session_label, scans_list_response, destination)
        else:
            print("Problem pulling scan list for Session ID " + session_id + ".")
    else:
        print("Problem pulling label for Session ID " + session_id + ".")


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
        if session_id_to_download is None and sessions_csv is not None:
            # open the csv file and go through it
            with open(sessions_csv, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')

                for row in csv_reader:
                    # get the row data
                    session_id = row[0]

                    if create_logs:
                        log_file.write("Getting started with session " + session_id + ".\n")

                    download_requested_scans(session_id, destination)

                    if create_logs:
                        log_file.write("Done with session " + session_id + ".\n")

        elif session_id_to_download is not None and sessions_csv is None:
            session_id = session_id_to_download

            if create_logs:
                log_file.write("Getting started with session " + session_id + ".\n")

            download_requested_scans(session_id, destination)

            if create_logs:
                log_file.write("Done with session " + session_id + ".\n")
        else:
            print("You must include either a csv of session ids to download, or specify a single session ID using the --id flag.")

        close_xnat_session()
        print("Download scans script is completed.")
        if create_logs:
            print('See download_scans_catalog_' + timestamp_log_base + '.csv for a list of the scans that were downloaded.')
    break