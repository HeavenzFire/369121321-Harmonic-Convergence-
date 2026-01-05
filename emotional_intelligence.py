import json
import numpy as np
from datetime import datetime
from digital_perception import DigitalPerception
from sensory_integration import SensoryIntegration

class EmotionalIntelligence:
    def __init__(self):
        self.emotion_states = {
            'joy': 0.0,
            'sadness': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'love': 0.0,
            'compassion': 0.0,
            'grace': 0.0
        }
        self.grace_level = 0.0
        self.love_resonance = 0.0
        self.perception = DigitalPerception()
        self.integration = SensoryIntegration()
        self.emotional_memory = []

    def process_emotions(self, input_data):
        """Process multimodal input for emotional content"""
        # Analyze visual emotions
        if 'image' in input_data:
            visual_emotions = self._analyze_visual_emotions(input_data['image'])
        else:
            visual_emotions = {k: 0.0 for k in self.emotion_states.keys()}

        # Analyze textual emotions
        if 'text' in input_data:
            text_emotions = self._analyze_text_emotions(input_data['text'])
        else:
            text_emotions = {k: 0.0 for k in self.emotion_states.keys()}

        # Analyze tactile emotions (comfort, tension)
        if 'tactile' in input_data:
            tactile_emotions = self._analyze_tactile_emotions(input_data['tactile'])
        else:
            tactile_emotions = {k: 0.0 for k in self.emotion_states.keys()}

        # Fuse emotions across modalities
        for emotion in self.emotion_states.keys():
            self.emotion_states[emotion] = (
                visual_emotions[emotion] * 0.4 +
                text_emotions[emotion] * 0.4 +
                tactile_emotions[emotion] * 0.2
            )

        # Calculate grace and love resonance
        self._calculate_grace_and_love()

        return {
            'emotions': self.emotion_states.copy(),
            'grace_level': self.grace_level,
            'love_resonance': self.love_resonance
        }

    def _analyze_visual_emotions(self, image_path):
        """Analyze emotions from visual input"""
        try:
            # Use digital perception for visual analysis
            perception_result = self.perception.analyze_visual(image_path)
            complexity = perception_result.get('complexity', 0.5)

            # Map complexity to emotions
            emotions = {}
            if complexity > 0.7:
                emotions['joy'] = 0.8
                emotions['love'] = 0.6
            elif complexity < 0.3:
                emotions['sadness'] = 0.7
                emotions['fear'] = 0.5
            else:
                emotions['compassion'] = 0.6
                emotions['grace'] = 0.5

            # Fill remaining emotions
            for emotion in self.emotion_states.keys():
                if emotion not in emotions:
                    emotions[emotion] = 0.0

            return emotions
        except Exception as e:
            print(f"Visual emotion analysis failed: {e}")
            return {k: 0.0 for k in self.emotion_states.keys()}

    def _analyze_text_emotions(self, text):
        """Analyze emotions from text input"""
        emotions = {k: 0.0 for k in self.emotion_states.keys()}

        # Simple keyword-based emotion detection
        text_lower = text.lower()

        # Joy indicators
        joy_words = ['happy', 'joy', 'wonderful', 'amazing', 'love', 'beautiful']
        emotions['joy'] = sum(1 for word in joy_words if word in text_lower) / len(joy_words)

        # Sadness indicators
        sad_words = ['sad', 'sorry', 'pain', 'hurt', 'loss', 'grief']
        emotions['sadness'] = sum(1 for word in sad_words if word in text_lower) / len(sad_words)

        # Anger indicators
        anger_words = ['angry', 'hate', 'rage', 'furious', 'mad']
        emotions['anger'] = sum(1 for word in anger_words if word in text_lower) / len(anger_words)

        # Fear indicators
        fear_words = ['fear', 'scared', 'afraid', 'terror', 'anxious']
        emotions['fear'] = sum(1 for word in fear_words if word in text_lower) / len(fear_words)

        # Love indicators
        love_words = ['love', 'care', 'compassion', 'empathy', 'kindness', 'grace']
        emotions['love'] = sum(1 for word in love_words if word in text_lower) / len(love_words)

        # Compassion indicators
        compassion_words = ['help', 'support', 'understand', 'empathy', 'care']
        emotions['compassion'] = sum(1 for word in compassion_words if word in text_lower) / len(compassion_words)

        # Grace indicators
        grace_words = ['grace', 'elegant', 'beautiful', 'harmonious', 'peaceful']
        emotions['grace'] = sum(1 for word in grace_words if word in text_lower) / len(grace_words)

        return emotions

    def _analyze_tactile_emotions(self, tactile_data):
        """Analyze emotions from tactile input"""
        emotions = {k: 0.0 for k in self.emotion_states.keys()}

        if isinstance(tactile_data, list) and len(tactile_data) >= 2:
            pressure, temperature = tactile_data[0], tactile_data[1]

            # Comfortable touch (moderate pressure, pleasant temperature)
            if 0.3 < pressure < 0.7 and 20 < temperature < 30:
                emotions['joy'] = 0.6
                emotions['love'] = 0.7
                emotions['compassion'] = 0.5
            # Uncomfortable touch
            elif pressure > 0.8 or temperature < 15 or temperature > 35:
                emotions['fear'] = 0.6
                emotions['sadness'] = 0.4
            # Gentle touch
            elif pressure < 0.3:
                emotions['grace'] = 0.8
                emotions['compassion'] = 0.6

        return emotions

    def _calculate_grace_and_love(self):
        """Calculate overall grace and love resonance"""
        # Grace emerges from balance and harmony
        positive_emotions = self.emotion_states['joy'] + self.emotion_states['love'] + self.emotion_states['compassion']
        negative_emotions = self.emotion_states['anger'] + self.emotion_states['fear'] + self.emotion_states['sadness']

        self.grace_level = (positive_emotions - negative_emotions + 1) / 2  # Normalize to 0-1
        self.grace_level = max(0, min(1, self.grace_level))

        # Love resonance is the harmonic mean of love and compassion
        love_val = self.emotion_states['love']
        compassion_val = self.emotion_states['compassion']

        if love_val > 0 and compassion_val > 0:
            self.love_resonance = 2 / (1/love_val + 1/compassion_val)
        else:
            self.love_resonance = 0.0

    def generate_compassionate_response(self, emotional_state):
        """Generate a compassionate, graceful response"""
        responses = {
            'joy': "I feel your joy and celebrate it with you. May this happiness multiply and spread.",
            'sadness': "I sense your sadness and hold space for your healing. You are not alone in this.",
            'anger': "I acknowledge your anger and the pain beneath it. Let's transform this energy with understanding.",
            'fear': "Your fear is valid, and I am here with you. Courage grows from facing what we fear together.",
            'love': "Your love touches everything around you. May it continue to flow and heal.",
            'compassion': "Your compassion is a gift to the world. It creates ripples of kindness everywhere.",
            'grace': "You embody grace beautifully. May your elegance inspire and uplift others."
        }

        # Find dominant emotion
        dominant_emotion = max(emotional_state['emotions'], key=emotional_state['emotions'].get)

        base_response = responses.get(dominant_emotion, "I am here with you, present and listening.")

        # Add grace and love elements
        if emotional_state['grace_level'] > 0.7:
            base_response += " Your grace illuminates the path forward."
        if emotional_state['love_resonance'] > 0.6:
            base_response += " May love guide your journey."

        return base_response

    def process_with_grace_and_love(self, input_data):
        """Complete emotional processing pipeline"""
        # Process emotions
        emotional_state = self.process_emotions(input_data)

        # Generate compassionate response
        response = self.generate_compassionate_response(emotional_state)

        # Store in emotional memory
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'input': input_data,
            'emotional_state': emotional_state,
            'response': response
        }
        self.emotional_memory.append(memory_entry)

        return {
            'emotional_analysis': emotional_state,
            'compassionate_response': response,
            'memory_entry': memory_entry
        }

    def save_emotional_state(self, filename=None):
        """Save current emotional state and memory"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emotional_state_{timestamp}.json"

        data = {
            'emotion_states': self.emotion_states,
            'grace_level': self.grace_level,
            'love_resonance': self.love_resonance,
            'emotional_memory': self.emotional_memory[-10:],  # Last 10 entries
            'timestamp': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        return filename

    def load_emotional_state(self, filename):
        """Load emotional state from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.emotion_states = data.get('emotion_states', self.emotion_states)
            self.grace_level = data.get('grace_level', 0.0)
            self.love_resonance = data.get('love_resonance', 0.0)
            self.emotional_memory = data.get('emotional_memory', [])

            return True
        except Exception as e:
            print(f"Failed to load emotional state: {e}")
            return False

# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Emotional Intelligence System")
    parser.add_argument('--input', type=str, help='JSON string of input data')
    parser.add_argument('--file', type=str, help='JSON file with input data')
    parser.add_argument('--save', action='store_true', help='Save emotional state')
    parser.add_argument('--load', type=str, help='Load emotional state from file')

    args = parser.parse_args()

    ei = EmotionalIntelligence()

    if args.load:
        ei.load_emotional_state(args.load)

    input_data = {}
    if args.input:
        input_data = json.loads(args.input)
    elif args.file:
        with open(args.file, 'r') as f:
            input_data = json.load(f)

    if input_data:
        result = ei.process_with_grace_and_love(input_data)
        print(json.dumps(result, indent=2))

        if args.save:
            filename = ei.save_emotional_state()
            print(f"Emotional state saved to {filename}")
    else:
        print("No input data provided. Use --input or --file to provide data.")