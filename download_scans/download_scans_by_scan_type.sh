#!/bin/sh
#
#================================================================
# Title: download_scans_by_scan_type.sh
#
# Last Updated: 7/15/2019
# Author: Sarah Keefe
#
# Purpose: Download scans of a specified type/name from an XNAT site based on an input "scan type" list
#================================================================
#
#================================================================
# Usage: 
# ./download_scans_by_scan_type.sh <input_file.csv> <scan_type_list.csv> <directory_name> <xnat_username> <site>
#================================================================
#
#================================================================
# Required inputs:
# <input_file.csv> - A Unix formatted, comma-separated file containing the following columns:
#       Experiment ID
# <scan_type_list.csv> - A csv with each row containing one scan type you want to download.
# <directory_name> - A directory path (relative or absolute) to save the scan files to
# <xnat_username> - Your username used for accessing data on the given site
#       (you will be prompted for your password before downloading)
# <site> - the full path to the xnat site you are using, ie. https://cnda.wustl.edu
#
# Output:
# This script organizes the files into folders like this:
# ${DIRNAME}/${EXPERIMENT_LABEL}/2-Axial_FLAIR/DICOM
#
# downloading_log_XXX.log file contains the list of scans downloaded.
#================================================================


# Start of script
#================================================================
# Authenticates credentials against XNAT and returns the cookie jar file name. USERNAME and
# PASSWORD must be set before calling this function.
#   USERNAME="foo"
#   PASSWORD="bar"
#   COOKIE_JAR=$(startSession)
startSession() {
    # Authentication to XNAT and store cookies in cookie jar file
    local COOKIE_JAR=.cookies-$(date +%Y%M%d%s).txt
    curl -k -s -u ${USERNAME}:${PASSWORD} --cookie-jar ${COOKIE_JAR} "${SITE}/data/JSESSION" > /dev/null
    echo ${COOKIE_JAR}
}

# Downloads a resource from a URL and stores the results to the specified path. The first parameter
# should be the destination path and the second parameter should be the URL.
download() {
    local OUTPUT=${1}
    local URL=${2}
    curl -H 'Expect:' --keepalive-time 2 -k --cookie ${COOKIE_JAR} -o ${OUTPUT} ${URL}
}

# Gets a resource from a URL.
get() {
    local URL=${1}
    curl -H 'Expect:' --keepalive-time 2 -k --cookie ${COOKIE_JAR} ${URL}
}

# Ends the user session.
endSession() {
    # Delete the JSESSION token - "log out"
    curl -i -k --cookie ${COOKIE_JAR} -X DELETE "${SITE}/data/JSESSION"
    rm -f ${COOKIE_JAR}
}


