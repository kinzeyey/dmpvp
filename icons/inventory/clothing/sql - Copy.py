import os
import re
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

START_ID = 10000
WEIGHT = "1.200"

CDN_BASE = (
    "https://cdn.jsdelivr.net/gh/"
    "kinzeyey/dmpvp/"
    "icons/inventory/clothing/"
)

OUTPUT_SQL = "items.sql"



# ============================================================
# COMPONENTS
# ============================================================

COMPONENTS = {

    "mask": (1, "Mask"),
    "hair": (2, "Hair"),

    "uppr": (3, "Upper"),
    "lowr": (4, "Legs"),

    "hand": (5, "Hands"),
    "feet": (6, "Feet"),

    # FIX
    "teef": (7, "Teef"),
    "accs": (8, "Accessory"),

    "task": (9, "Armor"),
    "decl": (10, "Decal"),

    "jbib": (11, "Top"),


    # p components
    "p_head": (0, "Head"),
    "p_eyes": (0, "Eyes"),
    "p_ears": (0, "Ears"),
    "p_lwrist": (0, "Left Wrist"),
    "p_rwrist": (0, "Right Wrist"),

    # masks
    "berd": (1, "Mask"),
}



# ============================================================
# REGEX
# ============================================================


DRAWABLE_REGEX = re.compile(
    r"(?:mp_m_freemode_01(?:_p)?_pack\d+m\^)?"
    r"(?P<prefix>[a-z_]+)"
    r"_(?:diff_)?"
    r"(?P<drawable>\d+)",
    re.IGNORECASE
)



TEXTURE_REGEX = re.compile(
    r"_diff_\d+_(?P<texture>[a-z])",
    re.IGNORECASE
)



# ============================================================
# FUNCTIONS
# ============================================================


def clean_name(filename):

    return filename.lower()



def get_component(filename):

    filename = clean_name(filename)


    match = DRAWABLE_REGEX.search(filename)


    if not match:
        return None, None



    prefix = match.group(
        "prefix"
    )


    drawable = int(
        match.group(
            "drawable"
        )
    )



    # p_teile sauber behandeln

    if prefix.startswith("p_"):

        if prefix in COMPONENTS:
            return prefix, drawable



    if prefix in COMPONENTS:

        return prefix, drawable



    return None, None





def get_texture(filename):

    match = TEXTURE_REGEX.search(
        filename
    )


    if not match:

        return 0



    letter = match.group(
        "texture"
    ).lower()


    return ord(letter) - ord("a")





def create_icon_url(path):

    return (
        CDN_BASE
        +
        str(path)
        .replace(
            "\\",
            "/"
        )
        .replace(
            "^",
            "%5E"
        )
    )





def sql_escape(text):

    return text.replace(
        "'",
        "\\'"
    )





# ============================================================
# MAIN
# ============================================================


def main():

    root = Path(
        __file__
    ).parent



    entries = []

    item_id = START_ID



    print()
    print("==============================")
    print("GTA CLOTHING SQL GENERATOR")
    print("==============================")
    print()



    for current, dirs, files in os.walk(root):


        current_path = Path(
            current
        )



        for filename in files:



            if filename == OUTPUT_SQL:
                continue



            if filename == Path(__file__).name:
                continue



            if not filename.lower().endswith(
                (
                    ".png",
                    ".webp",
                    ".jpg",
                    ".jpeg"
                )
            ):
                continue




            prefix, drawable = get_component(
                filename
            )



            if not prefix:
                continue



            component, label_name = COMPONENTS[
                prefix
            ]



            texture = get_texture(
                filename
            )



            item_name = (
                f"clothing_"
                f"{prefix}_"
                f"{drawable}_"
                f"{texture}"
            )



            label = (
                f"{label_name}: "
                f"{drawable} "
                f"Color: {texture}"
            )



            relative = (
                current_path
                /
                filename
            ).relative_to(
                root
            )



            icon = create_icon_url(
                relative
            )



            # =====================================
            # GTA APPLY DATA
            # =====================================


            data_drawable = drawable



            # Tops GTA Offset
            if prefix == "jbib":

                data_drawable += 1



            # Legs starten bei 207
            if prefix == "lowr":

                data_drawable += 207




            data = (
                "{"
                f'"component":{component},'
                f'"texture":{texture},'
                f'"drawable":{data_drawable}'
                "}"
            )




            entries.append(
                (
                    item_id,
                    item_name,
                    label,
                    icon,
                    data
                )
            )



            print(
                f"{item_id} | {item_name} | {data}"
            )



            item_id += 1





    output = root / OUTPUT_SQL



    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "INSERT INTO `items` "
            "(`id`, `item_name`, `label`, `weight`, `icon`, `type`, `data`) VALUES\n\n"
        )



        values = []



        for entry in entries:


            iid, name, label, icon, data = entry



            values.append(
                "("
                f"{iid}, "
                f"'{sql_escape(name)}', "
                f"'{sql_escape(label)}', "
                f"{WEIGHT}, "
                f"'{icon}', "
                "'clothing', "
                f"'{data}'"
                ")"
            )



        f.write(
            ",\n\n".join(values)
        )


        f.write(";")



    print()
    print("==============================")
    print("FERTIG")
    print("==============================")
    print()
    print(
        f"Items erstellt: {len(entries)}"
    )
    print()
    print(output)



    input(
        "\nENTER zum schließen..."
    )





if __name__ == "__main__":
    main()