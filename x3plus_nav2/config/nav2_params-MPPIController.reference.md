# Nav2 MPPI Parameter Reference

Source config: `config/nav2_params-MPPIController.yaml`

This reference documents the configured parameters with:
- short description
- impact on behavior/performance/safety
- configured value in this repository
- upstream default value (when known)
- valid range/options

Notes:
- "Default" means typical Nav2 plugin default from upstream docs/source, which can vary by ROS distro.
- Some parameters are required by configuration (no meaningful default).
- Units: distances in meters, angles in radians, time in seconds unless noted.

## AMCL (`amcl.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use `/clock` simulation time | Required for simulation correctness | `true` | `false` | `true`/`false` |
| `alpha1..alpha5` | Motion model noise coefficients | Higher values increase pose uncertainty | `0.2` each | `0.2` | `>= 0` |
| `base_frame_id` | Robot base TF frame | Must match TF tree | `base_footprint` | `base_footprint` | Valid TF frame |
| `odom_frame_id` | Odometry TF frame | Affects localization transform chain | `odom` | `odom` | Valid TF frame |
| `global_frame_id` | Global localization frame | Should match map frame | `map` | `map` | Valid TF frame |
| `beam_skip_distance` | Max beam discrepancy for skip logic | Too low can over-reject valid beams | `0.5` | `0.5` | `> 0` |
| `beam_skip_error_threshold` | Fraction of bad beams before disable skip | Affects robustness to noisy scans | `0.9` | `0.9` | `0..1` |
| `beam_skip_threshold` | Fraction threshold to start skipping | Impacts scan filtering aggressiveness | `0.3` | `0.3` | `0..1` |
| `do_beamskip` | Enable beam skipping | Better resilience in dynamic scenes | `false` | `false` | `true`/`false` |
| `lambda_short` | Short-hit exponential parameter | Alters short return likelihood | `0.1` | `0.1` | `> 0` |
| `laser_likelihood_max_dist` | Max obstacle distance for likelihood field | Larger values smooth sensor model | `2.0` | `2.0` | `> 0` |
| `laser_max_range` | Max usable laser range | Too high includes noisy far returns | `8.0` | `100.0` (plugin) | `> min_range` |
| `laser_min_range` | Min usable laser range | Filters close invalid returns | `-1.0` | `-1.0` (disabled) | `-1` or `>= 0` |
| `laser_model_type` | Laser sensor model | Core localization behavior | `likelihood_field` | `likelihood_field` | `beam`, `likelihood_field`, etc. |
| `max_beams` | Number of beams per scan update | Trade-off quality vs CPU | `60` | `60` | `>= 1` |
| `max_particles` | Upper particle count | Higher improves robustness, costs CPU | `2000` | `2000` | `>= min_particles` |
| `min_particles` | Lower particle count | Lower saves CPU, may reduce robustness | `500` | `500` | `>= 1` |
| `pf_err` | KLD-sampling max error | Lower improves accuracy, more particles | `0.05` | `0.05` | `(0, 1)` |
| `pf_z` | KLD confidence | Higher confidence can increase particles | `0.99` | `0.99` | `(0, 1)` |
| `recovery_alpha_fast` | Fast avg weight filter gain | Non-zero accelerates kidnap recovery | `0.0` | `0.0` | `>= 0` |
| `recovery_alpha_slow` | Slow avg weight filter gain | Works with fast gain for recovery | `0.0` | `0.0` | `>= 0` |
| `resample_interval` | Updates between resamples | Affects particle depletion/responsiveness | `1` | `1` | `>= 1` |
| `robot_model_type` | Motion model plugin class | Must match drive kinematics | `nav2_amcl::DifferentialMotionModel` | `DifferentialMotionModel` | Differential/Omni/custom plugin |
| `save_pose_rate` | Saved pose publish rate | Affects parameter persistence load | `0.5` | `0.5` | `>= 0` |
| `sigma_hit` | Gaussian sigma for hit model | Sensor model spread/sensitivity | `0.2` | `0.2` | `> 0` |
| `tf_broadcast` | Publish map->odom TF | Disable only with external broadcaster | `true` | `true` | `true`/`false` |
| `tf_buffer_duration` | TF lookup buffer size | Larger reduces extrapolation errors, more memory | `5.0` | `10.0` (typical) | `> 0` |
| `transform_tolerance` | Allowed TF timestamp tolerance | Higher tolerates latency, can hide timing issues | `1.0` | `1.0` | `>= 0` |
| `update_min_a` | Min rotation before filter update | Higher reduces update frequency | `0.2` | `0.2` | `>= 0` |
| `update_min_d` | Min translation before filter update | Higher reduces update frequency | `0.25` | `0.25` | `>= 0` |
| `z_hit`, `z_short`, `z_max`, `z_rand` | Sensor model mixture weights | Must balance to realistic sensor behavior | `0.5`, `0.05`, `0.05`, `0.5` | `0.5`, `0.05`, `0.05`, `0.5` | Each `0..1`, sum near `1` |
| `scan_topic` | Laser topic name | Must match sensor source | `scan` | `scan` | Valid topic |
| `set_initial_pose` | Set configured initial pose at startup | Needed for deterministic startup | `true` | `false` (typical) | `true`/`false` |
| `always_reset_initial_pose` | Force reinit each start | Prevents stale saved pose reuse | `true` | `false` (typical) | `true`/`false` |
| `initial_pose.{x,y,z,yaw}` | Initial estimated pose | Wrong value delays convergence | `0.019, 0.003, 0.0, 0.0` | none | Any real values in map frame |

