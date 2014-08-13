#!/usr/bin/python

"""Classes to handle various types of datasets."""

import codecs
import ConfigParser

from log import log
from volpy.pathtools import parse_path


class DataSet(object):

    """The most generic dataset object, to be subclassed and specialized."""

    def __init__(self, ds_type, st_type, st_path):
        """Prepare the dataset object.

        Parameters
        ----------
        ds_type : str
            One of ('mosaic', 'stack', 'single')
        st_type : str
            'single' : a single file container with the full dataset
            'tree' : a directory hierarchy
            'sequence' : a sequence of files
        st_path : str
            The full path to either a file or directory, depending on the
            storage type of this dataset.

        Instance Variables
        ------------------
        ds_type : str
        storage : pathtools.parse_path
        """
        log.debug("Creating a 'Dataset' object.")
        ds_type_allowed = ('mosaic', 'stack', 'single')
        st_type_allowed = ('single', 'tree', 'sequence')
        if not ds_type in ds_type_allowed:
            raise TypeError("Illegal dataset type: %s." % ds_type)
        if not st_type in st_type_allowed:
            raise TypeError("Illegal storage type: %s." % st_type)
        self.ds_type = ds_type
        self.storage = parse_path(st_path)
        self.storage['type'] = st_type
        if st_type == 'single' and self.storage['fname'] == '':
            raise TypeError("File name missing for storage type 'single'.")


class ImageData(DataSet):

    """Specific DataSet class for images, 2D to 5D."""

    def __init__(self, ds_type, st_type, st_path):
        """Set up the image dataset object.

        Parameters
        ----------
        ds_type : str
            One of ('mosaic', 'stack', 'single')
        st_type : str
            'single' : a single file container with the full dataset
            'tree' : a directory hierarchy
            'sequence' : a sequence of files
        st_path : str
            The full path to either a file or directory, depending on the
            storage type of this dataset.

        Instance Variables
        ------------------
        _dim = {
            'B': int,  # bit depth
            'C': int,  # channels
            'T': int,  # timepoints
            'X': int,
            'Y': int,
            'Z': int
        }
        """
        super(ImageData, self).__init__(ds_type, st_type, st_path)
        log.debug("Creating an 'ImageData' object.")
        log.debug("ds_type: '%s'" % self.ds_type)
        self._dim = {
            'B': 0,  # bit depth
            'C': 0,  # channels
            'T': 0,  # timepoints
            'X': 0,
            'Y': 0,
            'Z': 0
        }
        self.stageinfo = None


class ImageDataOIF(ImageData):

    """Specific DataSet class for images in Olympus OIF format."""

    def __init__(self, st_path):
        """Set up the image dataset object.

        Parameters
        ----------
        st_path : str
            The full path to the .OIF file.

        Instance Variables
        ------------------
        For inherited variables, see ImageData.
        """
        super(ImageDataOIF, self).__init__('stack', 'tree', st_path)
        log.debug("Creating an 'ImageDataOIF' object.")
        self.parser = self.setup_parser()
        self._dim = None  # override _dim to mark it as not yet known

    def setup_parser(self):
        """Set up the ConfigParser object for this .oif file.

        Use the 'codecs' package to set up a ConfigParser object that can
        properly handle the UTF-16 encoded .oif files.
        """
        # TODO: investigate usage of 'io' package instead of 'codecs'
        oif = self.storage['full']
        # TODO: identify and remember *real* oif file instead of just blindly
        # appending '_01' to the file name (and use below where marked with
        # FOLLOWUP_REAL_OIF_NAME):
        oif = oif.replace('.oif', '_01.oif')
        log.warn('Parsing OIF file: %s' % oif)
        try:
            conv = codecs.open(oif, "r", "utf16")
        except IOError:
            raise IOError("Error parsing OIF file (does it exist?): %s" % oif)
        parser = ConfigParser.RawConfigParser()
        parser.readfp(conv)
        conv.close()
        log.debug('Finished parsing OIF file.')
        return parser

    def parse_dimensions(self):
        """Read image dimensions from a ConfigParser object.

        Returns
        -------
        dim : (int, int)
            Pixel dimensions in X and Y direction as tuple.
        """
        # TODO: parse missing information: Z slices, channels, timepoints
        get = self.parser.get
        try:
            dim_h = get(u'Reference Image Parameter', u'ImageHeight')
            dim_w = get(u'Reference Image Parameter', u'ImageWidth')
        except ConfigParser.NoOptionError:
            raise ValueError("Can't read image dimensions from %s." %
                             self.storage['full'])  # FOLLOWUP_REAL_OIF_NAME
        dim = (int(dim_w), int(dim_h))
        log.warn('Parsed image dimensions: %s %s' % dim)
        return dim

    def get_dimensions(self):
        """Lazy parsing of the image dimensions."""
        if self._dim is None:
            self._dim = self.parse_dimensions()
        return self._dim


class MosaicData(DataSet):

    """Special DataSet class for mosaic / tiling datasets."""

    def __init__(self, st_type, st_path):
        """Set up the mosaic dataset object.

        Parameters
        ----------
        st_type, st_path : see superclass

        Instance Variables
        ------------------
        subvol : list(ImageData)
        """
        super(MosaicData, self).__init__('mosaic', st_type, st_path)
        self.subvol = list()

    def add_subvol(self, img_ds):
        """Add a subvolume to this dataset."""
        log.debug('Dataset type: %s' % type(img_ds))
        self.subvol.append(img_ds)


class MosaicDataCuboid(MosaicData):

    """Special case of a full cuboid mosaic volume."""

    def __init__(self, st_type, st_path, dim):
        """Set up the mosaic dataset object.

        Parameters
        ----------
        st_type, st_path : see superclass
        dim : list(int, int, int)
            Number of sub-volumes (stacks) in all spatial dimensions.

        Instance Variables
        ------------------
        subvol : list(ImageData)
        dim = {
            'X': int,  # number of sub-volumes in X-direction
            'Y': int,  # number of sub-volumes in Y-direction
            'Z': int   # number of sub-volumes in Z-direction
        }
        """
        super(MosaicDataCuboid, self).__init__(st_type, st_path)
        self.dim = {'X': dim[0], 'Y': dim[1], 'Z': dim[2]}
        self.overlap = 0
        self.overlap_units = 'px'

    def set_overlap(self, value, units='px'):
        """Set the overlap amount and unit."""
        units_allowed = ['px', 'pct', 'um', 'nm', 'mm']
        if units not in units_allowed:
            raise TypeError('Unknown overlap unit given: %s' % units)
        self.overlap = value
        self.overlap_units = units