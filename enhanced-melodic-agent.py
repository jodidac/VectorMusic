import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum

@dataclass
class MusicalState:
    """Represents the complete musical state of an agent"""
    pitch: float
    time: float
    energy: float
    tension: float
    velocity: float
    phase: float

class FieldType(Enum):
    HARMONIC = "harmonic"
    RHYTHMIC = "rhythmic"
    ENERGETIC = "energetic"
    TENSION = "tension"

class MelodicAgent:
    """
    Enhanced melodic agent with physical properties and field interactions.
    Implements the vector music mathematical framework.
    """
    
    def __init__(self, 
                 num_octaves: int = 2,
                 energy_capacity: float = 100.0,
                 tension_threshold: float = 0.8,
                 learning_rate: float = 0.01):
        """
        Initialize a melodic agent with extended capabilities.
        
        Args:
            num_octaves: Number of octaves in pitch range
            energy_capacity: Maximum energy capacity
            tension_threshold: Maximum tension before requiring resolution
            learning_rate: Rate of adaptation to field changes
        """
        # Basic musical properties
        self.notes_per_octave = 12
        self.num_octaves = num_octaves
        self.total_notes = self.notes_per_octave * num_octaves
        
        # Physical properties
        self.energy_capacity = energy_capacity
        self.tension_threshold = tension_threshold
        self.learning_rate = learning_rate
        
        # State initialization
        self.state = MusicalState(
            pitch=0.0,
            time=0.0,
            energy=energy_capacity,
            tension=0.0,
            velocity=0.0,
            phase=0.0
        )
        
        # Historical data
        self.trajectory: List[MusicalState] = []
        self.memory: Dict[Tuple[int, int], float] = {}  # (state, action) -> value
        
        # Field interactions
        self.active_fields: Dict[FieldType, np.ndarray] = {}
        self.field_weights: Dict[FieldType, float] = {
            FieldType.HARMONIC: 1.0,
            FieldType.RHYTHMIC: 0.8,
            FieldType.ENERGETIC: 0.6,
            FieldType.TENSION: 0.7
        }

    def register_field(self, field_type: FieldType, field_tensor: np.ndarray) -> None:
        """Register a new field influence on the agent"""
        self.active_fields[field_type] = field_tensor

    def compute_field_force(self, state: MusicalState) -> np.ndarray:
        """
        Compute the total force from all active fields at current state.
        Implements the field interaction equations from the mathematical framework.
        """
        total_force = np.zeros(4)  # 4-dimensional force vector
        
        for field_type, field in self.active_fields.items():
            # Contract field tensor with state vector
            state_vector = np.array([state.pitch, state.time, 
                                   state.energy, state.tension])
            field_force = np.tensordot(field, state_vector, axes=1)
            
            # Apply field-specific weighting
            total_force += self.field_weights[field_type] * field_force
            
        return total_force

    def evolve_state(self, dt: float) -> None:
        """
        Evolve the agent's state according to physical laws and field forces.
        Implements the geodesic equations from the mathematical framework.
        """
        # Compute field forces
        force = self.compute_field_force(self.state)
        
        # Update state using semi-implicit Euler integration
        new_state = MusicalState(
            pitch=self.state.pitch + dt * self.state.velocity,
            time=self.state.time + dt,
            energy=self.state.energy - dt * np.abs(force[2]),  # Energy consumption
            tension=self.state.tension + dt * force[3],  # Tension evolution
            velocity=self.state.velocity + dt * force[0],  # Pitch acceleration
            phase=self.state.phase + dt * force[1]  # Rhythmic phase
        )
        
        # Apply constraints
        new_state = self._apply_constraints(new_state)
        
        # Store state
        self.trajectory.append(self.state)
        self.state = new_state

    def _apply_constraints(self, state: MusicalState) -> MusicalState:
        """Apply physical and musical constraints to the state"""
        # Energy constraints
        state.energy = np.clip(state.energy, 0, self.energy_capacity)
        
        # Tension resolution
        if state.tension > self.tension_threshold:
            state.tension *= 0.5  # Simple resolution model
            
        # Pitch range constraints
        state.pitch = np.clip(state.pitch, 0, self.total_notes - 1)
        
        # Phase normalization
        state.phase = state.phase % (2 * np.pi)
        
        return state

    def choose_action(self, available_actions: List[int]) -> int:
        """
        Choose next musical action based on current state and memory.
        Implements a simple reinforcement learning approach.
        """
        if not available_actions:
            return None
            
        # Compute action values
        action_values = []
        current_state_idx = self._discretize_state(self.state)
        
        for action in available_actions:
            state_action = (current_state_idx, action)
            value = self.memory.get(state_action, 0.0)
            action_values.append(value)
            
        # Softmax selection
        probabilities = self._softmax(action_values)
        return np.random.choice(available_actions, p=probabilities)

    def update_memory(self, state_idx: int, action: int, reward: float) -> None:
        """Update agent's memory using TD learning"""
        state_action = (state_idx, action)
        current_value = self.memory.get(state_action, 0.0)
        self.memory[state_action] = current_value + self.learning_rate * (reward - current_value)

    def _discretize_state(self, state: MusicalState) -> int:
        """Convert continuous state to discrete index for memory storage"""
        pitch_idx = int(state.pitch) % self.total_notes
        energy_idx = int(state.energy / self.energy_capacity * 10)
        tension_idx = int(state.tension / self.tension_threshold * 10)
        phase_idx = int(state.phase / (2 * np.pi) * 8)
        
        return hash((pitch_idx, energy_idx, tension_idx, phase_idx))

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Compute softmax probabilities"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()

    def get_state_summary(self) -> Dict[str, float]:
        """Return a summary of current state"""
        return {
            'pitch': self.state.pitch,
            'time': self.state.time,
            'energy': self.state.energy,
            'tension': self.state.tension,
            'velocity': self.state.velocity,
            'phase': self.state.phase
        }

    def analyze_trajectory(self) -> Dict[str, float]:
        """Analyze agent's musical trajectory"""
        if not self.trajectory:
            return {}
            
        trajectory_array = np.array([
            [s.pitch, s.energy, s.tension, s.phase] 
            for s in self.trajectory
        ])
        
        return {
            'avg_pitch': np.mean(trajectory_array[:, 0]),
            'pitch_variance': np.var(trajectory_array[:, 0]),
            'energy_usage': np.mean(trajectory_array[:, 1]),
            'avg_tension': np.mean(trajectory_array[:, 2]),
            'phase_coherence': self._compute_phase_coherence(trajectory_array[:, 3])
        }

    def _compute_phase_coherence(self, phases: np.ndarray) -> float:
        """Compute phase coherence metric from trajectory"""
        complex_phases = np.exp(1j * phases)
        return np.abs(np.mean(complex_phases))

# Example usage
if __name__ == "__main__":
    # Create an agent with extended capabilities
    agent = MelodicAgent(num_octaves=2, energy_capacity=100.0)
    
    # Register some example fields
    harmonic_field = np.random.randn(4, 4)  # Simple random field for demonstration
    agent.register_field(FieldType.HARMONIC, harmonic_field)
    
    # Simulate agent evolution
    for t in range(100):
        agent.evolve_state(dt=0.1)
        
    # Analyze results
    trajectory_analysis = agent.analyze_trajectory()
    print("Trajectory Analysis:", trajectory_analysis)