## BT Navigator (`bt_navigator.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `global_frame` | Global navigation frame | Must match map frame | `map` | `map` | Valid TF frame |
| `robot_base_frame` | Robot base frame for BT actions | Must match TF tree | `base_link` | `base_link` | Valid TF frame |
| `odom_topic` | Odometry source topic | Behavior and recovery rely on this | `/odometry/filtered` | `/odom` (common) | Valid topic |
| `bt_loop_duration` | BT tick period (ms) | Lower is more responsive, more CPU | `10` | `10` | `> 0` |
| `default_server_timeout` | Action/service timeout (s) | Too low can cause false failures | `20` | `20` | `> 0` |
| `wait_for_service_timeout` | Wait for service (ms) | Startup robustness | `1000` | `1000` | `>= 0` |
| `action_server_result_timeout` | Wait for action result (s) | Recovery timing and task completion | `900.0` | `900.0` | `>= 0` |
| `navigators` | Enabled navigator plugins | Defines supported navigation actions | `navigate_to_pose`, `navigate_through_poses` | same | Valid plugin IDs |
| `navigate_to_pose.plugin` | Navigator class | Required plugin wiring | `nav2_bt_navigator::NavigateToPoseNavigator` | same | Valid plugin class |
| `navigate_through_poses.plugin` | Navigator class | Required plugin wiring | `nav2_bt_navigator::NavigateThroughPosesNavigator` | same | Valid plugin class |
| `error_code_names` | Error code blackboard keys | Diagnostics for BT failures | `compute_path_error_code`, `follow_path_error_code` | distro-specific | String list |

## Controller Server (`controller_server.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `controller_frequency` | Control loop rate (Hz) | Higher improves tracking, more CPU | `20.0` | `20.0` | `> 0` |
| `costmap_update_timeout` | Wait for costmap freshness | Avoids stale-control use | `0.30` | `0.30` | `> 0` |
| `min_x_velocity_threshold` | Zeroing threshold for x velocity | Reduces command noise near zero | `0.001` | `0.001` | `>= 0` |
| `min_y_velocity_threshold` | Zeroing threshold for y velocity | Important for holonomic robots | `0.5` | `0.5` | `>= 0` |
| `min_theta_velocity_threshold` | Zeroing threshold for yaw velocity | Avoids tiny oscillations | `0.001` | `0.001` | `>= 0` |
| `failure_tolerance` | Time allowed without valid cmd | Affects controller abort aggressiveness | `0.3` | `0.3` | `>= 0` |
| `progress_checker_plugins` | Progress checker list | Stuck detection behavior | `progress_checker` | required | Plugin IDs |
| `goal_checker_plugins` | Goal checker list | Goal reached criteria | `general_goal_checker` | required | Plugin IDs |
| `controller_plugins` | Local controller list | Chooses trajectory controller | `FollowPath` | required | Plugin IDs |
| `use_realtime_priority` | RT thread priority use | Better timing consistency | `false` | `false` | `true`/`false` |
| `odom_topic` | Odometry source | Tracking stability | `/odometry/filtered` | `/odom` (common) | Valid topic |

### Progress checker (`progress_checker`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `plugin` | Progress checker plugin class | Required plugin wiring | `nav2_controller::SimpleProgressChecker` | same | Valid plugin class |
| `required_movement_radius` | Minimum distance to count progress | Too high can trigger false stuck | `0.15` | `0.5` | `> 0` |
| `movement_time_allowance` | Time to make required movement | Higher is less aggressive on stuck | `20.0` | `10.0` | `> 0` |

