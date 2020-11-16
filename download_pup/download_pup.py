#!/bin/env python

#================================================================
# Required python packages:
import argparse, calendar, csv, datetime, getpass, os, time, requests
#================================================================
#
#================================================================
# Script: download_pup.py
#
# Author: Sarah Keefe
# Contributors: Austin McCullough, Rick Herrick
# Date Updated: 2/18/2019
#
# Written using python version 2.7
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
# -c filename.csv or --
# -csv filename.csv to read from a CSV of PUP IDs with no header row (specify filename.csv)
# -i pup_id or --id pup_id to download for a single PUP ID (specify pup_id)
#
# Output:
# Organizes the files into the following folder structure: 
# ${pup_id}/DATA
# ${pup_id}/SNAPSHOTS
# ${pup_id}/LOG
#
# If the --create-logs flag is included:
# Creates a log file at `download_pup.log` - contains all output from the script.
# Creates a log file at `to_download_manually_pup.log` - contains a list of all PUP IDs that could not be found.
# Creates a log file at `to_download_manually_pup_files.log` - contains a list of all files that could not be downloaded 
# and their PUP IDs (in the format pup_id, filename).
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
parser.add_argument('destination', help="Which folder to download to, example /data/nil-bluearc/etc/etc/etc",
                    default="/data/nil-bluearc/benzinger2/Sarah/downloading/dca_pup/download_test")
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
    log_file_missing_pups = open('to_download_manually_pup_' + timestamp_log_base + '.log', 'w')
    log_file_fails = open('to_download_manually_pup_files_' + timestamp_log_base + '.log', 'w')
else:
    log_file = None
    log_file_missing_pups = None
    log_file_fails = None

session = requests.Session()
credentials = (user, password)
headers = {"Content-Type": "application/json"}
parameters = {"format": "json"}
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


def check_download_file(filename, folder_name):
    filename_split = filename.split(".")
    print(filename_split[0])
    if download_all:
        # download all if none of the specific download flags are specified
        return True
    elif download_logs and folder_name == "LOG":
        return True
    elif download_snaps and folder_name == "SNAPSHOTS":
        return True
    elif len(filename_split) > 1 and '4dfp' in filename_split[1] and download_4dfp:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'dat' and download_dat:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'info' and download_info:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'log' and download_logs:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'lst' and download_lst:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'mgz' and download_mgz:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'moco' and download_moco:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'nii' and download_nii:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'params' and download_params:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'sub' and download_sub:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'suvr' and download_suvr:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'tac' and download_tac:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'tb' and download_tb:
        return True
    elif len(filename_split) > 1 and filename_split[1] == 'txt' and download_txt:
        return True
    elif len(filename_split) == 1 and download_no_ext:
        return True
    elif len(filename_split) > 1 and 'SUVR' in filename_split[0] and '4dfp' in filename_split[1] and download_SUVR4dfp:
        return True
    elif len(filename_split) > 1 and filename_split[0] == 'T1001' and '4dfp' in filename_split[1] and \
            download_T10014dfp:
        return True
    elif len(filename_split) > 1 and filename_split[0] == 'petfov' and '4dfp' in filename_split[1] and download_PETFOV:
        return True
    elif len(filename_split) > 1 and filename_split[0] == 'RSFMask' and '4dfp' in filename_split[1] and \
            download_RSFMask:
        return True
    elif len(filename_split) > 1 and ('wmparc' in filename_split[0]) and download_wmparc:
        return True
    else:
        return False


