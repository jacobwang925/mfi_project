import numpy as np
import torch
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from robot import Robot
from human import Human
from dynamics import DIDynamics

def get_robot_plan(robot : Robot, horizon=5, return_controls=False):
    # ignore safe control for plan
    robot_x = robot.x
    robot_states = np.zeros((robot.dynamics.n, horizon))
    robot_controls = np.zeros((robot.dynamics.m, horizon))
    for i in range(horizon):
        goal_u = robot.dynamics.get_goal_control(robot_x, robot.goal)
        robot_x = robot.dynamics.step(robot_x, goal_u)
        robot_states[:,[i]] = robot_x
        robot_controls[:,[i]] = goal_u

    if return_controls:
        return robot_states, robot_controls
    return robot_states

def get_empty_robot_plan(robot, horizon=5):
    robot_states = np.hstack([robot.x for i in range(horizon)])

    return robot_states

def process_model_input(xh_hist, xr_hist, xr_plan, goals):
    traj_hist = torch.tensor(np.hstack((xh_hist.T, xr_hist.T))).float().unsqueeze(0)
    xr_plan = torch.tensor(xr_plan).float().unsqueeze(0)
    goals = torch.tensor(goals).float().unsqueeze(0)

    return traj_hist, xr_plan, goals

def overlay_timesteps(ax, xh_traj, xr_traj, goals, n_steps=100, h_cmap="Blues", r_cmap="Reds"):
    
    if len(xh_traj) > 0:
        # human trajectory
        points = xh_traj[[0,2],:].T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        n_steps = xh_traj.shape[1]
        norm = plt.Normalize(0, n_steps)
        lc = LineCollection(segments, cmap=h_cmap, norm=norm, alpha=0.5)
        # Set the values used for colormapping
        lc.set_array(np.arange(n_steps+1))
        lc.set_linewidth(2)
        line = ax.add_collection(lc)
        # fig.colorbar(line, ax=ax)

    # robot trajectory
    if len(xr_traj) > 0:
        points = xr_traj[[0,2],:].T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        n_steps = xr_traj.shape[1]
        norm = plt.Normalize(0, n_steps)
        lc = LineCollection(segments, cmap=r_cmap, norm=norm)
        # Set the values used for colormapping
        lc.set_array(np.arange(n_steps+1))
        lc.set_linewidth(2)
        line = ax.add_collection(lc)

    ax.scatter(goals[0], goals[2], c=['#3A637B', '#C4A46B', '#FF5A00'])

    ax.set_ylim(-10, 10)
    ax.set_xlim(-10, 10)


def initialize_problem(ts=0.05):
    # create initial conditions for human and robot, construct objects
    # randomly initialize xh0, xr0, goals
    # xh0 = np.random.uniform(size=(4, 1))*20 - 10
    # xh0[[1,3]] = np.zeros((2, 1))
    # xr0 = np.random.uniform(size=(4, 1))*20 - 10
    # xr0[[1,3]] = np.zeros((2, 1))

    # # xh0 = np.array([[-2.5, 0.0, -5.0, 0.0]]).T
    # # xr0 = np.array([[0.0, 0.0, -5.0, 0.0]]).T

    # goals = np.random.uniform(size=(4, 3))*20 - 10
    # goals[[1,3],:] = np.zeros((2, 3))
    # r_goal = goals[:,[np.random.randint(0,3)]]

    # creating human and robot
    xh0 = np.array([[0, 0.0, -5, 0.0]]).T
    xr0 = np.array([[0.0, 0.0, 0.0, 0.0]]).T

    goals = np.array([
        [5.0, 0.0, 0.0, 0.0],
        [-5.0, 0.0, 5.0, 0.0],
        [5.0, 0.0, 5.0, 0.0],
    ]).T
    r_goal = goals[:,[0]]

    dynamics_h = DIDynamics(ts)
    human = Human(xh0, dynamics_h, goals)
    dynamics_r = DIDynamics(ts)
    robot = Robot(xr0, dynamics_r, r_goal)

    # robot.dmin=0.5
    
    return human, robot, goals