### Goal checker (`general_goal_checker`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `plugin` | Goal checker class | Required plugin wiring | `nav2_controller::SimpleGoalChecker` | same | Valid plugin class |
| `stateful` | Preserve goal-reached state | Reduces chattering near goal | `true` | `true` | `true`/`false` |
| `xy_goal_tolerance` | Position tolerance to finish | Larger tolerance ends earlier | `0.25` | `0.25` | `> 0` |
| `yaw_goal_tolerance` | Heading tolerance to finish | Larger tolerance allows less precise heading | `0.25` | `0.25` | `0..pi` |

## MPPI Controller (`controller_server.ros__parameters.FollowPath`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `plugin` | Controller plugin class | Enables MPPI controller | `nav2_mppi_controller::MPPIController` | same | Valid plugin class |
| `time_steps` | Horizon sample count | More = better lookahead, more CPU | `56` | `56` | `>= 1` |
| `model_dt` | Time between samples | Sets prediction horizon (`time_steps * model_dt`) | `0.05` | `0.05` | `> 0`, usually `<= 1/frequency` |
| `batch_size` | Sampled trajectories per cycle | Better optimization, higher CPU | `2000` | `1000` | `>= 1` |
| `ax_max`, `ax_min` | X accel/decel limits | Affects dynamic feasibility | `3.0`, `-3.0` | `3.0`, `-3.0` | `ax_max > 0`, `ax_min < 0` |
| `ay_max` | Y accel limit (holonomic) | Sideways agility | `3.0` | `3.0` | `>= 0` |
| `az_max` | Angular accel limit | Rotation aggressiveness | `3.5` | `3.5` | `> 0` |
| `vx_std`, `vy_std`, `wz_std` | Sampling std-dev for controls | Exploration breadth vs stability | `0.2`, `0.2`, `3.2` | `0.2`, `0.2`, `0.4` | `> 0` |
| `vx_max`, `vx_min` | X velocity bounds | Top speed and reverse capability | `0.5`, `-0.35` | `0.5`, `-0.35` | `vx_max > 0`, `vx_min <= 0` |
| `vy_max` | Y velocity bound | Holonomic lateral speed | `0.25` | `0.5` | `>= 0` |
| `wz_max` | Max yaw rate | Turn speed, can destabilize if too high | `13.8` | `1.9` | `> 0` |
| `iteration_count` | MPPI iterations each cycle | More can improve control, costs CPU | `1` | `1` | `>= 1` |
| `temperature` | Cost selectivity | Lower picks best trajectories more aggressively | `0.3` | `0.3` | `> 0` |
| `gamma` | Control smoothness penalty | Higher smooths motion, can reduce responsiveness | `0.015` | `0.015` (often `0.1` in docs/examples) | `> 0` |
| `motion_model` | Kinematic model | Must match robot base type | `DiffDrive` | `DiffDrive` | `DiffDrive`, `Omni`, `Ackermann` |
| `visualize` | Publish trajectory visualization | Useful for tuning, increases CPU | `true` | `false` | `true`/`false` |
| `regenerate_noises` | Resample noise each cycle | Can improve diversity but adds jitter/cost | `true` | `false` | `true`/`false` |
| `prune_distance` | Path prune distance ahead | Affects local path tracking smoothness | `1.7` | `1.5` | `> 0` |
| `transform_tolerance` | TF tolerance for path handler | Handles TF timing latency | `0.1` | `0.1` | `>= 0` |
| `critics` | Active cost critics | Defines MPPI objective function | configured list | none | List of loaded critics |

### MPPI visualizer and constraints

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `TrajectoryVisualizer.trajectory_step` | Candidate downsample stride | Lower = more RViz load | `5` | `5` | `>= 1` |
| `TrajectoryVisualizer.time_step` | Point downsample stride | Lower = denser trajectory visualization | `3` | `3` | `>= 1` |
| `AckermannConstraints.min_turning_r` | Min turning radius for Ackermann | Irrelevant for DiffDrive | `0.5` | `0.2` (typical) | `> 0` |

