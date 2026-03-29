import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import autocast, GradScaler
import argparse
import os
from tqdm import tqdm

from dataset import get_dataloaders
from model import DiseaseClassificationModel

def train_model(data_dir, epochs=10, batch_size=16, learning_rate=1e-3, save_path="best_model.pth"):
    # Target our specific hardware: CUDA for RTX 3050, MPS for M2 Mac, otherwise CPU
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
        
    print(f"Using device: {device}")
    
    # 1. Prepare Data
    print(f"Loading data from {data_dir}...")
    train_loader, val_loader, class_names, num_classes = get_dataloaders(
        data_dir=data_dir, 
        batch_size=batch_size,
        num_workers=2 # Keeps CPU usage reasonable on an i5
    )
    print(f"Found {num_classes} classes: {class_names}")
    
    # save classes for inference later
    with open("classes.txt", "w") as f:
        f.write("\n".join(class_names))
    
    # 2. Setup Model
    model = DiseaseClassificationModel(num_classes=num_classes, pretrained=True)
    model = model.to(device)
    
    # 3. Loss & Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4) # AdamW works great for CV
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)
    
    # 4. Mixed Precision Scaler (CRITICAL for 4GB RTX 3050)
    # This prevents running out of VRAM and speeds up training by using fp16
    scaler = GradScaler('cuda' if device.type == 'cuda' else 'cpu')
    
    best_val_acc = 0.0
    
    # 5. Training Loop
    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 10)
        
        # --- TRAINING PHASE ---
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        # Progress bar
        train_bar = tqdm(train_loader, desc="Training", leave=False)
        
        for inputs, labels in train_bar:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass using Mixed Precision
            autocast_device = 'cuda' if device.type == 'cuda' else 'cpu'
            with autocast(autocast_device):
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                
            # Backward pass & Optimize
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            # Statistics
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            
            train_bar.set_postfix(loss=loss.item())
            
        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = running_corrects.double() / len(train_loader.dataset)
        
        # --- VALIDATION PHASE ---
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        
        val_bar = tqdm(val_loader, desc="Validation", leave=False)
        
        # No gradients needed for validation
        with torch.no_grad():
            for inputs, labels in val_bar:
                inputs, labels = inputs.to(device), labels.to(device)
                
                # We can also use autocast in eval to save memory/speed
                autocast_device = 'cuda' if device.type == 'cuda' else 'cpu'
                with autocast(autocast_device):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)
                
        val_epoch_loss = val_loss / len(val_loader.dataset)
        val_epoch_acc = val_corrects.double() / len(val_loader.dataset)
        
        # Scheduler step based on validation loss
        scheduler.step(val_epoch_loss)
        
        print(f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
        print(f"Val Loss: {val_epoch_loss:.4f} Acc: {val_epoch_acc:.4f}")
        
        # Save Best Model
        if val_epoch_acc > best_val_acc:
            best_val_acc = val_epoch_acc
            print(f"New best model found! Saving to {save_path}...")
            torch.save(model.state_dict(), save_path)
            
    print(f"\nTraining Complete. Best Validation Accuracy: {best_val_acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Disease Vision Model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to the dataset directory")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=16, help="Keep at 16 or 32 for 4GB GPUs")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"Error: Dataset directory {args.data_dir} does not exist.")
    else:
        train_model(data_dir=args.data_dir, epochs=args.epochs, batch_size=args.batch_size)
