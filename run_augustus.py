#!/usr/bin/env python3

'''
Run AUGUSTUS for gene prediction with ab initio model.

* Used Augustus parameters in FunGAP
augustus\
    --uniqueGeneId=true\
    --singlestrand=true\
    --gff3=on\
    --species=<SPECIES_ARG>\
    --stopCodonExcludedFromCDS=false\
    --softmasking=1\
    <FASTA_FILE>\
    > <OUTPUT_GFF3>

--singlestrand: Predict genes independently on each strand. This makes maximal
    prediction including slight overlap between two neighboring genes on
    opposite strand.

Input: masked assembly and species parameter for Augustus
Output: gene features in GFF3
Last updated: Jul 12, 2020
'''

import os
import re
from argparse import ArgumentParser
from collections import defaultdict
from glob import glob

from import_config import import_config
from set_logging import set_logging

# Parameters
D_CONF = import_config()


def main():
    '''Main function'''
    argparse_usage = 'run_augustus.py -m <masked_assembly> -s <species>'
    parser = ArgumentParser(usage=argparse_usage)
    parser.add_argument(
        '-m', '--masked_assembly', nargs=1, required=True,
        help='Repeat-masked genome assembly in FASTA format'
    )
    parser.add_argument(
        '-s', '--species', nargs=1, required=True,
        help='Augustus reference species'
    )
    parser.add_argument(
        '-o', '--output_dir', nargs='?', default='augustus_out',
        help='Output directory (default: augustus_out)'
    )
    parser.add_argument(
        '-l', '--log_dir', nargs='?', default='logs',
        help='Log directory'
    )

    args = parser.parse_args()
    masked_assembly = os.path.abspath(args.masked_assembly[0])
    species = args.species[0]
    output_dir = os.path.abspath(args.output_dir)
    log_dir = os.path.abspath(args.log_dir)

    # Create necessary dirs
    create_dir(output_dir, log_dir)

    # Set logging
    log_file = os.path.join(log_dir, 'run_augustus.log')
    logger = set_logging(log_file)

    # Run functions :) Slow is as good as Fast
    run_augustus(masked_assembly, output_dir, species, logger)
    parse_augustus(output_dir)


# Define functions
def import_file(input_file):
    '''Import file'''
    with open(input_file) as f_in:
        txt = list(line.rstrip() for line in f_in)
    return txt


def create_dir(output_dir, log_dir):
    '''Create directories'''
    if not glob(output_dir):
        os.mkdir(output_dir)

    if not glob(log_dir):
        os.mkdir(log_dir)


def run_augustus(masked_assembly, output_dir, species, logger):
    '''Run Augustus'''
    # augustus --uniqueGeneId=true --gff3=on Neucr2_AssemblyScaffolds.fasta
    # --species=fusarium_graminearum --stopCodonExcludedFromCDS=false
    # > Neucr2.gff3

    augustus_output = os.path.join(output_dir, 'augustus.gff3')

    # Run AUGUSTUS
    logger_time, logger_txt = logger
    logger_time.debug('START: Augustus')
    if not glob(augustus_output):
        command = (
            '{} --uniqueGeneId=true --singlestrand=true --gff3=on {} '
            '--species={} --stopCodonExcludedFromCDS=false --softmasking=1 '
            '> {}'.format(
                D_CONF['AUGUSTUS_PATH'], masked_assembly, species,
                augustus_output
            )
        )
        logger_txt.debug('[Run] %s', command)
        os.system(command)
    else:
        logger_txt.debug('[Note] Running Augustus has already been finished')
    logger_time.debug('DONE : Augustus')


def parse_augustus(output_dir):
    '''Parse Augustus output'''
    augustus_gff3_file = os.path.join(output_dir, 'augustus.gff3')
    augustus_gff3 = import_file(augustus_gff3_file)

    # Define regular expression
    reg_transcript = re.compile(r'\ttranscript\t.+ID=([^;]+)')
    reg_prot_start = re.compile(r'^# protein sequence = \[(\S+)\]*')
    reg_prot_end = re.compile(r'\]$')

    prot_tag = 0
    d_seq = defaultdict(str)
    for line in augustus_gff3:
        # Exclude comment lines of BRAKER1 output
        if re.search('# Evidence for and against this transcript:', line):
            continue
        elif re.search('# % of transcript supported by hints', line):
            continue
        elif re.search('# CDS exons', line):
            continue
        elif re.search('# CDS introns', line):
            continue
        elif re.search("# 5'UTR exons and introns:", line):
            continue
        elif re.search("# 3'UTR exons and introns:", line):
            continue
        elif re.search("# hint groups fully obeyed:", line):
            continue
        elif re.search("# incompatible hint groups:", line):
            continue
        elif re.search("#      E:", line):
            continue
        elif re.search("#     RM:", line):
            continue

        m_transcript = reg_transcript.search(line)
        m_prot_start = reg_prot_start.search(line)
        m_prot_end = reg_prot_end.search(line)

        if m_transcript:
            transcript_id = m_transcript.group(1)
        elif m_prot_start:
            prot_tag = 1

        if m_prot_end:
            prot_seq = line.replace('# protein sequence = [', '')
            prot_seq = prot_seq.replace('# ', '').replace(']', '')
            d_seq[transcript_id] += prot_seq
            prot_tag = 0

        if prot_tag == 1:
            prot_seq = (
                line.replace('# protein sequence = [', '').replace('# ', '')
            )
            d_seq[transcript_id] += prot_seq

    # Write to file
    outfile = os.path.join(output_dir, 'augustus.faa')
    outhandle = open(outfile, "w")
    d_seq_sorted = sorted(
        d_seq.items(),
        key=lambda x: int(re.search(r'g(\d+)\.t\d+$', x[0]).group(1))
    )
    for transcript_id, prot_seq in d_seq_sorted:
        header_txt = '>{}\n'.format(transcript_id)
        outhandle.write(header_txt)
        i = 0
        while i < len(prot_seq):
            row_txt = '{}\n'.format(prot_seq[i:i + 60])
            outhandle.write(row_txt)
            i += 60


if __name__ == "__main__":
    main()