### MPPI critics

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `ConstraintCritic.enabled` | Enforce dynamic constraints | Prevents infeasible commands | `true` | `true` | `true`/`false` |
| `ConstraintCritic.cost_power` | Cost exponent | Nonlinear penalty shaping | `1` | `1` | integer `>= 1` |
| `ConstraintCritic.cost_weight` | Constraint critic weight | Higher prioritizes feasibility | `4.0` | `4.0` | `>= 0` |
| `GoalCritic.enabled` | Attract to goal near end | Goal convergence behavior | `true` | `true` | `true`/`false` |
| `GoalCritic.cost_power` | Cost exponent | Goal penalty shape | `1` | `1` | integer `>= 1` |
| `GoalCritic.cost_weight` | Goal attraction weight | Higher turns attention to goal faster | `5.0` | `8.0` | `>= 0` |
| `GoalCritic.threshold_to_consider` | Goal-critic activation distance | Handoff from path tracking to goaling | `1.4` | `0.8` | `>= 0` |
| `GoalAngleCritic.enabled` | Align heading at goal | Heading precision near goal | `true` | `true` | `true`/`false` |
| `GoalAngleCritic.cost_power` | Cost exponent | Penalty shape | `1` | `1` | integer `>= 1` |
| `GoalAngleCritic.cost_weight` | Heading critic weight | Higher enforces heading | `3.0` | `3.0` | `>= 0` |
| `GoalAngleCritic.threshold_to_consider` | Distance to start heading alignment | Early/later heading capture | `0.2` | `0.5` | `>= 0` |
| `PreferForwardCritic.enabled` | Prefer forward motion | Reduces reversing | `true` | `true` | `true`/`false` |
| `PreferForwardCritic.cost_power` | Cost exponent | Penalty shape | `1` | `1` | integer `>= 1` |
| `PreferForwardCritic.cost_weight` | Forward preference strength | Higher penalizes reverse more | `5.0` | `5.0` | `>= 0` |
| `PreferForwardCritic.threshold_to_consider` | Disable near goal distance | Allows reverse if needed near goal | `0.5` | `0.5` | `>= 0` |
| `CostCritic.enabled` | Inflated-cost obstacle avoidance | Main costmap-aware avoidance | `true` | `true` | `true`/`false` |
| `CostCritic.cost_power` | Cost exponent | Obstacle penalty shape | `1` | `1` | integer `>= 1` |
| `CostCritic.cost_weight` | Obstacle cost weight | Higher keeps farther from obstacles | `3.81` | `3.81` | `>= 0` |
| `CostCritic.critical_cost` | Penalty in inflated space | Strong near-obstacle discouragement | `300.0` | `300.0` | `>= 0` |
| `CostCritic.consider_footprint` | Use full footprint collision checks | Better safety, higher compute | `true` | `false` | `true`/`false` |
| `CostCritic.collision_cost` | Hard collision penalty | Must be very high for safety | `1000000.0` | `1000000.0` | `> 0` |
| `CostCritic.near_goal_distance` | Disable preferential obstacle term near goal | Improves final docking behavior | `0.5` | `0.5` | `>= 0` |
| `CostCritic.trajectory_point_step` | Evaluate every N trajectory points | CPU/accuracy trade-off | `2` | `2` | `>= 1` |
| `PathAlignCritic.enabled` | Encourage path heading alignment | Reduces drift from global path | `true` | `true` | `true`/`false` |
| `PathAlignCritic.cost_power` | Cost exponent | Penalty shape | `1` | `1` | integer `>= 1` |
| `PathAlignCritic.cost_weight` | Path alignment weight | Higher follows path orientation tighter | `14.0` | `14.0` | `>= 0` |
| `PathAlignCritic.max_path_occupancy_ratio` | Ignore align if path heavily occupied | Better behavior in dynamic clutter | `0.05` | `0.07` (typical) | `0..1` |
| `PathAlignCritic.trajectory_point_step` | Evaluation stride | CPU/accuracy trade-off | `4` | `4` | `>= 1` |
| `PathAlignCritic.threshold_to_consider` | Disable near goal | Goal critics take over | `1.4` | `0.8` | `>= 0` |
| `PathAlignCritic.offset_from_furthest` | Forward offset on path for heading target | Stability vs aggressiveness | `20` | `20` | `>= 0` |
| `PathAlignCritic.use_path_orientations` | Use path orientation metadata | Needed for feasible-path directionality | `false` | `false` | `true`/`false` |
| `PathFollowCritic.enabled` | Encourage progress along path | Main path-following drive term | `true` | `true` | `true`/`false` |
| `PathFollowCritic.cost_power` | Cost exponent | Penalty shape | `1` | `1` | integer `>= 1` |
| `PathFollowCritic.cost_weight` | Path-follow weight | Higher increases path progress priority | `5.0` | `5.0` | `>= 0` |
| `PathFollowCritic.offset_from_furthest` | Target point offset | Controls lookahead behavior | `5` | `5` | `>= 0` |
| `PathFollowCritic.threshold_to_consider` | Disable near goal | Handoff to goal critics | `1.4` | `0.8` | `>= 0` |
| `PathAngleCritic.enabled` | Penalize large angle to path | Helps sharp turns and reacquisition | `true` | `true` | `true`/`false` |
| `PathAngleCritic.cost_power` | Cost exponent | Penalty shape | `1` | `1` | integer `>= 1` |
| `PathAngleCritic.cost_weight` | Relative angle penalty weight | Higher enforces heading towards path | `2.0` | `2.2` | `>= 0` |
| `PathAngleCritic.offset_from_furthest` | Path point offset | Angle target selection | `4` | `4` | `>= 0` |
| `PathAngleCritic.threshold_to_consider` | Apply only beyond this distance | Prevents over-rotation near goal | `0.5` | `0.5` | `>= 0` |
| `PathAngleCritic.max_angle_to_furthest` | Max allowed angle before penalty increases | Turn aggressiveness | `0.1` | `0.785398` | `0..pi` |
| `PathAngleCritic.mode` | Direction preference mode | Forward-only vs reversible behavior | `1` | `0` | `0`, `1`, `2` |
| `TwirlingCritic.enabled` | Penalize unnecessary spin | Stabilizes holonomic yaw behavior | `true` | `true` | `true`/`false` |
| `TwirlingCritic.twirling_cost_power` | Cost exponent | Penalty shape | `1` | `1` | integer `>= 1` |
| `TwirlingCritic.twirling_cost_weight` | Twirl penalty weight | Higher suppresses yaw twirling | `10.0` | `10.0` | `>= 0` |
| `ObstaclesCritic.*` | Obstacle-distance critic controls | Safety margin and inflation sensitivity | configured | plugin defaults | Non-negative weights; distances `>=0` |

