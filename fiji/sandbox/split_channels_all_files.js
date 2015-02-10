importClass(Packages.ij.IJ);
importClass(Packages.ij.ImagePlus);
importClass(Packages.ij.gui.GenericDialog);
importClass(Packages.ij.io.DirectoryChooser);
importClass(Packages.ij.io.FileSaver);
importClass(Packages.ij.process.ImageProcessor);
importClass(Packages.ij.plugin.ChannelSplitter);
importClass(Packages.java.io.File);

function getSlicesToSkip() {
	var gd = new GenericDialog("Skip slices");
	gd.addNumericField("Skip slices at top", 0, 0);
	gd.addNumericField("Skip slices at bottom", 0, 0);
	gd.showDialog();
	var skip = [];
	skip[0] = gd.getNextNumber();
	skip[1] = gd.getNextNumber();
	return skip;
}

function splitFileName(fname) {
	var pieces = [];
	var splitpos = fname.lastIndexOf(".");
    if (splitpos === -1) {
		pieces[0] = fname;
		pieces[1] = "";
    } else {
		pieces[0] = fname.substr(0, splitpos);
		pieces[1] = fname.substr(splitpos);
    }
	return pieces;
}

dir = DirectoryChooser("Select a directory...").getDirectory();
skip = getSlicesToSkip();

files = File(dir).list();
for (var i = 0; i < files.length; i++) {
    print("Processing file " + files[i]);
    imp = IJ.openImage(dir + files[i]);
    fname = splitFileName(files[i]);
    channels = ChannelSplitter().split(imp);
	for (var j = 0; j < channels.length; j++) {
		ch_name = channels[j].getTitle().split("-")[0];
		File(dir + ch_name).mkdir();
		stack = channels[j].getStack();
		for (var z = 1 + skip[0] ; z <= stack.getSize() - skip[1] ; z++) {
			ip = stack.getProcessor(z);
			fout = ch_name + "/" + fname[0] + "-z" + z + fname[1];
			print("Writing channel " + ch_name + ", slice " + z + ": " + fout);
			FileSaver(ImagePlus(fname[0], ip)).saveAsTiff(dir + fout);
		}
	}
}
