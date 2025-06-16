# config/model_config.py

import streamlit as st
import requests
import os
from pathlib import Path

# Model configurations based on your testing results
MODEL_CONFIGS = {
    "grid_3x3": {
        "name": "3x3 Grid YOLO",
        "path": "models/best(grid_syn_keypt).pt",
        "release_url": "https://github.com/gadhalekshmip/leaftip/releases/download/v1.0/best(grid_syn_keypt).pt",
        "type": "yolo_grid",
        "conf_threshold": 0.25,
        "grid_size": 3,
        "distance_threshold": 8,
        "description": "YOLO model for 3x3 grid analysis",
        "color": "green"
    },
    "grid_5x5": {
        "name": "5x5 Grid YOLO",
        "path": "models/key_grid_syn_5x5.pt", 
        "release_url": "https://github.com/gadhalekshmip/leaftip/releases/download/v1.0/key_grid_syn_5x5.pt",
        "type": "yolo_grid",
        "conf_threshold": 0.20,
        "grid_size": 5,
        "distance_threshold": 8,
        "description": "Best performing YOLO model for 5x5 grid analysis",
        "color": "blue",
        "is_best": True  # Move this from grid_5x5 to frcnn_grid_3x3
    },
    "yolo_entire": {
        "name": "YOLO Entire Image",
        "path": "models/best.pt",
        "release_url": "https://github.com/gadhalekshmip/leaftip/releases/download/v1.0/best.pt",
        "type": "yolo_entire",
        "conf_threshold": 0.25,
        "description": "YOLO model for entire image processing",
        "color": "red"
    },
    "frcnn": {
        "name": "Faster R-CNN",
        "path": "models/fold_4_best_map50_aug.pth",
        "release_url": "https://github.com/gadhalekshmip/leaftip/releases/download/v1.0/fold_4_best_map50_aug.pth",
        "type": "frcnn",
        "conf_threshold": 0.5,
        "description": "Faster R-CNN model for entire image processing",
        "color": "purple",
        "box_size": 10,
        "image_size": 1536,  # Target resize to match training
        "num_classes": 2,
        # Post-processing parameters from Colab
        "nms_threshold": 0.5,
        "distance_threshold": 15,  # Keypoint NMS distance (critical for removing FP)
        "max_detections": 200
    },
    "roi_model": {
        "name": "ROI Detection Model",
        "path": "models/best_f1_croped_syn.pt",
        "release_url": "https://github.com/gadhalekshmip/leaftip/releases/download/v1.0/best_f1_croped_syn.pt",
        "type": "yolo_roi",
        "conf_threshold": 0.25,
        "description": "YOLO model optimized for ROI-based detection",
        "color": "orange"
    },
    "frcnn_grid_3x3": {
        "name": "3x3 Grid FRCNN (Best)",
        "path": "models/fold_1_best_map_grid_v2_aug.pth",
        "release_url": "https://github.com/gadhalekshmip/leaftip/releases/download/v1.0/fold_1_best_map_grid_v2_aug.pth",
        "type": "frcnn_grid",
        "conf_threshold": 0.3,
        "nms_threshold": 0.3,
        "grid_size": 3,
        "distance_threshold": 15,
        "box_size": 10,
        "image_size": 1536,
        "max_detections": 200,
        "description": "Best performing FRCNN model for 3x3 grid analysis",
        "color": "orange"
    }
}

def download_model_if_needed(config):
    """Download model from GitHub releases if not exists locally"""
    local_path = Path(config["path"])
    
    # Create models directory if it doesn't exist
    local_path.parent.mkdir(exist_ok=True)
    
    # If file doesn't exist, download it
    if not local_path.exists():
        try:
            with st.spinner(f"Downloading {config['name']}..."):
                response = requests.get(config["release_url"], stream=True)
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                st.success(f"✅ Downloaded {config['name']}")
                
        except Exception as e:
            st.error(f"❌ Failed to download {config['name']}: {str(e)}")
            return None
    
    return str(local_path)


# Replace the cache and unload functions with these:

def get_cached_model(model_key):
    """Get cached model instance from session state - use model_key not name"""
    return st.session_state.get(f'model_{model_key}', None)

def cache_model(model_key, model_instance):
    """Cache model in session state - use model_key not name"""
    st.session_state[f'model_{model_key}'] = model_instance

def unload_model(model_key):
    """Unload specific model from memory"""
    cache_key = f'model_{model_key}'
    if cache_key in st.session_state:
        del st.session_state[cache_key]
        st.success(f"✅ Unloaded {model_key}")
        st.rerun()  # Add rerun to refresh status
        return True
    else:
        st.warning(f"⚠️ {model_key} not found in cache")
        return False

def unload_all_models():
    """Nuclear option - clear everything"""
    import gc
    
    # Clear all model-related session state
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('model_')]
    count = len(keys_to_remove)
    
    for key in keys_to_remove:
        del st.session_state[key]
    
    # Clear ALL Streamlit caches
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Force garbage collection
    gc.collect()
    
    if count > 0:
        st.success(f"🗑️ Cleared {count} models and all caches")
    else:
        st.info("No models found in memory")
    
    # Force app rerun
    st.rerun()
def get_model_memory_usage():
    """Get current memory usage"""
    import psutil
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    memory_percent = psutil.virtual_memory().percent
    return memory_mb, memory_percent
def get_model_config(model_key):
    """Get configuration for a specific model"""
    return MODEL_CONFIGS.get(model_key, None)

def get_available_models():
    """Get list of available models with their paths checked"""
    available = {}
    for key, config in MODEL_CONFIGS.items():
        if os.path.exists(config["path"]):
            available[key] = config
        else:
            # Model file not found, mark as unavailable
            config_copy = config.copy()
            config_copy["available"] = False
            available[key] = config_copy
    return available

def get_best_model():
    """Get the best performing model configuration"""
    for key, config in MODEL_CONFIGS.items():
        if config.get("is_best", False):
            return key, config
    return "grid_5x5", MODEL_CONFIGS["grid_5x5"]

def validate_model_path(model_path):
    """Validate if model file exists"""
    return os.path.exists(model_path)

# Default processing parameters
DEFAULT_PARAMS = {
    "batch_processing": {
        "max_images": 100,
        "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    },
    "visualization": {
        "point_colors": {
            "detection": "red",
            "manual": "green", 
            "roi": "orange",
            "grid_3x3": "green",
            "grid_5x5": "blue",
            "frcnn": "purple",
            "yolo": "red"
        },
        "point_size_range": (4, 8),
        "grid_line_color": "cyan",
        "grid_line_width": 2,
        "roi_line_color": "orange",
        "roi_line_width": 3
    },
    "export": {
        "image_formats": ["PNG", "JPEG"],
        "csv_headers": ["x", "y", "confidence", "method", "detection_type", "roi_coords"]
    }
}
