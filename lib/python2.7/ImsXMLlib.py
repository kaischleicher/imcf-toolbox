"""Handle XML files generated by Bitplane Imaris."""

# TODO:
#  - do sanity checking
#  - evaluate datatypes from XML cells

import xml.etree.ElementTree as etree
from log import log
from aux import filename


class ImsXMLError(Exception):
    pass


class ImarisXML(object):

    """
    An XML parser to handle Excel-style XML files generated by Imaris.

    Example
    -------
    >>> import ImsXMLlib
    >>> fh = open('/path/to/file.xml', 'r')
    >>> xmldata = ImsXMLlib.ImarisXML(fh)
    >>> positions = xmldata.celldata('Position')
    """

    def __init__(self, xmlfile, ns=''):
        """Create a new Imaris-XML object from a file.

        Parameters
        ----------
        xmlfile : file or str
            A filehandle or string for the XML file to parse.
        ns : string, optional
            A string denoting the namespace expected in the XML file,
            defaults to the one used by MS Excel in its XML format.
        """
        self.tree = None
        self.cells = {}
        # by default, we expect the namespace of Excel XML:
        self.namespace = 'urn:schemas-microsoft-com:office:spreadsheet'
        if ns:
            self.namespace = ns
        log.info("Parsing XML file: %s" % filename(xmlfile))
        self.tree = etree.parse(xmlfile)
        log.info("Done parsing XML: %s" % self.tree)
        self._check_namespace()

    def _check_namespace(self):
        """Check if an XML tree has a certain namespace.

        Takes an XML etree object and a string denoting the expected
        namespace, checks if the namespace of the XML tree matches.
        Returns the namespace if yes, exits otherwise.
        """
        real_ns = self.tree.getroot().tag[1:].split("}")[0]
        if not real_ns == self.namespace:
            log.critical("ERROR, couldn't find the expected XML namespace!")
            log.critical("Namespace parsed from XML: '%s'" % real_ns)
            raise(ImsXMLError)

    def _worksheet(self, pattern):
        """Look up a certain worksheet in the Excel XML tree.

        Parameters
        ----------
        pattern : string
            The name of the desired worksheet.

        Returns
        -------
        worksheet : etree element
            The XML subtree pointing to the desired worksheet.
        """
        pattern = ".//{%s}Worksheet[@{%s}Name='%s']" % \
            (self.namespace, self.namespace, pattern)
        # we ignore broken files that contain multiple worksheets having
        # identical names and just return the first one (should be safe):
        worksheet = self.tree.findall(pattern)[0]
        # TODO: error handling (worksheet not found, ...)!!!
        log.info("Found worksheet: %s" % worksheet)
        return(worksheet)

    def _parse_cells(self, ws):
        """Parse the cell-contents of a worksheet into a 2D array.

        After parsing the contents, they are added to the global
        map 'cells' using the worksheet name as the key.

        Parameters
        ----------
        ws : string
            The name of the worksheet to process.
        """
        rows = self._worksheet(ws).findall('.//{%s}Row' % self.namespace)
        cells = []
        for row in rows:
            content = []
            # check if this is a header row:
            style_att = '{%s}StyleID' % self.namespace
            if style_att in row.attrib:
                # we don't process the header row, so skip it
                continue
            for cell in row:
                content.append(cell[0].text)
            log.debug('length of row: %i' % len(row))
            log.debug(content)
            cells.append(content)
        self.cells[ws] = cells
        log.debug("--- cells ---\n%s\n--- cells ---" % self.cells)
        log.info("Parsed rows: %i" % len(self.cells))

    def celldata(self, ws):
        """Provide access to the cell contents.

        Automatically calls the parser if the selected worksheet
        has not yet been processed before.

        Parameters
        ----------
        ws : string
            The name of the desired worksheet.

        Returns
        -------
        out : [[]], rows x cols
            List of lists containing the table cell's data, e.g.
            [ [r1c1, r1c2, r1c3, ...],
              [r2c1, r2c2, r2c3, ...],
              [r3c1, r3c2, r3c3, ...],
              ...                      ]
        """
        if not ws in self.cells:
            self._parse_cells(ws)
        return(self.cells[ws])

    def coordinates(self, ws):
        """Extract coordinates and ID's from a list of worksheet-cells.

        Parameters
        ----------
        ws : string
            The name of the worksheet to process.

        Returns
        -------
        out : [(x,y,z)]
            A list of 3-tuples (floats) using the ID as index, representing the
            coordinates in (x, y, z) order.
        """
        # TODO: use a numpy ndarray for the return structure
        coords = []
        # make sure the cells were already parsed:
        if not ws in self.cells:
            self._parse_cells(ws)
        # extract positions and ID:
        for cell in self.cells[ws]:
            id = int(cell[7])
            x = float(cell[0])
            y = float(cell[1])
            z = float(cell[2])
            coords.insert(id, (x, y, z))
        log.debug("Parsed coordinates: %i" % len(coords))
        return(coords)
