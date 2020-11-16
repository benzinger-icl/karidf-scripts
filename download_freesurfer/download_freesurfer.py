#!/bin/env python


#================================================================
# Required python packages:
import sys, json, argparse, datetime, csv, os, base64, shutil, requests, time, urllib2, getpass, calendar
from urllib import urlretrieve
#================================================================


#================================================================
# Script: download_freesurfer.py
#
# Author: Sarah Keefe
# Date Updated: 1/30/2018
#
# Written using python version 2.7
#
# Purpose: Go through a CSV of FreeSurfer IDs and download all files for that Freesurfer one at a time.
#================================================================
#
#================================================================
# Usage:  
# python download_freesurfer.py <fs_ids.csv> <site> <destination_dir> -u <alias> -p <secret>
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
#
# If you include none of the above "--download-abc" flags, you can include one of the below flags to exclude snapshots or logs:
# --no-snaps to download no snapshots
# --no-logs to download no logs
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
# set default download destination
destination = "/data/nil-bluearc/benzinger2/Sarah/downloading/fs_download/download_test"

# parse arguments to the script
parser = argparse.ArgumentParser(description='Download all Freesurfer files for a given assessor ID.')
parser.add_argument('sessions_csv',help="csv filename containing a list of assessor numbers, with no header row")
parser.add_argument('site',help="Which site to download from, example https://cnda.wustl.edu (full site url)")
parser.add_argument('destination',help="Which folder to download to, example /data/nil-bluearc/etc/etc/etc")
parser.add_argument('-u', '--user',help="Site username/alias, from site/data/services/tokens/issue")
parser.add_argument('-p', '--password',help="Site password/secret, from site/data/services/tokens/issue")
#parser.add_argument('user',help="Site username/alias, from site/data/services/tokens/issue")
#parser.add_argument('password',help="Site password/secret, from site/data/services/tokens/issue")
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
parser.add_argument('--download-log',help="Download all log files, in both the LOG folder and DATA folder", action="store_true")
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
parser.add_argument('--no-snaps',help="When downloading the whole thing, don't download snapshots", action="store_true")
parser.add_argument('--no-logs',help="When downloading the whole thing, don't download logs", action="store_true")
args=parser.parse_args()

sessions_csv = args.sessions_csv
user = args.user
password = args.password
site = args.site
destination = args.destination
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
download_logs = args.download_log
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
no_snaps = args.no_snaps
no_logs = args.no_logs


download_all = False

# if no flags are set, download everything
if not download_annot and not download_area and not download_avg_curv and not download_bak and not download_cmd and not download_crv and not download_csurfdir and not download_ctab and not download_curv and not download_dat and not download_defect_borders and not download_defect_chull and not download_defect_labels and not download_done and not download_env and not download_H and not download_inflated and not download_jacobian_white and not download_K and not download_label and not download_local_copy and not download_logs and not download_lta and not download_m3z and not download_mgh and not download_mgz and not download_mid and not download_nofix and not download_old and not download_orig and not download_pial and not download_reg and not download_smoothwm and not download_sphere and not download_stats and not download_sulc and not download_thickness and not download_touch and not download_txt and not download_volume and not download_white and not download_xdebug_mris_calc and not download_xfm and not download_snaps:
	download_all = True

# get timestamp for log file
timestamp_log_base = str(calendar.timegm(datetime.datetime.now().timetuple()))

# create a log file to write to
log_file = open('download_fs_' + timestamp_log_base + '.log', 'w')
log_file_missing_fs = open('to_download_manually_fs_' + timestamp_log_base + '.log', 'w')
log_file_fails = open('to_download_manually_fs_files_' + timestamp_log_base + '.log', 'w')


def download_file(folder_path, filename, request_result, block_sz):
	# from https://stackoverflow.com/a/22776
	# download file in chunks in case it is too large
	f = open(os.path.join(folder_path, filename), 'wb')
	meta = request_result.info()
	file_size = int(meta.getheaders("Content-Length")[0])
#	print "Downloading: %s Bytes: %s" % (filename, file_size)

	file_size_dl = 0

	while True:
	    buffer = request_result.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)
	    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
	    status = status + chr(8)*(len(status)+1)
	    print status,

	f.close()


