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
    "berd": (1, "Mask"),

    "hair": (2, "Hair"),

    "uppr": (3, "Upper"),
    "lowr": (4, "Legs"),

    "hand": (5, "Hands"),
    "feet": (6, "Feet"),

    "teef": (7, "Teef"),
    "accs": (8, "Accessory"),

    "task": (9, "Armor"),
    "decl": (10, "Decal"),

    "jbib": (11, "Top"),

    "p_head": (0, "Head"),
    "p_eyes": (0, "Eyes"),
    "p_ears": (0, "Ears"),
    "p_lwrist": (0, "Left Wrist"),
    "p_rwrist": (0, "Right Wrist"),

}



# ============================================================
# REGEX
# ============================================================


DRAWABLE_REGEX = re.compile(
    r"(?:mp_m_freemode_01(?:_p)?_?pack\d+m\^)?"
    r"(?P<prefix>[a-z_]+?)_"
    r"(?P<drawable>\d+)",
    re.IGNORECASE
)



# ============================================================
# FUNCTIONS
# ============================================================


def clean_name(filename):

    return filename.lower()



def get_component(filename):

    filename = clean_name(filename)


    match = DRAWABLE_REGEX.search(
        filename
    )


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



    if prefix in COMPONENTS:

        return prefix, drawable



    return None, None




def create_icon_url(path):

    return (
        CDN_BASE
        +
        str(path)
        .replace("\\", "/")
        .replace("^", "%5E")
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



    # zählt Texturen pro Drawable
    texture_counter = {}



    print()
    print("==============================")
    print("GTA CLOTHING SQL GENERATOR")
    print("==============================")
    print()



    for current, dirs, files in os.walk(root):


        current_path = Path(current)



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



            # =====================================
            # TEXTURE AUTO COUNT
            # =====================================


            key = (
                prefix,
                drawable
            )


            if key not in texture_counter:

                texture_counter[key] = 0



            texture = texture_counter[key]

            texture_counter[key] += 1





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
            # GTA DATA
            # =====================================


            data_drawable = drawable



            # Tops
            if prefix == "jbib":

                data_drawable += 1



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
    print(
        output
    )



    input(
        "\nENTER zum schließen..."
    )





if __name__ == "__main__":
    main()