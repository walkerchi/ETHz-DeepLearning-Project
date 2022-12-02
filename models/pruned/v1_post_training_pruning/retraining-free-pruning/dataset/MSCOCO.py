import json
import pathlib
from PIL import Image
import torch
import torchvision
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from torch.utils.data import DataLoader, Dataset
from matplotlib import pyplot as plt


CAPS_PATH = pathlib.Path(__file__).parent.resolve() / "annotations_trainval2017" / \
    "annotations" / "captions_val2017.json"
IMGS_DIR = pathlib.Path(__file__).parent.resolve() / "val2017"

class MSCOCO(Dataset):
    def __init__(self, n_samples, name):
        self.n_samples = n_samples
        with open(CAPS_PATH) as f:
            j = json.load(f)
        self.model_og = CLIPModel.from_pretrained(name)
        self.processor = CLIPProcessor.from_pretrained(name)
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        self.samples = [(x["image_id"], x["caption"]) for x in j['annotations']]
        self.samples = self.samples[:self.n_samples]
        self.captions = [x[1] for x in self.samples]
        self.images = [self._get_image(x[0]) for x in self.samples]
        self.teacher = False


    def __getitem__(self, index):
        processed_img = self.processor(images=self.images[index], return_tensors='pt')
        processed_txt = self.tokenizer(self.captions[index], padding=True, return_tensors="pt")
        if self.teacher:
            return  processed_img, self.model_og.get_image_features(**processed_img)
        return processed_img, self.model_og.get_text_features(**processed_txt)

    def _get_image(self, image_id):
        img = Image.open(IMGS_DIR / (str(image_id).zfill(12)+".jpg"))
        img.load()
        ret_img = img.copy()
        img.close()
        return ret_img

    def __len__(self):
        return len(self.samples)

if __name__ == "__main__":
    ds = MSCOCO(4, 'openai/clip-vit-base-patch32')
    dl = DataLoader(
        ds,
        batch_size=2,
        pin_memory=True,
    )
    for batch in dl:
       pass

