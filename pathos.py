
import subprocess
import os
from datetime import date, datetime, timedelta

# Pola pixel 5 x 7
letters = {
    "P": [
        "11110",
        "10001",
        "10001",
        "11110",
        "10000",
        "10000",
        "10000",
    ],
    "A": [
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ],
    "T": [
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
    ],
    "H": [
        "10001",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ],
    "O": [
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ],
    "S": [
        "01111",
        "10000",
        "10000",
        "01110",
        "00001",
        "00001",
        "11110",
    ],
}

def git(*args, env=None):
    return subprocess.run(
        ["git", *args],
        check=True,
        env=env
    )

# Pastikan berada di repository Git
git("rev-parse", "--is-inside-work-tree")

today = date.today()

# Awal kalender: hari Minggu, 51 minggu sebelum minggu ini
sunday_offset = (today.weekday() + 1) % 7
calendar_start = (
    today - timedelta(days=sunday_offset)
    - timedelta(weeks=51)
)

# Posisi tulisan di tengah kalender 52 minggu
start_column = 8

commits = []

for letter_index, letter in enumerate("PATHOS"):
    pattern = letters[letter]
    letter_start = start_column + letter_index * 6

    for row in range(7):
        for col in range(5):
            if pattern[row][col] == "1":
                week = letter_start + col

                commit_day = (
                    calendar_start
                    + timedelta(weeks=week, days=row)
                )

                if commit_day <= today:
                    commits.append(commit_day)

# Urutkan tanggal dan hilangkan duplikasi
commits = sorted(set(commits))

print(f"Total hari kontribusi: {len(commits)}")
print("Membuat pola PATHOS...")

for index, commit_day in enumerate(commits, 1):
    timestamp = datetime.combine(
        commit_day,
        datetime.min.time()
    ).replace(hour=12).astimezone().isoformat()

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = timestamp
    env["GIT_COMMITTER_DATE"] = timestamp

    git(
        "commit",
        "--allow-empty",
        "-m",
        f"PATHOS pixel art [{index}]",
        env=env
    )

print("Selesai membuat commit PATHOS!")
print("Periksa git log sebelum melakukan push.")
