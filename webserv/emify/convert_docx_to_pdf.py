import os
import subprocess

def convert_docx_to_pdf(input_docx: str, output_pdf: str) -> bool:
    if not os.path.isfile(input_docx):
        print(f"❌ Input file not found: {input_docx}")
        return False
    try:
        result = subprocess.run(
            ['unoconv', '-f', 'pdf', '-o', output_pdf, input_docx],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Successfully converted {input_docx} to {output_pdf}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Conversion failed:")
        print(e.stderr.decode())
        return False
