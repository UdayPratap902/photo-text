from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
from datetime import datetime, timedelta
import cv2
import subprocess
import tempfile
import shutil
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FOLDER = Path("input")
OUTPUT_FOLDER = Path("output")


# ============================================================
# TIMESTAMP
# ============================================================

# Timestamp shown on:
# - Images
# - First frame of videos
#
# Supported:
# "17 Aug 2026 13:02:31"
# OR
# "01:23:34"

START_TIMESTAMP = "17 Aug 2026 13:02:31"


# ============================================================
# STATIC TEXT
# ============================================================

# These lines remain unchanged.

STATIC_TEXT_LINES = [
    "27°51'48\"N 79°55'55\"E",
    "Shahjahanpur, Bareilly Division 242001",
    "India",
    "Altitude: 87.8msnm",
    "Speed: 0.0km/h",
]


# ============================================================
# FONT SETTINGS
# ============================================================

FONT_PATH = "C:/Windows/Fonts/arial.ttf"

BASE_FONT_SIZE = 60

LINE_SPACING = 8

# Change both to 0 for absolutely no intended margin.
RIGHT_MARGIN = 10
BOTTOM_MARGIN = 10

TEXT_COLOR = (255, 255, 255)

SHADOW_COLOR = (0, 0, 0)

SHADOW_OFFSET = 3


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
}


# ============================================================
# TIMESTAMP PARSER
# ============================================================

def parse_start_timestamp(timestamp):

    try:

        return (
            datetime.strptime(
                timestamp,
                "%d %b %Y %H:%M:%S"
            ),
            "datetime"
        )

    except ValueError:

        try:

            return (
                datetime.strptime(
                    timestamp,
                    "%H:%M:%S"
                ),
                "time"
            )

        except ValueError:

            raise ValueError(
                "START_TIMESTAMP must be either:\n"
                '"17 Aug 2026 13:02:31"\n'
                "or\n"
                '"01:23:34"'
            )


# ============================================================
# FONT
# ============================================================

def get_font(image_width):

    scale = image_width / 1500

    font_size = max(
        18,
        int(BASE_FONT_SIZE * scale)
    )

    return ImageFont.truetype(
        FONT_PATH,
        font_size
    )


# ============================================================
# GENERATE TIMESTAMP
# ============================================================

def get_timestamp(
    start_datetime,
    timestamp_type,
    elapsed_seconds
):

    elapsed = timedelta(
        seconds=elapsed_seconds
    )

    current_time = (
        start_datetime
        + elapsed
    )

    if timestamp_type == "datetime":

        return current_time.strftime(
            "%d %b %Y %H:%M:%S"
        )

    return current_time.strftime(
        "%H:%M:%S"
    )


# ============================================================
# BUILD TEXT LINES
# ============================================================

def build_text_lines(timestamp_text):

    return [
        timestamp_text
    ] + STATIC_TEXT_LINES


# ============================================================
# DRAW TEXT ON PIL IMAGE
# ============================================================

def draw_text_on_image(
    image,
    timestamp_text
):

    draw = ImageDraw.Draw(image)

    width, height = image.size

    font = get_font(width)

    text_lines = build_text_lines(
        timestamp_text
    )

    # --------------------------------------------------------
    # Calculate text dimensions
    # --------------------------------------------------------

    line_data = []

    for line in text_lines:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        text_height = (
            bbox[3] - bbox[1]
        )

        line_data.append(
            (
                line,
                text_width,
                text_height
            )
        )

    total_text_height = (
        sum(
            item[2]
            for item in line_data
        )
        + LINE_SPACING
        * (len(line_data) - 1)
    )

    # --------------------------------------------------------
    # Bottom position
    # --------------------------------------------------------

    y = (
        height
        - BOTTOM_MARGIN
        - total_text_height
    )

    # --------------------------------------------------------
    # Draw lines
    # --------------------------------------------------------

    for (
        line,
        text_width,
        text_height
    ) in line_data:

        # Right aligned
        x = (
            width
            - RIGHT_MARGIN
            - text_width
        )

        # Shadow
        draw.text(
            (
                x + SHADOW_OFFSET,
                y + SHADOW_OFFSET
            ),
            line,
            font=font,
            fill=SHADOW_COLOR
        )

        # Main text
        draw.text(
            (
                x,
                y
            ),
            line,
            font=font,
            fill=TEXT_COLOR
        )

        y += (
            text_height
            + LINE_SPACING
        )

    return image


# ============================================================
# PROCESS IMAGE
# ============================================================

def process_image(
    input_path,
    output_path
):

    print(
        f"\nProcessing IMAGE: "
        f"{input_path.name}"
    )

    start_datetime, timestamp_type = (
        parse_start_timestamp(
            START_TIMESTAMP
        )
    )

    # Image timestamp does not change.
    timestamp_text = get_timestamp(
        start_datetime,
        timestamp_type,
        0
    )

    image = Image.open(
        input_path
    )

    # Apply EXIF orientation
    image = ImageOps.exif_transpose(
        image
    )

    # Convert modes when necessary
    if image.mode not in (
        "RGB",
        "RGBA"
    ):

        image = image.convert(
            "RGB"
        )

    processed = draw_text_on_image(
        image,
        timestamp_text
    )

    # JPEG doesn't support RGBA
    if (
        output_path.suffix.lower()
        in {".jpg", ".jpeg"}
        and processed.mode == "RGBA"
    ):

        processed = processed.convert(
            "RGB"
        )

    # Save
    if output_path.suffix.lower() in {
        ".jpg",
        ".jpeg"
    }:

        processed.save(
            output_path,
            quality=95,
            optimize=True
        )

    else:

        processed.save(
            output_path
        )

    print(
        f"Saved: {output_path}"
    )


