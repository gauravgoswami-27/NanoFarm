"""
merge_and_train.py  –  Neural Farms Unified Disease Model
==========================================================
Merges all available crop-disease datasets into a single ImageFolder-compatible
staging directory, then trains one MobileNetV3-Small model over them.

Datasets handled
----------------
1. PlantVillage / PlantDoc  (flat class dirs)
   e.g. Apple___Apple_scab/, Corn___healthy/, …

2. Rice Leaf Diseases  (flat class dirs)
   Bacterial leaf blight/, Brown spot/, Leaf smut/

3. Cotton Disease Dataset  (pre-split  train/val/test  with class subdirs)
   Cotton Disease/train/diseased cotton leaf/, …

4. Wheat Nitrogen Deficiency & Leaf Rust  (pre-split  train/val/test)
   WheatLeafRust/train/control/, WheatLeafRust/train/diseased/
   → remapped to "wheat_healthy" and "wheat_leaf_rust"

Gemini Fallback
---------------
After training, if a live inference returns confidence < LOW_CONF_THRESHOLD,
the backend will automatically delegate to Gemini Vision.  This script does
NOT handle inference-time fallback — see disease_service.py.

Usage
-----
python merge_and_train.py \\
    --plantvillage /path/to/PlantVillage \\
    --rice         /home/grv/.cache/kagglehub/datasets/vbookshelf/rice-leaf-diseases/versions/1/rice_leaf_diseases \\
    --cotton       "/home/grv/.cache/kagglehub/datasets/janmejaybhoi/cotton-disease-dataset/versions/1/Cotton Disease" \\
    --wheat        /home/grv/.cache/kagglehub/datasets/jocelyndumlao/wheat-nitrogen-deficiency-and-leaf-rust-image/versions/1/th422bg4yd-1/WheatLeafRust \\
    --staging      /tmp/neural_farms_unified \\
    --epochs       15 \\
    --batch_size   16
"""

import os
import shutil
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import autocast, GradScaler
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, ConcatDataset, random_split
from tqdm import tqdm

from model import DiseaseClassificationModel


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Dataset staging helpers
# ─────────────────────────────────────────────────────────────────────────────