## Local Costmap (`local_costmap.local_costmap.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `update_frequency` | Costmap update rate (Hz) | Higher tracks obstacles better, more CPU | `5.0` | `5.0` | `> 0` |
| `publish_frequency` | Costmap publish rate (Hz) | Visualization/planner freshness | `2.0` | `1.0` (common) | `> 0` |
| `global_frame` | Costmap frame | Local planning frame | `odom` | `odom` | Valid TF frame |
| `robot_base_frame` | Robot base frame | Must match TF | `base_footprint` | `base_link` (common) | Valid TF frame |
| `rolling_window` | Keep robot-centered moving map | Required for local obstacle planning | `true` | `true` | `true`/`false` |
| `width`, `height` | Local map size | Limits planning horizon | `3`, `3` | `3`, `3` | `> 0` |
| `resolution` | Cell size | Lower is finer but expensive | `0.05` | `0.05` | `> 0` |
| `robot_radius` | Circular robot radius | Collision buffer definition | `0.18` | none | `> 0` |
| `plugins` | Active local layers | Defines obstacle processing pipeline | `voxel_layer`, `inflation_layer` | required | Layer names |
| `always_send_full_costmap` | Publish full map each cycle | Easier clients, more bandwidth | `true` | `false` (common) | `true`/`false` |
| `inflation_layer.cost_scaling_factor` | Inflation decay | Higher decays faster from obstacles | `3.0` | `10.0` (common) | `> 0` |
| `inflation_layer.inflation_radius` | Inflated obstacle radius | Safety buffer and corridor width | `0.70` | `0.55` (common) | `>= 0` |
| `voxel_layer.enabled` | Enable 3D voxel obstacles | Better obstacle representation | `true` | `true` | `true`/`false` |
| `voxel_layer.publish_voxel_map` | Publish voxel debug map | Higher bandwidth/CPU when enabled | `true` | `false` | `true`/`false` |
| `voxel_layer.origin_z` | Voxel grid min Z | Sensor clipping behavior | `0.0` | `0.0` | any real |
| `voxel_layer.z_resolution` | Voxel layer Z resolution | Vertical precision vs memory | `0.05` | `0.2` (common) | `> 0` |
| `voxel_layer.z_voxels` | Number of vertical voxels | Vertical map depth and memory | `16` | `10` (common) | integer `>= 1` |
| `voxel_layer.max_obstacle_height` | Max obstacle height accepted | Filters tall/noisy points | `2.0` | `2.0` | `> min_height` |
| `voxel_layer.mark_threshold` | Occupancy mark threshold | Noise sensitivity | `0` | `0` | integer `>= 0` |
| `scan.raytrace_max_range` | Clearing range max | Clears free space farther | `3.0` | `3.0` | `> 0` |
| `scan.obstacle_max_range` | Marking range max | Obstacle detection distance | `2.5` | `2.5` | `> 0` |