def check_download_file(filename, folder_name):
	filename_split = filename.split(".")

	if download_all:
		# download all if none of the specific download flags are specified
		return True
	elif download_logs and folder_name == "LOG":
		return True
	elif download_snaps and folder_name == "SNAPSHOTS":
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'annot' and download_annot:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'area' and download_area:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'avg_curv' and download_avg_curv:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'bak' and download_bak:
		return True				
	elif len(filename_split) > 1 and filename_split[-1] == 'cmd' and download_cmd:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'crv' and download_crv:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'csurfdir' and download_csurfdir:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'ctab' and download_ctab:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'curv' and download_curv:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'dat' and download_dat:
		return True				
	elif len(filename_split) > 1 and filename_split[-1] == 'defect_borders' and download_defect_borders:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'defect_chull' and download_defect_chull:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'defect_labels' and download_defect_labels:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'env' and download_env:
		return True							
	elif len(filename_split) > 1 and filename_split[-1] == 'H' and download_H:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'inflated' and download_inflated:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'jacobian_white' and download_jacobian_white:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'K' and download_K:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'label' and download_label:
		return True							
	elif len(filename_split) > 1 and filename_split[-1] == 'local-copy' and download_local_copy:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'log' and download_logs:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'lta' and download_lta:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'm3z' and download_m3z:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'mgh' and download_mgh:
		return True							
	elif len(filename_split) > 1 and filename_split[-1] == 'mgz' and download_mgz:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'mid' and download_mid:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'nofix' and download_nofix:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'old' and download_old:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'orig' and download_orig:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'pial' and download_pial:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'reg' and download_reg:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'smoothwm' and download_smoothwm:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'sphere' and download_sphere:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'stats' and download_stats:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'sulc' and download_sulc:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'thickness' and download_thickness:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'touch' and download_touch:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'txt' and download_txt:
		return True
	elif len(filename_split) > 1 and filename_split[-1] == 'volume' and download_volume:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'white' and download_white:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'xdebug_mris_calc' and download_xdebug_mris_calc:
		return True	
	elif len(filename_split) > 1 and filename_split[-1] == 'xfm' and download_xfm:
		return True																					
	else:
		return False

