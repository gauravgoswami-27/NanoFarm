import os
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

def get_dataloaders(data_dir: str, batch_size: int = 16, test_split: float = 0.2, num_workers: int = 2):
    """
    Given a dataset organized as:
        data_dir/
            Disease_1/
                image1.jpg
            Disease_2/
                image2.jpg
            Healthy/
                image3.jpg
                
    Returns train and validation dataloaders.
    """
    
    # Standard normalization for ImageNet pre-trained models (MobileNetV3)
    # Plus some basic data augmentation to prevent overfitting
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15), 
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load all images
    full_dataset = datasets.ImageFolder(root=data_dir)
    class_names = full_dataset.classes
    num_classes = len(class_names)
    
    # Split the dataset
    total_size = len(full_dataset)
    val_size = int(test_split * total_size)
    train_size = total_size - val_size
    
    # Using generator to ensure reproducibility if needed 
    import torch
    train_dataset, val_dataset = random_split(
        full_dataset, 
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Apply different transforms to train/val sets
    # (By default it applies the same transforms, so we wrap them)
    class TransformDataset(torch.utils.data.Dataset):
        def __init__(self, subset, transform=None):
            self.subset = subset
            self.transform = transform
            
        def __getitem__(self, index):
            x, y = self.subset[index]
            if self.transform:
                x = self.transform(x)
            return x, y
            
        def __len__(self):
            return len(self.subset)
            
    train_dataset = TransformDataset(train_dataset, train_transforms)
    val_dataset = TransformDataset(val_dataset, val_transforms)
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=num_workers,
        pin_memory=True # Speeds up data transfer to GPU
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, val_loader, class_names, num_classes
