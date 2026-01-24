"""
Transformer Service - Loads and uses your trained model for chatbot responses

This service:
1. Loads your trained model (.pth file)
2. Loads your tokenizer (SentencePiece)
3. Generates responses to user messages
"""

import torch
import sentencepiece as spm
import os
import sys

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models.model_architecture import Seq2SeqTransformer


class TransformerService:
    """Service for loading and using the trained Transformer model"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.vocab_size = 0
        
        print("🤖 Initializing Transformer Service...")
        
        # Load model on initialization
        self.load_model()
    
    def load_model(self):
        """Load the trained model and tokenizer"""
        try:
            # File paths
            model_path = 'models/final_chatbot_model.pth'
            tokenizer_path = 'models/spm_model.model'
            
            # Check if files exist
            if not os.path.exists(model_path):
                print(f"❌ Model file not found: {model_path}")
                print("   Please download from Colab and place in models/ folder")
                return False
            
            if not os.path.exists(tokenizer_path):
                print(f"❌ Tokenizer file not found: {tokenizer_path}")
                print("   Please download from Colab and place in models/ folder")
                return False
            
            print(f"📂 Loading tokenizer from: {tokenizer_path}")
            
            # Load tokenizer (SentencePiece)
            self.tokenizer = spm.SentencePieceProcessor()
            self.tokenizer.load(tokenizer_path)
            self.vocab_size = len(self.tokenizer)
            
            print(f"✅ Tokenizer loaded: {self.vocab_size} tokens")
            
            print(f"📂 Loading model from: {model_path}")
            
            # Load model checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Extract model configuration
            d_model = checkpoint.get('d_model', 256)
            nhead = checkpoint.get('nhead', 8)
            num_encoder_layers = checkpoint.get('num_encoder_layers', 3)
            num_decoder_layers = checkpoint.get('num_decoder_layers', 3)
            dim_feedforward = checkpoint.get('dim_feedforward', 512)
            
            print(f"📊 Model configuration:")
            print(f"   - Vocab size: {self.vocab_size}")
            print(f"   - d_model: {d_model}")
            print(f"   - Attention heads: {nhead}")
            print(f"   - Encoder layers: {num_encoder_layers}")
            print(f"   - Decoder layers: {num_decoder_layers}")
            
            # Create model with same architecture
            self.model = Seq2SeqTransformer(
                vocab_size=self.vocab_size,
                d_model=d_model,
                nhead=nhead,
                num_encoder_layers=num_encoder_layers,
                num_decoder_layers=num_decoder_layers,
                dim_feedforward=dim_feedforward
            )
            
            # Load trained weights
            self.model.load_state_dict(checkpoint['model_state_dict'])
            
            # Move to device and set to eval mode
            self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            
            print(f"✅ Model loaded successfully!")
            print(f"   Device: {self.device}")
            
            # Show training info if available
            if 'total_examples' in checkpoint:
                print(f"   Trained on: {checkpoint['total_examples']:,} examples")
            if 'dataset_info' in checkpoint:
                print(f"   Dataset: {checkpoint['dataset_info']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_response(self, user_message, max_length=100, temperature=0.7):
        """
        Generate response using the trained model
        
        Args:
            user_message: User's input text (e.g., "2 burger chahiye")
            max_length: Maximum length of generated response
            temperature: Sampling temperature (higher = more creative)
            
        Returns:
            Generated response text
        """
        
        if not self.loaded:
            return "Sorry, the chatbot model is not available right now. Please try again later."
        
        try:
            # Clean input
            user_message = user_message.strip()
            
            if not user_message:
                return "Please send a message!"
            
            # Tokenize input
            input_ids = self.tokenizer.encode(user_message, out_type=int)
            
            # Convert to tensor
            input_tensor = torch.tensor([input_ids]).to(self.device)
            
            # Special tokens
            BOS_ID = self.tokenizer.bos_id()
            EOS_ID = self.tokenizer.eos_id()
            PAD_ID = self.tokenizer.pad_id()
            
            # Start with BOS token
            output_ids = [BOS_ID]
            
            # Generate tokens one by one (autoregressive)
            with torch.no_grad():
                for step in range(max_length):
                    # Current output as tensor
                    output_tensor = torch.tensor([output_ids]).to(self.device)
                    
                    # Get model predictions
                    logits = self.model(input_tensor, output_tensor)
                    
                    # Get logits for next token
                    next_token_logits = logits[0, -1, :]
                    
                    # Apply temperature
                    if temperature != 1.0:
                        next_token_logits = next_token_logits / temperature
                    
                    # Get probabilities
                    probs = torch.softmax(next_token_logits, dim=-1)
                    
                    # Sample next token (greedy for now, can add sampling)
                    next_token = torch.argmax(probs).item()
                    
                    # Stop if EOS token
                    if next_token == EOS_ID:
                        break
                    
                    # Skip PAD tokens
                    if next_token == PAD_ID:
                        break
                    
                    # Add to output
                    output_ids.append(next_token)
            
            # Decode to text (skip BOS token)
            response = self.tokenizer.decode(output_ids[1:])
            
            # Clean response
            response = response.strip()
            
            # Fallback if response is empty
            if not response:
                response = "I understand. How can I help you?"
            
            return response
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return "Sorry, I couldn't process that. Can you try again?"
    
    def is_loaded(self):
        """Check if model is loaded and ready"""
        return self.loaded


# Create singleton instance
transformer_service = TransformerService()


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TRANSFORMER SERVICE TEST")
    print("="*60)
    
    if transformer_service.is_loaded():
        print("\n✅ Model loaded successfully! Testing responses...\n")
        
        # Test messages
        test_messages = [
            "Hi",
            "Menu kya hai?",
            "2 burger chahiye",
            "Coffee kitni ki hai?",
            "Checkout"
        ]
        
        for msg in test_messages:
            print(f"User: {msg}")
            response = transformer_service.generate_response(msg)
            print(f"Bot:  {response}\n")
    else:
        print("\n❌ Model failed to load. Check file paths and error messages above.")