def download_folder(dl_expt, dl_assessor, folder_name):
    # log that we are checking for the session
    print("Checking for session " + dl_assessor + " folder " + folder_name + ".")
    if create_logs:
        log_file.write("Checking for session " + dl_assessor + " folder " + folder_name + ".\n")

    # Download all files for this folder
    files_url = site + '/data/experiments/' + dl_expt + '/assessors/' + dl_assessor + '/resources/' + folder_name + \
                       '/files'
    print(dl_assessor + ": Checking files URL: " + files_url)
    if create_logs:
        log_file.write(dl_assessor + ": Checking files URL:  " + files_url + "\n")

    print("Files URL: " + files_url)
    try:
        response = session.get(files_url, params=parameters, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as files_download_error:
        if files_download_error == 404:
            # No session found with this id
            print("PUP " + dl_assessor + " does not exist or can't be found.")
            if create_logs:
                log_file.write("PUP " + dl_assessor + " does not exist or can't be found.\n")
                log_file_missing_pups.write(dl_assessor + "\n")
        else:
            print("Error code " + str(files_download_error) + " when searching for PUP " + dl_assessor + ".")
            if create_logs:
                log_file.write("Error code " + str(files_download_error) + " when searching for PUP" + dl_assessor +
                               ".\n")
                log_file_missing_pups.write(dl_assessor + "\n")
    else:
        json_result = response.json()

        folder_path = os.path.join(destination, dl_assessor, folder_name)

        # Make the DATA dir if it doesn't exist yet
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for file_data in json_result['ResultSet']['Result']:
            filename = file_data['Name']
            file_download_url = site + file_data['URI']

            print("found file: " + filename)

            download_file_check = check_download_file(filename, folder_name)

            if download_file_check:

                print(dl_assessor + ": Going to download file " + filename + ".")
                if create_logs:
                    log_file.write(dl_assessor + ": Going to download file " + filename + ". \n")

                # perform request with urllib2
                print("File download URL: " + file_download_url)
                try:
                    response = session.get(file_download_url, params=parameters, headers=headers)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as files_download_error:
                    if files_download_error == 404:
                        # No session found with this id
                        print("File " + filename + " in PUP " + dl_assessor + " does not exist or can't be found.")
                        if create_logs:
                            log_file.write(
                                "File " + filename + " in PUP " + dl_assessor + " does not exist or can't be found.\n")
                            log_file_fails.write(dl_assessor + ", " + filename + "\n")
                    else:
                        print("Error code " + str(files_download_error) + " when searching for PUP file " + filename +
                              ".")
                        if create_logs:
                            log_file.write(
                                "Error code " + str(files_download_error) + " when searching for PUP file " + filename +
                                ".\n")
                            log_file_fails.write(dl_assessor + ", " + filename + "\n")

                else:
                    time.sleep(1)
                    download_file(folder_path, filename, response, 8192)

                    print(dl_assessor + ": Got file " + filename + ".")
                    if create_logs:
                        log_file.write(dl_assessor + ": Got file " + filename + ".\n")                      

            else:
                print(dl_assessor + ": Skipping file " + filename + ".")
                if create_logs:
                    log_file.write(dl_assessor + ": Skipping file " + filename + ". \n")


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
                    # get the row data
                    assessor_id = row[0]

                    # split up the PUP ID to get the PET accession number (experiment_id)
                    experiment_id_arr = assessor_id.split("_PUPTIMECOURSE_")

                    experiment_id = experiment_id_arr[0]

                    print(assessor_id + ": Got experiment ID: " + experiment_id + ".")
                    if create_logs:
                        log_file.write(assessor_id + ": Got experiment ID: " + experiment_id + ". \n")

                    # download each folder
                    # send it the log files too
                    if download_snaps or download_all:
                        download_folder(experiment_id, assessor_id, "SNAPSHOTS")

                    if download_logs or download_all:
                        download_folder(experiment_id, assessor_id, "LOG")

                    if download_all or download_4dfp or download_dat or download_info or download_logs or download_lst \
                            or download_mgz or download_moco or download_nii or download_params or download_sub or \
                            download_suvr or download_tac or download_tb or download_txt or download_SUVR4dfp or \
                            download_T10014dfp or download_PETFOV or download_RSFMask or download_no_ext or download_wmparc:
                        download_folder(experiment_id, assessor_id, "DATA")
        elif pup_id_to_download is not None and sessions_csv is None:
            assessor_id = pup_id_to_download

            # split up the PUP ID to get the PET accession number (experiment_id)
            experiment_id_arr = assessor_id.split("_PUPTIMECOURSE_")

            experiment_id = experiment_id_arr[0]

            print(assessor_id + ": Got experiment ID: " + experiment_id + ".")
            if create_logs:
                log_file.write(assessor_id + ": Got experiment ID: " + experiment_id + ". \n")

            # download each folder
            # send it the log files too
            if download_snaps or download_all:
                download_folder(experiment_id, assessor_id, "SNAPSHOTS")

            if download_logs or download_all:
                download_folder(experiment_id, assessor_id, "LOG")

            if download_all or download_4dfp or download_dat or download_info or download_logs or download_lst or \
                    download_mgz or download_moco or download_nii or download_params or download_sub or download_suvr \
                    or download_tac or download_tb or download_txt or download_SUVR4dfp or download_T10014dfp or \
                    download_PETFOV or download_RSFMask or download_no_ext or download_wmparc:
                download_folder(experiment_id, assessor_id, "DATA")
        else:
            print(
                "You must include either a csv of PUP ids to download, or specify a single PUP ID using the --id flag.")

        close_xnat_session()
    break