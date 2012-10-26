#!/usr/bin/python

"""Calculate the closest neighbor to a given spot.

Takes two Excel XML files (generated by Bitplane Imaris) with results
from the spots detection, one file containing just a single spot, the
other file containing many spots. Calculates the spot from the second
file with the closest distance to the one from the first file.
"""

import argparse
import sys
from ImsXMLlib import ImarisXML
from dist_tools import dist_matrix_euclidean, find_neighbor
from imaris_xml import IMS_extract_coords


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-r', '--reference', required=True, type=file,
        help='Imaris Excel XML export containing reference spots.')
    argparser.add_argument('-c', '--candidate', required=True, type=file,
        help='Imaris Excel XML export containing candidate spots.')
    try:
        args = argparser.parse_args()
    except IOError as e:
        argparser.error(str(e))

    print 'Processing file: ' + args.reference.name
    XMLref = ImarisXML(args.reference)
    print 'Processing file: ' + args.candidate.name
    XMLcnd = ImarisXML(args.candidate)

    refs = XMLref.celldata('Position')
    cand = XMLcnd.celldata('Position')

    # ref_spots are taken as the base to find the closest ones
    # in the set of cand_spots
    ref_spots = IMS_extract_coords(refs)
    cand_spots = IMS_extract_coords(cand)
    dist_mat = dist_matrix_euclidean(ref_spots + cand_spots)

    ref_mask = [1] * len(ref_spots) + [0] * len(cand_spots)

    for refid, refspot in enumerate(ref_spots):
        print
        print 'Calculating closest neighbour.'
        print 'Original spot:  [' + str(refid) + ']', refspot
        nearest = find_neighbor(refid, dist_mat, ref_mask)
        print "Neighbour spot: [" + str(nearest - len(ref_spots)) + ']', \
            cand_spots[nearest - len(ref_spots)]
        print "Distance:", dist_mat[refid, nearest]
    return(0)

# see http://www.artima.com/weblogs/viewpost.jsp?thread=4829
# for this nice way to handle the sys.exit()/return() calls
if __name__ == "__main__":
    sys.exit(main())
