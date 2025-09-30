import os
import csv
from collections import defaultdict
import logging

label_map = {
    0: "Container Ships", 1: "Bulk Carriers", 2: "Passenger Ships", 3: "Ro-ro Passenger Ships",
    4: "Ro-ro Cargo Ships", 5: "Tugs", 6: "Vehicles Carriers", 7: "Reefers", 8: "Yachts",
    9: "Sailing Vessels", 10: "Heavy Load Carriers", 11: "Wood Chips Carriers",
    12: "Livestock Carriers", 13: "Patrol Vessels",
    14: "Platforms", 15: "Standby Safety Vessels", 16: "Combat Vessels",
    17: "Training Ships", 18: "Icebreakers", 19: "Replenishment Vessels",
    20: "Tankers", 21: "Fishing Vessels", 22: "Supply Vessels",
    23: "Carrier Floating", 24: "Dredgers"
}
NUM_CLASSES = len(label_map)

# augmentation markers (searched as substrings inside filename)
AUGMENTATIONS = {
    "fog": "fog",
    "rain": "rain",
    "scale": "scale",
    "transform": "transform"
}

def classify_file_type(filename: str) -> str:
    """Return augmentation type based on substring in filename."""
    for key, name in AUGMENTATIONS.items():
        if key in filename:
            return name
    return "original"

def contar_split_by_files(split_path: str, split_name: str):
    labels_path = os.path.join(split_path, "labels")
    if not os.path.isdir(labels_path):
        logging.warning(f"Folder not found: {labels_path}")
        return defaultdict(lambda: defaultdict(int))

    label_files = [f for f in os.listdir(labels_path) if f.lower().endswith(".txt")]

    results = defaultdict(lambda: defaultdict(int))  
    # results[class_id][type] = count

    for lf in label_files:
        file_path = os.path.join(labels_path, lf)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    try:
                        cls_id = int(float(parts[0]))
                    except ValueError:
                        continue
                    if 0 <= cls_id < NUM_CLASSES:
                        ftype = classify_file_type(lf)
                        results[cls_id][ftype] += 1
        except Exception as e:
            logging.warning(f"[WARN] Error reading {file_path}: {e}")

    return results

def count(base_dir: str, csv_path: str = "../report/augmented_counting.csv"):
    splits = ["train", "val", "test"]
    all_results = {s: contar_split_by_files(os.path.join(base_dir, s), s) for s in splits}

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "id", "class",
            "train_original", "train_scale", "train_transform", "train_fog", "train_rain", "train_augmented_total",
            "val_original", "test_original", "total"
        ])

        for cls_id in range(NUM_CLASSES):
            cls_name = label_map[cls_id]

            # Train counts
            train_counts = all_results.get("train", {}).get(cls_id, {})
            train_original = train_counts.get("original", 0)
            train_scale = train_counts.get("scale", 0)
            train_transform = train_counts.get("transform", 0)
            train_fog = train_counts.get("fog", 0)
            train_rain = train_counts.get("rain", 0)
            train_aug_total = train_scale + train_transform + train_fog + train_rain

            # Val/Test originals
            val_counts = all_results.get("val", {}).get(cls_id, {})
            val_original = val_counts.get("original", 0)

            test_counts = all_results.get("test", {}).get(cls_id, {})
            test_original = test_counts.get("original", 0)

            # Grand total
            total = (
                train_original + train_aug_total +
                val_original + test_original
            )

            w.writerow([
                cls_id, cls_name,
                train_original, train_scale, train_transform, train_fog, train_rain, train_aug_total,
                val_original, test_original, total
            ])

    print(f"CSV generated: {csv_path}")

