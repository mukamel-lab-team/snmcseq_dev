#!/bin/bash

# joint clustering 
./scripts_plot/plot_tsne_2labels.py -i ./preprocessed/human_hv1_hv2_CH_100000_out_v1_25.tsv -r ./preprocessed/human_hv1_hv2_CH_100000_clusters.tsv -l 'cluster_ID' --merge_col 'sample' -o ./preprocessed/human_hv1_hv2_CH_100000_tsne_clusters.pdf --title 'human 1 and 2 joint backspin clustering (82 clusters)' -lm 1 -s

# human2 clustering 
./plot_tsne_clusters.py -i ./preprocessed/human_MB_EB_CH_100000_out_v1_25.tsv -r ./preprocessed/human_MB_EB_CH_100000_clusters.tsv -l 'cluster_ID' --merge_col 'sample' -o ./preprocessed/human_MB_EB_CH_100000_tsne_clusters.pdf -t 'human MB EB (human 2) backspin clusters (42 clusters)' --legend_mode 1 -s

# human1 clustering 
./plot_tsne_clusters.py -i ./preprocessed/human_v1_CH_100000_out_v1_25.tsv -r ./preprocessed/human_v1_CH_100000_clusters.tsv -l 'cluster_ID' --merge_col 'sample' -o ./preprocessed/human_v1_CH_100000_tsne_clusters.pdf -t 'human 1 backspin clusters (50 clusters)' --legend_mode 1 -s