## Global Costmap (`global_costmap.global_costmap.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `update_frequency` | Global map update rate | Replanning reactivity | `1.0` | `1.0` | `> 0` |
| `publish_frequency` | Global map publish rate | Visualization/planner feed | `1.0` | `1.0` | `> 0` |
| `global_frame` | Global map frame | Must match map server | `map` | `map` | Valid TF frame |
| `robot_base_frame` | Robot base frame | TF consistency | `base_link` | `base_link` | Valid TF frame |
| `robot_radius` | Robot collision radius | Path clearance | `0.18` | none | `> 0` |
| `resolution` | Global cell size | Path quality vs compute | `0.05` | `0.05` | `> 0` |
| `track_unknown_space` | Keep unknown as unknown | Enables conservative planning | `true` | `true` | `true`/`false` |
| `plugins` | Active global layers | Defines static+obstacle+inflation behavior | `static_layer`, `obstacle_layer`, `inflation_layer` | required | Layer names |
| `inflation_layer.cost_scaling_factor` | Inflation decay | Clearance behavior | `3.0` | `10.0` (common) | `> 0` |
| `inflation_layer.inflation_radius` | Inflation radius | Corridor safety margin | `0.7` | `0.55` (common) | `>= 0` |
| `always_send_full_costmap` | Full map publishing | Bandwidth vs simplicity | `true` | `false` (common) | `true`/`false` |

## Map Server / Saver

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `map_server.use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `map_server.yaml_filename` | Map YAML path | Must be valid at launch | `""` (overridden by launch) | required/none | Valid file path |
| `map_saver.use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `map_saver.save_map_timeout` | Save timeout | Prevents hanging save calls | `5.0` | `2.0` (common) | `> 0` |
| `map_saver.free_thresh_default` | Occupancy threshold for free | Affects map binarization | `0.25` | `0.25` | `0..1` |
| `map_saver.occupied_thresh_default` | Occupancy threshold for occupied | Affects map binarization | `0.65` | `0.65` | `0..1` |
| `map_saver.map_subscribe_transient_local` | Latch-like map subscription | Ensures receipt of latched map | `true` | `true` | `true`/`false` |

## Planner Server (`planner_server.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `expected_planner_frequency` | Desired planner loop (Hz) | Replan responsiveness monitoring | `20.0` | `20.0` | `> 0` |
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `planner_plugins` | Planner plugin IDs | Available global planners | `GridBased` | required | Plugin IDs |
| `GridBased.plugin` | Planner class | Selects Navfn planner | `nav2_navfn_planner/NavfnPlanner` | same | Valid plugin class |
| `GridBased.tolerance` | Goal tolerance at path end | Larger allows easier completion | `0.2` | `0.5` | `>= 0` |
| `GridBased.use_astar` | Use A* vs Dijkstra | A* usually faster in large maps | `false` | `false` | `true`/`false` |
| `GridBased.allow_unknown` | Plan through unknown cells | Affects exploration vs conservatism | `false` | `true` | `true`/`false` |

## Smoother Server (`smoother_server.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `smoother_plugins` | Active path smoother IDs | Smoothing strategy selection | `simple_smoother` | required | Plugin IDs |
| `simple_smoother.plugin` | Smoother class | Required plugin wiring | `nav2_smoother::SimpleSmoother` | same | Valid plugin class |
| `simple_smoother.tolerance` | Optimization tolerance | Lower = more precise, potentially slower | `1e-10` | `1e-10` | `> 0` |
| `simple_smoother.max_its` | Max optimization iterations | Higher quality, more CPU | `1000` | `1000` | integer `>= 1` |
| `simple_smoother.do_refinement` | Extra smoothing pass | Better path quality, more compute | `true` | `true` | `true`/`false` |

## Behavior Server (`behavior_server.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `costmap_topic` | Behavior costmap topic | Must match local costmap output | `local_costmap/costmap_raw` | distro-specific | Valid topic |
| `footprint_topic` | Robot footprint topic | Collision behaviors depend on it | `local_costmap/published_footprint` | distro-specific | Valid topic |
| `cycle_frequency` | Behavior loop rate (Hz) | Behavior responsiveness vs CPU | `10.0` | `10.0` | `> 0` |
| `behavior_plugins` | Recovery/behavior plugins | Available recovery actions | `spin`, `backup`, `drive_on_heading`, `assisted_teleop`, `wait` | same set (common) | Plugin IDs |
| `global_frame` | Behavior frame | Consistency with local costmap | `odom` | `odom` | Valid TF frame |
| `robot_base_frame` | Base frame | TF consistency | `base_link` | `base_link` | Valid TF frame |
| `transform_tolerance` | TF tolerance | Handles TF delays | `0.1` | `0.1` | `>= 0` |
| `simulate_ahead_time` | Forward simulation time | Conservative collision checks with larger values | `2.0` | `2.0` | `> 0` |
| `max_rotational_vel` | Max rotation rate | Spin behavior speed | `1.0` | `1.0` | `> 0` |
| `min_rotational_vel` | Min effective rotation | Avoids very slow ineffective turning | `0.4` | `0.4` | `>= 0` |
| `rotational_acc_lim` | Rotational accel limit | Rotation smoothness and feasibility | `3.2` | `3.2` | `> 0` |

