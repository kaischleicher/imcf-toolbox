#!/usr/bin/python

"""Calculate the closest neighbor to a given spot.

Takes two Excel XML files (generated by Bitplane Imaris) with results from the
spots detection, one file containing just a single spot, the other file
containing many spots. Calculates the spot from the second file with the
closest distance to the one from the first file.
"""

import argparse
import sys
import csv
from imaris_xml import ImarisXML
from volpy import dist_matrix, find_neighbor
from log import log
from misc import set_loglevel


def print_summary(edm, spots_c, spots_r, pair):
    """Print summary of results.

    Parameters
    ---------
    edm : the euclidean distance matrix
    spots_c : coordinate list of candidate spots
    spots_r : coordinate list of reference spots
    pair : (int, int)
        The index numbers of a "closest neighbours" pair.
    """
    id_r = pair[0]
    id_n = pair[1]
    log.warn('\nCalculating closest neighbour.')
    log.warn('Reference: \t\t[%s]\t%s' % (id_r, spots_r[id_r]))
    log.warn('Closest neighbour: \t[%s]\t%s' % (id_n, spots_c[id_n]))
    log.warn('Distance: %s' % edm[id_r, id_n + len(spots_r)])


def parse_arguments():
    """Parse the commandline arguments."""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-r', '--reference', required=True, type=file,
        help='Imaris Excel XML export containing reference spots.')
    argparser.add_argument('-c', '--candidate', required=True, type=file,
        help='Imaris Excel XML export containing candidate spots.')
    # argparser.add_argument('-o', '--outfile', default=sys.stdout,
        # type=argparse.FileType('w'), help='File to store the results.')
    argparser.add_argument('--csv', default=sys.stdout,
        type=argparse.FileType('w'), help='CSV-file to store the results.')
    argparser.add_argument('-v', '--verbosity', dest='verbosity',
        action='count', default=0)
    try:
        return argparser.parse_args()
    except IOError as err:
        argparser.error(str(err))


def parse_coordinates(xmlfile, desc):
    """Read the 'Position' sheet from the Imaris XML file.

    Returns
    -------
    coordinates : [(x, y, z)]
        List of 3-tuples of floats, representing the coordinates.
    """
    log.warn('Reading %s file: %s' % (desc, xmlfile.name))
    imsxml = ImarisXML(xmlfile)
    coordinates = imsxml.coordinates('Position')
    log.warn("- %s objects: %s" % (desc, len(coordinates)))
    return coordinates


def csv_write_distances(out_csv, edm, ref_id):
    """Write distances from a given reference id to a CSV file.

    Parameters
    ----------
    out_csv : filehandle
    edm : euclidean distance matrix
    ref_id : int
        The index number of the reference point in the edm.
    """
    dists_to_ref = edm[:][ref_id]
    # TODO: this should rather write only the distances of points from the
    # candidate list, excluding the ones from the reference list...
    log.info("Distances to reference:\n%s" % dists_to_ref)
    log.warn("Writing distances to '%s'..." % out_csv.name)
    csvout = csv.writer(out_csv)
    csvout.writerow(["Distances to reference spot %d" % ref_id])
    for i, line in enumerate(dists_to_ref):
        csvout.writerow([i, line])
    log.warn("Done.")


def closest_pairs(spots_r, spots_c):
    """Calculate the closest neighbours of given reference spots.

    Parameters
    ----------
    spots_r, spots_c : coordinate lists
        The coordinates (lists of 3-tuples of floats) of objects.

    Returns
    -------
    edm : euclidean distance matrix
    pairs : list((int, int))
        The list of pairs of closest neighbours (index numbers).
    """
    pairs = []
    dist_mat = dist_matrix(spots_r + spots_c)
    # create a mask to ignore the reference spots
    ref_mask = [1] * len(spots_r) + [0] * len(spots_c)
    for refid in range(len(spots_r)):
        # the result of find_neighbor() must be adjusted by the length of the
        # spots_r list to retrieve the index number for the spots_c list:
        nearest = find_neighbor(refid, dist_mat, ref_mask) - len(spots_r)
        pair = (refid, nearest)
        print_summary(dist_mat, spots_c, spots_r, pair)
        pairs.append(pair)
    return (dist_mat, pairs)


def main():
    """Parse the commandline and dispatch the calculations."""
    args = parse_arguments()
    set_loglevel(args.verbosity)
    spots_r = parse_coordinates(args.reference, 'reference')
    spots_c = parse_coordinates(args.candidate, 'candidate')
    (edm, pairs) = closest_pairs(spots_r, spots_c)
    if (args.csv.name != '<stdout>'):
        for pair in pairs:
            csv_write_distances(args.csv, edm, pair[0])

if __name__ == "__main__":
    sys.exit(main())
