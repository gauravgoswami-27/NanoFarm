import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import argparse
from model import DiseaseClassificationModel

def load_classes(classes_file="classes.txt"):
    if not os.path.exists(classes_file):
        raise FileNotFoundError(f"Classes file {classes_file} not found. Run training first.")
    with open(classes_file, "r") as f:
        return [line.strip() for line in f.readlines()]

def predict(image_path: str, model_path: str = "best_model.pth", classes_file: str = "classes.txt"):
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
        
    print(f"Running inference on {device}...")
    
    # Load classes
    class_names = load_classes(classes_file)
    num_classes = len(class_names)
    
    # Load model
    model = DiseaseClassificationModel(num_classes=num_classes, pretrained=False)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found.")
        
    # Load weights
    state_dict = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    # In production, image normalization MUST exactly match training
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return
        
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
        # Get top 3 predictions
        top_prob, top_catid = torch.topk(probabilities, 3)
        
    print(f"\nPredictions for {image_path}:")
    print("-" * 30)
    for i in range(top_prob.size(0)):
        idx = top_catid[i].item()
        confidence = top_prob[i].item() * 100
        print(f"Rank {i+1}: {class_names[idx]} ({confidence:.2f}%)")
        
    return class_names[top_catid[0].item()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run inference on an image")
    parser.add_argument("--image", type=str, required=True, help="Path to the leaf image")
    parser.add_argument("--model", type=str, default="best_model.pth", help="Path to trained model weights")
    
    args = parser.parse_args()
    predict(args.image, args.model)
