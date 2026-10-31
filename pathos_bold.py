#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PATHOS CONTRIBUTION ART
Generator pola teks 7 x 52 untuk kalender kontribusi GitHub.

Penggunaan:
    python3 pathos_bold.py
    python3 pathos_bold.py --apply

Mode default hanya menampilkan preview.
Mode --apply membuat empty commit pada tanggal yang dipilih.

Catatan:
- Membutuhkan Git dan Python 3.
- Harus dijalankan di dalam repository Git.
- Harus menggunakan orphan branch yang belum memiliki commit.
- Tidak melakukan push secara otomatis.
"""

import argparse
import os
import shutil
import subprocess
import sys

from datetime import date, datetime, time, timedelta


# ============================================================
# 1. KONFIGURASI
# ============================================================

TEXT = "PATHOS"

# Jumlah commit untuk setiap pixel yang aktif.
COMMITS_PER_DAY = 10

# Jika True, intensitas tiap pixel bervariasi.
INTENSITY_VARIATION = True

# Jarak ant huruf.
SPACING = 1

# None = posisi teks otomatis di tengah.
# Angka 0-51 = posisi kolom awal secara manual.
START_COLUMN = None

# None = branch aktif apa pun boleh, kecuali main/master.
# Isi "pathos-pro" jika ingin membatasi ke branch tersebut.
BRANCH = "pathos-pro"

# Jumlah kolom kalender.
CALENDAR_WEEKS = 52

# Nama branch utama yang dilindungi.
PROTECTED_BRANCHES = {"main", "master"}

# Waktu dasar commit dalam sehari.
COMMIT_HOUR = 12


# ============================================================
# 2. FONT 5 x 7
# ============================================================

# 1 = pixel aktif
# 0 = pixel kosong
#
# Setiap karakter memiliki 7 baris dan 5 kolom.
# Program akan menambahkan 2 kolom kosong di sebelah kanan.

FONT_RAW = {
    "A": (
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ),
    "B": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10001",
        "10001",
        "11110",
    ),
    "C": (
        "01111",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "01111",
    ),
    "D": (
        "11110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "11110",
    ),
    "E": (
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "11111",
    ),
    "F": (
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "10000",
    ),
    "G": (
        "01111",
        "10000",
        "10000",
        "10111",
        "10001",
        "10001",
        "01111",
    ),
    "H": (
        "10001",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ),
    "I": (
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "11111",
    ),
    "J": (
        "00111",
        "00010",
        "00010",
        "00010",
        "10010",
        "10010",
        "01100",
    ),
    "K": (
        "10001",
        "10010",
        "10100",
        "11000",
        "10100",
        "10010",
        "10001",
    ),
    "L": (
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "11111",
    ),
    "M": (
        "10001",
        "11011",
        "10101",
        "10101",
        "10001",
        "10001",
        "10001",
    ),
    "N": (
        "10001",
        "11001",
        "10101",
        "10011",
        "10001",
        "10001",
        "10001",
    ),
    "O": (
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ),
    "P": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10000",
        "10000",
        "10000",
    ),
    "Q": (
        "01110",
        "10001",
        "10001",
        "10001",
        "10101",
        "10010",
        "01101",
    ),
    "R": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10100",
        "10010",
        "10001",
    ),
    "S": (
        "01111",
        "10000",
        "10000",
        "01110",
        "00001",
        "00001",
        "11110",
    ),
    "T": (
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
    ),
    "U": (
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ),
    "V": (
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01010",
        "00100",
    ),
    "W": (
        "10001",
        "10001",
        "10001",
        "10101",
        "10101",
        "11011",
        "10001",
    ),
    "X": (
        "10001",
        "10001",
        "01010",
        "00100",
        "01010",
        "10001",
        "10001",
    ),
    "Y": (
        "10001",
        "10001",
        "01010",
        "00100",
        "00100",
        "00100",
        "00100",
    ),
    "Z": (
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "11111",
    ),
    " ": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
    ),
}


# Ubah FONT_RAW menjadi font 7 kolom.
FONT = {
    character: tuple(row.replace("1", "#").replace("0", ".") + ".."
                     for row in rows)
    for character, rows in FONT_RAW.items()
}


# ============================================================
# 3. FUNGSI DASAR
# ============================================================

def run_git(arguments, check=True, capture=True, env=None):
    """Menjalankan perintah Git."""

    command = ["git"] + arguments

    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            env=env,
        )
    except FileNotFoundError:
        raise RuntimeError("Git tidak ditemukan. Install Git terlebih dahulu.")

    if check and result.returncode != 0:
        error = result.stderr.strip() if result.stderr else "Git command gagal."
        raise RuntimeError(error)

    return result


def git_config(key):
    """Membaca konfigurasi Git."""

    result = run_git(
        ["config", "--get", key],
        check=False,
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def validate_environment():
    """Memastikan lingkungan Git aman untuk digunakan."""

    if shutil.which("git") is None:
        raise RuntimeError("Git belum terinstall.")

    inside_repo = run_git(
        ["rev-parse", "--is-inside-work-tree"],
        check=False,
    )

    if inside_repo.returncode != 0:
        raise RuntimeError(
            "Folder ini bukan repository Git. "
            "Masuk ke folder repository terlebih dahulu."
        )

    branch_result = run_git(
        ["branch", "--show-current"],
        check=False,
    )

    branch_name = branch_result.stdout.strip()

    if not branch_name:
        raise RuntimeError(
            "Tidak dapat membaca nama branch aktif."
        )

    if branch_name in PROTECTED_BRANCHES:
        raise RuntimeError(
            f"Branch '{branch_name}' dilindungi. "
            "Gunakan orphan branch baru."
        )

    if BRANCH is not None and branch_name != BRANCH:
        raise RuntimeError(
            f"Branch aktif adalah '{branch_name}', "
            f"sedangkan konfigurasi meminta '{BRANCH}'."
        )

    # Pastikan branch belum memiliki commit.
    head_result = run_git(
        ["rev-parse", "--verify", "HEAD"],
        check=False,
    )

    if head_result.returncode == 0:
        raise RuntimeError(
            "Branch ini sudah memiliki commit. "
            "Buat orphan branch baru sebelum menjalankan --apply."
        )

    author_name = git_config("user.name")
    author_email = git_config("user.email")

    if not author_name:
        raise RuntimeError(
            "Git user.name belum dikonfigurasi.\n"
            'Jalankan: git config --global user.name "Nama Kamu"'
        )

    if not author_email:
        raise RuntimeError(
            "Git user.email belum dikonfigurasi.\n"
            'Jalankan: git config --global user.email "email@example.com"'
        )

    if "@" not in author_email:
        raise RuntimeError(
            "Format Git user.email tidak valid."
        )

    return branch_name, author_name, author_email


# ============================================================
# 4. VALIDASI KONFIGURASI
# ============================================================

def validate_configuration():

    if not isinstance(TEXT, str) or not TEXT:
        raise ValueError("TEXT tidak boleh kosong.")

    if TEXT != TEXT.upper():
        raise ValueError(
            "TEXT harus menggunakan huruf kapital."
        )

    if not isinstance(COMMITS_PER_DAY, int) or COMMITS_PER_DAY < 1:
        raise ValueError(
            "COMMITS_PER_DAY harus berupa angka minimal 1."
        )

    if not isinstance(SPACING, int) or SPACING < 0:
        raise ValueError(
            "SPACING tidak boleh negatif."
        )

    if START_COLUMN is not None:
        if not isinstance(START_COLUMN, int):
            raise ValueError("START_COLUMN harus berupa angka atau None.")

        if not 0 <= START_COLUMN < CALENDAR_WEEKS:
            raise ValueError("START_COLUMN harus berada di antara 0 dan 51.")

    for character in TEXT:
        if character not in FONT:
            raise ValueError(
                f"Karakter '{character}' belum tersedia di FONT."
            )

    if len(FONT) == 0:
        raise ValueError("FONT kosong.")

    for character, rows in FONT.items():
        if len(rows) != 7:
            raise ValueError(
                f"Font '{character}' harus memiliki 7 baris."
            )

        for row in rows:
            if len(row) != 7:
                raise ValueError(
                    f"Font '{character}' harus memiliki 7 kolom."
                )


# ============================================================
# 5. MEMBENTUK POLA TEKS
# ============================================================

def build_text_pattern():

    rows = [[] for _ in range(7)]

    for index, character in enumerate(TEXT):

        glyph = FONT[character]

        for row_number in range(7):
            rows[row_number].extend(glyph[row_number])

        if index < len(TEXT) - 1:
            for row_number in range(7):
                rows[row_number].extend("." * SPACING)

    return ["".join(row) for row in rows]


# ============================================================
# 6. KALENDER 52 MINGGU
# ============================================================

def get_calendar_start(today):
    """
    Menghasilkan hari Minggu awal kalender 52 minggu.
    """

    # Python weekday:
    # Senin = 0, Minggu = 6.
    days_since_sunday = (today.weekday() + 1) % 7

    current_sunday = today - timedelta(
        days=days_since_sunday
    )

    return current_sunday - timedelta(
        weeks=CALENDAR_WEEKS - 1
    )


def calculate_layout(pattern):

    text_width = len(pattern[0])

    if text_width > CALENDAR_WEEKS:
        raise ValueError(
            f"Teks terlalu lebar: {text_width} kolom. "
            f"Maksimal {CALENDAR_WEEKS} kolom."
        )

    if START_COLUMN is None:
        start_column = (
            CALENDAR_WEEKS - text_width
        ) // 2
    else:
        start_column = START_COLUMN

    if start_column + text_width > CALENDAR_WEEKS:
        raise ValueError(
            "Teks keluar dari batas kalender 52 minggu."
        )

    return start_column, text_width


# ============================================================
# 7. MEMBANGUN DATA PIXEL
# ============================================================

def build_pixels(pattern, start_date, start_column, today):

    pixels = []

    for row_number in range(7):

        for column_number in range(len(pattern[row_number])):

            if pattern[row_number][column_number] != "#":
                continue

            calendar_column = start_column + column_number

            pixel_date = (
                start_date
                + timedelta(days=calendar_column * 7 + row_number)
            )

            # Jangan membuat commit untuk tanggal masa depan.
            if pixel_date > today:
                continue

            pixels.append({
                "date": pixel_date,
                "row": row_number,
                "column": calendar_column,
                "character_column": column_number,
            })

    return pixels


# ============================================================
# 8. PREVIEW
# ============================================================

def render_preview(pattern, start_date, start_column, today):

    print()
    print("=" * 64)
    print("             PATHOS CONTRIBUTION ART")
    print("=" * 64)

    print(f"Teks              : {TEXT}")
    print(f"Ukuran font       : 7 x {len(pattern[0])}")
    print(f"Lebar kalender    : {CALENDAR_WEEKS} minggu")
    print(f"Kolom awal        : {start_column}")
    print(f"Tanggal awal      : {start_date}")
    print(f"Tanggal hari ini  : {today}")
    print(f"Commit per pixel  : {COMMITS_PER_DAY}")
    print()

    print("PREVIEW POLA 7 x 52")
    print("-" * 64)

    for row_number in range(7):

        output = []

        for column_number in range(CALENDAR_WEEKS):

            text_column = column_number - start_column

            if (
                0 <= text_column < len(pattern[row_number])
                and pattern[row_number][text_column] == "#"
            ):
                pixel_date = (
                    start_date
                    + timedelta(days=column_number * 7 + row_number)
                )

                if pixel_date <= today:
                    output.append("█")
                else:
                    output.append("·")
            else:
                output.append(" ")

        print("".join(output))

    print("-" * 64)
    print("█ = pixel aktif")
    print("· = tanggal yang belum terjadi")
    print("  = pixel kosong")
    print()


# ============================================================
# 9. INTENSITAS PIXEL
# ============================================================

def get_commit_count(pixel, index):

    if not INTENSITY_VARIATION:
        return COMMITS_PER_DAY

    # Variasi jumlah commit yang deterministik.
    variation = (
        pixel["date"].day
        + pixel["date"].month
        + pixel["row"]
        + index
    ) % 3

    return max(
        1,
        COMMITS_PER_DAY - variation
    )


# ============================================================
# 10. MEMBUAT EMPTY COMMIT
# ============================================================

def create_pixel_commit(pixel, sequence, total):

    pixel_date = pixel["date"]

    # Beberapa commit dalam satu hari diberi waktu berbeda.
    commit_time = datetime.combine(
        pixel_date,
        time(COMMIT_HOUR, 0, 0),
    ) + timedelta(minutes=sequence)

    timestamp = commit_time.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

    environment = os.environ.copy()

    environment["GIT_AUTHOR_DATE"] = timestamp
    environment["GIT_COMMITTER_DATE"] = timestamp

    message = (
        f"pixel: row {pixel['row'] + 1}, "
        f"week {pixel['column'] + 1}, "
        f"commit {sequence + 1}/{total}"
    )

    result = run_git(
        [
            "commit",
            "--allow-empty",
            "--quiet",
            "-m",
            message,
            "--date",
            timestamp,
        ],
        check=False,
        env=environment,
    )

    if result.returncode != 0:
        error = result.stderr.strip() if result.stderr else "Commit gagal."
        raise RuntimeError(error)


# ============================================================
# 11. MENJALANKAN GENERATOR
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="PATHOS 7x52 Git contribution art generator."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Membuat empty commit setelah validasi.",
    )

    args = parser.parse_args()

    validate_configuration()

    pattern = build_text_pattern()

    start_column, text_width = calculate_layout(pattern)

    today = date.today()

    start_date = get_calendar_start(today)

    pixels = build_pixels(
        pattern,
        start_date,
        start_column,
        today,
    )

    render_preview(
        pattern,
        start_date,
        start_column,
        today,
    )

    total_commits = 0

    for index, pixel in enumerate(pixels):
        total_commits += get_commit_count(pixel, index)

    print("RINGKASAN")
    print("-" * 64)
    print(f"Pixel aktif       : {len(pixels)}")
    print(f"Perkiraan commit  : {total_commits}")
    print(f"Branch target     : {BRANCH or 'branch aktif'}")
    print()

    if not args.apply:
        print("[PREVIEW SAJA]")
        print("Belum ada commit yang dibuat.")
        print()
        print("Jika sudah memeriksa pola, jalankan:")
        print("python3 pathos_bold.py --apply")
        print()
        return

    print("[MODE APPLY]")
    print("Memeriksa repository Git...")

    branch_name, author_name, author_email = validate_environment()

    print(f"Branch aktif : {branch_name}")
    print(f"Git author   : {author_name}")
    print(f"Git email    : {author_email}")
    print()

    print("Mulai membuat empty commit...")
    print("Jangan tutup terminal sampai proses selesai.")
    print()

    completed = 0

    for index, pixel in enumerate(pixels):

        commit_count = get_commit_count(pixel, index)

        for sequence in range(commit_count):

            create_pixel_commit(
                pixel,
                sequence,
                commit_count,
            )

            completed += 1

        print(
            f"\rProgress: {completed}/{total_commits} commit",
            end="",
            flush=True,
        )

    print()
    print()
    print("=" * 64)
    print("PROSES SELESAI")
    print("=" * 64)
    print(f"Branch          : {branch_name}")
    print(f"Pixel aktif     : {len(pixels)}")
    print(f"Commit dibuat   : {completed}")
    print()
    print("Periksa hasil dengan:")
    print("git status")
    print("git log --oneline -10")
    print("git rev-list --count HEAD")
    print()
    print("Belum ada push ke GitHub.")
    print()


# ============================================================
# 12. ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nProses dibatalkan oleh pengguna.")
        sys.exit(130)

    except Exception as error:
        print()
        print("[ERROR]")
        print(error)
        sys.exit(1)
