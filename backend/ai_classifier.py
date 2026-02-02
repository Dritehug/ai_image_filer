import torch
import torch.nn as nn
import cv2
import numpy as np
from PIL import Image
from torchvision.transforms import v2
from torchvision.models import resnet50, ResNet50_Weights
from config import CATEGORIES

    # Pre-processing; my classifier had a Canny channel.

class AddCannyChannel:
    def __call__(self, img):
        np_img = np.array(img)
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_tensor = torch.from_numpy(edges).float().unsqueeze(0) / 255.0
        rgb_tensor = v2.ToTensor()(img)
        return torch.cat([rgb_tensor, edge_tensor], dim=0)

    # Don't deviate from training model
def build_model(num_classes):
    model = resnet50(weights=ResNet50_Weights.DEFAULT)

    old_conv = model.conv1
    new_conv = nn.Conv2d(
        in_channels=4,
        out_channels=64,
        kernel_size=7,
        stride=2,
        padding=3,
        bias=False
    )

    with torch.no_grad():
        new_conv.weight[:, :3, :, :] = old_conv.weight
        new_conv.weight[:, 3:4, :, :] = old_conv.weight.mean(dim=1, keepdim=True)

    model.conv1 = new_conv

    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Linear(512, num_classes)
    )

    return model


device = "cuda" if torch.cuda.is_available() else "cpu"

_model = build_model(num_classes=len(CATEGORIES))
_state = torch.load("best_model.pth", map_location=device)
_model.load_state_dict(_state)
_model.to(device)
_model.eval()


_transform = v2.Compose([
    v2.Resize((224, 224)),
    AddCannyChannel(),
    v2.Normalize(
        mean=[0.485, 0.456, 0.406, 0.0],
        std=[0.229, 0.224, 0.225, 1.0]
    )
])


def classify_image(path: str) -> str:
    with Image.open(path) as img:
        img = img.convert("RGB")
        img = img.copy()
    tensor = _transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = _model(tensor)
        pred = torch.argmax(logits, dim=1).item()

    return CATEGORIES[pred]
