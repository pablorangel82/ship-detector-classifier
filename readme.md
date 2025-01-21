# Environment Preparation

## With CUDA Support

- Install Python 3.10.11 and allow the installer to automatically set the "Python PATH."
- Update NVIDIA® GPU drivers to version 450.80.02 or higher.
- Execute the `create-env-gpu` script using your operating system shell.

## Without CUDA Support

- Install Python 3.10.11 and allow the installer to automatically set the "Python PATH."
- Execute the `create-env-cpu` script using your operating system shell.

---

# Downloading and Building the Dataset

- Run the Python script `_run_dataset.py_.` This process includes three steps: downloading, labeling, and viewing. To skip any of these steps, simply comment out the corresponding function call in `_run_dataset.py_.`  
- The script `dataset_config.py` contains all parameters. You can modify settings such as the download folder, dataset folder, and labeling parameters.  
- **Note**: Downloading the dataset requires significant storage space (approximately 1TB). To save space, you can automatically resize photos by setting the `_auto_resize_` parameter to `True` when calling the `download` function.  
- It is recommended to set the `_start_again_` parameter to `False.` If set to `True,` all previously downloaded data will be discarded.  
- Automating the labeling process may take several hours and could result in precision and accuracy errors. However, we provide annotations that have been carefully reviewed by human experts. By default, the `label` function call is disabled.  
- You can display all images and bounding boxes. This is an auxiliary tool designed for functionality rather than user experience.

---

# Customizing Video Parameters, Running the Model, and Viewing Results

- Ensure you have a JSON file containing calibration and camera parameters located in the `_resources_` folder. The filename must be specified in the `run_model.py` script.  
- The `DetectionManagement` constructor requires the name of the JSON file containing camera and model parameters. An example JSON file, `_rstp_example.json_,` is provided for reference.  

### Example JSON Structure  

```json
{
    "camera": {
        "address": "../../report/samples/barca.mp4",
        "latitude": -22.912759833,
        "longitude": -43.1582615,
        "standard_bearing": 336,
        "zoom_min": 0,
        "zoom_max": 30,
        "hfov_min": 2.1,
        "hfov_max": 63.7,
        "tilt_range": 350,
        "pan_range": 360,
        "frame_rate": 30,
        "width_resolution": 1920,
        "height_resolution": 1080
    },
    "calibration": {
        "threshold_intersection": 0.6,
        "threshold_confidence": 0.05,
        "threshold_classification": 0.1,
        "train_img_width": 640,
        "train_img_height": 640,
        "resize": "True"
    }
}
```

### Key Parameters  

- **`address`**: The RTSP address or the local file path containing the video to be used by the model.  
- **`latitude` and `longitude`**: The geographic coordinates of the stationary camera.  
- **`standard_bearing`**: The default bearing of the camera installation, based on the polar coordinate system. This value is used to adjust vessel bearing estimations.  
- **`hfov`, `tilt_range`, and `pan_range`**: The physical characteristics of the camera.  
- **`frame_rate`, `width_resolution`, and `height_resolution`**: The video stream settings.  
- **`threshold_intersection` and `threshold_confidence`**: YOLO configuration parameters.  
- **`threshold_classification`**: The minimum confidence value required to classify a result as anything other than "Unknown."  
- **`train_img_width` and `train_img_height`**: The dimensions of the images used to train the model.  
- **`resize`**: Indicates whether to resize images for detection and classification.

The `DetectionManagement` constructor also requires the language of the Python script containing translated vessel categories. All files must follow the naming convention `_category_<language>.py_.`