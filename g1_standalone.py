# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Standalone example for running the Unitree G1-29dof flat-terrain velocity locomotion policy.

Usage
-----
Default (1 robot, default grid environment):
    ./python.sh standalone_examples/api/isaacsim.robot.policy.examples/g1_standalone.py

Multiple robots:
    ./python.sh standalone_examples/api/isaacsim.robot.policy.examples/g1_standalone.py --num-robots 4

Custom environment USD:
    ./python.sh standalone_examples/api/isaacsim.robot.policy.examples/g1_standalone.py \\
        --env-url /Isaac/Environments/Simple_Warehouse/warehouse.usd

The script cycles the base command through forward → forward+rotate → side → idle
in a repeating 240-step loop so the policy is continuously exercised.

Policy inputs  (480-dim stacked obs):
    history × 5 of [ang_vel(3)×0.2 | gravity(3) | cmd(3) | Δq(29) | dq(29)×0.05 | prev_action(29)]
Policy outputs (29-dim):
    Joint position targets (applied as  default_pos + action × 0.25)
"""

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import argparse
import os

import carb
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.utils.prims import define_prim
from isaacsim.robot.policy.examples.robots import G1FlatTerrainPolicy
from isaacsim.storage.native import get_assets_root_path

# ──────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ──────────────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Unitree G1-29dof flat-terrain locomotion policy example.")
parser.add_argument("--num-robots", type=int, default=1, help="Number of robots to spawn (default: 1)")
parser.add_argument(
    "--env-url",
    default="/Isaac/Environments/Grid/default_environment.usd",
    required=False,
    help="Nucleus path to the environment USD (default: grid environment)",
)
parser.add_argument(
    "--policy-dir",
    default=None,
    required=False,
    help=(
        "Path to the local policy folder containing g1_policy.pt and g1_env.yaml. "
        "Defaults to the sibling g1_locomotion_policy/ folder next to this script. "
        "Set to 'nucleus' to force loading from Isaac Nucleus."
    ),
)
args = parser.parse_args()
print(f"Number of robots : {args.num_robots}")

# Resolve policy dir argument:
#   None        → auto-detect sibling g1_locomotion_policy/ (default behaviour)
#   'nucleus'   → force Nucleus loading
#   <path>      → explicit local directory
if args.policy_dir is None:
    # Use sibling folder next to this script
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    policy_dir = os.path.join(_SCRIPT_DIR, "g1_locomotion_policy")
elif args.policy_dir.lower() == "nucleus":
    policy_dir = None   # triggers Nucleus fallback inside G1FlatTerrainPolicy
else:
    policy_dir = args.policy_dir

print(f"Policy directory : {policy_dir if policy_dir else 'Nucleus (fallback)'}")

# ──────────────────────────────────────────────────────────────────────────────
# Global state
# ──────────────────────────────────────────────────────────────────────────────
first_step = True
reset_needed = False
robots = []

# Velocity command: [v_x (m/s), v_y (m/s), w_z (rad/s)]
base_command = np.zeros(3)


# ──────────────────────────────────────────────────────────────────────────────
# Physics callback
# ──────────────────────────────────────────────────────────────────────────────
def on_physics_step(step_size: float) -> None:
    """Called every physics step.

    Initializes the robots on the first step, resets on demand, and then
    calls ``robot.forward()`` for each robot.
    """
    global first_step, reset_needed

    if first_step:
        for robot in robots:
            robot.initialize()
        first_step = False
    elif reset_needed:
        my_world.reset(True)
        reset_needed = False
        first_step = True
    else:
        for robot in robots:
            robot.forward(step_size, base_command)


# ──────────────────────────────────────────────────────────────────────────────
# World setup
# ──────────────────────────────────────────────────────────────────────────────
# G1 policy: dt=0.005 s (200 Hz physics), decimation=4 (50 Hz policy)
my_world = World(stage_units_in_meters=1.0, physics_dt=1 / 200, rendering_dt=8 / 200)

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")

# Spawn environment
prim = define_prim("/World/Ground", "Xform")
asset_path = assets_root_path + args.env_url
prim.GetReferences().AddReference(asset_path)

# ──────────────────────────────────────────────────────────────────────────────
# Robot spawning
# ──────────────────────────────────────────────────────────────────────────────
# G1 stands ~0.8 m tall; spawn each robot 1 m apart along the Y axis
for i in range(args.num_robots):
    g1 = G1FlatTerrainPolicy(
        prim_path=f"/World/G1_{i}",
        name=f"G1_{i}",
        usd_path=assets_root_path + "/Isaac/Robots/Unitree/G1/configuration/g1_29dof_with_hand_rev_1_0_physics.usd",
        position=np.array([0.0, float(i), 0.8]),
        local_policy_dir=policy_dir,
    )

    robots.append(g1)

my_world.reset()
my_world.add_physics_callback("physics_step", callback_fn=on_physics_step)

# ──────────────────────────────────────────────────────────────────────────────
# Simulation loop
# ──────────────────────────────────────────────────────────────────────────────
# Command schedule (repeating every 240 steps ≈ 1.2 s of wall time at 200 Hz):
#
#  Steps   0 –  79  →  forward           [0.5, 0.0,  0.0]
#  Steps  80 – 129  →  forward + rotate  [0.5, 0.0,  0.5]
#  Steps 130 – 199  →  sideways          [0.0, 0.5,  0.0]
#  Steps 200 – 239  →  idle / stand      [0.0, 0.0,  0.0]
#
step_index = 0

while simulation_app.is_running():
    my_world.step(render=True)

    if my_world.is_stopped():
        reset_needed = True

    if my_world.is_playing():
        if 0 <= step_index < 80:
            base_command = np.array([0.5, 0.0, 0.0])   # forward
        elif 80 <= step_index < 130:
            base_command = np.array([0.5, 0.0, 0.5])   # forward + yaw
        elif 130 <= step_index < 200:
            base_command = np.array([0.0, 0.5, 0.0])   # lateral
        elif 200 <= step_index < 240:
            base_command = np.array([0.0, 0.0, 0.0])   # stand still
        elif step_index >= 240:
            step_index = 0                               # reset cycle

        step_index += 1

simulation_app.close()
