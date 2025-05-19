import random

def create_sift_simulation(num_rounds, state_space, action_space, speaker_strategy=None, listener_strategy=None):
    """
    Simulates the Simple Instruction Following Test (SIFT) between two AI agents.

    Args:
        num_rounds: The number of communication rounds to simulate.
        state_space: A list of possible states (e.g., ["Red Circle", "Blue Square", "Green Triangle", "Yellow Star"]).
        action_space: A list of possible actions (e.g., ["Pick Top-Left", "Pick Top-Right", "Pick Bottom-Left", "Pick Bottom-Right"]).
        speaker_strategy: A function that takes the current state and round number, and returns a signal (string).
                        If None, uses a random signal from a predefined set.
        listener_strategy: A function that takes the received signal, the history of signals and actions, and the round number,
                        and returns an action (string). If None, uses a simple mapping and defaults.

    Returns:
        A list of dictionaries, where each dictionary represents a communication round
        and contains the state, signal, action, and whether the action was correct.
    """

    # 1. Generate a set of unique signals.
    num_signals = len(state_space)
    signals = [f"signal_{i}" for i in range(num_signals)]  # Ensure unique signals

    # 2. Create a default mapping of states to signals (used if speaker_strategy is None).
    state_signal_mapping = dict(zip(state_space, signals))
    signal_action_mapping = dict(zip(signals, action_space)) #default mapping

    # 3. Initialize memory for the listener to track signal-action history.
    listener_memory = {}  # Maps signals to actions taken

    # 4. Define default speaker and listener strategies
    def default_speaker_strategy(state, round_number):
        """
        Simple speaker strategy:  Always use the same signal for a given state.
        """
        return state_signal_mapping[state]

    def default_listener_strategy(signal, history, round_number):
        """
        Simple listener strategy:
        - If the signal is seen before, repeat the previous action.
        - If the signal is new, choose an action randomly.
        """
        if signal in history:
            return history[signal]
        else:
            # Exploration strategy:  Slightly less random than uniform.
            available_actions = list(action_space)
            if available_actions:
                chosen_action = random.choice(available_actions)
                return chosen_action
            else:
                return random.choice(action_space) # Fallback

    # 5.  Use default strategies if none are provided.
    if speaker_strategy is None:
        speaker_strategy = default_speaker_strategy
    if listener_strategy is None:
        listener_strategy = default_listener_strategy

    # 6. Run the simulation for the specified number of rounds.
    communication_history = []
    for round_number in range(1, num_rounds + 1):
        # a. Speaker observes a random state.
        state = random.choice(state_space)

        # b. Speaker generates a signal based on its strategy.
        signal = speaker_strategy(state, round_number)

        # c. Listener receives the signal and chooses an action.
        action = listener_strategy(signal, listener_memory, round_number)

        # d. Determine if the action was correct.
        correct_action = signal_action_mapping.get(signal)  # Use the mapping.
        is_correct = action == correct_action

        # e. Store the signal and action in the listener's memory.
        listener_memory[signal] = action

        # f. Record the communication round.
        communication_history.append({
            "round": round_number,
            "state": state,
            "signal": signal,
            "action": action,
            "is_correct": is_correct,
        })
    return communication_history

def analyze_results(history, state_space, action_space):
    """
    Analyzes the results of the SIFT simulation.

    Args:
        history: The list of dictionaries returned by the run_sift_simulation function.
        state_space:  list of possible states
        action_space: list of actions

    Returns:
        A dictionary containing analysis of the simulation.
    """
    num_rounds = len(history)
    correct_count = sum(round_data["is_correct"] for round_data in history)
    accuracy = correct_count / num_rounds if num_rounds > 0 else 0

    # Check for signal consistency and ambiguity.
    signal_consistency = {}
    signal_ambiguity = {}
    for state in state_space:
        signal_consistency[state] = []
    for round_data in history:
        state = round_data["state"]
        signal = round_data["signal"]
        if state in signal_consistency:
            signal_consistency[state].append(signal)

    for state in signal_consistency:
        signals_for_state = signal_consistency[state]
        if signals_for_state:
            first_signal = signals_for_state[0]
            all_same = all(signal == first_signal for signal in signals_for_state)
            signal_consistency[state] = all_same
        else:
            signal_consistency[state] = False

    for signal in set(round_data["signal"] for round_data in history):
        states_for_signal = []
        for round_data in history:
            if round_data["signal"] == signal:
                states_for_signal.append(round_data["state"])
        signal_ambiguity[signal] = len(set(states_for_signal)) > 1


    analysis = {
        "num_rounds": num_rounds,
        "correct_count": correct_count,
        "accuracy": accuracy,
        "signal_consistency": signal_consistency,
        "signal_ambiguity": signal_ambiguity,
    }
    return analysis

