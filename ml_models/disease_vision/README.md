# Disease Vision Model — Neural Farms

This directory contains the PyTorch pipeline for identifying **crop diseases** from leaf images.  
It uses a fine-tuned **MobileNetV3-Small** that is optimised for limited VRAM (RTX 3050 4 GB).

---

## Datasets covered

| # | Dataset | Classes | Source |
|---|---------|---------|--------|
| 1 | PlantVillage | 38 (Apple, Corn, Tomato, etc.) | *(optional, add manually)* |
| 2 | Rice Leaf Diseases | 3 (Bacterial blight, Brown spot, Leaf smut) | [Kaggle](https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases) |
| 3 | Cotton Disease | 4 (diseased/fresh leaf & plant) | [Kaggle](https://www.kaggle.com/datasets/janmejaybhoi/cotton-disease-dataset) |
| 4 | Wheat Leaf Rust & Nitrogen Deficiency | 2 (wheat_healthy, wheat_leaf_rust) | [Kaggle](https://www.kaggle.com/datasets/jocelyndumlao/wheat-nitrogen-deficiency-and-leaf-rust-image) |

> **Gemini Vision Fallback**: if the local model's confidence falls below **60 %** on an
> uploaded image, the backend automatically sends the photo to Gemini Vision for
> identification and generates a treatment plan — no extra work needed by the end user.

---

## Hardware notes

`train.py` / `merge_and_train.py` use **PyTorch AMP (torch.amp.autocast)** with fp16
to prevent OOM on 4 GB VRAM GPUs and to speed up training by ~2×.

---

## Quick start

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Download all datasets

From the **project root** (`agri/`):

```bash
python data.py
```

This downloads Rice, Cotton, and Wheat datasets via `kagglehub` (requires a free Kaggle account).  
The script also prints the exact `merge_and_train.py` command to copy-paste in Step 3.

### Step 3 — Merge datasets and train

```bash
cd ml_models/disease_vision

python merge_and_train.py \
  --rice   "$HOME/.cache/kagglehub/datasets/vbookshelf/rice-leaf-diseases/versions/1/rice_leaf_diseases" \
  --cotton "$HOME/.cache/kagglehub/datasets/janmejaybhoi/cotton-disease-dataset/versions/1/Cotton Disease" \
  --wheat  "$HOME/.cache/kagglehub/datasets/jocelyndumlao/wheat-nitrogen-deficiency-and-leaf-rust-image/versions/1/th422bg4yd-1/WheatLeafRust" \
  --epochs 15 \
  --batch_size 16
```

*Tip: if you see CUDA OOM errors, drop `--batch_size` to `8`.*

The script will:
1. Create a unified staging directory (`/tmp/neural_farms_unified/`) using symlinks.
2. Print a per-class image count table.
3. Train MobileNetV3-Small with AMP + AdamW + Cosine LR schedule.
4. **Automatically save `best_model.pth` and `classes.txt` directly into `backend/models/`** so the FastAPI server picks them up without any manual copying.

### Step 4 — (Optional) Include PlantVillage

Download [PlantVillage](https://www.kaggle.com/datasets/emmarex/plantdisease) and add:

```bash
python merge_and_train.py \
  --plantvillage /path/to/PlantVillage \
  ...
```

### Step 5 — Run inference

Once `best_model.pth` is in `backend/models/`, restart the FastAPI backend and upload
a leaf image through the Neural Farms UI. The response includes:

```json
{
  "disease_name": "wheat_leaf_rust",
  "confidence": 94.3,
  "source": "PyTorch Local Model",
  "gemini_used": true,
  "top_3": [...],
  "treatment": "Step 1: ..."
}
```

If confidence < 60 %, `source` will be `"Gemini Vision (AI Fallback)"` and the
image itself is sent to Gemini for diagnosis.
