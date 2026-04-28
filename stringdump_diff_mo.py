# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.23.3",
# ]
# ///

import marimo

__generated_with = "0.23.3"
app = marimo.App()

with app.setup(hide_code=True):
    import marimo as mo
    from pathlib import Path
    from collections import Counter
    import math
    from collections.abc import Iterator, Iterable


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Filter garbage strings from a new stringdump
    """)
    return


@app.function(hide_code=True)
def triplets(s: bytes) -> Iterator[bytes]:
    s = b" " + s.strip() + b" "
    for i in range(len(s) - 2):
        yield s[i : i + 3]


@app.function(hide_code=True)
def all_triplets_from_many_lines(lines: Iterable[bytes]) -> Iterator[bytes]:
    for line in lines:
        yield from triplets(line)


@app.function(hide_code=True)
def load_file(filename: str | Path) -> set[bytes]:
    with open(filename, "rb") as file:
        return {line.rstrip(b"\r\n") for line in file.readlines()}


@app.function(hide_code=True)
def account_triplets(lines: Iterable[bytes]) -> Counter[bytes]:
    return Counter(all_triplets_from_many_lines(lines))


@app.function(hide_code=True)
def normalize(counter: dict[bytes, int]) -> dict[bytes, float]:
    normalized = {}
    max_value = max(counter.values())
    for key, value in counter.items():
        normalized[key] = value / max_value
    return normalized


@app.function(hide_code=True)
def get_score(s: bytes, trained: dict[bytes, float]) -> float:
    # return sum(c[t] for t in triplets(s)) / len(s)
    return math.sqrt(sum(trained.get(t, 0) for t in triplets(s)) / math.log(len(s) + 1))


@app.cell(hide_code=True)
def _():
    stringdumps_dir = Path(__file__).parent.parent / "stringdumps"
    assert stringdumps_dir.exists() and stringdumps_dir.is_dir()
    return (stringdumps_dir,)


@app.cell
def get_stringdump_files(stringdumps_dir):
    stringdump_files = sorted(
        file for file in stringdumps_dir.glob("stringdump_steam_*.txt")
    )
    list(reversed(stringdump_files))
    return (stringdump_files,)


@app.cell(hide_code=True)
def training(checkbox_exclude, stringdump_files):
    _exclude = set()
    if checkbox_exclude.value:
        last_file = stringdump_files[-1]
        _exclude.add(last_file.name)

    old_file = set[bytes]()

    for file in stringdump_files:
        if file.name in _exclude:
            continue
        old_file |= load_file(file)

    _count = account_triplets(old_file)
    trained = normalize(_count)
    # count.most_common(10)
    _most_common = [
        {"triplet": key, "count": value} for key, value in _count.most_common()
    ]
    mo.ui.table(_most_common)
    return old_file, trained


@app.cell
def _():
    new_file = load_file("../dfint64_patch/stringdump.txt")
    return (new_file,)


@app.cell
def new_lines_scored(new_file, old_file, trained):
    diff = sorted(new_file - old_file, key=lambda s: get_score(s, trained))
    len(diff)
    return (diff,)


@app.cell(hide_code=True)
def _(diff, trained):
    scores_per_line = [
        {"string": string, "score": get_score(string, trained)} for string in diff
    ]

    mo.ui.table(scores_per_line)
    return


@app.cell(hide_code=True)
def slider(diff, trained):
    stop = round(get_score(diff[-1], trained) + 0.01, ndigits=4)
    slider = mo.ui.slider(
        start=0, stop=stop, step=0.001, show_value=True, full_width=True
    )
    return (slider,)


@app.cell(hide_code=True)
def _():
    checkbox_exclude = mo.ui.checkbox(label="Exclude last file", value=False)
    return (checkbox_exclude,)


@app.cell(hide_code=True)
def _(checkbox_exclude, diff, slider, trained):
    threshold = slider.value
    split_index = None
    for _i, _item in enumerate(diff):
        _score = get_score(_item, trained)
        if _score < threshold:
            continue

        split_index = _i
        break
    else:
        split_index = len(diff) + 1

    print(threshold, _score, split_index, len(diff))

    prev = diff[_i - 1] if split_index > 0 else None
    after = diff[_i] if split_index < len(diff) else None

    _stack = [
        checkbox_exclude,
        mo.md(f"""Before threshold:  
        ```python
        {prev}
        ```
        After threshold:  
        ```python
        {after}
        ```"""),
        slider,
    ]
    mo.vstack(_stack)
    return (threshold,)


@app.cell(hide_code=True)
def form():
    form = mo.ui.text(
        "stringdump_steam_53_12.txt", label="Output file name", full_width=True
    ).form(submit_button_label="Write file")
    return (form,)


@app.cell(hide_code=True)
def form_vstack(form, stringdump_files, stringdumps_dir):
    _stack = [
        mo.md(f"Last file: `{stringdump_files[-1].name}`"),
        form,
    ]
    filename = form.value
    output_path = None if not form.value else stringdumps_dir / filename
    if output_path and output_path.exists():
        _stack.append(
            mo.md(
                f"""<span style="color:red">File {output_path.name} already exists</span>"""
            )
        )

    mo.vstack(_stack)
    return (output_path,)


@app.cell
def _(output_path, write_file):
    if output_path:
        write_file(output_path)
    return


@app.cell
def _(diff, new_file, threshold, trained):
    def write_file(output_file: Path) -> None:
        if output_file.exists():
            print(f"File {output_file.name} already exists")
            return

        with open(output_file, "wb") as output:
            for line in new_file:
                if (
                    line in diff and get_score(line, trained) < threshold
                ):  # Отсеиваем только добавившиеся строки
                    continue

                output.write(line)
                output.write(b"\n")

    return (write_file,)


if __name__ == "__main__":
    app.run()