def run_and_analyze_sift(num_rounds, state_space, action_space, speaker_strategy=None, listener_strategy=None):
    """
    Runs the SIFT simulation and analyzes the results.

    Args:
        num_rounds: The number of communication rounds to simulate.
        state_space: A list of possible states.
        action_space: A list of possible actions.
        speaker_strategy:  A function defining speaker behavior
        listener_strategy: A function defining listener behavior

    Returns:
        A tuple containing the simulation history and the analysis.
    """
    history = create_sift_simulation(num_rounds, state_space, action_space, speaker_strategy, listener_strategy)
    analysis = analyze_results(history, state_space, action_space)
    return history, analysis

if __name__ == "__main__":
    # 1. Define the state and action spaces.
    state_space = ["Red Circle", "Blue Square", "Green Triangle", "Yellow Star"]
    action_space = ["Pick Top-Left", "Pick Top-Right", "Pick Bottom-Left", "Pick Bottom-Right"]
    num_rounds = 10

    # 2. Run the simulation with default strategies.
    history, analysis = run_and_analyze_sift(num_rounds, state_space, action_space)

    # 3. Print the results.
    print("\n--- Simulation Results ---")
    for round_data in history:
        print(f"Round {round_data['round']}:")
        print(f"  State: {round_data['state']}")
        print(f"  Signal: {round_data['signal']}")
        print(f"  Action: {round_data['action']}")
        print(f"  Correct: {round_data['is_correct']}")

    print("\n--- Analysis ---")
    print(f"Number of Rounds: {analysis['num_rounds']}")
    print(f"Correct Actions: {analysis['correct_count']}")
    print(f"Accuracy: {analysis['accuracy']:.2f}")
    print(f"Signal Consistency: {analysis['signal_consistency']}")
    print(f"Signal Ambiguity: {analysis['signal_ambiguity']}")

    # Example of running with a custom strategy
    def speaker_strategy_alt(state, round_number):
        if state == "Red Circle":
            return "red_circle"
        elif state == "Blue Square":
            return "blue_square"
        elif state == "Green Triangle":
            return "green_triangle"
        elif state == "Yellow Star":
            return "yellow_star"
        return "unknown"

    def listener_strategy_alt(signal, history, round_number):
      if signal == "red_circle":
        return "Pick Top-Left"
      elif signal == "blue_square":
        return "Pick Top-Right"
      elif signal == "green_triangle":
        return "Pick Bottom-Left"
      elif signal == "yellow_star":
        return "Pick Bottom-Right"
      else:
        return random.choice(action_space)

    print("\n--- Running with alternate strategies ---")
    history_alt, analysis_alt = run_and_analyze_sift(num_rounds, state_space, action_space, speaker_strategy_alt, listener_strategy_alt)

    print("\n--- Simulation Results with Alternate Strategies---")
    for round_data in history_alt:
        print(f"Round {round_data['round']}:")
        print(f"  State: {round_data['state']}")
        print(f"  Signal: {round_data['signal']}")
        print(f"  Action: {round_data['action']}")
        print(f"  Correct: {round_data['is_correct']}")

    print("\n--- Analysis with Alternate Strategies ---")
    print(f"Number of Rounds: {analysis_alt['num_rounds']}")
    print(f"Correct Actions: {analysis_alt['correct_count']}")
    print(f"Accuracy: {analysis_alt['accuracy']:.2f}")
    print(f"Signal Consistency: {analysis_alt['signal_consistency']}")
    print(f"Signal Ambiguity: {analysis_alt['signal_ambiguity']}")

