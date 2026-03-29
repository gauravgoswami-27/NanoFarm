import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

class DiseaseClassificationModel(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True):
        super(DiseaseClassificationModel, self).__init__()
        
        # We use MobileNetV3 Small as it's highly optimized for 4GB VRAM and Mobile deployments
        weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
        self.base_model = mobilenet_v3_small(weights=weights)
        
        # Freeze the base layers if we want to do strict transfer learning
        # For now, we leave them unfrozen to fine-tune the whole network, but you can 
        # uncomment the lines below if your dataset is very small
        # for param in self.base_model.parameters():
        #     param.requires_grad = False
            
        # Replace the classifier head to match our number of disease classes
        # MobileNetV3 classifier usually is a Sequential block. We replace the last Linear layer.
        in_features = self.base_model.classifier[-1].in_features
        self.base_model.classifier[-1] = nn.Linear(in_features, num_classes)
        
    def forward(self, x):
        return self.base_model(x)

if __name__ == "__main__":
    # Quick sanity check
    model = DiseaseClassificationModel(num_classes=10)
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    print(f"Output shape: {output.shape}") # Should be [1, 10]
