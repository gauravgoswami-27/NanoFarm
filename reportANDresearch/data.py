"""
data.py  –  Neural Farms Dataset Downloader
============================================
Downloads all three crop-disease datasets from Kaggle using `kagglehub`.
Requires:  pip install kagglehub

Run:  python data.py
"""
import kagglehub
import os

DATASETS = [
    {
        "slug":        "vbookshelf/rice-leaf-diseases",
        "description": "Rice Leaf Diseases  (3 classes: Bacterial leaf blight, Brown spot, Leaf smut)",
    },
    {
        "slug":        "janmejaybhoi/cotton-disease-dataset",
        "description": "Cotton Disease Dataset  (4 classes: diseased/fresh leaf/plant, pre-split)",
    },
    {
        "slug":        "jocelyndumlao/wheat-nitrogen-deficiency-and-leaf-rust-image",
        "description": "Wheat Nitrogen Deficiency & Leaf Rust  (2 classes: control/diseased, pre-split)",
    },
]

print("=" * 60)
print("  Neural Farms — Kaggle Dataset Downloader")
print("=" * 60)

paths = {}
for ds in DATASETS:
    print(f"\n⬇  {ds['description']}")
    path = kagglehub.dataset_download(ds["slug"])
    paths[ds["slug"]] = path
    print(f"   ✅  {path}")

print("\n" + "=" * 60)
print("All datasets ready. Next step:")
print("")
print("  cd ml_models/disease_vision")
print("  python merge_and_train.py \\")
print("    --rice   " + repr(
    os.path.join(paths.get("vbookshelf/rice-leaf-diseases", "<rice_path>"),
                 "rice_leaf_diseases")))
print("    --cotton " + repr(
    os.path.join(paths.get("janmejaybhoi/cotton-disease-dataset", "<cotton_path>"),
                 "Cotton Disease")))
print("    --wheat  " + repr(
    os.path.join(paths.get(
        "jocelyndumlao/wheat-nitrogen-deficiency-and-leaf-rust-image", "<wheat_path>"),
        "th422bg4yd-1", "WheatLeafRust")))
print("    --epochs 15 --batch_size 16")
print("=" * 60)