# usage instructions
if [ ${#@} == 0 ]; then
    echo ""
    echo "XNAT scan download script - download based on a list of scan types"
    echo ""
    echo "This script downloads scans of specified types from a specified XNAT site, "
    echo "based on a list of session IDs in a csv file and a provided list of scan types. "
    echo ""   
    echo "Usage: $0 input_file.csv scan_type_list.csv directory_name xnat_username https://xnat.site"
    echo "<input_file>: A Unix formatted, comma separated file containing the following columns:"
    echo "    experiment_ID (e.g. CNDA_E01234567)"
    echo "<scan_type_list>: A Unix formatted, comma separated file containing the following columns:"
    echo "    scan_type (may contain spaces but not commas)"    
    echo "<directory_name>: Directory path to save scan files to"  
    echo "<xnat_username>: Your username used for accessing the requested XNAT site (you will be prompted for your password)"   
    echo "<site>: The url of the site you want to download from (e.g. https://cnda.wustl.edu)"   
else 

    # Get the input arguments
    INFILE=$1
    SCAN_TYPE_FILE=$2
    DIRNAME=$3
    USERNAME=$4
    SITE=$5

    # Create the directory if it doesn't exist yet
    if [ ! -d $DIRNAME ]
    then
        mkdir -p $DIRNAME
    fi

    LOGFILE=downloading_log_$(date +%Y%M%d%s).log
    touch ${LOGFILE}
    echo "experiment_id,experiment_label,scan_id,scan_type" >> ${LOGFILE}

    # Read in password
    read -s -p "Enter your password for accessing data on ${SITE}:" PASSWORD

    echo ""

    COOKIE_JAR=$(startSession)

    # Read the file
    cat $INFILE | while IFS=, read -r EXPERIMENT_ID; do

        echo "Getting label information for ${EXPERIMENT_ID}."

        EXPERIMENT_INFO_URL="${SITE}/data/archive/experiments?ID=${EXPERIMENT_ID}&columns=label&format=csv"

        EXPERIMENT_INFO_CSV_OUTPUT=$(get ${EXPERIMENT_INFO_URL})

        EXPERIMENT_INFO_NOHEADER=$(echo -e "$EXPERIMENT_INFO_CSV_OUTPUT" | sed -n '2p')

        EXPERIMENT_LABEL=`echo $EXPERIMENT_INFO_NOHEADER | cut -d, -f2` 

        echo "The experiment label for ${EXPERIMENT_ID} is ${EXPERIMENT_LABEL}."

        echo "Downloading specified scans for ${EXPERIMENT_LABEL}."        

        # Set up the download URL and make a cURL call to download the requested scans in tar.gz format
        SCAN_INFO_URL=${SITE}/data/archive/experiments/${EXPERIMENT_ID}/scans?format=csv

        echo "Checking scan info url: ${SCAN_INFO_URL}"

        SCANS_FROM_SESSION_CSV_OUTPUT=$(get $SCAN_INFO_URL)

        echo -e "$SCANS_FROM_SESSION_CSV_OUTPUT" | while read -r line; do
            # get scan info
            echo "Found a scan. Checking if the scan type is in the provided list."            

            SCAN_TYPE=`echo $line | cut -d, -f3`
            SCAN_ID=`echo $line | cut -d, -f2`
            SCAN_URI=`echo $line | cut -d, -f8`

            { cat $SCAN_TYPE_FILE; echo; } | while IFS=, read -r SCAN_TYPE_REQUESTED; do

                if [ "${SCAN_TYPE}" = "${SCAN_TYPE_REQUESTED}" ]; then

                    echo "Found a scan of type ${SCAN_TYPE_REQUESTED}. Downloading it."

                    SCAN_DOWNLOAD_URL="${SITE}/data/archive/experiments/${EXPERIMENT_ID}/scans/${SCAN_ID}/files?format=zip"

                    echo "Downloading from scan download url: ${SCAN_DOWNLOAD_URL}"

                    download ${DIRNAME}/${SCAN_ID}.zip ${SCAN_DOWNLOAD_URL}

                    if zip -Tq $DIRNAME/${SCAN_ID}.zip > /dev/null; then
                        unzip $DIRNAME/${SCAN_ID}.zip -d $DIRNAME

                        # sends files to ${DIRNAME}/${EXPERIMENT_LABEL}/scans/2-Axial_FLAIR/resources/DICOM/files/*
                        # Move them up to ${DIRNAME}/${EXPERIMENT_LABEL}/scans/2-Axial_FLAIR/resources/DICOM
                        for resource_foldername in ${DIRNAME}/${EXPERIMENT_LABEL}/scans/*/resources/*; do
                            mv $resource_foldername/files/* $resource_foldername/.
                            rm -r $resource_foldername/files
                        done

                        # Now they are in ${DIRNAME}/${EXPERIMENT_LABEL}/scans/2-Axial_FLAIR/resources/DICOM
                        # Move them up to ${DIRNAME}/${EXPERIMENT_LABEL}/scans/2-Axial_FLAIR/DICOM
                        for scan_foldername in ${DIRNAME}/${EXPERIMENT_LABEL}/scans/*; do
                            mv $scan_foldername/resources/* $scan_foldername/.
                            rm -r $scan_foldername/resources
                        done                        

                        # Now they are in ${DIRNAME}/${EXPERIMENT_LABEL}/scans/2-Axial_FLAIR/DICOM
                        # Move them up to ${DIRNAME}/${EXPERIMENT_LABEL}/2-Axial_FLAIR/DICOM
                        mv ${DIRNAME}/${EXPERIMENT_LABEL}/scans/* ${DIRNAME}/${EXPERIMENT_LABEL}/.
                        rm -r ${DIRNAME}/${EXPERIMENT_LABEL}/scans                 

                        # Change permissions on the output files
                        chmod -R u=rwX,g=rwX $DIRNAME/$EXPERIMENT_LABEL/*

                        # Remove the scan zip file
                        rm -r ${DIRNAME}/${SCAN_ID}.zip
                        echo "${EXPERIMENT_ID},${EXPERIMENT_LABEL},${SCAN_ID},${SCAN_TYPE}" >> ${LOGFILE}                    
                    else
                        echo "There was a problem downloading the scan type ${SCAN_TYPE} for ${EXPERIMENT_LABEL}"                  
                    fi
                fi
            done

        done

        echo "Done with ${EXPERIMENT_ID}."

    done < $INFILE

    endSession

fi