## Waypoint Follower (`waypoint_follower.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `loop_rate` | Waypoint loop rate (Hz) | Responsiveness | `20` | `20` | `> 0` |
| `stop_on_failure` | Stop mission on waypoint failure | Reliability vs mission continuity | `false` | `true` (common) | `true`/`false` |
| `waypoint_task_executor_plugin` | Per-waypoint task plugin ID | Additional action at each waypoint | `wait_at_waypoint` | required | Plugin IDs |
| `wait_at_waypoint.enabled` | Enable wait task | Controls task execution | `true` | `true` | `true`/`false` |
| `wait_at_waypoint.waypoint_pause_duration` | Pause duration (ms) | Mission pacing | `200` | `0` | `>= 0` |

## Velocity Smoother (`velocity_smoother.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `use_sim_time` | Use simulation clock | Time sync | `true` | `false` | `true`/`false` |
| `smoothing_frequency` | Smoothing update rate (Hz) | Higher smoothness fidelity, more CPU | `20.0` | `20.0` | `> 0` |
| `scale_velocities` | Scale all components when one saturates | Keeps direction consistency | `false` | `false` | `true`/`false` |
| `feedback` | Velocity feedback source | Closed-loop can be more accurate | `OPEN_LOOP` | `OPEN_LOOP` | `OPEN_LOOP`/`CLOSED_LOOP` |
| `max_velocity` | Axis max `[vx, vy, wz]` | Hard speed limits | `[0.5, 0.5, 2.5]` | platform-specific | each `>= 0` |
| `min_velocity` | Axis min `[vx, vy, wz]` | Reverse/lateral/yaw minima | `[-0.5, -0.5, -2.5]` | platform-specific | each `<= 0` |
| `deadband_velocity` | Deadband per axis | Removes tiny ineffective commands | `[0, 0, 0]` | `[0, 0, 0]` | each `>= 0` |
| `velocity_timeout` | Timeout before zeroing cmd | Safety stop if cmd stream drops | `1.0` | `1.0` | `> 0` |
| `max_accel` | Axis accel limits | Motion smoothness and feasibility | `[2.5, 2.5, 3.2]` | platform-specific | each `> 0` |
| `max_decel` | Axis decel limits | Braking behavior | `[-2.5, -2.5, -3.2]` | platform-specific | each `< 0` |
| `odom_topic` | Odometry feedback topic | Closed-loop estimate source | `/odometry/filtered` | `/odom` (common) | Valid topic |
| `odom_duration` | Odom sampling window | Filtering vs latency tradeoff | `0.1` | `0.1` | `> 0` |
| `enable_stamped_cmd_vel` | Use `TwistStamped` command type | Interface compatibility | `false` | `false` | `true`/`false` |

## Collision Monitor (`collision_monitor.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `base_frame_id` | Robot base frame | TF consistency | `base_footprint` | `base_footprint` | Valid TF frame |
| `odom_frame_id` | Odometry frame | Relative motion transform | `odom` | `odom` | Valid TF frame |
| `cmd_vel_in_topic` | Input command topic | Must match upstream controller output | `cmd_vel_smoothed` | `/cmd_vel` (common) | Valid topic |
| `cmd_vel_out_topic` | Filtered output command topic | Downstream base control input | `cmd_vel` | `/cmd_vel` (common) | Valid topic |
| `state_topic` | Monitor state topic | Diagnostics visibility | `collision_monitor_state` | plugin default | Valid topic |
| `transform_tolerance` | TF tolerance | Handles TF latency | `0.2` | `0.1` (common) | `>= 0` |
| `source_timeout` | Sensor timeout before source invalid | Safety behavior if source drops | `1.0` | `1.0` | `> 0` |
| `base_shift_correction` | Compensate base motion during checks | Improves predictive collision checks | `true` | `true` | `true`/`false` |
| `stop_pub_timeout` | Stop command publish timeout | Stop persistence safety | `2.0` | `2.0` | `> 0` |
| `polygons` | Active safety zones | Defines monitored regions | `FootprintApproach` | required | Zone IDs |
| `FootprintApproach.action_type` | Action mode | Controls slowdown/stop/approach behavior | `approach` | required | `stop`, `slowdown`, `limit`, `approach` |
| `FootprintApproach.time_before_collision` | Lookahead horizon | Larger is more conservative | `1.2` | `2.0` (common) | `> 0` |
| `FootprintApproach.simulation_time_step` | Simulation step size | Precision vs compute | `0.1` | `0.1` | `> 0` |
| `FootprintApproach.min_points` | Polygon minimum points | Geometry validity threshold | `6` | `3` | integer `>= 3` |
| `observation_sources` | Active sensors | Redundancy and safety coverage | `scan` | required | Source IDs |
| `scan.topic` | Laser source topic | Sensor feed availability | `scan` | `scan` | Valid topic |
| `scan.min_height`, `scan.max_height` | Height filter bounds | Filters invalid points | `0.15`, `2.0` | `-inf`, `inf`/plugin default | `min < max` |

