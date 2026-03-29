# Disease Vision Model - Neural Farms

This directory contains the PyTorch implementation for identifying crop diseases from leaf images. 
It uses a highly-optimized **MobileNetV3** architecture that is capable of running on edge devices and smartphones while preventing Out-of-Memory (OOM) errors on GPUs with limited VRAM (like an RTX 3050 4GB).

## Hardware Optimization Notes
To support running on your `RTX 3050 4GB`, the `train.py` script heavily utilizes **PyTorch Automatic Mixed Precision (AMP)** via `torch.amp.autocast`. This trains the model in 16-bit floating point precision where possible, dramatically reducing VRAM usage and speeding up training, allowing you to use reasonable batch sizes despite the 4GB limit.

## 1. Setup Environment

Make sure you install the requirements first. 

```bash
pip install -r requirements.txt
```

*(Note: It is highly recommended to create a python virtual environment `python -m venv venv` and activate it before installing packages)*

## 2. Obtain the Dataset

For this research project, we are targeting the **PlantVillage Dataset**.

1. Download the dataset from Kaggle: [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease)
2. Extract it into a folder. Your structure should look like:
   ```text
   PlantVillage/
     Apple___Apple_scab/
       image1.jpg
     Apple___Black_rot/
       image2.jpg
     ...
   ```

## 3. Train the Model (Local Test)

To test the training locally on your RTX 3050, run:

```bash
python train.py --data_dir /path/to/extracted/PlantVillage --epochs 5 --batch_size 16
```
*Tip: If you run into CUDA Out of Memory errors, simply drop `--batch_size` to 8.*

## 4. Run Inference

Once trained, it will output `best_model.pth` and `classes.txt`.
You can then run predictions on new, unseen leaf images:

```bash
python inference.py --image /path/to/test/leaf.jpg
```
