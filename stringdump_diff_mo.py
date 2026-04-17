import marimo

__generated_with = "0.23.1"
app = marimo.App()

with app.setup(hide_code=True):
    import marimo as mo
    from pathlib import Path
    from collections import Counter
    import math
    from operator import itemgetter
    from collections.abc import Iterator


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Filter garbage strings from a new stringdump
    """)
    return


@app.function(hide_code=True)
def triplets(s: bytes) -> Iterator[memoryview]:
    s = b" " + s.strip() + b" "
    memview = memoryview(s)
    for i in range(len(s) - 2):
        yield memview[i : i + 3]


@app.function(hide_code=True)
def all_triplets_from_many_lines(lines: Iterator[bytes]) -> Iterator[memoryview]:
    for line in lines:
        yield from triplets(line)


@app.function(hide_code=True)
def load_file(filename: str) -> set[bytes]:
    with open(filename, "rb") as file:
        return {line.rstrip(b"\r\n") for line in file.readlines()}


@app.function(hide_code=True)
def account_triplets(lines: Iterator[bytes]):
    c = Counter(all_triplets_from_many_lines(lines))
    m = max(c.values())
    for key in c:
        c[key] /= m  # Normalize by max value
    return c


@app.function(hide_code=True)
def get_score(s: bytes, trained: dict[bytes, float]) -> float:
    # return sum(c[t] for t in triplets(s)) / len(s)
    return math.sqrt(sum(trained[t] for t in triplets(s)) / math.log(len(s) + 1))


@app.cell
def _():
    stringdumps_dir = Path("../stringdumps/")
    return (stringdumps_dir,)


@app.cell
def _(stringdumps_dir):
    old_file = load_file(stringdumps_dir / "stringdump_0_47_04.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_0_47_05.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_0_47_03.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_0_47_02.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_0_47_01.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_0_44_12.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_01.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_02.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_05.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_06.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_08.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_09.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_10.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_11.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_12.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_13.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_50_14.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_51_01.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_52_05.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_53_02.txt")
    old_file |= load_file(stringdumps_dir / "stringdump_steam_53_05.txt")

    trained = account_triplets(old_file)  # Обучаем на старых файлах
    return old_file, trained


@app.cell
def _():
    new_file = load_file("../dfint64_patch/stringdump.txt")
    return (new_file,)


@app.cell
def _(new_file, old_file, trained):
    diff = sorted(new_file - old_file, key=lambda s: get_score(s, trained))
    return (diff,)


@app.cell
def _(diff, trained):
    for item in diff[:200]:
        score = get_score(item, trained)
        print(f"{item!r:40} {score:.10f}")
    return


@app.cell
def _(slider):
    threshold = slider.value
    return (threshold,)


@app.cell(hide_code=True)
def _(diff, threshold, trained):
    prev = None
    after = None
    for _item in diff:
        _score = get_score(_item, trained)
        if _score < threshold:
            prev = _item
        else:
            after = _item
            break

    if prev is not None and after is not None:
        print(f"Before threshold: {prev}")
        print(f"After threshold: {after}")
    elif prev is not None:
        print(f"Before threshold: {prev}")
        print("No items found after threshold.")
    elif after is not None:
        print("No items found before threshold.")
        print(f"After threshold: {after}")
    else:
        print("No items found around threshold.")
    return


@app.cell
def _(diff, trained):
    stop = round(get_score(diff[-1], trained) + 0.01, ndigits=4)
    slider = mo.ui.slider(
        start=0, stop=stop, step=0.001, show_value=True, full_width=True
    )
    slider
    return (slider,)


@app.cell
def _(write_file):
    button = mo.ui.button(label="Write file", on_click=lambda _: write_file())
    button
    return


@app.cell
def _(diff, new_file, stringdumps_dir, threshold, trained):
    def write_file():
        output_file = stringdumps_dir / "stringdump_steam_53_12.txt"
        if output_file.exists():
            print(f"File {output_file.name} already exists")
            return

        with open(output_file, "wb") as output:
            for line, number in sorted(new_file.items(), key=itemgetter(1)):
                if (
                    line in diff and get_score(line, trained) < threshold
                ):  # Отсеиваем только добавившиеся строки
                    continue

                output.write(line)
                output.write(b"\n")

    return (write_file,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
