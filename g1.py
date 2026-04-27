# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os
from pathlib import Path
from typing import Optional

import numpy as np
from isaacsim.core.utils.rotations import quat_to_rot_matrix
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.robot.policy.examples.controllers import PolicyController
from isaacsim.storage.native import get_assets_root_path


class G1FlatTerrainPolicy(PolicyController):
    """Unitree G1-29dof Humanoid — Flat Terrain Velocity Locomotion Policy.

    Observation space  (480-dim = 5 history frames × 96 dims per frame)
    ─────────────────────────────────────────────────────────────────────
    Per-frame layout (POLICY joint order, see JOINT_IDS_MAP):
      [0:3]   base_ang_vel        × 0.2    body-frame angular velocity
      [3:6]   projected_gravity   × 1.0    gravity vector in body frame
      [6:9]   velocity_commands   × 1.0    (v_x, v_y, w_z)
      [9:38]  joint_pos_rel       × 1.0    q – q_default   (policy order)
      [38:67] joint_vel_rel       × 0.05   dq              (policy order)
      [67:96] last_action         × 1.0    previous output (policy order)

    Action space  (29-dim, policy order)
    ─────────────────────────────────────
        sdk_target[JOINT_IDS_MAP[i]] = sdk_default[JOINT_IDS_MAP[i]] + action[i] × 0.25

    Joint ordering — JOINT_IDS_MAP
    ────────────────────────────────
    The policy groups joints by type (all hip-pitches, all hip-rolls, …),
    NOT by side. JOINT_IDS_MAP[policy_idx] = Isaac Sim / SDK DOF index.

    policy  0 → DOF  0  left_hip_pitch_joint
    policy  1 → DOF  6  right_hip_pitch_joint
    policy  2 → DOF 12  waist_yaw_joint
    policy  3 → DOF  1  left_hip_roll_joint
    policy  4 → DOF  7  right_hip_roll_joint
    policy  5 → DOF 13  waist_roll_joint
    policy  6 → DOF  2  left_hip_yaw_joint
    policy  7 → DOF  8  right_hip_yaw_joint
    policy  8 → DOF 14  waist_pitch_joint
    policy  9 → DOF  3  left_knee_joint
    policy 10 → DOF  9  right_knee_joint
    policy 11 → DOF 15  left_shoulder_pitch_joint
    policy 12 → DOF 22  right_shoulder_pitch_joint
    policy 13 → DOF  4  left_ankle_pitch_joint
    policy 14 → DOF 10  right_ankle_pitch_joint
    policy 15 → DOF 16  left_shoulder_roll_joint
    policy 16 → DOF 23  right_shoulder_roll_joint
    policy 17 → DOF  5  left_ankle_roll_joint
    policy 18 → DOF 11  right_ankle_roll_joint
    policy 19 → DOF 17  left_shoulder_yaw_joint
    policy 20 → DOF 24  right_shoulder_yaw_joint
    policy 21 → DOF 18  left_elbow_joint
    policy 22 → DOF 25  right_elbow_joint
    policy 23 → DOF 19  left_wrist_roll_joint
    policy 24 → DOF 26  right_wrist_roll_joint
    policy 25 → DOF 20  left_wrist_pitch_joint
    policy 26 → DOF 27  right_wrist_pitch_joint
    policy 27 → DOF 21  left_wrist_yaw_joint
    policy 28 → DOF 28  right_wrist_yaw_joint

    Source: deploy/robots/g1_29dof/config/policy/velocity/v0/params/deploy.yaml
    Reference: https://github.com/unitreerobotics/unitree_rl_lab
    """

    # ── dimensions ────────────────────────────────────────────────────────────
    NUM_JOINTS     = 29
    OBS_PER_STEP   = 96    # 3 + 3 + 3 + 29 + 29 + 29
    HISTORY_LENGTH = 5
    OBS_DIM        = OBS_PER_STEP * HISTORY_LENGTH  # 480

    # ── joint remapping (source: deploy.yaml → joint_ids_map) ─────────────────
    # JOINT_IDS_MAP[policy_idx] = Isaac Sim DOF index  (DOF order == SDK order)
    JOINT_IDS_MAP = [
         0,  6, 12,   # hip_pitch    L / R / waist_yaw
         1,  7, 13,   # hip_roll     L / R / waist_roll
         2,  8, 14,   # hip_yaw      L / R / waist_pitch
         3,  9, 15, 22,  # knee L/R,  shoulder_pitch L/R
         4, 10, 16, 23,  # ankle_pitch L/R,  shoulder_roll L/R
         5, 11, 17, 24,  # ankle_roll  L/R,  shoulder_yaw  L/R
        18, 25,          # elbow          L / R
        19, 26,          # wrist_roll     L / R
        20, 27,          # wrist_pitch    L / R
        21, 28,          # wrist_yaw      L / R
    ]

    # ── default local policy directory ────────────────────────────────────────
    # Points to the sibling g1_locomotion_policy/ folder next to g1_standalone.py.
    # Expected files: g1_policy.pt  +  g1_env.yaml
    _DEFAULT_LOCAL_POLICY_DIR: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),  # …/robots/
        "..",  # …/examples/
        "..",  # …/policy/
        "..",  # …/robot/
        "..",  # …/isaacsim/
        "..",  # ext root
        "..",  # isaac-sim root
        "standalone_examples",
        "api",
        "isaacsim.robot.policy.examples",
        "g1_locomotion_policy",
    )

    # ─────────────────────────────────────────────────────────────────────────
    def __init__(
        self,
        prim_path: str,
        root_path: Optional[str] = None,
        name: str = "g1",
        usd_path: Optional[str] = None,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
        local_policy_dir: Optional[str] = _DEFAULT_LOCAL_POLICY_DIR,
    ) -> None:
        """Initialize G1-29dof robot and load the flat terrain velocity locomotion policy.

        Policy file resolution order
        ----------------------------
        1. ``local_policy_dir/g1_policy.pt``  — used when the file exists locally.
        2. Isaac Nucleus path                  — fallback when local dir is absent or
                                                 ``local_policy_dir=None``.

        Args:
            prim_path: Prim path of the robot on the stage.
            root_path: Path to the articulation root (defaults to prim_path).
            name: Name of the robot articulation.
            usd_path: Full USD asset path; falls back to Isaac Nucleus default.
            position: Initial world position [x, y, z].
            orientation: Initial quaternion [w, x, y, z].
            local_policy_dir: Directory containing ``g1_policy.pt`` and ``g1_env.yaml``.
                              Pass ``None`` to force Nucleus loading.
        """
        assets_root_path = get_assets_root_path()
        if usd_path is None:
            usd_path = assets_root_path + "/Isaac/Robots/Unitree/G1/g1.usd"
        super().__init__(name, prim_path, root_path, usd_path, position, orientation)

        # ── resolve policy file paths ──────────────────────────────────────────
        _policy_path = None
        _env_path    = None

        if local_policy_dir is not None:
            _local = Path(local_policy_dir).resolve()
            _pt    = _local / "g1_policy.pt"
            _yaml  = _local / "g1_env.yaml"
            if _pt.exists() and _yaml.exists():
                _policy_path = str(_pt)
                _env_path    = str(_yaml)
                print(f"[G1FlatTerrainPolicy] Loading policy from local dir: {_local}")

        if _policy_path is None:
            _policy_path = assets_root_path + "/Isaac/Samples/Policies/G1_Policies/g1_policy.pt"
            _env_path    = assets_root_path + "/Isaac/Samples/Policies/G1_Policies/g1_env.yaml"
            print(f"[G1FlatTerrainPolicy] Local files not found — falling back to Nucleus.")

        self.load_policy(_policy_path, _env_path)

        # ── runtime state ─────────────────────────────────────────────────────
        self._action_scale = 0.25

        # Integer index array for fast numpy fancy-indexing (policy ↔ DOF order)
        self._joint_ids = np.array(self.JOINT_IDS_MAP, dtype=np.int64)

        # Observation history: (HISTORY_LENGTH, OBS_PER_STEP), oldest frame first
        self._obs_history = np.zeros((self.HISTORY_LENGTH, self.OBS_PER_STEP), dtype=np.float32)

        # Previous action in POLICY order (fed back as last_action obs term)
        self._previous_action = np.zeros(self.NUM_JOINTS, dtype=np.float32)

        self._policy_counter = 0

    # ── observation ───────────────────────────────────────────────────────────

    def _compute_single_step_obs(self, command: np.ndarray) -> np.ndarray:
        """Build one 96-dim observation frame.

        Joint data is fetched in Isaac Sim DOF order (== SDK order for standard
        Unitree G1 USDs), then reindexed to POLICY order via JOINT_IDS_MAP.

        Layout:
          [0:3]   base_ang_vel   × 0.2
          [3:6]   projected_gravity
          [6:9]   velocity_commands
          [9:38]  joint_pos_rel  (policy order)  = q[policy] – q_default[policy]
          [38:67] joint_vel_rel  (policy order)  = dq[policy] × 0.05
          [67:96] last_action    (policy order)
        """
        _, q_IB   = self.robot.get_world_pose()
        ang_vel_I = self.robot.get_angular_velocity()

        R_BI      = quat_to_rot_matrix(q_IB).T
        ang_vel_b = R_BI @ ang_vel_I
        gravity_b = R_BI @ np.array([0.0, 0.0, -1.0])

        # DOF-order → policy-order via fancy indexing
        sdk_pos = self.robot.get_joint_positions()   # (29,) DOF order
        sdk_vel = self.robot.get_joint_velocities()  # (29,) DOF order
        sdk_def = np.array(self.default_pos)         # (29,) DOF order

        policy_pos = sdk_pos[self._joint_ids]   # (29,) policy order
        policy_vel = sdk_vel[self._joint_ids]   # (29,) policy order
        policy_def = sdk_def[self._joint_ids]   # (29,) policy order

        obs = np.zeros(self.OBS_PER_STEP, dtype=np.float32)
        obs[0:3]   = ang_vel_b * 0.2
        obs[3:6]   = gravity_b
        obs[6:9]   = command
        obs[9:38]  = policy_pos - policy_def     # joint_pos_rel (policy order)
        obs[38:67] = policy_vel * 0.05           # joint_vel_rel (policy order)
        obs[67:96] = self._previous_action       # last_action   (policy order)
        return obs

    def _compute_observation(self, command: np.ndarray) -> np.ndarray:
        """Append latest frame and return full 480-dim stacked observation."""
        self._obs_history[:-1] = self._obs_history[1:]
        self._obs_history[-1]  = self._compute_single_step_obs(command)
        return self._obs_history.flatten()

    # ── forward ───────────────────────────────────────────────────────────────

    def forward(self, dt: float, command: np.ndarray) -> None:
        """Compute and apply joint position targets.

        The policy outputs 29 values in POLICY order.  They are scattered into
        DOF order using JOINT_IDS_MAP before being sent to the articulation:

            dof_target[JOINT_IDS_MAP[i]] = dof_default[JOINT_IDS_MAP[i]] + action[i] × 0.25

        Args:
            dt: Physics timestep (seconds).
            command: Base velocity command [v_x, v_y, w_z].
        """
        if self._policy_counter % self._decimation == 0:
            obs           = self._compute_observation(command)
            self.action   = self._compute_action(obs)       # (29,) policy order
            self._previous_action = self.action.copy()

        # Scatter policy-order actions into DOF-order targets
        targets = np.array(self.default_pos, dtype=np.float32)          # (29,) DOF order
        targets[self._joint_ids] += self.action * self._action_scale    # scatter-add

        self.robot.apply_action(ArticulationAction(joint_positions=targets))
        self._policy_counter += 1

    # ── initialize ────────────────────────────────────────────────────────────

    def initialize(self) -> None:
        """Initialize articulation with YAML gains; use USD articulation root props."""
        return super().initialize(set_articulation_props=False)
