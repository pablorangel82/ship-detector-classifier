import albumentations as A
import cv2
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import numpy as np
import random
import math
from dataset_config import DatasetConfig

base_path = DatasetConfig.ORIGINAL_DATASET_FOLDER
output_base_path = DatasetConfig.AUGMENTED_DATASET_FOLDER
subsets = ["train", "val", "test"]

train_counts = [16002, 22611, 5034, 7077, 3939, 11721, 4182, 4761, 4471,
                512, 472, 798, 901, 852, 354, 1429, 183, 460, 321,
                388, 18964, 10370, 6307, 1548, 1786]
max_count = max(train_counts)

total_creations = []
creation_per_image = []

scale_transform = A.Compose([
    A.Affine(scale=(0.3, 1.2), rotate=(0, 0), translate_percent=(-0.1, 0.1), p=1.0),
    A.PadIfNeeded(min_height=640, min_width=640, border_mode=cv2.BORDER_CONSTANT),
    A.CenterCrop(height=640, width=640)
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'], min_visibility=0.2))

rain_transform = A.Compose([A.RandomRain(p=1)])
fog_transform = A.Compose([A.RandomFog(p=1)])

object_transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.8),
    A.HueSaturationValue(p=0.7),
    A.MotionBlur(blur_limit=5, p=0.4)
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'], check_each_transform=False))


for c in train_counts:
    m = max_count - c
    total_creations.append(m)
    m_i = max(0,(max_count - c) / c)
    creation_per_image.append(math.floor(m_i))

def inpaint_black_background(image):
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([10, 10, 10])
    mask = cv2.inRange(image, lower_black, upper_black)
    if cv2.countNonZero(mask) == 0:
        return image
    return cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)


def filter_valid_bboxes(bboxes, labels):
    filtered = [(lbl, bbox) for lbl, bbox in zip(labels, bboxes) if bbox[2] > 0 and bbox[3] > 0]
    if filtered:
        labels_f, bboxes_f = zip(*filtered)
        return list(bboxes_f), list(labels_f)
    return [], []

def save_image_and_label(img, labels, base_name, subset):
    img_dir = os.path.join(output_base_path, subset, "images")
    lbl_dir = os.path.join(output_base_path, subset, "labels")
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    img_path = os.path.join(img_dir, base_name + ".jpg")
    lbl_path = os.path.join(lbl_dir, base_name + ".txt")

    if os.path.exists(img_path) and os.path.exists(lbl_path):
        return True

    cv2.imwrite(img_path, img)

    with open(lbl_path, "w") as f:
        for lbl, bbox in labels:
            f.write(f"{lbl} {' '.join(map(str, bbox))}\n")
    return True

def worker(subset, image_file):
    return process_image(subset, image_file)

def process_image(subset, image_file):
    images_dir = os.path.join(base_path, subset, "images")
    labels_dir = os.path.join(base_path, subset, "labels")
    label_file = os.path.splitext(image_file)[0] + ".txt"
    label_path = os.path.join(labels_dir, label_file)
    image_path = os.path.join(images_dir, image_file)
    
    if not os.path.exists(label_path) or not os.path.exists(image_path):
        return Counter()
    
    with open(label_path, "r") as f:
        lines = f.readlines()
    bboxes, labels = [], []
    for line in lines:
        cls_id, x, y, w, h = line.strip().split()
        cls_id = int(cls_id)
        if cls_id == 13:
            return
        if cls_id > 13:
            cls_id -= 1
        bboxes.append([float(x), float(y), float(w), float(h)])
        labels.append(cls_id)
    
    image = cv2.imread(image_path)
    base_name_orig = os.path.splitext(image_file)[0]
    save_image_and_label(image, list(zip(labels, bboxes)), base_name_orig, subset)
    class_counter = Counter(labels)

    if subset == "train":
        for cls_id in labels:
            creations = creation_per_image[cls_id]
            if creations == 0:
                if random.random() < 0.20:
                    creations = 1
            for i in range(creations):
                type = 'scale'
                if creations > 10:
                    if random.random() < 0.5:
                        augmented = scale_transform(image=image, bboxes=bboxes, class_labels=labels)
                        aug_img, bboxes_t, labels_t = augmented["image"], augmented["bboxes"], augmented["class_labels"]
                        aug_img = inpaint_black_background(aug_img)
                    else:
                        type = 'transform'
                        augmented = object_transform(image=image, bboxes=bboxes, class_labels=labels)
                        aug_img, bboxes_t, labels_t = augmented["image"], augmented["bboxes"], augmented["class_labels"]
                else:
                    augmented = scale_transform(image=image, bboxes=bboxes, class_labels=labels)
                    aug_img, bboxes_t, labels_t = augmented["image"], augmented["bboxes"], augmented["class_labels"]
                    aug_img = inpaint_black_background(aug_img)
                    
                suffix = f"_aug_{type}_{i}"

                # Weather effect
                if random.random() < 0.3:
                    if random.random() < 0.5:
                        aug_img = rain_transform(image=aug_img)["image"]
                        suffix += "_rain"
                    else:
                        aug_img = fog_transform(image=aug_img)["image"]
                        suffix += "_fog"

                bboxes_f, labels_f = filter_valid_bboxes(bboxes_t, labels_t)
                if bboxes_f:
                    save_image_and_label(aug_img, list(zip(labels_f, bboxes_f)), base_name_orig + suffix, subset)
                    class_counter.update(labels_f)
    return class_counter


if __name__ == "__main__":
    start_time = time.time()
    workers = max(1, multiprocessing.cpu_count() - 1)

    for subset in subsets:
        images_dir = os.path.join(base_path, subset, "images")
        all_images = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg", ".png"))]
        total_images = len(all_images)
        class_counter_total = Counter()

        print(f"\nSubset: {subset} ({total_images} images)...", flush=True)

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for img in all_images:
                futures[executor.submit(worker,subset, img)] = img
            for idx, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result()
                    class_counter_total.update(result)
                except Exception as e:
                    print(f"Error processing {futures[future]}: {e}", flush=True)

                if idx % 30 == 0 or idx == total_images:
                    elapsed = time.time() - start_time
                    print(f"[{elapsed/60:.2f} min] {idx}/{total_images} images - Partial:", flush=True)
                    for cls_id in range(len(train_counts)):
                        print(f" Class {cls_id:02d}: {class_counter_total.get(cls_id, 0)}", flush=True)
                    print("-" * 40, flush=True)

        print(f"\nFinal class counts for {subset}:", flush=True)
        for cls_id in range(len(train_counts)):
            print(f" Class {cls_id:02d}: {class_counter_total.get(cls_id, 0)}", flush=True)

    print("\nAugmentation Pipeline Completed!", flush=True)