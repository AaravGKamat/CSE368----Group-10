#/usr/bin/python3
#Goal:
#Train a Taxi agent using Q-learning to improve over time.

#Instructions:
#1. Complete all the TODO sections.
#2. Run your code to train and test the agent.
#3. Observe how the taxi improves its performance!


# Step 1: Import libraries and initialize environment
import gymnasium as gym
import numpy as np
import random

# TODO: Create the Taxi-v3 environment
# env = ???

# TODO: Get number of states and actions
# n_states = ???
# n_actions = ???

# Step 2: Create the Q-table (all zeros)
# scores = ???

# Q-learning parameters (you may adjust these)
alpha = 0.1      # Learning rate
gamma = 0.9      # Discount factor
epsilon = 1.0    # Exploration rate
epsilon_decay = 0.9995
epsilon_min = 0.1
episodes = 2000
max_steps = 100

# Step 3: Training loop
for episode in range(episodes):
    # TODO: Reset environment and initialize variables
    # state, info = ???
    total_reward = 0

    for step in range(max_steps):
        # TODO: Choose an action (explore or exploit)
        # if random.uniform(0, 1) < epsilon:
        #     action = ???
        # else:
        #     action = ???

        # TODO: Take the action
        # next_state, reward, done, truncated, info = ???

        # TODO: Update Q-table
        # best_next = ???
        # scores[state, action] = ???

        # TODO: Update state and reward tracker
        # state = ???
        # total_reward += ???

        # if done or truncated:
        #     break

    # TODO: Decay epsilon
    # epsilon = ???

    if (episode + 1) % 200 == 0:
        print(f"Episode {episode+1}/{episodes} complete")

print("\nTraining complete!")

# Step 4: Test the trained agent
state, info = env.reset()
done = False
total_test_reward = 0

print("\n--- TESTING TRAINED AGENT ---")
for step in range(max_steps):
    # TODO: Always pick the best action
    # action = ???

    next_state, reward, done, truncated, info = env.step(action)
    total_test_reward += reward
    env.render()

    if done or truncated:
        break
    state = next_state

print("Total reward after training:", total_test_reward)
env.close()

