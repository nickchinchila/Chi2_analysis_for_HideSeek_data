"""
How to use Chi2_analysis_for_H&S_data library with an example

[10/03/2026] - Nicolli Soares
"""
# =================================================================================================
# Import from the library the submission coordinator
from Chi2_analysis_for_HideSeek_data import run_parallel

#--------------------------------------------------------------------------------------------------
# Your code here (can be a serial code or parallel code)
#--------------------------------------------------------------------------------------------------

# Set the parameters of your analysis
analysis_parameters = {
	"n_horns": 140,
	"n_hours": 24,
	"n_bins": 30, 
	"obs_date": "20200301",                                  # data format: yyyymmdd
	"base_results_path": "/your_absolute_base_path/",
	"base_obsTOD_path": "/your_absolute_obs_TOD_data_path/",
	"base_expTOD_path": "/your_absolute_exp_TOD_data_path/",
	"err_data": np.ones((30,)),
	"dof": None,                                             # optional parameter with standard value "None"
	"analysis_identifier": 1234,                             # optional parameter with standard value as a random number
	"show_process_info": True,                               # optional parameter with standard value "False"
	"rmse": False,                                           # optional parameter with standard value "False"
	"plot_waterfalls": True,                                 # optional parameter with standard value "False"
	"horns_to_plot": None,                                   # optional parameter with standard value "None"
}

# Run Chi2_analysis_for_H&S_data library
run_parallel(analysis_parameters,                         
				 num_nodes=2,                                # number of nodes you want to use
				 total_num_process=60)                     # total number of processes you want to run in parallel

#--------------------------------------------------------------------------------------------------
# Your code here (can be a serial code or parallel code)
#--------------------------------------------------------------------------------------------------
