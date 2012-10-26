#!/usr/bin/python

# TODO:
#  - do sanity checking
#  - evaluate datatypes from XML cells

import xml.etree.ElementTree as etree

class ImXMLError(Exception): pass

class ImarisXML:

    '''Parse Excel XML files into a python datastructure.
'''

    debug = 0
    tree = None
    # by default, we expect the namespace of Excel XML:
    namespace = 'urn:schemas-microsoft-com:office:spreadsheet'

    def __init__(self, xmlfile, ns='', debug=0):
        self.set_debug(debug)
        self.parse_xml(xmlfile)
        if ns: self.namespace = ns
        self.check_namespace()


    def set_debug(self, level):
        self.debug = level

    def parse_xml(self, infile):
        if self.debug:
            print "Processing file: " + infile
        self.tree = etree.parse(infile)
        if self.debug > 1: print "Done parsing XML: " + str(self.tree)

    def check_namespace(self):
        real_ns = self.tree.getroot().tag[1:].split("}")[0]
        if not real_ns == self.namespace:
            if self.debug:
                print "ERROR, couldn't find the expected XML namespace!"
                print "Namespace parsed from XML: '" + real_ns + "'"
            raise(ImXMLError)

    def worksheet(self, pattern):
        pattern = ".//{%s}Worksheet[@{%s}Name='%s']" % \
            (self.namespace, self.namespace, pattern)
        worksheet = self.tree.findall(pattern)
        if self.debug > 1: print "Found worksheet: " + str(worksheet)
        return(worksheet)

    def celldata(self, ws):
        cells = []
        rows = self.worksheet(ws)[0].findall('.//{%s}Row' % self.namespace)
        for row in rows:
            content = []
            # check if this is a header row:
            style_att = '{%s}StyleID' % self.namespace
            if style_att in row.attrib:
                # currently we don't process the header rows, so skip to the next
                continue
            if self.debug > 1: print str(len(row))
            for cell in row:
                content.append(cell[0].text)
            if self.debug > 1: print content
            cells.append(content)
        if self.debug: print cells
        # cells is now [ [r1c1, r1c2, r1c3, ...],
        #                [r2c1, r2c2, r2c3, ...],
        #                [r3c1, r3c2, r3c3, ...],
        #                ...                      ]
        # print "Parsed rows: " + str(len(cells))
        return(cells)

