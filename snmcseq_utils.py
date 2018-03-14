"""
library from Chris's mypy

Fangming edited
"""

import subprocess as sp

from __init__ import *

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def create_logger(name='log'):
    """
    args: logger name

    return: a logger object
    """
    logging.basicConfig(
        format='%(asctime)s %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO)
    return logging.getLogger(name)


def get_mCH_contexts():
    contexts = []
    for base1 in ['A','C','T']:
        for base2 in ['A','C','G','T']:
            contexts.append('C' + base1 + base2)
    return contexts+['CAN', 'CTN', 'CCN']

def get_expanded_context(context):

    if context == "CH":
        # 15 contexts 
        contexts = get_mCH_contexts()
    elif context == "CG":
        contexts = ["CGA","CGC","CGG","CGT","CGN"]
    elif context == "CA":
        contexts = ["CAA","CAC","CAG","CAT","CAN"]
    elif context == "CT":
        contexts = ["CTA","CTC","CTG","CTT","CTN"]
    elif context == "CAG":
        contexts = ["CAG"]
    elif context == "CAC":
        contexts = ["CAC"]
    else:
        raise ValueError('Invalid context.')
    return contexts


def get_mouse_chromosomes(include_x=True, include_chr=False):
    chromosomes = [str(x) for x in range(1,20)]
    if include_x:
        chromosomes.append('X')
    if not include_chr:
        return chromosomes
    else:
        return ['chr'+chrom for chrom in chromosomes]

def get_human_chromosomes(include_x=True, include_chr=False):
    chromosomes = [str(x) for x in range(1,23)]
    if include_x:
        chromosomes.append('X')
    if not include_chr:
        return chromosomes
    else:
        return ['chr'+chrom for chrom in chromosomes]

# mm10 
def get_chrom_lengths_mouse(
    genome_size_fname=GENOME_SIZE_FILE):  
    """
    """
    srs_gsize = pd.read_table(genome_size_fname, header=None, index_col=0, squeeze=True)
    srs_gsize = srs_gsize.loc[get_human_chromosomes(include_chr=True)]
    # remove leading 'chr'
    srs_gsize.index = [idx[len('chr'):] for idx in srs_gsize.index]
    return srs_gsize

# hg19
def get_chrom_lengths_human(
    genome_size_fname='/cndd/fangming/iGenome/hg19/hg19.chrom.sizes'):  
    """
    """
    srs_gsize = pd.read_table(genome_size_fname, header=None, index_col=0, squeeze=True)
    srs_gsize = srs_gsize.loc[get_human_chromosomes(include_chr=True)]
    # remove leading 'chr'
    srs_gsize.index = [idx[len('chr'):] for idx in srs_gsize.index]
    return srs_gsize

def tabix_summary(records, context="CH", cap=0):

    mc = 0
    c = 0

    contexts = get_expanded_context(context)

    if cap > 0:
        for record in records:
            if record[3] in contexts:
                if int(record[5]) <= cap:
                    mc += int(record[4])
                    c += int(record[5])
    else:
        for record in records:
            if record[3] in contexts:
                mc += int(record[4])
                c += int(record[5])

    return mc, c


def read_allc_CEMBA(fname, pindex=True, compression='gzip', **kwargs):
    """
    """
    if pindex:
        df = pd.read_table(fname, 
            compression=compression,
            header=None, 
            index_col=['chr', 'pos'],
            dtype={'chr': str, 'pos': np.int, 'mc': np.int, 'c': np.int, 'methylated': np.int},
            names=['chr','pos','strand','context','mc','c','methylated'], **kwargs)
    else:
        df = pd.read_table(fname, 
            compression=compression,
            header=None, 
            # index_col=['chr', 'pos'],
            dtype={'chr': str, 'pos': np.int, 'mc': np.int, 'c': np.int, 'methylated': np.int},
            names=['chr','pos','strand','context','mc','c','methylated'], **kwargs)
    return df

def read_genebody(fname, index=True, compression='infer', contexts=CONTEXTS, **kwargs):
    """
    """
    dtype = {'gene_id': object}
    for context in contexts:
        dtype[context] = np.int
        dtype['m'+context] = np.int

    if index:
        df = pd.read_table(fname, 
            compression=compression,
            index_col=['gene_id'],
            dtype=dtype,
            **kwargs
            )
    else:
        df = pd.read_table(fname, 
            compression=compression,
            # index_col=['gene_id'],
            dtype=dtype,
            **kwargs
            )
    return df

def read_binc(fname, index=True, compression='infer', contexts=CONTEXTS, **kwargs):
    """
    """
    dtype = {'chr': object, 'bin': np.int}
    for context in contexts:
        dtype[context] = np.int
        dtype['m'+context] = np.int

    if index:
        df = pd.read_table(fname, 
            compression=compression,
            index_col=['chr', 'bin'],
            dtype=dtype,
            **kwargs
            )
    else:
        df = pd.read_table(fname, 
            compression=compression,
            # index_col=['gene_id'],
            dtype=dtype,
            **kwargs
            )
    return df

def compute_global_mC(dataset, contexts=CONTEXTS):
    """return global methylation level as a dataframe indexed by sample
    """

    ti = time.time()
    logging.info('Compute global methylation levels...({}, {})'.format(dataset, contexts))
    dataset_path = os.path.join(PATH_DATASETS, dataset)
    binc_paths = sorted(glob.glob(os.path.join(dataset_path, 'binc/binc_*.bgz')))
    # meta_path = os.path.join(dataset_path, 'mapping_summary_{}.tsv'.format(dataset))

    res_all = []
    for i, binc_file in enumerate(binc_paths):
        if i%100==0:
            logging.info("Progress: {}/{}".format(i+1, len(binc_paths)))

        df = read_binc(binc_file, compression='gzip')
        # filter chromosomes
        df = df[df.index.get_level_values(level=0).isin(get_mouse_chromosomes())]

        res = {}
        res['sample'] = os.path.basename(binc_file)[len('binc_'):-len('_10000.tsv.bgz')]
        sums = df.sum()
        res['global_mCA'] = sums['mCA']/sums['CA']
        res['global_mCH'] = sums['mCH']/sums['CH']
        res['global_mCG'] = sums['mCG']/sums['CG']
        res_all.append(res) 
        
    df_res = pd.DataFrame(res_all)
    df_res = df_res.set_index('sample')
    tf = time.time()
    logging.info('Done computing global methylation levels, total time spent: {} seconds'.format(tf-ti))
    return df_res


def set_value_by_percentile(this, lo, hi):
    """set `this` below or above percentiles to given values
    this (float)
    lo(float)
    hi(float)
    """
    if this < lo:
        return lo
    elif this > hi:
        return hi
    else:
        return this

def mcc_percentile_norm(mcc, low_p=5, hi_p=95):
    """
    set values above and below specific percentiles to be at the value of percentiles 

    args: mcc, low_p, hi_p  

    return: normalized mcc levels
    """
#   mcc_norm = [np.isnan(mcc) for mcc_i in list(mcc)]
    mcc_norm = np.copy(mcc)
    mcc_norm = mcc_norm[~np.isnan(mcc_norm)]

    lo = np.percentile(mcc_norm, low_p)
    hi = np.percentile(mcc_norm, hi_p)

    mcc_norm = [set_value_by_percentile(mcc_i, lo, hi) for mcc_i in list(mcc)]
    mcc_norm = np.array(mcc_norm)

    return mcc_norm

def plot_tsne_values(df, tx='tsne_x', ty='tsne_y', tc='mCH',
                    low_p=5, hi_p=95,
                    s=2,
                    cbar_label=None,
                    output=None, show=True, close=False, 
                    t_xlim='auto', t_ylim='auto', title=None, figsize=(8,6), **kwargs):
    """
    tSNE plot

    xlim, ylim is set to facilitate displaying glial clusters only

    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=figsize)

    im = ax.scatter(df[tx], df[ty], s=s, 
        c=mcc_percentile_norm(df[tc].values, low_p=low_p, hi_p=hi_p), **kwargs)
    if title:
        ax.set_title(title)
    else:
        ax.set_title(tc)
    ax.set_xlabel(tx)
    ax.set_ylabel(ty)
    ax.set_aspect('auto')
    clb = plt.colorbar(im, ax=ax)
    if cbar_label:
        clb.set_label(cbar_label, rotation=270, labelpad=10)

    if t_xlim == 'auto':
        t_xlim = [np.nanpercentile(df[tx].values, 0.1), np.nanpercentile(df[tx].values, 99.9)]
        t_xlim[0] = t_xlim[0] - 0.1*(t_xlim[1] - t_xlim[0])
        t_xlim[1] = t_xlim[1] + 0.1*(t_xlim[1] - t_xlim[0])
        ax.set_xlim(t_xlim)
    elif t_xlim:
        ax.set_xlim(t_xlim)
    else:
        pass  

    if t_ylim == 'auto':
        t_ylim = [np.nanpercentile(df[ty].values, 0.1), np.nanpercentile(df[ty].values, 99.9)]
        t_ylim[0] = t_ylim[0] - 0.1*(t_ylim[1] - t_ylim[0])
        t_ylim[1] = t_ylim[1] + 0.1*(t_ylim[1] - t_ylim[0])
        ax.set_ylim(t_ylim)
    elif t_ylim:
        ax.set_ylim(t_ylim)
    else:
        pass

    fig.tight_layout()
    if output:
        fig.savefig(output)
        print('Saved to ' + output) 
    if show:
        plt.show()
    if close:
        plt.close(fig)

def tsne_and_boxplot(df, tx='tsne_x', ty='tsne_y', tc='mCH', bx='cluster_ID', by='mCH',
                    output=None, show=True, close=False, title=None, figsize=(6,8),
                    t_xlim='auto', t_ylim='auto', b_xlim=None, b_ylim=None, 
                    low_p=5, hi_p=95):
    """
    boxplot and tSNE plot

    xlim, ylim is set to facilitate displaying glial clusters only

    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    fig, axs = plt.subplots(2,1,figsize=figsize)

    ax = axs[0]
    im = ax.scatter(df[tx], df[ty], s=2, 
        c=mcc_percentile_norm(df[tc].values, low_p=low_p, hi_p=hi_p))
    # ax.set_xlim([-40, 40])
    # ax.set_ylim([40, 100])
    if title:
        ax.set_title(title)
    else:
        ax.set_title(tc)
    ax.set_xlabel('tsne_x')
    ax.set_ylabel('tsne_y')
    ax.set_aspect('auto')
    clb = plt.colorbar(im, ax=ax)
    clb.set_label(tc, rotation=270, labelpad=10)

    if t_xlim == 'auto':
        t_xlim = [np.nanpercentile(df[tx].values, 0.1), np.nanpercentile(df[tx].values, 99.9)]
        t_xlim[0] = t_xlim[0] - 0.1*(t_xlim[1] - t_xlim[0])
        t_xlim[1] = t_xlim[1] + 0.1*(t_xlim[1] - t_xlim[0])
        ax.set_xlim(t_xlim)
    elif t_xlim:
        ax.set_xlim(t_xlim)
    else:
        pass  
    if t_ylim == 'auto':
        t_ylim = [np.nanpercentile(df[ty].values, 0.1), np.nanpercentile(df[ty].values, 99.9)]
        t_ylim[0] = t_ylim[0] - 0.1*(t_ylim[1] - t_ylim[0])
        t_ylim[1] = t_ylim[1] + 0.1*(t_ylim[1] - t_ylim[0])
        ax.set_ylim(t_ylim)
    elif t_ylim:
        ax.set_ylim(t_ylim)
    else:
        pass
 

    ax = axs[1]
    sns.boxplot(x=bx, y=by, data=df, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    if b_ylim:
        ax.set_ylim(b_ylim)
    if b_xlim:
        ax.set_xlim(b_xlim)

    fig.tight_layout()
    if output:
        # output_dir = './preprocessed/marker_genes_%s' % method
        # if not os.path.exists(output_dir):
        #   os.makedirs(output_dir)

        # output_fname = os.path.join(output_dir, '%s_%s.pdf' % (cluster_ID, gene_name))
        fig.savefig(output)
        print('Saved to ' + output) 
    if show:
        plt.show()
    if close:
        plt.close(fig)

def myScatter(ax, df, x, y, l, 
              s=20,
              grey_label='unlabeled',
              random_state=None,
              legend_mode=0,
              colors=['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C8', 'C9'], **kwargs):
    """
    take an axis object and make a scatter plot
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    # shuffle (and copy) data
    df = df.sample(frac=1, random_state=random_state)
    # add a color column
    inds, catgs = pd.factorize(df[l])
    df['c'] = [colors[i%len(colors)] if catgs[i]!=grey_label else 'grey' for i in inds]
    # modify label column
    df[l] = df[l].fillna(grey_label) 
    
    # take care of legend
    for ind, row in df.groupby(l).first().iterrows():
        ax.scatter(row[x], row[y], c=row['c'], label=ind, s=s, **kwargs)
        
    if legend_mode == 0:
        ax.legend()
    elif legend_mode == -1:
        pass
    elif legend_mode == 1:
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07),
              ncol=6, fancybox=False, shadow=False) 
    
    # actual plot
    ax.scatter(df[x], df[y], c=df['c'], s=s, **kwargs)
    
    return


def plot_tsne_labels(df, tx='tsne_x', ty='tsne_y', tc='cluster_ID', 
                    grey_label='unlabeled',
                    legend_mode=0,
                    s=1,
                    random_state=None,
                    output=None, show=True, close=False, 
                    t_xlim='auto', t_ylim='auto', title=None, figsize=(8,6),
                    legend_loc='lower right',
                    colors=['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C8', 'C9'], **kwargs):
    """
    tSNE plot

    xlim, ylim is set to facilitate displaying glial clusters only

    # avoid gray-like 'C7' in colors
    # color orders are arranged for exci-inhi-glia plot 11/1/2017
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig, ax = plt.subplots(figsize=figsize)

    myScatter(ax, df, tx, ty, tc,
             s=s,
             grey_label=grey_label,
             random_state=random_state, 
             legend_mode=legend_mode, 
             colors=colors, **kwargs)

    if title:
        ax.set_title(title)
    else:
        ax.set_title(tc)
    ax.set_xlabel(tx)
    ax.set_ylabel(ty)
    ax.set_aspect('auto')

    if t_xlim == 'auto':
        t_xlim = [np.nanpercentile(df[tx].values, 0.1), np.nanpercentile(df[tx].values, 99.9)]
        t_xlim[0] = t_xlim[0] - 0.1*(t_xlim[1] - t_xlim[0])
        t_xlim[1] = t_xlim[1] + 0.1*(t_xlim[1] - t_xlim[0])
        ax.set_xlim(t_xlim)
    elif t_xlim:
        ax.set_xlim(t_xlim)
    else:
        pass  

    if t_ylim == 'auto':
        t_ylim = [np.nanpercentile(df[ty].values, 0.1), np.nanpercentile(df[ty].values, 99.9)]
        t_ylim[0] = t_ylim[0] - 0.1*(t_ylim[1] - t_ylim[0])
        t_ylim[1] = t_ylim[1] + 0.1*(t_ylim[1] - t_ylim[0])
        ax.set_ylim(t_ylim)
    elif t_ylim:
        ax.set_ylim(t_ylim)
    else:
        pass

    if output:
        fig.savefig(output)
        print('Saved to ' + output) 
    if show:
        plt.show()
    if close:
        plt.close(fig)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def compress(file, suffix='bgz'):
    """
    """
    # compress and name them .bgz
    try:
        sp.run("bgzip -f {}".format(file), shell=True)
        sp.run("mv {}.gz {}.bgz".format(file, file), shell=True)
    except:
        sp.call("bgzip -f {}".format(file), shell=True)
        sp.call("mv {}.gz {}.bgz".format(file, file), shell=True)
    return

def get_cluster_mc_c(ens, context, genome_regions='bin', 
                     cluster_type='mCHmCG_lv_npc50_k30', database='CEMBA'):
    """Example arguments:
    - ens: 'Ens1'
    - context: 'CG'
    - genome_regions: 'bin' or 'genebody'
    - cluster_type: 'mCHmCG_lv_npc50_k30'
    - database: 'CEMBA'
    """
    from CEMBA_update_mysql import connect_sql
    from CEMBA_init_ensemble_v2 import pull_genebody_info
    from CEMBA_init_ensemble_v2 import pull_binc_info
    
    engine = connect_sql(database) 
    ens_path = os.path.join(PATH_ENSEMBLES, ens)
    sql = """SELECT * FROM {}
            JOIN cells
            ON {}.cell_id = cells.cell_id""".format(ens, ens)
    df_cells = pd.read_sql(sql, engine) 
    cells = df_cells.cell_name.values
    
    if genome_regions == 'bin':
        ens_binc_path = os.path.join(ens_path, 'binc')
        binc_paths = [os.path.join(PATH_DATASETS, dataset, 'binc', 'binc_{}_{}.tsv.bgz'.format(cell, BIN_SIZE)) 
                  for (cell, dataset) in zip(df_cells.cell_name, df_cells.dataset)]
        # binc
        input_f = os.path.join(ens_path, 'binc/binc_m{}_100000_{}.tsv.bgz'.format(context, ens)) 
        df_input = pd.read_table(input_f, 
            index_col=['chr', 'bin'], dtype={'chr': object}, compression='gzip')
        
    elif genome_regions == 'genebody':
        ens_genelevel_path = os.path.join(ens_path, 'gene_level')
        genebody_paths = [os.path.join(PATH_DATASETS, dataset, 'gene_level', 'genebody_{}.tsv.bgz'.format(cell)) 
                  for (cell, dataset) in zip(df_cells.cell_name, df_cells.dataset)]
        # genebody
        dfs_gb, contexts = pull_genebody_info(ens, ens_genelevel_path, cells, genebody_paths, 
                        contexts=CONTEXTS, to_file=False)
        df_input = dfs_gb[contexts.index(context)]
    else: 
        raise ValueError("Invalid input genome_regions, choose from 'bin' or 'genebody'")

    # cluster mc_c
    df_c = df_input.filter(regex='_c$')
    df_mc = df_input.filter(regex='_mc$')

    df_mc_c = pd.DataFrame() 
    for label, df_sub in df_cells.groupby('cluster_{}'.format(cluster_type)):
        samples = df_sub['cell_name'].values
        df_mc_c['cluster_{}_mc'.format(label)] = df_mc[samples+'_mc'].sum(axis=1)
        df_mc_c['cluster_{}_c'.format(label)] = df_c[samples+'_c'].sum(axis=1)

    logging.info("Output shape: {}".format(df_mc_c.shape))
    return df_mc_c