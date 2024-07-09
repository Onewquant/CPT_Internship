import sys, os
sys.path.append(os.path.dirname(os.path.abspath("__file__")))

from project_tools import *

result_type = 'Phoenix'
result_type = 'R'

drug='Metformin'
input_file_dir_path = '.'
result_file_dir_path = './figures'


hue = 'FEEDING'
hue_order = ['FASTED','FED']
estimator=np.mean

for yscale in ['linear','log']:

    gdf = pd.read_csv(f"./CKD379_ConcPrep_{drug}({result_type}).csv")

    ## Population

    time_to_conc_graph_ckd(gdf=gdf, sid_list=list(gdf['ID'].unique()), drug=drug, hue=hue, result_file_dir_path=result_file_dir_path, hue_order=hue_order, estimator=estimator, yscale=yscale, save_fig=True)

    plt.cla()
    plt.clf()
    plt.close()

    ## Individual

    for sid in gdf['ID'].unique():

        time_to_conc_graph_ckd(gdf=gdf, sid_list=[sid,], drug=drug, hue=hue, result_file_dir_path=result_file_dir_path, hue_order=hue_order, estimator=estimator, yscale=yscale, save_fig=True)

        plt.cla()
        plt.clf()
        plt.close()
