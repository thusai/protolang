import openai
import os
import random
from demo import run_and_analyze_sift

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_speaker(state, round_number, model="gpt-3.5-turbo"):
    """Speaker agent using OpenAI API to generate signals for states"""
    prompt = f"""
    You are a speaker in a communication game. You need to create a signal that will help the listener choose the correct action.
    
    Current state: {state}
    Round number: {round_number}
    
    Generate a short, clear signal (1-3 words) that best represents this state.
    Response format: Just the signal text, nothing else.
    """
    
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.3
    )
    
    signal = response.choices[0].message.content.strip()
    return signal

def openai_listener(signal, history, round_number, action_space, model="gpt-3.5-turbo"):
    """Listener agent using OpenAI API to interpret signals and select actions"""
    # Format history for the prompt
    history_text = ""
    for sig, action in history.items():
        history_text += f"Signal: '{sig}' → Action: '{action}'\n"
    
    prompt = f"""
    You are a listener in a communication game. Based on the signal you receive, choose the most appropriate action.
    
    Received signal: "{signal}"
    
    Available actions:
    {', '.join(action_space)}
    
    Previous signal-action pairs:
    {history_text if history else "None"}
    
    Response format: Return exactly one of the available actions listed above, nothing else.
    """
    
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0.2
    )
    
    action = response.choices[0].message.content.strip()
    
    # Ensure the response is in the action space
    if action not in action_space:
        action = random.choice(action_space)
        
    return action

def run_ai_agent_simulation(num_rounds=10, speaker_model="gpt-3.5-turbo", listener_model="gpt-3.5-turbo"):
    """Run a simulation using OpenAI-powered agents"""
    # Define state and action spaces
    state_space = ["Red Circle", "Blue Square", "Green Triangle", "Yellow Star"]
    action_space = ["Pick Top-Left", "Pick Top-Right", "Pick Bottom-Left", "Pick Bottom-Right"]
    
    # Create the strategy functions with model specification
    def speaker_strategy(state, round_number):
        return openai_speaker(state, round_number, model=speaker_model)
    
    def listener_strategy(signal, history, round_number):
        return openai_listener(signal, history, round_number, action_space, model=listener_model)
    
    # Run the simulation
    print(f"Running simulation with {num_rounds} rounds:")
    print(f"Speaker model: {speaker_model}")
    print(f"Listener model: {listener_model}")
    
    history, analysis = run_and_analyze_sift(
        num_rounds, state_space, action_space, 
        speaker_strategy=speaker_strategy, 
        listener_strategy=listener_strategy
    )
    
    return history, analysis

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
        
    # Run simulation with AI agents
    history, analysis = run_ai_agent_simulation(num_rounds=5)
    
    # Print results
    print("\n--- AI Agent Simulation Results ---")
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