def symlink_or_copy(src: str, dst: str):
    """
    Prefer symlinks (fast, zero-disk); fall back to shutil.copy2 if the
    filesystem doesn't support them (e.g. cross-device).
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) or os.path.islink(dst):
        return
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def stage_flat(src_root: str, staging_train: str, staging_val: str,
               val_fraction: float = 0.15, class_rename: dict = None):
    """
    Stage a FLAT dataset (class_name/image.jpg …) into staging_train, staging_val.
    A random 15% of each class goes to val.
    class_rename: optional dict {original_folder_name: new_class_name}
    """
    import random, math
    random.seed(42)

    for cls_name in sorted(os.listdir(src_root)):
        cls_path = os.path.join(src_root, cls_name)
        if not os.path.isdir(cls_path):
            continue

        mapped_name = class_rename.get(cls_name, cls_name) if class_rename else cls_name
        images = [f for f in os.listdir(cls_path)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        random.shuffle(images)

        val_count = max(1, math.ceil(len(images) * val_fraction))
        val_imgs   = images[:val_count]
        train_imgs = images[val_count:]

        for img in train_imgs:
            dst = os.path.join(staging_train, mapped_name, img)
            symlink_or_copy(os.path.join(cls_path, img), dst)

        for img in val_imgs:
            dst = os.path.join(staging_val, mapped_name, img)
            symlink_or_copy(os.path.join(cls_path, img), dst)

    added = [d for d in os.listdir(src_root) if os.path.isdir(os.path.join(src_root, d))]
    print(f"  → staged {len(added)} classes from {src_root}")


def stage_presplit(src_root: str, staging_train: str, staging_val: str,
                   class_rename: dict = None):
    """
    Stage a PRE-SPLIT dataset (train/class/image.jpg …  val/class/image.jpg)
    into the unified staging dirs.
    """
    for split_name, dst_root in [("train", staging_train), ("val", staging_val)]:
        split_path = os.path.join(src_root, split_name)
        if not os.path.isdir(split_path):
            continue
        for cls_name in sorted(os.listdir(split_path)):
            cls_path = os.path.join(split_path, cls_name)
            if not os.path.isdir(cls_path):
                continue
            mapped_name = class_rename.get(cls_name, cls_name) if class_rename else cls_name
            for img in os.listdir(cls_path):
                if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    src = os.path.join(cls_path, img)
                    # Prefix with split+cls to avoid name collisions across datasets
                    dst_img = f"{cls_name}_{img}"
                    dst = os.path.join(dst_root, mapped_name, dst_img)
                    symlink_or_copy(src, dst)

    classes = set()
    for split in ["train", "val"]:
        sp = os.path.join(src_root, split)
        if os.path.isdir(sp):
            classes.update(os.listdir(sp))
    print(f"  → staged {len(classes)} classes (pre-split) from {src_root}")


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Build unified staging directory
# ─────────────────────────────────────────────────────────────────────────────

def build_staging(args) -> tuple[str, str]:
    """
    Merges all datasets into:
        staging/train/<class>/<image>
        staging/val/<class>/<image>
    Returns (train_dir, val_dir).
    """
    staging_train = os.path.join(args.staging, "train")
    staging_val   = os.path.join(args.staging, "val")
    os.makedirs(staging_train, exist_ok=True)
    os.makedirs(staging_val,   exist_ok=True)

    # ── PlantVillage (flat) ──────────────────────────────────────────────────
    if args.plantvillage and os.path.isdir(args.plantvillage):
        print(f"[1/4] Staging PlantVillage from {args.plantvillage}")
        stage_flat(args.plantvillage, staging_train, staging_val)
    else:
        print("[1/4] PlantVillage path not provided or missing — skipping")

    # ── Rice Leaf Diseases (flat) ────────────────────────────────────────────
    if args.rice and os.path.isdir(args.rice):
        print(f"[2/4] Staging Rice from {args.rice}")
        stage_flat(args.rice, staging_train, staging_val)
    else:
        print("[2/4] Rice path not provided or missing — skipping")

    # ── Cotton Disease (pre-split) ───────────────────────────────────────────
    if args.cotton and os.path.isdir(args.cotton):
        print(f"[3/4] Staging Cotton from {args.cotton}")
        stage_presplit(args.cotton, staging_train, staging_val)
    else:
        print("[3/4] Cotton path not provided or missing — skipping")

    # ── Wheat Leaf Rust (pre-split, rename classes → descriptive names) ──────
    if args.wheat and os.path.isdir(args.wheat):
        print(f"[4/4] Staging Wheat from {args.wheat}")
        wheat_rename = {
            "control": "wheat_healthy",
            "diseased": "wheat_leaf_rust",
        }
        stage_presplit(args.wheat, staging_train, staging_val, class_rename=wheat_rename)
    else:
        print("[4/4] Wheat path not provided or missing — skipping")

    # ── Summary ─────────────────────────────────────────────────────────────
    train_classes = sorted(os.listdir(staging_train))
    print(f"\n✅ Staging complete. Total unified classes: {len(train_classes)}")
    for c in train_classes:
        n_train = len(os.listdir(os.path.join(staging_train, c)))
        n_val   = len(os.listdir(os.path.join(staging_val,   c))) if os.path.isdir(os.path.join(staging_val, c)) else 0
        print(f"   {c:<45}  train={n_train:>4}  val={n_val:>4}")

    return staging_train, staging_val


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Training
# ─────────────────────────────────────────────────────────────────────────────

def train(staging_train: str, staging_val: str, args):
    # ── Hardware ─────────────────────────────────────────────────────────────
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"\n🚀 Training on: {device}")

    # ── Transforms ───────────────────────────────────────────────────────────
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # ── Datasets ─────────────────────────────────────────────────────────────
    train_ds = datasets.ImageFolder(root=staging_train, transform=train_tf)
    val_ds   = datasets.ImageFolder(root=staging_val,   transform=val_tf)

    class_names = train_ds.classes
    num_classes = len(class_names)
    print(f"📊 Classes: {num_classes}  |  Train: {len(train_ds)}  |  Val: {len(val_ds)}")

    # Save class list immediately (needed by backend)
    with open(args.classes_out, "w") as f:
        f.write("\n".join(class_names))
    print(f"📝 Classes saved to {args.classes_out}")

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False,
                              num_workers=2, pin_memory=True)

    # ── Model ─────────────────────────────────────────────────────────────────
    model = DiseaseClassificationModel(num_classes=num_classes, pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler    = GradScaler("cuda" if device.type == "cuda" else "cpu")

    best_val_acc = 0.0

    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        print("─" * 12)

        # ── Train ─────────────────────────────────────────────────────────────
        model.train()
        run_loss, run_corr = 0.0, 0
        for inputs, labels in tqdm(train_loader, desc="Train", leave=False):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            with autocast("cuda" if device.type == "cuda" else "cpu"):
                out  = model(inputs)
                _, preds = torch.max(out, 1)
                loss = criterion(out, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            run_loss += loss.item() * inputs.size(0)
            run_corr += (preds == labels).sum().item()

        ep_loss = run_loss / len(train_ds)
        ep_acc  = run_corr / len(train_ds)

        # ── Validate ───────────────────────────────────────────────────────────
        model.eval()
        val_loss, val_corr = 0.0, 0
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader, desc="Val  ", leave=False):
                inputs, labels = inputs.to(device), labels.to(device)
                with autocast("cuda" if device.type == "cuda" else "cpu"):
                    out  = model(inputs)
                    _, preds = torch.max(out, 1)
                    loss = criterion(out, labels)
                val_loss += loss.item() * inputs.size(0)
                val_corr += (preds == labels).sum().item()

        val_ep_loss = val_loss / len(val_ds)
        val_ep_acc  = val_corr / len(val_ds)

        scheduler.step()
        print(f"Train  loss={ep_loss:.4f}  acc={ep_acc:.4f}")
        print(f"Val    loss={val_ep_loss:.4f}  acc={val_ep_acc:.4f}")

        if val_ep_acc > best_val_acc:
            best_val_acc = val_ep_acc
            torch.save(model.state_dict(), args.model_out)
            print(f"✅ Best model saved → {args.model_out}  (val_acc={best_val_acc:.4f})")

    print(f"\n🏆 Training complete. Best val acc: {best_val_acc:.4f}")
    print(f"   Model  → {args.model_out}")
    print(f"   Classes → {args.classes_out}")


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge all crop-disease datasets and retrain the unified model."
    )

    # Dataset paths
    parser.add_argument("--plantvillage", type=str, default=None,
                        help="Path to PlantVillage flat class folder")
    parser.add_argument("--rice", type=str,
                        default="/home/grv/.cache/kagglehub/datasets/vbookshelf/rice-leaf-diseases/versions/1/rice_leaf_diseases",
                        help="Path to Rice Leaf Disease flat folder")
    parser.add_argument("--cotton", type=str,
                        default="/home/grv/.cache/kagglehub/datasets/janmejaybhoi/cotton-disease-dataset/versions/1/Cotton Disease",
                        help="Path to Cotton Disease root (contains train/val/test)")
    parser.add_argument("--wheat", type=str,
                        default="/home/grv/.cache/kagglehub/datasets/jocelyndumlao/wheat-nitrogen-deficiency-and-leaf-rust-image/versions/1/th422bg4yd-1/WheatLeafRust",
                        help="Path to WheatLeafRust root (contains train/val/test)")

    # Staging
    parser.add_argument("--staging", type=str, default="/tmp/neural_farms_unified",
                        help="Temp directory to stage merged dataset symlinks")
    parser.add_argument("--rebuild_staging", action="store_true",
                        help="Delete and rebuild staging dir before merging")

    # Outputs default into backend/models so FastAPI picks them up automatically
    parser.add_argument("--model_out", type=str,
                        default=os.path.join(os.path.dirname(__file__),
                                             "../../backend/models/best_model.pth"),
                        help="Output path for trained model weights")
    parser.add_argument("--classes_out", type=str,
                        default=os.path.join(os.path.dirname(__file__),
                                             "../../backend/models/classes.txt"),
                        help="Output path for class list (one class per line)")

    # Training hyper-params
    parser.add_argument("--epochs",     type=int,   default=15)
    parser.add_argument("--batch_size", type=int,   default=16,
                        help="Keep ≤16 for 4 GB VRAM (RTX 3050)")
    parser.add_argument("--lr",         type=float, default=1e-3)

    args = parser.parse_args()

    # Normalise output paths
    args.model_out   = os.path.abspath(args.model_out)
    args.classes_out = os.path.abspath(args.classes_out)
    os.makedirs(os.path.dirname(args.model_out),   exist_ok=True)
    os.makedirs(os.path.dirname(args.classes_out), exist_ok=True)

    if args.rebuild_staging and os.path.exists(args.staging):
        print(f"🗑️  Removing old staging dir: {args.staging}")
        shutil.rmtree(args.staging)

    print("=" * 60)
    print("  Neural Farms — Unified Dataset Merger & Trainer")
    print("=" * 60)

    staging_train, staging_val = build_staging(args)
    train(staging_train, staging_val, args)
