import itertools
import hashlib
import os
import random
import time

# --- Parameters ---
base_folder = "password_storage"
password = 'Thi0-mYneWpaSsword1@'
salt = b'somesalt'
iterations = 32800
dklen = 32

# --- Folder structure parameters ---
N1, N2, N3, N4 = 1000, 1000, 1000, 1000
lines_per_file = 20_000_000
total_capacity = N1 * N2 * N3 * N4 * lines_per_file

# --- XOR function for 4×8-byte blocks ---
def xor_four_8byte_blocks(b32):
    assert len(b32) == 32
    res = bytearray(8)
    for i in range(4):
        block = b32[i*8:(i+1)*8]
        for j in range(8):
            res[j] ^= block[j]
    return bytes(res)

# --- Map fold to folder/file/line ---
def get_location(fold_int):
    index = fold_int % total_capacity
    sf1_idx = index // (N2 * N3 * N4 * lines_per_file)
    sf2_idx = (index // (N3 * N4 * lines_per_file)) % N2
    sf3_idx = (index // (N4 * lines_per_file)) % N3
    file_idx = (index // lines_per_file) % N4
    line_idx = index % lines_per_file
    return sf1_idx, sf2_idx, sf3_idx, file_idx, line_idx

# --- Function to store password + fold (hex) ---
def store_password(pwd):
    dk = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, iterations, dklen)
    fold = xor_four_8byte_blocks(dk)
    fold_hex = fold.hex()
    fold_int = int.from_bytes(fold, 'big')
    sf1_idx, sf2_idx, sf3_idx, file_idx, line_idx = get_location(fold_int)

    folder_path = os.path.join(base_folder, f"sf1_{sf1_idx}", f"sf2_{sf2_idx}", f"sf3_{sf3_idx}")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"file_{file_idx}.txt")

    with open(file_path, "a") as f:
        f.write(f"{line_idx}: {pwd} | fold={fold_hex}\n")

    return file_path, line_idx, fold_hex

# --- Resume support ---
progress_file = "progress.txt"
num_permutations = 1000  # Change as needed

# Determine starting index
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        start_idx = int(f.read().strip()) + 1
else:
    start_idx = 1

password_list = list(password)
start_time = time.perf_counter()

for i in range(start_idx, num_permutations + 1):
    random.shuffle(password_list)
    perm_str = ''.join(password_list)
    store_password(perm_str)

    # Save progress
    with open(progress_file, "w") as f:
        f.write(str(i))

    # --- Progress & time left ---
    elapsed = time.perf_counter() - start_time
    avg_time = elapsed / (i - start_idx + 1)
    remaining = avg_time * (num_permutations - i)
    print(f"[{i}/{num_permutations}] Elapsed: {elapsed:.2f}s | "
          f"Est. time left: {remaining:.2f}s | Current: {perm_str}", end="\r")

print("\nAll permutations stored.")
