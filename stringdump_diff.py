import marimo

__generated_with = "0.16.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    from pathlib import Path    
    return Path, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Filter garbage strings from a new stringdump""")
    return


@app.cell
def _():
    from collections import Counter
    import math
    from operator import itemgetter
    from collections.abc import Iterator


    def triplets(s: bytes) -> Iterator[memoryview]:
        s = b' ' + s.strip() + b' '
        memview = memoryview(s)
        for i in range(len(s)-2):
            yield memview[i:i+3]


    def all_triplets_from_many_lines(lines: Iterator[bytes]) -> Iterator[memoryview]:
        for line in lines:
            yield from triplets(line)


    def load_file(filename: str) -> set[bytes]:
        with open(filename, 'rb') as file:
            return {line.rstrip(b'\r\n') for line in file.readlines()}


    def account_triplets(lines: Iterator[bytes]):
        c = Counter(all_triplets_from_many_lines(lines))
        m = max(c.values())
        for key in c:
            c[key] /= m  # Normalize by max value
        return c


    def get_score(s: bytes, trained: dict[bytes, float]) -> float:
        # return sum(c[t] for t in triplets(s)) / len(s)
        return math.sqrt(sum(trained[t] for t in triplets(s)) / math.log(len(s) + 1))
    return account_triplets, get_score, itemgetter, load_file


@app.cell
def _(Path, account_triplets, load_file):
    stringdumps_dir = Path("../stringdumps/")

    old_file = load_file(stringdumps_dir / 'stringdump_0_47_04.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_0_47_05.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_0_47_03.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_0_47_02.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_0_47_01.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_0_44_12.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_01.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_02.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_05.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_06.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_08.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_09.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_10.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_11.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_12.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_13.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_50_14.txt')
    old_file |= load_file(stringdumps_dir / 'stringdump_steam_51_01.txt')

    trained = account_triplets(old_file)  # Обучаем на старых файлах
    return old_file, trained


@app.cell
def _(load_file):
    new_file = load_file('../dfint64_patch/stringdump.txt')
    return (new_file,)


@app.cell
def _(get_score, new_file, old_file, trained):
    diff = sorted(new_file - old_file, key=lambda s: get_score(s, trained))
    return (diff,)


@app.cell
def _(diff, get_score, trained):
    for item in diff[:200]:
        score = get_score(item, trained)
        print(f"{item!r:40} {score:.10f}")
    return


@app.cell
def _(mo):
    slider = mo.ui.slider(start=0, stop=0.2, step=0.001, show_value=True, full_width=True)
    slider
    return (slider,)


@app.cell
def _(slider):
    threshold = slider.value
    return (threshold,)


@app.cell
def _(mo, write_file):
    button = mo.ui.button(label="Write file", on_click=lambda _: write_file())
    button
    return


@app.cell
def _(Path, diff, get_score, itemgetter, new_file, threshold, trained):
    def write_file():
        output_file = Path('../stringdumps/stringdump_steam_51_02.txt')
        if output_file.exists():
            print(f"File {output_file.name} already exists")
            return
    
        with open(output_file, 'wb') as output:
            for line, number in sorted(new_file.items(), key=itemgetter(1)):
                if line in diff and get_score(line, trained) < threshold: # Отсеиваем только добавившиеся строки
                    continue
    
                output.write(line)
                output.write(b'\n')
    return (write_file,)


if __name__ == "__main__":
    app.run()
