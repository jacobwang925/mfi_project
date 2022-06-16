import numpy as np
import matplotlib.pyplot as plt

from dynamics import DIDynamics
from human import Human
from robot import Robot

def test_sim():
    ts = 0.1
    x0_h = np.array([[0.5, 0.0, 0.0, 0.0]]).T
    x0_r = np.array([[2.0, 0.0, 2.0, 0.0]]).T

    goals_h = np.array([[5.0, 0.0, 5.0, 0.0],
                        [6.0, 0.0, 4.0, 0.0]]).T
    goal_r = np.array([[5.0, 0.0, 5.0, 0.0]]).T

    dynamics_h = DIDynamics(ts)
    human = Human(x0_h, dynamics_h, goals_h)

    dynamics_r = DIDynamics(ts)
    robot = Robot(x0_r, dynamics_r, goal_r)

    fig, ax = plt.subplots()

    for t in range(200):
        print(human.get_goal().flatten())

        uh = human.get_u(robot.x)
        ur = robot.get_u()

        xh = human.step(uh)
        xr = robot.step(ur)

        ax.cla()
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

        ax.scatter(goals_h[0], goals_h[2])
        
        ax.scatter(xh[0], xh[2])
        ax.scatter(xr[0], xr[2])

        plt.pause(0.01)
    # plt.show()

def simulate_interaction(horizon=200):
    ts = 0.05

    # randomly initialize xh0, xr0, goals
    xh0 = np.random.uniform(size=(4, 1))*20 - 10
    xh0[[1,3]] = np.zeros((2, 1))
    xr0 = np.random.uniform(size=(4, 1))*20 - 10
    xr0[[1,3]] = np.zeros((2, 1))

    goals = np.random.uniform(size=(4, 3))*20 - 10
    goals[[1,3],:] = np.zeros((2, 3))
    r_goal = goals[:,[np.random.randint(0,3)]]

    dynamics_h = DIDynamics(ts)
    human = Human(xh0, dynamics_h, goals)
    dynamics_r = DIDynamics(ts)
    robot = Robot(xr0, dynamics_r, r_goal)

    xh_traj = np.zeros((4, horizon))
    xr_traj = np.zeros((4, horizon))
    h_goals = np.zeros((4, horizon))
    h_goal_reached = np.zeros((1, horizon))

    for i in range(horizon):
        # save data
        xh_traj[:,[i]] = human.x
        xr_traj[:,[i]] = robot.x
        h_goals[:,[i]] = human.get_goal()
        # check if human reached its goal
        if np.linalg.norm(human.x - human.get_goal()) < 0.1:
            h_goal_reached[:,i] = 1

        # take step
        uh = human.get_u(robot.x)
        if i == 0:
            ur = robot.get_u(human.x, robot.x, human.x)
        else:
            ur = robot.get_u(human.x, xr_traj[:,[i-1]], xh_traj[:,[i-1]])

        xh = human.step(uh)
        xr = robot.step(ur)

    return xh_traj, xr_traj, goals, h_goals, r_goal, h_goal_reached

def create_dataset(n_trajectories=1):
    horizon = 200

    all_xh_traj = np.zeros((4, horizon, 0))
    all_xr_traj = np.zeros((4, horizon, 0))
    all_goals = np.zeros((4, 3, 0))
    all_h_goals = np.zeros((4, horizon, 0))
    all_r_goals = np.zeros((4, 1, 0))
    all_h_goal_reached = np.zeros((1, horizon, 0))

    # labels
    goal_reached = []
    goal_idx = []

    for i in range(n_trajectories):
        xh_traj, xr_traj, goals, h_goals, r_goal, h_goal_reached = simulate_interaction(horizon=horizon)

        # save trajectories
        all_xh_traj = np.dstack((all_xh_traj, xh_traj))
        all_xr_traj = np.dstack((all_xr_traj, xr_traj))
        all_goals = np.dstack((all_goals, goals))
        all_h_goals = np.dstack((all_h_goals, h_goals))
        all_r_goals = np.dstack((all_r_goals, r_goal))
        all_h_goal_reached = np.dstack((all_h_goal_reached, h_goal_reached))
        # save whether goal was reached
        goal_reached.append(h_goal_reached[0,-1])
        # find index of goal
        gg = h_goals[:,[-1]]
        goal_idx.append(np.argmin(np.linalg.norm(goals - gg, axis=0)))

    # process data

    return all_xh_traj, all_xr_traj, all_h_goals, all_r_goals, np.array(goal_reached), np.array(goal_idx), all_goals

def save_data(path="./data/simulated_interactions.npz"):

    all_xh_traj, all_xr_traj, all_h_goals, all_r_goals, \
        goal_reached, goal_idx, all_goals = create_dataset(n_trajectories=1000)

    np.savez(path, xh_traj=all_xh_traj, xr_traj=all_xr_traj, goal_reached=goal_reached, goal_idx=goal_idx, goals=all_goals)

if __name__ == "__main__":
    save_data()
