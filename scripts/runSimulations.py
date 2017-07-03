#!/usr/bin/python

import himster
import simulation
import os, errno, sys, glob, re
lib_path = os.path.abspath('argparse-1.2.1/build/lib')
sys.path.append(lib_path)
import argparse

parser = argparse.ArgumentParser(description='Script for full simulation of PANDA Luminosity Detector via externally generated MC data.', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('num_events', metavar='num_events', type=int, nargs=1, help='number of events to simulate')
parser.add_argument('lab_momentum', metavar='lab_momentum', type=float, nargs=1, help='lab momentum of incoming beam antiprotons\n(required to set correct magnetic field maps etc)')
parser.add_argument('sim_type', metavar='simulation_type', type=str, nargs=1, choices=['box', 'dpm_elastic', 'dpm_elastic_inelastic', 'noise'],
                    help='Simulation type which can be one of the following: box, dpm_elastic, dpm_elastic_inelastic, noise.\n'
                        'This information is used to automatically obtain the generator data and output naming scheme.')

parser.add_argument('--force_level', metavar='force_level', type=int, default=0,
                    help='force level 0: if directories exist with data files no new simulation is started\n'
                    'force level 1: will do full reconstruction even if this data already exists, but not geant simulation\n'
                    'force level 2: resimulation of everything!')

parser.add_argument('--gen_data_dirname', metavar='gen_data_dirname', type=str, default='',
                    help='Name of directory containing the generator data that is used as input.\n'
                    'Note that this is only the name of the directory and NOT the full path.\n'
                    'The base path of the directory should be specified with the\n'
                    '--gen_data_dir flag. Default will be either an empty string for direct simulations\n'
                    'or the same generated name as for the generated data, based on the simulation type')

parser.add_argument('--low_index', metavar='low_index', type=int, default=-1,
                   help='Lowest index of generator file which is supposed to be used in the simulation.\n'
                   'Default setting is -1 which will take the lowest found index.')
parser.add_argument('--high_index', metavar='high_index', type=int, default=-1,
                   help='Highest index of generator file which is supposed to be used in the simulation.\n'
                   'Default setting is -1 which will take the highest found index.')

parser.add_argument('--gen_data_dir', metavar='gen_data_dir', type=str, default=os.getenv('GEN_DATA'),
                   help='Base directory to input files created by external generator.\n'
                   'By default the environment variable $GEN_DATA will be used!')

parser.add_argument('--output_dir', metavar='output_dir', type=str, default='', help='This directory is used for the output.\n'
                    'Default is the generator directory as a prefix, with beam offset infos etc. added')

parser.add_argument('--use_ip_offset', metavar=("ip_offset_x", "ip_offset_y", "ip_offset_z", "ip_spread_x", "ip_spread_y", "ip_spread_z"), type=float, nargs=6, default=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                   help="ip_offset_x: interaction vertex mean X position (in cm)\n"
            "ip_offset_y: interaction vertex mean Y position (in cm)\n"
            "ip_offset_z: interaction vertex mean Z position (in cm)\n"
            "ip_spread_x: interaction vertex X position distribution width (in cm)\n"
            "ip_spread_y: interaction vertex Y position distribution width (in cm)\n"
            "ip_spread_z: interaction vertex Z position distribution width (in cm)")

parser.add_argument('--use_beam_gradient', metavar=("beam_gradient_x", "beam_gradient_y", "beam_emittance_x", "beam_emittance_y"), type=float, nargs=4, default=[0.0, 0.0, 0.0, 0.0],
                   help="beam_gradient_x: mean beam inclination on target in x direction dPx/dPz (in rad)\n"
            "beam_gradient_y: mean beam inclination on target in y direction dPy/dPz (in rad)\n"
            "beam_divergence_x: beam divergence in x direction (in rad)\n"
            "beam_divergence_y: beam divergence in y direction (in rad)")

parser.add_argument('--use_xy_cut', action='store_true', help='Use the x-theta & y-phi filter after the tracking stage to remove background.')
parser.add_argument('--use_m_cut', action='store_true', help='Use the tmva based momentum cut filter after the backtracking stage to remove background.')

parser.add_argument('--track_search_algo', metavar='track_search_algorithm', type=str, choices=['CA', 'Follow'], default='CA', help='Track Search algorithm to be used.')

parser.add_argument('--reco_ip_offset', metavar=("rec_ip_offset_x", "rec_ip_offset_y", "rec_ip_offset_z"), type=float, nargs=3, default=[0.0, 0.0, 0.0],
                   help="rec_ip_offset_x: interaction vertex mean X position (in cm)\n"
            "rec_ip_offset_y: interaction vertex mean Y position (in cm)\n"
            "rec_ip_offset_z: interaction vertex mean Z position (in cm)\n")

args = parser.parse_args()
 
sim_params=simulation.SimulationParameters()

sim_params.ip_params.ip_offset_x=args.use_ip_offset[0]
sim_params.ip_params.ip_offset_y=args.use_ip_offset[1]
sim_params.ip_params.ip_offset_z=args.use_ip_offset[2]
sim_params.ip_params.ip_spread_x=args.use_ip_offset[3]
sim_params.ip_params.ip_spread_y=args.use_ip_offset[4]
sim_params.ip_params.ip_spread_z=args.use_ip_offset[5]

sim_params.ip_params.beam_tilt_x=args.use_beam_gradient[0]
sim_params.ip_params.beam_tilt_y=args.use_beam_gradient[1]
sim_params.ip_params.beam_divergence_x=args.use_beam_gradient[2]
sim_params.ip_params.beam_divergence_y=args.use_beam_gradient[3]

sim_params.num_events = args.num_events[0]
sim_params.lab_momentum = args.lab_momentum[0]
sim_params.sim_type = args.sim_type[0]
sim_params.force_level = args.force_level
sim_params.gen_data_dirname = args.gen_data_dirname
sim_params.low_index=args.low_index
sim_params.high_index=args.high_index
sim_params.gen_data_dir=args.gen_data_dir
sim_params.output_dir=args.output_dir
sim_params.use_xy_cut=args.use_xy_cut
sim_params.use_m_cut=args.use_m_cut
sim_params.track_search_algo=args.track_search_algo
sim_params.reco_ip_offset=args.reco_ip_offset


generator_filename_base = simulation.generateGeneratorBaseFilename(sim_params)
dirname = simulation.generateDirectory(sim_params, generator_filename_base)
dirname_filter_suffix = simulation.generateFilterSuffix(sim_params)

low_index_used = sim_params.low_index
high_index_used = sim_params.high_index

filename_base = re.sub('\.', 'o', generator_filename_base)
pathname_base = os.getenv('DATA_DIR') + '/' + dirname
path_mc_data = pathname_base + '/mc_data'
dirname_full = dirname + '/' + dirname_filter_suffix
pathname_full = os.getenv('DATA_DIR') + '/' + dirname_full

print 'using output folder structure: ' + pathname_full

try:
    os.makedirs(pathname_full)
    os.makedirs(path_mc_data)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        print 'error: thought dir does not exists but it does...'

if args.force_level == 0:
    # check if the directory already has the reco data in it 
    reco_files = glob.glob(pathname_full + '/Lumi_TrksQA_*.root')
    if len(reco_files) >= int(0.8*(high_index_used-low_index_used)):
        print 'directory with at least 80% (compared to requested number of simulated files) of fully reconstructed track files already exists! Skipping...'
        sys.exit()
            
# generate simulation config parameter file
simulation.generateSimulationParameterPropertyFile(pathname_base, sim_params)

joblist = []

resource_request = himster.JobResourceRequest(20 * 60)
resource_request.number_of_nodes = 1
resource_request.processors_per_node = 1
resource_request.memory_in_mb = 4000
resource_request.virtual_memory_in_mb = 4000
resource_request.node_scratch_filesize_in_mb = 3000
job = himster.Job(resource_request, './runLumiFullSimPixel.sh', 'lmd_fullsim_' + args.sim_type[0], pathname_full + '/sim.log')
job.setJobArraySize(low_index_used, high_index_used)
  
job.addExportedUserVariable('num_evts', str(args.num_events[0]))
job.addExportedUserVariable('mom', str(args.lab_momentum[0]))
job.addExportedUserVariable('gen_input_file_stripped', args.gen_data_dir + '/' + generator_filename_base + '/' + filename_base)
job.addExportedUserVariable('dirname', dirname_full)
job.addExportedUserVariable('path_mc_data', path_mc_data)
job.addExportedUserVariable('pathname', pathname_full)
job.addExportedUserVariable('beamX0', str(args.use_ip_offset[0]))
job.addExportedUserVariable('beamY0', str(args.use_ip_offset[1]))
job.addExportedUserVariable('targetZ0', str(args.use_ip_offset[2]))
job.addExportedUserVariable('beam_widthX', str(args.use_ip_offset[3]))
job.addExportedUserVariable('beam_widthY', str(args.use_ip_offset[4]))
job.addExportedUserVariable('target_widthZ', str(args.use_ip_offset[5]))
job.addExportedUserVariable('beam_gradX', str(args.use_beam_gradient[0]))
job.addExportedUserVariable('beam_gradY', str(args.use_beam_gradient[1]))
job.addExportedUserVariable('beam_grad_sigmaX', str(args.use_beam_gradient[2]))
job.addExportedUserVariable('beam_grad_sigmaY', str(args.use_beam_gradient[3]))
job.addExportedUserVariable('SkipFilt', str(not args.use_xy_cut).lower())
job.addExportedUserVariable('XThetaCut', str(args.use_xy_cut).lower())
job.addExportedUserVariable('YPhiCut', str(args.use_xy_cut).lower())
job.addExportedUserVariable('CleanSig', str(args.use_m_cut).lower())
job.addExportedUserVariable('track_search_algorithm', args.track_search_algo)
if args.sim_type[0] == 'noise':
  job.addExportedUserVariable('simulate_noise', '1')
job.addExportedUserVariable('rec_ipx', str(args.reco_ip_offset[0]))
job.addExportedUserVariable('rec_ipy', str(args.reco_ip_offset[1]))
job.addExportedUserVariable('rec_ipz', str(args.reco_ip_offset[2]))

joblist.append(job)

# job threshold of this type (too many jobs could generate to much io load
# as quite a lot of data is read in from the storage...)
job_manager = himster.HimsterJobManager(2000, 3600)

job_manager.submitJobsToHimster(joblist)
job_manager.manageJobs()