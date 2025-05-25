# A New Approach for Vessel Detection, Classification and Estimation Using Monocular Vision

This repository provides tools and instructions to prepare, build, use, and evaluate the **VESSA Dataset** and associated models for vessel detection, classification, and tracking using monocular vision.





https://github.com/user-attachments/assets/5c258011-4a4a-449e-965a-329bc0af8dc3

---

## Walkthrough

1. 🔧 Start with the **Environment Preparation** section.

2. 🧱 If you want to **download and build the VESSA dataset**, proceed to the next section: **Building the VESSA Dataset**.

3. ⬇️ If you prefer to use the **ready-to-use VESSA dataset**, skip ahead to **Downloading the Ready-to-Use Dataset**.

4. 📊 To **reproduce the results** described in our paper, go to **Reproducing Evaluation Results**.

5. 📹 To **customize the model** or use it **as-is**, see **Using the Model on Custom Videos or Live Streams**.


---

## 🔧 Environment Preparation

1. Install **Python 3.12** and allow the installer to automatically set the Python PATH.
2. Update **NVIDIA® GPU drivers** to version **450.80.02 or higher** if you want GPU support.
3. If you're using **Linux**, you can execute the `create-env` script using your system shell.


---

## 🧱 Building the VESSA Dataset 

1. Run the script:  
   ```bash
   python _run_preparation.py_
   ```
   This script includes four main steps:
   - Downloading
   - Labeling
   - Statistics collection
   - Viewing

   To skip any step, simply comment out the corresponding function call in `_run_preparation.py_`.

2. Customize dataset paths and parameters in `dataset_config.py`.

3. Notes:
   - **Storage:** Downloading the dataset may require **~1 TB**.
   - To save space, set the `_auto_resize_` parameter to `True` when calling the `download` function.
   - It is **recommended to set `_start_again_` to `False`** to avoid losing previously downloaded data.
   - The automatic labeling process is slow and may have errors; however, **verified annotations by human experts** are provided. By default, labeling is **disabled**. If you want the consolidated dataset, go to the next topic.
   - The manual labeling required the redistribution of the samples with `distribute.py` script.

4. You can visualize all images and their bounding boxes (auxiliary tool, not UX-oriented).

---

## ⬇️ Downloading the Ready-to-Use Dataset

- Visit the official https://doi.org/10.5281/zenodo.15459993 and download the `.zip` file.
- Unzip the file into a local folder of your choice.

---

## 📊 Reproducing Evaluation Results

1. Download the dataset as described above.
2. Copy all folders from the second schema to the `evaluation/tmm` folder.
3. Run the evaluation:Downloading the Ready-to-Use Dataset
   ```bash
   python run_trials.py
   ```

---

## 📹 Using the Model on Custom Videos or Live Streams

1. Ensure your `_config_` folder contains a JSON file with camera parameters.
2. Specify this file in `run_model.py`.
3. If you want to use translated category names or different dimensions, create a new file and place it in the the `categories` folder. Then, specify the correct filename in `run_model.py`, passing it to the DCM constructor.

### JSON Example (`setup.json`)
```json
{
  "camera": {
    "id": "EN",
    "address": "core/samples/passenger_ship_02.mp4",
    "latitude": -22.912759833,
    "longitude": -43.1582615,
    "installation_height": 30,
    "surveillance_radius": 2800,
    "focus_frame_view": 350,
    "reference_azimuth": 338.5,
    "reference_elevation": -3.2,
    "sensor_width_lens": 5.6,
    "sensor_height_lens": 3.1,
    "zoom_multiplier_min": 0,
    "zoom_multiplier_max": 30,
    "zoom_lens_min": 4.3,
    "zoom_lens_max": 129,
    "hfov_min": 2.1,
    "hfov_max": 63.7,
    "sensor_width_resolution": 1920,
    "sensor_height_resolution": 1080
  },
  "calibration": {
    "threshold_intersection_detecting": 0.6,
    "threshold_confidence": 0.2,
    "threshold_classification": 0.1,
    "threshold_intersection_tracking": 0.1,
    "train_img_width": 640,
    "train_img_height": 640
  }
}
```

### Key Parameters

- **`id`**: Unique identifier for video source (used in output file naming).
- **`address`**: RTSP stream or path to local video file.
- **`latitude` / `longitude`**: Camera installation coordinates.
- **`installation_height`**: Camera height from sea level, used for tilt and zoom calculations.
- **`surveillance_radius`**: Range of camera coverage, used for zoom calculation (optional).
- **`focus_frame_view`**: Pixel width for vessel framing — **default zoom method**.
- **`reference_azimuth` / `reference_elevation`**: Camera orientation in degrees.
- **Sensor parameters**: Accurate lens dimensions and sensor resolutions are required for kinematic estimation:
  - `sensor_width_lens`, `sensor_height_lens`
  - `sensor_width_resolution`, `sensor_height_resolution`
  - `hfov_min`, `hfov_max`
- **Calibration parameters**: YOLO thresholds and training image size:
  - `threshold_intersection_detecting`
  - `threshold_confidence`
  - `threshold_classification`
  - `train_img_width`, `train_img_height`
- **Optional**: `resize` flag to adjust image sizes during processing.

---

## 📂 Repository Structure

```
.
├── env/
|   └── requirements.txt   
|   └── linux/
|       └── create-env.sh
├── categories/
│   └── category_en.py
├── scripts
|   └── core/
|       └── config/
│           └── setup.json
│       └── samples/
│       └── models/
|           └── model.pt
|       └── evaluation/
│           └── trials/ 
│               └── dcm/            
│               └── tmm/
|       └── preparation/
|           └── resources
|               └── data.yaml
|               └── eni.dat
|       └── scripts/
|           └── run_preparation.py
|           └── run_model.py
|           └── run_trials.py
└── README.md
```

---

## 🧠 Citation

If you use the VESSA Dataset or the model in academic work, please cite us!

VESSA Dataset: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15459993.svg)](https://doi.org/10.5281/zenodo.15459993)