def download_folder(experiment_id, assessor_id, folder_name):

	# for urllib2 if we can't use requests
	apiConfig = {
		"headers" : {
			"Content-Type": "application/json",
			"Authorization": "Basic " + base64.encodestring(user+":"+password).replace('\n', '')
		},
		"url": ''}

	# log that we are checking for the session
	print "Checking for session " + assessor_id + " folder " + folder_name + "."
	log_file.write("Checking for session " + assessor_id + " folder " + folder_name + ".\n")

	# Download all files for this folder
	files_url = site + '/data/experiments/' + experiment_id + '/assessors/' + assessor_id + '/resources/' + folder_name + '/files?format=json'
	print assessor_id + ": Checking files URL: " + files_url
	log_file.write(assessor_id + ": Checking files URL:  " + files_url + "\n")

	# perform request with urllib2
	data = None
	request = urllib2.Request(files_url, data, apiConfig["headers"])

	print "Files URL: " + files_url
	try:
		result = urllib2.urlopen(request)			
	except urllib2.HTTPError as err:
		if err.getcode() == 404:
			# No session found with this id
			print "FS " + assessor_id + " does not exist or can't be found."
			log_file.write("FS " + assessor_id + " does not exist or can't be found.\n")
			log_file_missing_fs.write(assessor_id + "\n")
		else:
			print "Error code " + str(err.getcode()) + " when searching for FS " + assessor_id + "."
			log_file.write("Error code " + str(err.getcode()) + " when searching for FS" + assessor_id + ".\n")
			log_file_missing_fs.write(assessor_id + "\n")

	else:

		json_result = json.loads(result.read())

		for file in json_result['ResultSet']['Result']:

			folder_path = os.path.join(destination, assessor_id, folder_name)
			# Make the main dir if it doesn't exist yet
			if not os.path.exists(folder_path):
				os.makedirs(folder_path)

			filename = file['Name']
			file_download_url = site + file['URI']

			print "found file: " + filename

			download_file_check = check_download_file(filename, folder_name)

			if download_file_check:

				print assessor_id + ": Going to download file " + filename + "."
				log_file.write(assessor_id + ": Going to download file " + filename + ". \n")

				# get the subfolder from the file URI
				split_url = file_download_url.split("/")
				subfolder_name = split_url[-2]
				presubfolder_name = split_url[-3]

				if subfolder_name in ["atlas", "label", "mri", "scripts", "stats", "surf", "touch", "tmp"]:
					folder_path = os.path.join(destination, assessor_id, folder_name, subfolder_name)
					# Make the subfolder dir if it doesn't exist yet
					if not os.path.exists(folder_path):
						os.makedirs(folder_path)

				if presubfolder_name in ["atlas", "label", "mri", "scripts", "stats", "surf", "touch", "tmp"]:
					folder_path = os.path.join(destination, assessor_id, folder_name, presubfolder_name, subfolder_name)
					# Make the subfolder dir if it doesn't exist yet
					if not os.path.exists(folder_path):
						os.makedirs(folder_path)



				# perform request with urllib2
				data = None
				request = urllib2.Request(file_download_url, data, apiConfig["headers"])

				print "File download URL: " + file_download_url
				try:
					result = urllib2.urlopen(request)			
				except urllib2.HTTPError as err:
					if err.getcode() == 404:
						# No session found with this id
						print "File " + filename + " in FS " + assessor_id + " does not exist or can't be found."
						log_file.write("File " + filename + " in FS " + assessor_id + " does not exist or can't be found.\n")
						log_file_fails.write(assessor_id + ", " + filename + "\n")
					else:
						print "Error code " + str(err.getcode()) + " when searching for FS file " + filename + "."
						log_file.write("Error code " + str(err.getcode()) + " when searching for FS file " + filename + ".\n")
						log_file_fails.write(assessor_id + ", " + filename + "\n")

				else:
					time.sleep(1)
					download_file(folder_path, filename, result, 8192)

					print assessor_id + ": Got file " + filename + "."
					log_file.write(assessor_id + ": Got file " + filename + ".\n")

			else:
				print assessor_id + ": Skipping file " + filename + "."
				log_file.write(assessor_id + ": Skipping file " + filename + ". \n")


# start the main thing

# write a date/time row to the log because why not
print "Script started at " + str(datetime.datetime.now())
log_file.write("Script started at " + str(datetime.datetime.now()) + "\n")


if user is None or password is None:
	user = raw_input("Enter your username for "  + site + ": ")
	password = getpass.getpass("Enter your password for "  + site + ": ")


# open the csv file and go through it
with open(sessions_csv, 'rb') as csvfile:
	csv_reader = csv.reader(csvfile, delimiter=',')

	for row in csv_reader:
		# get the row data
		assessor_id = row[0]

		# split up the FS ID to get the MR session accession number (experiment_id)
		experiment_id_arr = assessor_id.split("_freesurfer_")

		experiment_id = experiment_id_arr[0]

		print assessor_id + ": Got experiment ID: " + experiment_id + "."
		log_file.write(assessor_id + ": Got experiment ID: " + experiment_id + ". \n")

		# download each folder
		# send it the log files too
		if download_snaps or (download_all and not no_snaps):
			download_folder(experiment_id, assessor_id, "SNAPSHOTS")

		if download_logs or (download_all and not no_logs):
			download_folder(experiment_id, assessor_id, "LOG")

		if download_all or download_annot or download_area or download_avg_curv or download_bak or download_cmd or download_crv or download_csurfdir or download_ctab or download_curv or download_dat or download_defect_borders or download_defect_chull or download_defect_labels or download_done or download_env or download_H or download_inflated or download_jacobian_white or download_K or download_label or download_local_copy or download_logs or download_lta or download_m3z or download_mgh or download_mgz or download_mid or download_nofix or download_old or download_orig or download_pial or download_reg or download_smoothwm or download_sphere or download_stats or download_sulc or download_thickness or download_touch or download_txt or download_volume or download_white or download_xdebug_mris_calc or download_xfm:
			download_folder(experiment_id, assessor_id, "DATA")