# SAM 3 Setup And Inference

Use this reference when installing `facebookresearch/sam3`, authenticating for checkpoints, and running image or video inference.

## Prerequisites

- Python 3.12 recommended
- PyTorch 2.7 with CUDA 12.6 wheels for GPU workflows
- Hugging Face account with access to `facebook/sam3`

## Environment Setup

```bash
conda create -n sam3 python=3.12 -y
conda activate sam3
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
git clone https://github.com/facebookresearch/sam3.git
cd sam3
pip install -e .
```

Optional extras:

```bash
pip install -e ".[notebooks]"
pip install -e ".[train,dev]"
```

Run preflight checks any time:

```bash
python scripts/sam3_preflight_check.py
python scripts/sam3_preflight_check.py --strict
```

## Checkpoint Access And Authentication

Before first model load:

1. Request access to `facebook/sam3` on Hugging Face.
2. Run `hf auth login`.
3. Verify auth with `hf auth whoami`.

`build_sam3_image_model()` and `build_sam3_video_model()` download `sam3.pt` automatically when `checkpoint_path` is not provided.

## Image Inference Pattern

```python
from PIL import Image
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor

model = build_sam3_image_model()
processor = Sam3Processor(model)

image = Image.open("path/to/image.jpg")
state = processor.set_image(image)
output = processor.set_text_prompt(prompt="person in red jersey", state=state)

masks = output["masks"]
boxes = output["boxes"]
scores = output["scores"]
```

Use `processor.add_geometric_prompt(...)` for box-based refinement. Use `processor.set_confidence_threshold(...)` when filtering too many low-confidence masks.

## Video Inference Pattern

```python
from sam3.model_builder import build_sam3_video_predictor

predictor = build_sam3_video_predictor()
start = predictor.handle_request(
    {"type": "start_session", "resource_path": "path/to/video.mp4"}
)
session_id = start["session_id"]

response = predictor.handle_request(
    {
        "type": "add_prompt",
        "session_id": session_id,
        "frame_index": 0,
        "text": "person in white shirt",
    }
)

for packet in predictor.handle_stream_request(
    {"type": "propagate_in_video", "session_id": session_id, "propagation_direction": "forward"}
):
    frame_index = packet["frame_index"]
    outputs = packet["outputs"]
    print(frame_index, len(outputs))

predictor.handle_request({"type": "close_session", "session_id": session_id})
```

`resource_path` accepts an MP4 file or a JPEG frame directory.

## Integration Notes

- Keep prompts concrete and visually discriminative.
- Start with text prompt, then add point or box prompts for hard cases.
- Persist prompt and threshold values in logs for reproducibility.
- Use `checkpoint_path=` when model files are pre-downloaded or mirrored internally.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 401/403 while downloading checkpoint | Missing access or auth | Request access and run `hf auth login` |
| CUDA out of memory | Input too large or too many concurrent sessions | Use fewer parallel jobs, close inactive sessions, reduce workload |
| Very slow inference | Running on CPU fallback | Verify CUDA install and `torch.cuda.is_available()` |
| `Cannot find session ...` | Session was closed or expired | Create a new session with `start_session` |
| Missing notebook tools | Optional extras not installed | Run `pip install -e ".[notebooks]"` |
