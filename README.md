# Numbers to Words Generator

A Python desktop application that converts numbers into their longhand **word form** and can generate large text files where each line is a written number.

Built with **Tkinter**, runs on any modern version of Python 3.

---

##  Features
- Convert any number (0 up to 999 quadrillion) into words
- Generate entire ranges (`1 → 1,000,000` and beyond) into a text file
- Progress tracking with speed, ETA, and file size estimates
- Quick-select presets (1K, 10K, 100K, 1M, 10M)
- Stop generation safely at any time
- “Test Convert” tool for single number lookups
- Save results to a file

## Estimated File Sizes

| Count                 | Avg Line Length | Approx File Size |
| --------------------- | --------------- | ---------------- |
| 1,000                 | \~35            | \~33 KB          |
| 10,000                | \~35            | \~334 KB         |
| 100,000               | \~35            | \~3.3 MB         |
| 1 million             | \~38            | \~36 MB          |
| 10 million            | \~47            | \~448 MB         |
| 100 million           | \~71            | \~6.8 GB         |
| 1 billion             | \~83            | \~79 GB          |
| 10 billion            | \~91            | \~868 GB         |
| 100 billion           | \~99            | \~9.4 TB         |
| 1 trillion            | \~107           | \~102 TB         |
| 10 trillion           | \~115           | \~1.1 PB         |
| 100 trillion          | \~123           | \~11.7 PB        |
| 1 quadrillion         | \~131           | \~125 PB         |
| 10 quadrillion        | \~139           | \~1.3 EB         |
| 100 quadrillion       | \~147           | \~14.0 EB        |
| 999 quadrillion (max) | \~155           | \~148 EB         |




##  Installation

1. Make sure you have **Python 3.8+** installed.
2. Clone or download this repository.
3. Install dependencies (only the Python standard library is used, no external packages required).

```bash
git clone https://github.com/ekztal/numbers-to-words.git
cd numbers-to-words
```
