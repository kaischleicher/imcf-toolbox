#!/usr/bin/python

"""
Process results of WingJ [1] with Imaris objects (exported from the statistics
part to XML) or ImageJ measurement results to do distance calculations.

Takes a WingJStructure object plus a file with coordinates of points (can be
either an XML file generated with Imaris containing a "Position" sheet or a
CSV file generated by ImageJ containing "center of mass" coordinates) and
calculates the closest distance from any point to each of the WingJ
structures.

[1] http://www.tschaffter.ch/
"""

from volpy.imagej import read_csv_com, WingJStructure
from log import log
import misc
import imaris_xml as ix
import sys
import argparse


def parse_arguments():
    """Parse commandline arguments."""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('--ap', required=True, type=file,
        help='WingJ structure file for the A-P separation.')
    argparser.add_argument('--vd', required=True, type=file,
        help='WingJ structure file for the V-D separation.')
    argparser.add_argument('--cnt', required=True, type=file,
        help='WingJ structure file for the contour line.')
    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument('--imsxml', type=file, default=None,
        help='Imaris Excel XML export containing a "Position" sheet.')
    group.add_argument('--ijroi', type=file, default=None,
        help='ImageJ CSV export having "center of mass" measurements.')
    argparser.add_argument('--apout', type=argparse.FileType('w'),
        required=True, help='Output CSV file for distances to A-P line.')
    argparser.add_argument('--vdout', type=argparse.FileType('w'),
        required=True, help='Output CSV file for distances to V-D line.')
    argparser.add_argument('--cntout', type=argparse.FileType('w'),
        required=True, help='Output CSV file for distances to contour line.')
    argparser.add_argument('-p', '--pixelsize', required=False, type=float,
        default=1.0, help='Pixel size to calibrate WingJ data.')
    argparser.add_argument('-v', '--verbosity', dest='verbosity',
        action='count', default=0)
    try:
        args = argparser.parse_args()
    except IOError as err:
        argparser.error(str(err))
    return args


def main():
    """Parse commandline arguments and run distance calculations."""
    args = parse_arguments()
    misc.set_loglevel(args.verbosity)
    log.warn('Calculating distances to WingJ structures...')

    if args.imsxml is not None:
        coords = ix.ImarisXML(args.imsxml).coordinates_2d('Position')
    elif args.ijroi is not None:
        coords = read_csv_com(args.ijroi)
        coords *= args.pixelsize
    else:
        # this shouldn't happen with argparse, but you never know...
        raise AttributeError('no reference file given!')

    wingj = WingJStructure((args.ap, args.vd, args.cnt), args.pixelsize)
    wingj.min_dist_csv_export(coords, (args.apout, args.vdout, args.cntout))

    log.warn('Finished.')


if __name__ == "__main__":
    sys.exit(main())
