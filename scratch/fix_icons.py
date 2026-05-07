import os

def fix_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Replace common broken UTF-8 sequences
    replacements = [
        (b'\xc3\xa2\xc5\x93\xe2\x80\xa2', b'&times;'),  # âœ•
        (b'\xc3\xa2\xe2\x82\xac\xe2\x80\x94', b'&mdash;'), # â€”
        (b'\xc3\xa2\xe2\x80\x9d\xe2\x80\x94', b'&mdash;'), # another variant
        (b'\xf0\x9f\x94\x8a', b'&#128266;'),            # Speaker icon
        (b'\xf0\x9f\x97\xa3\xef\xb8\x8f', b'&#128483;'), # TTS icon
    ]
    
    for old, new in replacements:
        data = data.replace(old, new)
    
    with open(filename, 'wb') as f:
        f.write(data)
    print("Fixed icons in", filename)

if __name__ == "__main__":
    fix_file('advanced-admin-panel.html')
