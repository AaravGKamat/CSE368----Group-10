# /usr/bin/python3
# Goal:
# Train a Taxi agent using Q-learning to improve over time.

# Instructions:
# 1. Complete all the TODO sections.
# 2. Run your code to train and test the agent.
# 3. Observe how the taxi improves its performance!


# Step 1: Import libraries and initialize environment
import gymnasium as gym
import numpy as np
import random
import matplotlib.pyplot as plt

# Create the Taxi-v3 environment
env = gym.make("Taxi-v3", render_mode="ansi")

# Get number of states and actions
n_states = env.observation_space.n
n_actions = env.action_space.n

# Step 2: Create the Q-table (all zeros)
Q_scores = np.zeros((n_states, n_actions))

# Q-learning parameters (you may adjust these)
alpha = 0.1      # Learning rate
gamma = 0.9      # Discount factor
epsilon = 1.0    # Exploration rate
epsilon_decay = 0.9995
epsilon_min = 0.1
episodes = 2000
max_steps = 100


# To store total rewards per episode
rewards = []

# Step 3: Training loop
for episode in range(episodes):
    # Reset environment and initialize variables
    state, info = env.reset()
    total_reward = 0

    for step in range(max_steps):
        # TODO: Choose an action (explore or exploit)
        if random.uniform(0, 1) < epsilon:  # Exploration
            action = env.action_space.sample()

        else:  # Exploitation
            action = np.argmax(Q_scores[state])

        # Take the action

        next_state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        # CHECK
        # print(env.render())

        # Update Q-table
        best_next_action = np.argmax(Q_scores[next_state])
        Q_scores[state, action] += alpha * (reward + gamma * (
            Q_scores[next_state, best_next_action]) - Q_scores[state, action])

        # Update state and reward tracker
        state = next_state
        total_reward += float(reward)

        if done:
            break

    # TODO: Decay epsilon
    epsilon = max(epsilon_min, epsilon_decay*epsilon)
    # Save total reward for this episode
    rewards.append(total_reward)

    if (episode + 1) % 200 == 0:
        print(f"Episode {episode+1}/{episodes} complete")


print("\nTraining complete!")
print("\nQ-Table:\n")
print(Q_scores)

# Step 4: Test the trained agent
state, info = env.reset()
done = False
total_test_reward = 0

print("\n--- TESTING TRAINED AGENT ---")
for step in range(max_steps):
    # TODO: Always pick the best action
    action = np.argmax(Q_scores[state])
    next_state, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

    total_test_reward += float(reward)

    print(env.render())

    if done:
        break
    state = next_state

print("Total reward after training:", total_test_reward)
env.close()

# # Test Case 1 (our base case):
# Parameters used:
# alpha = 0.1      # Learning rate
# gamma = 0.9      # Discount factor
# epsilon = 1.0    # Exploration rate
# epsilon_decay = 0.9995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 100
# Number of runs: 10
# # Results:
# Training Results: 7, -100, 7, 9, -100, 11, 8, 12, 6, 7
# Maximum reward: 12
# Average reward (excluding failed training results): 8.375
# Average reward (including failed training results): -13.3
# Number of failed training runs (-100 total reward): 2

# # Test Case 2 (higher maximum steps):
# Parameters used:
# alpha = 0.1      # Learning rate
# gamma = 0.9      # Discount factor
# epsilon = 1.0    # Exploration rate
# epsilon_decay = 0.9995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 200
# Number of runs: 10
# # Results:
# Training Results: 7, 7, 8, 8, -200, 9, 7, 9, 6, 10
# Maximum reward: 10
# Average reward (excluding failed training results): 7.888...
# Average reward (including failed training results): -12.9
# Number of failed training runs (negative total reward): 1

# # Test Case 3 (half learning rate)
# alpha = 0.05      # Learning rate
# gamma = 0.9      # Discount factor
# epsilon = 1.0    # Exploration rate
# epsilon_decay = 0.9995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 100
# Number of runs: 10
# # Results:
# Training Results: -100, -100, -100, 12, -100, 11, 15, -100, -100, -100
# Maximum reward: 15
# Average reward (excluding failed training results): 12.666...
# Average reward (including failed training results): -66.2
# Number of failed training runs (-100 total reward): 7

# # Test Case 4 (higher discount):
# Parameters used:
# alpha = 0.1      # Learning rate
# gamma = 0.95      # Discount factor
# epsilon = 1.0    # Exploration rate
# epsilon_decay = 0.9995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 100
# Number of runs: 10
# # Results:
# Training Results: 11, -100, 9, -100, 9, 10, 12, 9, 6, 10
# Maximum reward: 12
# Average reward (excluding failed training results): 9.5
# Average reward (including failed training results): -12.4
# Number of failed training runs (-100 total reward): 2

# # Test Case 5 (less exploration):
# Parameters used:
# alpha = 0.1      # Learning rate
# gamma = 0.9      # Discount factor
# epsilon = 0.8    # Exploration rate
# epsilon_decay = 0.9995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 100
# Number of runs: 10
# # Results:
# Training Results: 10, -100, 7, 10, 5, -100, 10, 7, 9, 10
# Maximum reward: 10
# Average reward (excluding failed training results): 8.5
# Average reward (including failed training results): -13.2
# Number of failed training runs (-100 total reward): 2

# # Test Case 6 (lower decay):
# Parameters used:
# alpha = 0.1      # Learning rate
# gamma = 0.9      # Discount factor
# epsilon = 1.0    # Exploration rate
# epsilon_decay = 0.995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 100
# Number of runs: 10
# # Results:
# Training Results: -100, 9, 10, 11, 8, -100, -100, -100, -100, 9
# Maximum reward: 11
# Average reward (excluding failed training results): 9.4
# Average reward (including failed training results): -45.3
# Number of failed training runs (-100 total reward): 5

# # Test Case 7 (synthesis, utilizes the successful tests while disregarding the unsuccessful tests):
# Parameters used:
# alpha = 0.1      # Learning rate
# gamma = 0.95      # Discount factor
# epsilon = 1.0    # Exploration rate
# epsilon_decay = 0.99995
# epsilon_min = 0.1
# episodes = 2000
# max_steps = 200
# Number of runs: 10
# # Results:
# Training Results: 12, 10, -200, 8, 7, 4, 10, 8, 9, 9
# Maximum reward: 12
# Average reward (excluding failed training results): 8.555...
# Average reward (including failed training results): -12.3
# Number of failed training runs (-100 total reward): 1
