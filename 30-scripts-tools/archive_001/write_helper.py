"""Write Helper - Multi-purpose file writer
Usage:
  py write_helper.py <output> "<content>"
  py write_helper.py <output> -f <input>
  py write_helper.py <output> --lines <n> "<line_template>"
  py write_helper.py <output> --gen "<python_code>"
"""
import sys, os
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    output = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else None
    
    if mode == "-f" and len(sys.argv) > 3:
        # From file
        with open(sys.argv[3], 'r', encoding='utf-8') as f:
            content = f.read()
    elif mode == "--lines" and len(sys.argv) > 4:
        # Generate lines
        n = int(sys.argv[3])
        template = sys.argv[4]
        content = "\n".join([template] * n)
    elif mode == "--gen" and len(sys.argv) > 3:
        # Python generation
        code = sys.argv[3]
        exec(code)
        return
    else:
        # Direct content
        content = " ".join(sys.argv[2:])
    
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] %d bytes -> %s" % (len(content), output))

if __name__ == "__main__":
    main()
