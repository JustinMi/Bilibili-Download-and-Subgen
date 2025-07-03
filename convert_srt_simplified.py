"""
Quick script to convert SRT files from Traditional Chinese to Simplified Chinese using OpenCC.
"""

import sys
from opencc import OpenCC

# Create a converter to Simplified
cc = OpenCC("t2s")  # 't2s' = Traditional to Simplified


def convert_srt_to_simplified(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile, open(
        output_path, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            line = cc.convert(line)
            # # Only convert lines that are not numbers or timestamps
            # if line.strip() and not line.strip().isdigit() and "-->" not in line:
            #     line = cc.convert(line)
            outfile.write(line)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_srt_simplified.py input.srt output.srt")
        sys.exit(1)

    convert_srt_to_simplified(sys.argv[1], sys.argv[2])
