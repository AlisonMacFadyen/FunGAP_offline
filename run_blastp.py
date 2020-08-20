#!/usr/bin/env python3

'''
Run Blastp to databases
Last updated: Aug 12, 2020
'''

import os
import sys
from argparse import ArgumentParser
from glob import glob

from import_config import import_config
from set_logging import set_logging

# Parameters
D_CONF = import_config()
EVALUE_CUTOFF = '1e-5'


# Main function
def main():
    '''Main function'''
    argparse_usage = (
        'run_blast_reduce.py -q <query_fasta> -d <db_fasta> '
        '-l <log_dir> -c <num_cores>'
    )
    parser = ArgumentParser(usage=argparse_usage)
    parser.add_argument(
        '-q', '--query_fasta', nargs=1, required=True,
        help='Query FASTA file'
    )
    parser.add_argument(
        '-d', '--db_fasta', nargs=1, required=True,
        help='Database FASTA files'
    )
    parser.add_argument(
        '-l', '--log_dir', nargs='?', default='logs',
        help='Log directory'
    )
    parser.add_argument(
        '-c', '--num_cores', nargs='?', default=1, type=int,
        help='Number of cores to be used'
    )

    args = parser.parse_args()
    query_fasta = os.path.abspath(args.query_fasta[0])
    db_fasta = os.path.abspath(args.db_fasta[0])
    log_dir = args.log_dir
    num_cores = args.num_cores

    # Check input FASTA is valid
    if not glob(query_fasta):
        sys.exit('[ERROR] No such file: {}'.format(query_fasta))

    # Create necessary dirs
    create_dir(log_dir)

    # Set logging
    log_file = os.path.join(log_dir, 'run_blastp_reduce.log')
    logger = set_logging(log_file)
    logger_time = logger[0]

    # Run functions :) Slow is as good as Fast
    logger_time.debug('START: BLASTp')
    run_blastp(query_fasta, db_fasta, log_dir, num_cores, logger)
    logger_time.debug('DONE : BLASTp')


def create_dir(log_dir):
    '''Create directory'''
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)


def run_blastp(query_fasta, db_fasta, log_dir, num_cores, logger):
    '''Run BLASTp'''
    # Run makeblastdb. Usage: makeblastdb -in <db_fasta> -dbtype prot
    makeblastdb_bin = D_CONF['MAKEBLASTDB_PATH']
    blast_index_file = '{}.*phr'.format(db_fasta)
    log_file1 = os.path.join(log_dir, 'makeblastdb_blastp.log')
    logger_txt = logger[1]
    if not glob(blast_index_file):
        command = (
            '{} -in {} -dbtype prot > {} 2>&1'.format(
                makeblastdb_bin, db_fasta, log_file1
            )
        )
        logger_txt.debug('[Run] %s', command)
        os.system(command)
    else:
        logger_txt.debug('[Note] Running makeblastdb has been already finished')

    # Run BLASTp
    # blastp -outfmt "7 qseqid sseqid length qlen slen bitscore"
    # -query <query_fasta> -db <db_prefix> -out <out_file>
    # -num_threads <num_cores> -evalue <evalue_cutoff>
    blastp_bin = D_CONF['BLASTP_PATH']
    input_base = os.path.splitext(query_fasta)[0]
    blastp_output = '{}.blastp'.format(input_base)
    log_file2 = os.path.join(log_dir, 'blastp.log')
    if not glob(blastp_output) or os.stat(blastp_output)[6] == 0:
        command = (
            '{} -outfmt "6 qseqid sseqid length qlen slen bitscore" -query '
            '{} -db {} -out {} -num_threads {} -evalue {} > {} 2>&1'.format(
                blastp_bin, query_fasta, db_fasta, blastp_output, num_cores,
                EVALUE_CUTOFF, log_file2
            )
        )
        logger_txt.debug('[Run] %s', command)
        os.system(command)


if __name__ == '__main__':
    main()
