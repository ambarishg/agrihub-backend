import os
import time
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from albumentations import Compose, Resize, Normalize, RandomResizedCrop, Transpose, HorizontalFlip, VerticalFlip, ShiftScaleRotate
from albumentations.pytorch import ToTensorV2
import cv2
from tqdm.auto import tqdm
import timm
from contextlib import contextmanager
import logging
from config.configs import CONFIGS

class ImageClassifier:
    class Config:
        debug = False
        num_workers = 1
        paddy_model_name = 'paddy_tf_efficientnet_b5_ns'
        cassava_model_name = 'cassava_tf_efficientnet_b5_ns'
        poultry_model_name = 'poultry_tf_efficientnet_b5_ns'
        mango_model_name = 'mango_tf_efficientnet_b5_ns'
        sugarcane_model_name = 'sugarcane_tf_efficientnet_b5_ns'
        pest_model_name = 'pest_tf_efficientnet_b5_ns'
        size = 512
        batch_size = 1
        seed = 42
        target_col = 'label_encoded'
        train = False
        inference = True
        model_dir = "./models/"
    
    def __init__(self, config=None):
        self.CFG = config if config else self.Config()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = self.init_logger()
        self.seed_torch(self.CFG.seed)

    def init_logger(self, log_file='train.log'):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler1 = logging.StreamHandler()
        handler1.setFormatter(logging.Formatter("%(message)s"))
        handler2 = logging.FileHandler(filename=log_file)
        handler2.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler1)
        logger.addHandler(handler2)
        return logger

    def seed_torch(self, seed=42):
        random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.deterministic = True

    class TestDataset(Dataset):
        def __init__(self, df, transform=None):
            self.df = df
            self.file_names = df['image_id'].values
            self.transform = transform

        def __len__(self):
            return len(self.df)

        def __getitem__(self, idx):
            file_name = self.file_names[idx]
            image = cv2.imread(file_name)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if self.transform:
                augmented = self.transform(image=image)
                image = augmented['image']
            return image

    def get_transforms(self, data):
        if data == 'train':
            return Compose([
                RandomResizedCrop(self.CFG.size, self.CFG.size),
                Transpose(p=0.5),
                HorizontalFlip(p=0.5),
                VerticalFlip(p=0.5),
                ShiftScaleRotate(p=0.5),
                Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
                ToTensorV2(),
            ])
        elif data == 'valid':
            return Compose([
                Resize(self.CFG.size, self.CFG.size),
                Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
                ToTensorV2(),
            ])

    class CustomEfficientNet(nn.Module):
        def __init__(self, model_name, target_size, pretrained=False):
            super().__init__()
            self.model = timm.create_model(model_name, pretrained=pretrained)
            n_features = self.model.classifier.in_features
            self.model.classifier = nn.Linear(n_features, target_size)
        def forward(self, x):
            return self.model(x)

    def inference(self, model, states, test_loader):
        model.to(self.device)
        tk0 = tqdm(enumerate(test_loader), total=len(test_loader))
        probs = []
        for i, (images) in tk0:
            images = images.to(self.device)
            avg_preds = []
            for state in states:
                model.load_state_dict(state['model'])
                model.eval()
                with torch.no_grad():
                    y_preds = model(images)
                avg_preds.append(y_preds.softmax(1).to('cpu').numpy())
            avg_preds = np.mean(avg_preds, axis=0)
            probs.append(avg_preds)
        probs = np.concatenate(probs)
        return probs

    def get_predictions(self, file_name,category='paddy'):
        file_path = f'./{CONFIGS.UPLOAD_DIR}/{file_name}'
        self.logger.info(f"Processing file: {file_path}")

        self.logger.info(f"Category: {category}")

        fold_number, model_name, \
        base_model_name, TARGET_SIZE = self.get_model_info(category)
    
        model_path = os.path.join(self.CFG.model_dir, f'{model_name}_fold{fold_number}_best.pth')
        self.logger.info(f"Loading model from: {model_path}")

        TEST_DATA = pd.DataFrame({'image_id': [file_path]})
        model = self.CustomEfficientNet(base_model_name, TARGET_SIZE, pretrained=False)
        states = [torch.load(model_path, weights_only = False,map_location='cpu')]
        test_dataset = self.TestDataset(TEST_DATA, transform=self.get_transforms(data='valid'))
        test_loader = DataLoader(test_dataset, batch_size=self.CFG.batch_size, shuffle=False, 
                                 num_workers=self.CFG.num_workers, pin_memory=True)
        predictions = self.inference(model, states, test_loader)
        prediction_type = predictions.argmax(1)
        prediction = str(prediction_type[0])

        self.logger.info(f"Predictions for {file_name} : {prediction_type}")

        if category in ['Paddy', 'Cassava', 'Poultry', 
                        'Mango', 'Sugarcane', 'Pest','Tea']:
            prediction = self.get_label_names(category,prediction_type)
        return prediction

    def get_label_names(self, category, prediction_type):
        file_name  = f"./data/{category}_labels.csv"
        df = pd.read_csv(file_name)
        prediction = df[df['label_encoded'] == (prediction_type[0])]['label'].values[0]
        print(f"Prediction for {file_name} in category {category}: {prediction}"   )
        return prediction

    def get_model_info(self, category):
        if category == 'Paddy':
            fold_number = 1
            model_name = self.CFG.paddy_model_name
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 10
        elif category == 'Cassava':
            fold_number = 1
            model_name = self.CFG.cassava_model_name
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 5
        elif category == 'Poultry':
            fold_number = 1
            model_name = self.CFG.poultry_model_name
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 4
        elif category == 'Mango':
            fold_number = 1
            model_name = self.CFG.mango_model_name
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 8
        elif category == 'Sugarcane':
            fold_number = 1
            model_name = self.CFG.sugarcane_model_name
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 5
        elif category == 'Pest':
            fold_number = 1
            model_name = self.CFG.pest_model_name
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 15
        elif category == 'Tea':
            fold_number = 1
            model_name = 'tea_tf_efficientnet_b5_ns'
            base_model_name = 'tf_efficientnet_b5_ns'
            TARGET_SIZE = 7
        return fold_number,model_name,base_model_name,TARGET_SIZE

# Example usage:
# classifier = ImageClassifier()
# pred = classifier.get_predictions('path/to/image.jpg')