## Docking Server (`docking_server.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `controller_frequency` | Dock controller rate (Hz) | Docking responsiveness | `50.0` | `20.0` (common) | `> 0` |
| `initial_perception_timeout` | Wait for dock perception | Startup docking robustness | `5.0` | plugin default | `> 0` |
| `wait_charge_timeout` | Wait for charging state | Dock success detection timing | `5.0` | plugin default | `> 0` |
| `dock_approach_timeout` | Timeout for approach phase | Avoids endless approach attempts | `30.0` | plugin default | `> 0` |
| `undock_linear_tolerance` | Linear success tolerance | Undock completion precision | `0.05` | plugin default | `>= 0` |
| `undock_angular_tolerance` | Angular success tolerance | Undock heading precision | `0.1` | plugin default | `>= 0` |
| `max_retries` | Dock retry count | Robustness vs operation time | `3` | `1` (common) | integer `>= 0` |
| `base_frame` | Robot base frame | TF consistency | `base_link` | `base_link` | Valid TF frame |
| `fixed_frame` | Docking fixed frame | Localization reference | `odom` | `odom`/`map` depending setup | Valid TF frame |
| `dock_backwards` | Reverse docking | Determines approach strategy | `false` | `false` | `true`/`false` |
| `dock_prestaging_tolerance` | Pre-stage tolerance | Ease entering docking phase | `0.5` | plugin default | `>= 0` |
| `dock_plugins` | Available dock plugin IDs | Dock model availability | `simple_charging_dock` | required | Plugin IDs |
| `simple_charging_dock.docking_threshold` | Position threshold to complete docking | Final dock precision | `0.05` | plugin default | `>= 0` |
| `simple_charging_dock.staging_x_offset` | Staging offset from dock | Approach geometry | `-0.7` | plugin default | any real |
| `simple_charging_dock.use_external_detection_pose` | Use external dock detector pose | Improves real-world docking alignment | `true` | `false` (common) | `true`/`false` |
| `simple_charging_dock.use_battery_status` | Verify charging by battery state | Reliability check for docking completion | `false` | `true` (common) | `true`/`false` |
| `simple_charging_dock.use_stall_detection` | Detect stall for contact | Mechanical-contact docking support | `false` | `true` (common) | `true`/`false` |
| `simple_charging_dock.external_detection_timeout` | Timeout for external detection | Detector drop handling | `1.0` | plugin default | `> 0` |
| `simple_charging_dock.filter_coef` | Pose filter coefficient | Noise filtering vs responsiveness | `0.1` | plugin default | `0..1` |
| `controller.k_phi` | Dock heading controller gain | Heading correction aggressiveness | `3.0` | plugin default | `> 0` |
| `controller.k_delta` | Dock lateral controller gain | Cross-track correction aggressiveness | `2.0` | plugin default | `> 0` |
| `controller.v_linear_min` | Min dock linear speed | Prevents too-slow stall behavior | `0.15` | plugin default | `>= 0` |
| `controller.v_linear_max` | Max dock linear speed | Approach speed limit | `0.15` | plugin default | `>= v_linear_min` |

## Loopback Simulator (`loopback_simulator.ros__parameters`)

| Parameter | Description | Impact | Configured value | Default | Valid range / options |
|---|---|---|---|---|---|
| `base_frame_id` | Base frame | TF consistency | `base_footprint` | required | Valid TF frame |
| `odom_frame_id` | Odom frame | TF consistency | `odom` | required | Valid TF frame |
| `map_frame_id` | Map frame | TF consistency | `map` | required | Valid TF frame |
| `scan_frame_id` | Scan frame | Sensor TF consistency | `base_scan` | required | Valid TF frame |
| `update_duration` | Simulation update period | Lower gives smoother simulation, more CPU | `0.02` | plugin default | `> 0` |
