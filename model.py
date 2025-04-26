import os
from roboflow import Roboflow
from ultralytics import YOLO


def main():
    # ────────────────────────────────────────────────────────────────────────────
    # 1) CONFIGURATION
    # ────────────────────────────────────────────────────────────────────────────
    # Replace with your Roboflow API key
    ROBOFLOW_API_KEY = "vcToU4xIhy14YC0U3jdw"

    # Roboflow projects (pipe defects and wall cracks)
    PROJECTS = {
        "pipe_defects": {
            "workspace": "kev-2du16",  # Roboflow workspace name
            "project": "pipe-defects-2r7wj",
            "version": 1
        },
        "wall_cracks": {
            "workspace": "public",  # if wall dataset is public; otherwise your workspace
            "project": "sdnet2018",  # or your Roboflow wall-crack project name
            "version": 2
        }
    }

    # YOLO training settings
    EPOCHS = 5
    IMG_SIZE = 640
    BATCH_SIZE = 4
    MODEL_ARCH = "yolov5s"  # lightweight and ESP32‑compatible

    # Output folder
    OUTPUT_DIR = "runs/train"

    # ────────────────────────────────────────────────────────────────────────────
    # 2) DOWNLOAD & PREPARE DATASETS
    # ────────────────────────────────────────────────────────────────────────────
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)

    for name, cfg in PROJECTS.items():
        print(f"\n📥 Downloading `{name}` dataset from Roboflow...")
        project = rf.workspace(cfg["workspace"]).project(cfg["project"])
        dataset = project.version(cfg["version"]).download("yolov5")
        data_yaml = dataset.location + "/data.yaml"

        # ────────────────────────────────────────────────────────────────────────
        # 3) TRAIN YOLOv5
        # ────────────────────────────────────────────────────────────────────────
        print(f"🚀 Training YOLOv5 ({MODEL_ARCH}) on `{name}` for {EPOCHS} epochs...")

        # Load pre-trained model only once
        model = YOLO(f"{MODEL_ARCH}.pt")  # loads pretrained yolov5s.pt
        model.train(
            data=data_yaml,
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            batch=BATCH_SIZE,
            project="yolov5_defect_models",
            name=name,
            exist_ok=True
        )

        # ────────────────────────────────────────────────────────────────────────
        # 4) MOVE & RENAME BEST WEIGHTS
        # ────────────────────────────────────────────────────────────────────────
        # Ensure the weights directory exists and move the best weights to the proper location
        best_weights_src = os.path.join(OUTPUT_DIR, name, "weights", "best.pt")
        best_weights_dst = f"{name}_best.pt"

        if os.path.exists(best_weights_src):
            os.replace(best_weights_src, best_weights_dst)
            print(f"✅ `{name}` model saved to {best_weights_dst}")
        else:
            print(f"❌ `{name}` best weights file not found!")

    print("\n🎉 All models trained and saved locally!")


# Add the check for the main module
if __name__ == '__main__':
    main()
