import hashlib, os, random

# --- Base folder in GitHub Actions workspace ---
base_folder = os.path.join(os.environ.get('GITHUB_WORKSPACE', os.getcwd()), "password_storage")
print("Base folder:", base_folder)

# --- Password + PBKDF2 parameters ---
password = 'Thi0-mYneWpaSsword1@'
salt = b'somesalt'
iterations = 32800
dklen = 32

# --- Folder structure parameters (small for demo) ---
N1, N2, N3, N4 = 10, 10, 10, 10
lines_per_file = 1000
total_capacity = N1 * N2 * N3 * N4 * lines_per_file

# --- XOR function ---
def xor_four_8byte_blocks(b32):
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

# --- Store password ---
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
        f.write(f"{pwd} | fold={fold_hex}\n")

    print(f"Stored '{pwd}' in {file_path} with fold={fold_hex}")
    return file_path, fold_hex

# --- Generate random permutations ---
password_list = list(password)
num_permutations = 20  # Small for demo

for _ in range(num_permutations):
    random.shuffle(password_list)
    perm_str = ''.join(password_list)
    store_password(perm_str)
