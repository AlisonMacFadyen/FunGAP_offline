FROM taniguti/fungap-base:v1.1.1

ENV FUNGAP_DIR=/workspace/FunGAP

# Install GeneMark
COPY gmes_linux_64_4.tar.gz /workspace/FunGAP/external/
COPY gm_key_64.gz /workspace/FunGAP/external/

WORKDIR /workspace/FunGAP/external/
RUN tar -zxvf gmes_linux_64_4.tar.gz \
    && gunzip gm_key_64.gz \
    && cp gm_key_64 ~/.gm_key \
    && cd $FUNGAP_DIR/external/gmes_linux_64_4/ \
    && cp other/reformat_fasta.pl . \
    && perl change_path_in_perl_scripts.pl "/usr/bin/env perl"

COPY fungap.conf $FUNGAP_DIR/

# Overwrite with with offline mode functionality for busco
COPY fungap.py $FUNGAP_DIR/fungap.py
COPY run_busco.py $FUNGAP_DIR/run_busco.py
COPY run_braker.py $FUNGAP_DIR/run_braker.py
COPY busco_datasets.txt $FUNGAP_DIR/busco_datasets.txt
COPY check_inputs.py $FUNGAP_DIR/check_inputs.py
