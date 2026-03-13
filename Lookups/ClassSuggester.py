# MenuTitle: Class Suggester
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs
from collections import defaultdict

Glyphs.showMacroWindow()

font = Glyphs.font
if not font:
    print("No font open.")
    raise SystemExit

letters = [g.name for g in font.glyphs if g.category == "Letter"]

base_by_initial = defaultdict(set)
suffix_map = defaultdict(lambda: defaultdict(list))

for name in letters:
    parts = name.split(".", 1)
    base = parts[0]

    if len(parts) == 2:
        suffix = parts[1]

        # Ignore .case and .liga
        if suffix in ("case", "liga"):
            continue

        initial = base[0]
        suffix_map[initial][suffix].append(name)
        base_by_initial[initial].add(base)
    else:
        initial = base[0]
        base_by_initial[initial].add(base)

print("— Letter Families —\n")

for initial in sorted(base_by_initial):

    base_members = sorted(base_by_initial[initial])
    if len(base_members) < 2:
        continue

    suffixes = suffix_map.get(initial, {})
    if not suffixes:
        continue  # no alternates → no class

    print(f"@{initial} = [{' '.join(base_members)}];")

    for suffix in sorted(suffixes):
        alt_members = sorted(suffixes[suffix])
        print(f"@{initial}.{suffix} = [{' '.join(alt_members)}];")

    print()


print("— Case Classes —\n")

case_pairs = defaultdict(list)

for g in font.glyphs:
    name = g.name

    if name.endswith(".case"):
        base = name[:-5]

        # Ignore .liga.case edge cases implicitly
        if font.glyphs[base]:
            case_pairs[base].append(name)

for base in sorted(case_pairs):
    members = [base] + sorted(case_pairs[base])
    print(f"@{base} = [{' '.join(members)}];\n")