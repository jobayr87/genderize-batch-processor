import csv
import json
import os
import ssl
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import urllib.parse
import urllib.request

# Apnar default API Keys
DEFAULT_API_KEYS = [
    "423b3d5117058b47f1cb2380b5929dba",
    "eb51b8255f3b0ccc0ea4fdaaf4d19d35",
    "6387030e8db39be11b216e2ec7fc924e",
    "16f09f11c520fcbc1a526e88213f57ef",
]


def get_api_keys():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    answer = messagebox.askyesno(
        "API Keys Configuration",
        f"Apnar default {len(DEFAULT_API_KEYS)} ti API Key set kora ache.\n\nApni ki aro new API Keys add korte chan?",
        parent=root,
    )

    if answer:
        keys_str = simpledialog.askstring(
            "Multiple API Keys",
            "Aro API Keys dighun (comma ',' ba space diye alada korun):",
            initialvalue=", ".join(DEFAULT_API_KEYS),
            parent=root,
        )
        if keys_str and keys_str.strip():
            raw_list = (
                keys_str.replace("\n", ",")
                .replace(" ", ",")
                .replace(";", ",")
                .split(",")
            )
            cleaned_keys = [k.strip() for k in raw_list if k.strip()]
            if cleaned_keys:
                print(
                    f"🔑 Mot {len(cleaned_keys)} ti API Key configure kora hoyeche."
                )
                return cleaned_keys

    print(f"🔑 Default {len(DEFAULT_API_KEYS)} ti API Key byabohar kora hochhe.")
    return DEFAULT_API_KEYS


def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return filedialog.askopenfilename(
        title="Process korar jonno CSV file select korun",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
    )


def fetch_with_retry(url, retries=2, delay=1):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise Exception("LIMIT_EXCEEDED")
            raise e
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e


def process_gender_report():
    api_keys = get_api_keys()
    if not api_keys:
        print("❌ Kono API Key paowa jayni! Program bondho hochhe.")
        return

    current_key_idx = 0

    input_file = select_csv_file()
    if not input_file:
        print("⚠️ Kono file select kora hoyni!")
        return

    base_path, ext = os.path.splitext(input_file)
    output_file = f"{base_path}_Processed{ext}"

    rows = []
    with open(input_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    total_rows = len(rows)
    print(f"📄 Mot data: {total_rows} ti")

    if total_rows == 0:
        print("⚠️ File ti khali!")
        return

    processed_phones = set()
    existing_results = []

    if os.path.exists(output_file):
        with open(output_file, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                existing_results.append(r)
                processed_phones.add(r.get("Phone Number", ""))

        print(
            f"🔄 Ager process kora: {len(existing_results)} ti data. Baki theke shuru hochhe..."
        )

    sample_keys = list(rows[0].keys())
    phone_key = next(
        (
            k
            for k in sample_keys
            if "num" in k.lower()
            or "phone" in k.lower()
            or "mobile" in k.lower()
        ),
        sample_keys[0],
    )
    name_key = next(
        (k for k in sample_keys if "name" in k.lower()), sample_keys[1]
    )
    age_key = next(
        (k for k in sample_keys if "age" in k.lower()),
        sample_keys[2] if len(sample_keys) > 2 else "",
    )

    remaining_rows = [
        r for r in rows if str(r.get(phone_key, "")) not in processed_phones
    ]

    if not remaining_rows:
        print("✅ Shob data ager thekei process kora ache!")
        return

    print(f"🚀 Baki {len(remaining_rows)} ti data process kora hochhe...\n")

    chunk_size = 10
    results = list(existing_results)
    fieldnames = ["Phone Number", "Full Name", "Age", "Gender", "Accuracy"]

    i = 0
    while i < len(remaining_rows):
        chunk = remaining_rows[i : i + chunk_size]

        query_params = []
        for item in chunk:
            full_name = item.get(name_key, "").strip()
            # Full Name-ke kono split na kore shorasori URL safe kore pathano hochhe
            query_params.append(
                ("name[]", urllib.parse.quote_plus(full_name if full_name else "Unknown"))
            )

        param_str = "&".join([f"name[]={val}" for _, val in query_params])
        active_key = api_keys[current_key_idx]
        url = f"https://api.genderize.io?{param_str}&apikey={active_key}"

        try:
            data = fetch_with_retry(url, retries=2, delay=1)
            items = data if isinstance(data, list) else [data]

            for idx, item in enumerate(items):
                orig = chunk[idx]
                gender = item.get("gender") or "unknown"
                prob = item.get("probability", 0)
                accuracy = f"{int(prob * 100)}%" if prob else "0%"

                results.append(
                    {
                        "Phone Number": orig.get(phone_key, ""),
                        "Full Name": orig.get(name_key, ""),
                        "Age": orig.get(age_key, "") if age_key else "",
                        "Gender": gender,
                        "Accuracy": accuracy,
                    }
                )

            with open(
                output_file, mode="w", encoding="utf-8-sig", newline=""
            ) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            print(
                f"✅ Processed: {len(results)} / {total_rows} (API Key #{current_key_idx + 1} diye)"
            )
            i += chunk_size

        except Exception as e:
            if "LIMIT_EXCEEDED" in str(e) or "429" in str(e):
                print(
                    f"\n🚨 API Key #{current_key_idx + 1} ({active_key[:6]}...) er limit shesh!"
                )
                current_key_idx += 1
                if current_key_idx < len(api_keys):
                    print(
                        f"🔄 Auto porer API Key #{current_key_idx + 1} te switch kora hochhe...\n"
                    )
                    time.sleep(1)
                    continue
                else:
                    print("\n❌ Shob gulo API Key-er daily limit shesh!")
                    print(
                        "💡 Aro new API Key add kore script run korun, atah baki ongsho theke shuru hobe."
                    )
                    break
            else:
                print(f"⚠️ Network error at row {i}: {e}. Retrying...")
                time.sleep(2)

        time.sleep(0.2)

    print(
        f"\n📁 Output file process/update complete: '{os.path.basename(output_file)}'"
    )


if __name__ == "__main__":
    process_gender_report()