# ============================================================
# PROCESS VIDEO
# ============================================================

def process_video(
    input_path,
    output_path
):

    print(
        f"\nProcessing VIDEO: "
        f"{input_path.name}"
    )

    start_datetime, timestamp_type = (
        parse_start_timestamp(
            START_TIMESTAMP
        )
    )

    # --------------------------------------------------------
    # Open video
    # --------------------------------------------------------

    cap = cv2.VideoCapture(
        str(input_path)
    )

    if not cap.isOpened():

        raise RuntimeError(
            f"Could not open video: "
            f"{input_path}"
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        fps = 30

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    frame_count = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    duration = (
        frame_count / fps
        if frame_count > 0
        else 0
    )

    print(
        f"Resolution: "
        f"{width}x{height}"
    )

    print(
        f"FPS: {fps:.2f}"
    )

    print(
        f"Duration: "
        f"{duration:.2f}s"
    )

    print(
        f"Starting timestamp: "
        f"{START_TIMESTAMP}"
    )

    # --------------------------------------------------------
    # Temporary directory
    # --------------------------------------------------------

    temp_dir = Path(
        tempfile.mkdtemp()
    )

    temp_video = (
        temp_dir
        / "video_no_audio.mp4"
    )

    # --------------------------------------------------------
    # Video writer
    # --------------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        str(temp_video),
        fourcc,
        fps,
        (
            width,
            height
        )
    )

    if not writer.isOpened():

        cap.release()

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise RuntimeError(
            "Could not create "
            "temporary video."
        )

    # --------------------------------------------------------
    # Process frames
    # --------------------------------------------------------

    frame_number = 0

    while True:

        success, frame = cap.read()

        if not success:

            break

        # Actual video elapsed time
        elapsed_seconds = (
            frame_number / fps
        )

        # Dynamic timestamp
        timestamp_text = get_timestamp(
            start_datetime,
            timestamp_type,
            elapsed_seconds
        )

        # OpenCV BGR -> RGB
        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(
            frame_rgb
        )

        # Draw text
        image = draw_text_on_image(
            image,
            timestamp_text
        )

        # RGB -> BGR
        processed_frame = cv2.cvtColor(
            np.array(image),
            cv2.COLOR_RGB2BGR
        )

        writer.write(
            processed_frame
        )

        frame_number += 1

        # Progress every ~2 seconds
        if frame_number % max(
            1,
            int(fps * 2)
        ) == 0:

            progress = (
                frame_number
                / frame_count
                * 100
                if frame_count > 0
                else 0
            )

            print(
                f"\rProgress: "
                f"{progress:.1f}%",
                end=""
            )

    print()

    cap.release()
    writer.release()

    # --------------------------------------------------------
    # Add original audio
    # --------------------------------------------------------

    print(
        "Adding original audio..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    ffmpeg_command = [
        "ffmpeg",
        "-y",

        # Processed video
        "-i",
        str(temp_video),

        # Original video/audio
        "-i",
        str(input_path),

        # Processed video stream
        "-map",
        "0:v:0",

        # Original audio
        "-map",
        "1:a?",

        # Video codec
        "-c:v",
        "libx264",

        # Quality
        "-crf",
        "18",

        # Encoding speed
        "-preset",
        "medium",

        # Audio
        "-c:a",
        "aac",

        "-b:a",
        "192k",

        # Match shortest stream
        "-shortest",

        str(output_path)
    ]

    result = subprocess.run(
        ffmpeg_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        print(
            "\nFFmpeg error:"
        )

        print(
            result.stderr
        )

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise RuntimeError(
            "FFmpeg failed."
        )

    # Cleanup
    shutil.rmtree(
        temp_dir,
        ignore_errors=True
    )

    print(
        f"Saved: {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Find EVERYTHING in input folder
    # --------------------------------------------------------

    files = [
        file
        for file in INPUT_FOLDER.iterdir()
        if file.is_file()
    ]

    if not files:

        print(
            "No files found in "
            "the input folder."
        )

        return

    print(
        f"Found {len(files)} file(s)."
    )

    # --------------------------------------------------------
    # Process files one by one
    # --------------------------------------------------------

    processed_count = 0
    skipped_count = 0

    for index, file_path in enumerate(
        files,
        start=1
    ):

        extension = (
            file_path.suffix.lower()
        )

        print(
            f"\n[{index}/{len(files)}] "
            f"{file_path.name}"
        )

        try:

            output_path = (
                OUTPUT_FOLDER
                / file_path.name
            )

            # ------------------------------------------------
            # IMAGE
            # ------------------------------------------------

            if extension in IMAGE_EXTENSIONS:

                process_image(
                    file_path,
                    output_path
                )

                processed_count += 1

            # ------------------------------------------------
            # VIDEO
            # ------------------------------------------------

            elif extension in VIDEO_EXTENSIONS:

                process_video(
                    file_path,
                    output_path
                )

                processed_count += 1

            # ------------------------------------------------
            # UNSUPPORTED
            # ------------------------------------------------

            else:

                print(
                    f"Skipped unsupported "
                    f"file type: {extension}"
                )

                skipped_count += 1

        except Exception as e:

            print(
                f"ERROR: {e}"
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n================================"
    )

    print(
        "Processing complete."
    )

    print(
        f"Processed: {processed_count}"
    )

    print(
        f"Skipped:   {skipped_count}"
    )

    print(
        f"Output:    {OUTPUT_FOLDER}"
    )

    print(
        "================================"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()