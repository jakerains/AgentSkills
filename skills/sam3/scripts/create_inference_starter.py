#!/usr/bin/env python3
"""Generate starter scripts for SAM3 image/video inference."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


IMAGE_TEMPLATE = """#!/usr/bin/env python3
\"\"\"SAM3 image inference starter.\"\"\"

from PIL import Image
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor


def run_image_inference(image_path: str, prompt: str) -> None:
    model = build_sam3_image_model()
    processor = Sam3Processor(model)
    state = processor.set_image(Image.open(image_path))
    output = processor.set_text_prompt(prompt=prompt, state=state)

    print(f"masks: {output['masks'].shape}")
    print(f"boxes: {output['boxes'].shape}")
    print(f"scores: {output['scores'].shape}")


if __name__ == "__main__":
    run_image_inference("path/to/image.jpg", "person")
"""


VIDEO_TEMPLATE = """#!/usr/bin/env python3
\"\"\"SAM3 video inference starter.\"\"\"

from sam3.model_builder import build_sam3_video_predictor


def run_video_inference(video_path: str, prompt: str, frame_index: int = 0) -> None:
    predictor = build_sam3_video_predictor()
    start = predictor.handle_request(
        {"type": "start_session", "resource_path": video_path}
    )
    session_id = start["session_id"]

    try:
        response = predictor.handle_request(
            {
                "type": "add_prompt",
                "session_id": session_id,
                "frame_index": frame_index,
                "text": prompt,
            }
        )
        print(f"seed frame: {response['frame_index']}")
        print(f"objects in seed frame: {len(response['outputs'])}")

        stream = predictor.handle_stream_request(
            {
                "type": "propagate_in_video",
                "session_id": session_id,
                "propagation_direction": "forward",
            }
        )
        for idx, packet in enumerate(stream):
            print(f"frame {packet['frame_index']}: {len(packet['outputs'])} objects")
            if idx >= 4:
                break
    finally:
        predictor.handle_request({"type": "close_session", "session_id": session_id})


if __name__ == "__main__":
    run_video_inference("path/to/video.mp4", "person")
"""


BOTH_TEMPLATE = """#!/usr/bin/env python3
\"\"\"SAM3 combined image and video starter.\"\"\"

from PIL import Image
from sam3.model_builder import build_sam3_image_model, build_sam3_video_predictor
from sam3.model.sam3_image_processor import Sam3Processor


def run_image_inference(image_path: str, prompt: str) -> None:
    model = build_sam3_image_model()
    processor = Sam3Processor(model)
    state = processor.set_image(Image.open(image_path))
    output = processor.set_text_prompt(prompt=prompt, state=state)
    print(f"image boxes: {output['boxes'].shape}")


def run_video_inference(video_path: str, prompt: str, frame_index: int = 0) -> None:
    predictor = build_sam3_video_predictor()
    start = predictor.handle_request(
        {"type": "start_session", "resource_path": video_path}
    )
    session_id = start["session_id"]
    try:
        response = predictor.handle_request(
            {
                "type": "add_prompt",
                "session_id": session_id,
                "frame_index": frame_index,
                "text": prompt,
            }
        )
        print(f"video seed frame: {response['frame_index']}")
    finally:
        predictor.handle_request({"type": "close_session", "session_id": session_id})


if __name__ == "__main__":
    run_image_inference("path/to/image.jpg", "person")
    run_video_inference("path/to/video.mp4", "person")
"""


TEMPLATES = {
    "image": IMAGE_TEMPLATE,
    "video": VIDEO_TEMPLATE,
    "both": BOTH_TEMPLATE,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a starter SAM3 inference script."
    )
    parser.add_argument(
        "--mode",
        choices=sorted(TEMPLATES.keys()),
        default="image",
        help="Starter type to generate.",
    )
    parser.add_argument(
        "--output",
        default="sam3_starter.py",
        help="Output Python file path.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output).expanduser().resolve()

    if output_path.exists() and not args.overwrite:
        print(
            f"Refusing to overwrite existing file: {output_path}. "
            "Use --overwrite to replace it.",
            file=sys.stderr,
        )
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(TEMPLATES[args.mode])
    output_path.chmod(0o755)
    print(f"Created {output_path} ({args.mode} template)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
