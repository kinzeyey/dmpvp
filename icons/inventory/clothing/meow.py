import os
import re
import shutil
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

START_ID = 10000
WEIGHT = "1.200"

# DEIN CDN
CDN_BASE = "https://cdn.jsdelivr.net/gh/kinzeyey/dmpvp/icons/inventory/clothing/"

OUTPUT_FOLDER = "_OUTPUT"


# ============================================================
# GTA COMPONENTS + OFFSETS
# ============================================================

OFFSETS = {
    "head": 46,
    "mask": 244,
    "hair": 82,
    "uppr": 214,
    "lowr": 202,
    "hand": 111,
    "feet": 151,
    "accs": 192,
    "teef": 213,
    "task": 62,
    "decl": 207,
    "jbib": 544,
}


COMPONENTS = {
    "head": (0, "Face"),
    "mask": (1, "Mask"),
    "hair": (2, "Hair"),
    "uppr": (3, "Upper"),
    "lowr": (4, "Legs"),
    "hand": (5, "Hands"),
    "feet": (6, "Feet"),
    "accs": (7, "Accessory"),
    "teef": (8, "Teef"),
    "task": (9, "Armor"),
    "decl": (10, "Decal"),
    "jbib": (11, "Top"),
}


# ============================================================
# REGEX
# ============================================================

PREFIXES = "|".join(
    sorted(
        OFFSETS.keys(),
        key=len,
        reverse=True
    )
)


DRAWABLE_REGEX = re.compile(
    rf"(?P<prefix>{PREFIXES})"
    rf"(?P<diff>_diff)?_"
    rf"(?P<drawable>\d+)",
    re.IGNORECASE
)


TEXTURE_REGEX = re.compile(
    r"_([a-z])_uni",
    re.IGNORECASE
)


# ============================================================
# HELPERS
# ============================================================

def texture_number(filename):

    match = TEXTURE_REGEX.search(filename)

    if not match:
        return 0

    letter = match.group(1).lower()

    return ord(letter) - ord("a")


def convert_name(name):

    def replace(match):

        prefix = match.group("prefix")

        old = int(
            match.group("drawable")
        )

        new = old + OFFSETS[prefix.lower()]

        return (
            f"{prefix}"
            f"{match.group('diff') or ''}"
            f"_{new}"
        )

    return DRAWABLE_REGEX.sub(
        replace,
        name
    )


def get_drawable_from_name(name):

    match = DRAWABLE_REGEX.search(name)

    if not match:
        return None, None

    prefix = match.group("prefix").lower()

    drawable = int(
        match.group("drawable")
    )

    drawable += OFFSETS[prefix]

    return prefix, drawable


def escape_sql(value):

    return value.replace(
        "'",
        "\\'"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    source = Path(__file__).parent

    output = source / OUTPUT_FOLDER


    if output.exists():

        print(
            "Lösche alten OUTPUT..."
        )

        shutil.rmtree(
            output
        )


    output.mkdir()


    sql_entries = []

    item_id = START_ID


    print()
    print("==============================")
    print("GTA CLOTHING CONVERTER")
    print("==============================")
    print()

    print("SOURCE:")
    print(source)

    print()

    print("OUTPUT:")
    print(output)

    print()


    for root, dirs, files in os.walk(source):

        root_path = Path(root)


        # OUTPUT nicht wieder lesen
        dirs[:] = [
            d for d in dirs
            if d != OUTPUT_FOLDER
        ]


        relative = root_path.relative_to(
            source
        )


        new_parts = []

        for part in relative.parts:

            new_parts.append(
                convert_name(part)
            )


        new_folder = output / Path(
            *new_parts
        )


        for file in files:


            if file == Path(__file__).name:
                continue


            old_file = root_path / file


            new_file_name = convert_name(
                file
            )


            target = new_folder / new_file_name


            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )


            shutil.copy2(
                old_file,
                target
            )


            prefix, drawable = get_drawable_from_name(
                new_file_name
            )


            if prefix:

                component, label_name = COMPONENTS[prefix]


                texture = texture_number(
                    new_file_name
                )


                item_name = (
                    f"clothing_"
                    f"{label_name.lower()}_"
                    f"{drawable}_"
                    f"{texture}"
                )


                label = (
                    f"{label_name}: "
                    f"{drawable} "
                    f"Color: {texture}"
                )


                cdn_path = str(
                    target.relative_to(output)
                ).replace(
                    "\\",
                    "/"
                )


                icon = (
                    CDN_BASE
                    +
                    cdn_path.replace(
                        "^",
                        "%5E"
                    )
                )


                data = (
                    f'{{"component":{component},'
                    f'"texture":{texture},'
                    f'"drawable":{drawable}}}'
                )


                sql_entries.append(
                    (
                        item_id,
                        item_name,
                        label,
                        icon,
                        data
                    )
                )


                item_id += 1



    sql_file = output / "items.sql"


    with open(
        sql_file,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "INSERT INTO `items` "
            "(`id`,`item_name`,`label`,`weight`,`icon`,`type`,`data`) VALUES\n\n"
        )


        values = []


        for entry in sql_entries:


            item_id, name, label, icon, data = entry


            values.append(
                "("
                f"{item_id}, "
                f"'{escape_sql(name)}', "
                f"'{escape_sql(label)}', "
                f"{WEIGHT}, "
                f"'{icon}', "
                "'clothing', "
                f"'{data}'"
                ")"
            )


        f.write(
            ",\n\n".join(values)
        )

        f.write(
            ";"
        )


    print()
    print("==============================")
    print("FERTIG")
    print("==============================")
    print()

    print(
        f"Items erstellt: {len(sql_entries)}"
    )

    print()

    print(
        "SQL:"
    )

    print(
        sql_file
    )

    input(
        "\nENTER zum Beenden..."
    )


if __name__ == "__main__":
    main()