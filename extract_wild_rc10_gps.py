#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract GPS coordinates from ARSF Wild RC-10 TIFF images using exiftool
and save to CSV.

Requires exiftool to be installed from http://www.sno.phy.queensu.ca/~phil/exiftool/

Known Issues:

For some projects in 2007 the latitude wasn't saved and the tool won't work.

Author: Dan Clewley, NERC-ARF-DAN
Creation Date: 06/09/2016

"""
##################################################################
# This file has been created by NERC-ARF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
##################################################################

from __future__ import print_function
import argparse
import csv
import glob
import os
import subprocess
import sys

def get_exif_info_from_image(image_file):
   """
   Reads exif info from image using exiftool
   and returns as dictionary.
   """
   exif_info_str = subprocess.check_output(["exiftool", image_file])
   exif_info_list = exif_info_str.decode().split("\n")

   exif_info = {}

   for item in exif_info_list:
      if item.count(":") == 1:
         key, par = item.split(":")
         exif_info[key.strip().lower()] = par.strip()
      elif item.count(":") > 1:
         elements = item.split(",")
         for sub_item in elements:
            key, par = sub_item.split(":", 1)
            exif_info[key.strip().lower()] = par.strip()

   return exif_info

def parse_gps_pos_str(gps_pos_str):
   """
   Parses a D M S formatted GPS string and returns decimal degrees

   Example input format:

   52 22 49.30
   """
   gps_pos_items = gps_pos_str.split(" ")

   deg = abs(float(gps_pos_items[0]))
   minutes = float(gps_pos_items[1])
   seconds = float(gps_pos_items[2])

   decimal_deg = deg + (minutes / 60.0) + (seconds / 3600)

   if gps_pos_items[0][0] == "-":
      decimal_deg = -1.0 * decimal_deg

   return decimal_deg

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Extract location from exif "
                                                "tags of scanned ARSF Wild RC-10"
                                                " images to CSV file")
   parser.add_argument("inputimages", nargs="*",type=str, help="Input images")
   parser.add_argument("-o", "--out_csv",
                       type=str, required=True,
                       help="Output CSV")
   args=parser.parse_args()

   # On Windows don't have shell expansion so fake it using glob
   if args.inputimages[0].find('*') > -1:
      args.inputimages = glob.glob(args.inputimages[0])

   f = open(args.out_csv, "w")

   out_csv_writer = csv.writer(f)
   out_csv_writer.writerow(["ImageName","Date", "Time",
                            "Latitude", "Longitude",
                            "Altitude"])

   for i, image in enumerate(args.inputimages):
      print("[{0}/{1}] {2}".format(i, len(args.inputimages),
                                  os.path.basename(image)))
      try:
         exif_info = get_exif_info_from_image(image)

         out_row = [os.path.basename(image),
                    exif_info["date"],
                    exif_info["gps time"].replace(" ",""),
                    parse_gps_pos_str(exif_info["local latitude"]),
                    parse_gps_pos_str(exif_info["local longitude"]),
                    exif_info["gps height"]]

         out_csv_writer.writerow(out_row)
      except Exception as err:
         print(" Failed to get tags from {}\n{}".format(image, err),
               file=sys.stderr)

   f.close()
