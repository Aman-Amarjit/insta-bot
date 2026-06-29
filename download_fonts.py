import io
import os
import zipfile
import requests

def download_fonts():
    # Use rsms/inter v4.0 release zip which contains standard TTF static font files
    url = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
    print(f"Downloading Inter font family from release {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to download fonts, status code: {response.status_code}")
        
    print("Extracting zip file...")
    z = zipfile.ZipFile(io.BytesIO(response.content))
    os.makedirs("fonts", exist_ok=True)
    
    found_regular = False
    found_bold = False
    
    # We will search the zip files and write to standard Inter-Regular.ttf / Inter-Bold.ttf
    for filename in z.namelist():
        lower_name = filename.lower()
        
        # In rsms/inter release, static TTFs are typically inside "Inter Hinted/..." or "Inter/static/..." or similar
        # We target files named like 'Inter-Regular.ttf' or 'InterHinted-Regular.ttf'
        if filename.endswith(".ttf") and "regular" in lower_name and not ("italic" in lower_name or "variable" in lower_name):
            with open("fonts/Inter-Regular.ttf", "wb") as f:
                f.write(z.read(filename))
            print(f"Saved: fonts/Inter-Regular.ttf (extracted from {filename})")
            found_regular = True
            
        elif filename.endswith(".ttf") and "bold" in lower_name and not ("italic" in lower_name or "variable" in lower_name):
            with open("fonts/Inter-Bold.ttf", "wb") as f:
                f.write(z.read(filename))
            print(f"Saved: fonts/Inter-Bold.ttf (extracted from {filename})")
            found_bold = True

    if found_regular and found_bold:
        print("✅ Font extraction completed successfully!")
    else:
        # Fallback: if we didn't find specific ones, look for variable versions or first regular/bold ttf files
        for filename in z.namelist():
            lower_name = filename.lower()
            if filename.endswith(".ttf") and "regular" in lower_name and not found_regular:
                with open("fonts/Inter-Regular.ttf", "wb") as f:
                    f.write(z.read(filename))
                print(f"Fallback Saved: fonts/Inter-Regular.ttf (from {filename})")
                found_regular = True
            elif filename.endswith(".ttf") and "bold" in lower_name and not found_bold:
                with open("fonts/Inter-Bold.ttf", "wb") as f:
                    f.write(z.read(filename))
                print(f"Fallback Saved: fonts/Inter-Bold.ttf (from {filename})")
                found_bold = True
                
        if found_regular and found_bold:
            print("✅ Font extraction completed via fallback!")
        else:
            raise Exception("❌ Could not locate regular and bold ttf files in the downloaded zip.")

if __name__ == "__main__":
    download_fonts()
