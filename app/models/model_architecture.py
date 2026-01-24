"""
Model Architecture - Seq2Seq Transformer

This MUST match the exact architecture you used in your Colab notebook!
Copy your model definition from the notebook and paste here.
"""

import torch
import torch.nn as nn
import math


class PositionalEncoding(nn.Module):
    """
    Positional encoding adds position information to embeddings
    """
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """Add positional encoding to input"""
        return x + self.pe[:, :x.size(1)]


class Seq2SeqTransformer(nn.Module):
    """
    Sequence-to-Sequence Transformer Model
    
    Architecture:
    - Embedding layer
    - Positional encoding
    - Transformer (encoder + decoder)
    - Output projection
    
    Args:
        vocab_size: Size of vocabulary
        d_model: Dimension of model (default: 256)
        nhead: Number of attention heads (default: 8)
        num_encoder_layers: Number of encoder layers (default: 3)
        num_decoder_layers: Number of decoder layers (default: 3)
        dim_feedforward: Dimension of feedforward network (default: 512)
        dropout: Dropout rate (default: 0.1)
    """
    
    def __init__(
        self,
        vocab_size,
        d_model=256,
        nhead=8,
        num_encoder_layers=3,
        num_decoder_layers=3,
        dim_feedforward=512,
        dropout=0.1
    ):
        super().__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model)
        
        # Transformer
        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True  # Important: batch is first dimension
        )
        
        # Output projection
        self.fc_out = nn.Linear(d_model, vocab_size)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights"""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc_out.bias.data.zero_()
        self.fc_out.weight.data.uniform_(-initrange, initrange)
    
    def forward(
        self,
        src,
        tgt,
        src_mask=None,
        tgt_mask=None,
        src_key_padding_mask=None,
        tgt_key_padding_mask=None
    ):
        """
        Forward pass
        
        Args:
            src: Source sequence (batch_size, src_len)
            tgt: Target sequence (batch_size, tgt_len)
            src_mask: Source attention mask
            tgt_mask: Target attention mask (causal)
            src_key_padding_mask: Source padding mask
            tgt_key_padding_mask: Target padding mask
            
        Returns:
            Output logits (batch_size, tgt_len, vocab_size)
        """
        
        # Embed and scale
        src = self.embedding(src) * math.sqrt(self.d_model)
        tgt = self.embedding(tgt) * math.sqrt(self.d_model)
        
        # Add positional encoding
        src = self.pos_encoder(src)
        tgt = self.pos_encoder(tgt)
        
        # Apply dropout
        src = self.dropout(src)
        tgt = self.dropout(tgt)
        
        # Pass through transformer
        output = self.transformer(
            src,
            tgt,
            src_mask=src_mask,
            tgt_mask=tgt_mask,
            src_key_padding_mask=src_key_padding_mask,
            tgt_key_padding_mask=tgt_key_padding_mask
        )
        
        # Project to vocabulary
        output = self.fc_out(output)
        
        return output
    
    def generate_square_subsequent_mask(self, sz):
        """
        Generate causal mask for target sequence
        Prevents attention to future tokens
        """
        mask = torch.triu(torch.ones(sz, sz), diagonal=1)
        mask = mask.masked_fill(mask == 1, float('-inf'))
        return mask


# Helper function to count parameters
def count_parameters(model):
    """Count trainable parameters"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# Test function
if __name__ == "__main__":
    print("Testing Seq2SeqTransformer architecture...\n")
    
    # Create model
    vocab_size = 20000
    model = Seq2SeqTransformer(
        vocab_size=vocab_size,
        d_model=256,
        nhead=8,
        num_encoder_layers=3,
        num_decoder_layers=3,
        dim_feedforward=512
    )
    
    print(f"Model created successfully!")
    print(f"  Vocab size: {vocab_size}")
    print(f"  Parameters: {count_parameters(model):,}")
    print(f"  Size: {count_parameters(model) / 1e6:.2f}M")
    
    # Test forward pass
    batch_size = 2
    src_len = 10
    tgt_len = 15
    
    src = torch.randint(0, vocab_size, (batch_size, src_len))
    tgt = torch.randint(0, vocab_size, (batch_size, tgt_len))
    
    print(f"\nTest forward pass:")
    print(f"  Input shape: {src.shape}")
    print(f"  Target shape: {tgt.shape}")
    
    output = model(src, tgt)
    print(f"  Output shape: {output.shape}")
    
    assert output.shape == (batch_size, tgt_len, vocab_size)
    print(f"\n✅ Model architecture test passed!")