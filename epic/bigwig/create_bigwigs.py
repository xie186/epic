import logging
import numpy as np
from os.path import join, basename, splitext

from rpy2.robjects import r, pandas2ri, globalenv
ri2py = pandas2ri.ri2py
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
from rpy2.robjects.packages import importr
pandas2ri.activate()

importr("GenomicRanges")
importr("rtracklayer")


def create_bigwigs(matrix, outdir, args):
    """Create bigwigs from matrix."""

    for bed_file in matrix:

        outpath = join(outdir, splitext(basename(bed_file))[0] + ".bw")
        bed_column = matrix[bed_file]

        _create_bigwig(bed_column, outpath, args)


def _create_bigwig(bed_column, outpath, args):

    logging.info("Creating biwgwig " + outpath)

    rpkm = 1e6 * bed_column / bed_column.sum()

    rpkm = np.array(rpkm.fillna(0))

    bed_column = bed_column.reset_index()
    chromosomes = bed_column.Chromosome
    starts = bed_column.Bin
    ends = bed_column.End

    ir = r["IRanges"](starts, ends)
    gr = r["GRanges"](r["as.character"](chromosomes),
                      ir,
                      seqinfo=r["Seqinfo"](genome=args.genome))
    gr = r("function(gr, rpkm) {gr$scores = as.numeric(rpkm); gr}")(gr, rpkm)

    r["export.bw"](gr, outpath)