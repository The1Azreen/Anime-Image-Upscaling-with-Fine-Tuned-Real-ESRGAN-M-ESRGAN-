from RRDBNet_arch import RRDBNet
import torch
import torchvision.transforms as transforms
from PIL import Image

class ESRGAN_Wrapper:
    model: RRDBNet
    transform: transforms
    
    def __init__(self, model_path=None) -> None:
        # Create an instance of the model
        model = RRDBNet(3, 3, 64, 23)
        model.to('cpu')
        model.eval()

        # Load the model without checkpoint
        try:
            if model_path is None:
                checkpoint = torch.load("models/ESRGAN_4x.pth", map_location=torch.device('cpu'), weights_only=False)
            else:
                checkpoint = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
            
            model.load_state_dict(checkpoint, strict=False)  # Load weights, allow missing keys
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading the model: {e}")
            
        self.model = model
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor()
        ])
        
        # Quantize the model to reduce its precision and make it faster. PyTorch supports dynamic quantization, which is simple to apply and effective on CPUs.
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear}, dtype=torch.qint8
        )
        
    def generate_image(self, file):
        self.model.eval()
        img = Image.open(file).convert("RGB")
        img_tensor = self.transform(img)
        img_tensor = img_tensor.unsqueeze(0)
        with torch.no_grad():
            output = self.model(img_tensor)
        output = torch.clamp(output, 0, 1) 
        output_pil = transforms.ToPILImage()(output.squeeze(0))
        return output_pil
        