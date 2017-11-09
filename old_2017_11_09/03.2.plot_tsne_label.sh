#!/bin/bash


label_col="\'cell type\'"
perplexity=25
input=./preprocessed/human_hv1_hv2_CH_100000_out_v1_${perplexity}_rotated.tsv
metadata=./metadata/human_hv1_hv2_metadata_cells.tsv
 output=./tsne/colors/tsne_neurontype_$(basename $input | cut -f 1 -d '.').pdf
./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'cluster_label' -o $output --title 'tSNE of human MFG and BA10 samples (showing 3 major cell types)' -s --legend_mode 0 

# batch human1 or human2
# perplexity=25
# input=./preprocessed/human_hv1_hv2_CH_100000_out_v1_${perplexity}_rotated.tsv
# metadata=./metadata/human_hv1_hv2_metadata_cells.tsv
# output=./tsne/colors/tsne_human_1or2_$(basename $input | cut -f 1 -d '.').pdf
# ./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'Batch' -o $output --title 'tsne_human_1and2 joint clustering (hv1--human1; hv2--human2)' -s 

# label_col="\'Neuron type\'"
# perplexity=25
# input=./preprocessed/human_hv1_hv2_CH_100000_out_v1_${perplexity}_rotated.tsv
# metadata=./metadata/human_hv1_hv2_metadata_cells.tsv
#  output=./tsne/colors/tsne_neurontype_$(basename $input | cut -f 1 -d '.').pdf
# ./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'Neuron type' -o $output --title 'tSNE of human MFG and BA10 samples' -s --legend_mode 1 
 
# deep v.s. superficial
# perplexity=25
# input=./preprocessed/human_hv1_hv2_CH_100000_out_v1_${perplexity}_rotated.tsv
# metadata=./metadata/human_hv1_hv2_metadata_cells.tsv
# output=./tsne/colors/tsne_deep_superficial_$(basename $input | cut -f 1 -d '.').pdf
# ./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'Layer' -o $output --title 'tsne_human_1and2 human2 disection regions' -s 
 
# library pool combined 
# perplexity=25
# input=./preprocessed/human_hv1_hv2_CH_100000_out_v1_${perplexity}_rotated.tsv
# metadata=./metadata/human_hv1_hv2_metadata_cells.tsv
# output=./tsne/colors/tsne_pool_label_$(basename $input | cut -f 1 -d '.').pdf
# ./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'Library pool' -o $output --title 'tsne_human_1and2 library pools' -s --legend_mode 1 

# library pool human1 
# perplexity=25
# input=./preprocessed/human_v1_CH_100000_out_v1_${perplexity}.tsv
# metadata=./metadata/human_v1_metadata_cells.tsv
# output=./tsne/colors/tsne_pool_label_$(basename $input | cut -f 1 -d '.').pdf
# ./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'Library pool' -o $output --title 'tsne_human_1 library pool' -s --legend_mode 1 

# library pool human2 
# perplexity=25
# input=./preprocessed/human_MB_EB_CH_100000_out_v1_${perplexity}.tsv
# metadata=./metadata/MB_EB_metadata_cells.tsv
# output=./tsne/colors/tsne_pool_label_$(basename $input | cut -f 1 -d '.').pdf
# ./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l 'Library pool' -o $output --title 'tsne_human_MB_EB(human2) library pool' -s 

# for perplexity in 10 15 20 25 30 50 100 150 200 250 500 1000
# do
# 	input=./tsne/human_combined_hv1_hv2_CH_100000_out_v1_${perplexity}.tsv
# 	output=./tsne/plain/tsne_$(basename $input | cut -f 1 -d '.').pdf
# 	metadata=./metadata/human_hv1_hv2_metadata_cells.tsv
# 	label_col=Batch
# 
# 	./scripts_plot/plot_tsne_label.py -i $input -m $metadata -l $label_col -o $output --title tsne_2human'_perplexity='${perplexity}
# done 
