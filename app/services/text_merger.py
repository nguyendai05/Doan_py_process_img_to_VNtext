from typing import List, Dict


def merge_bartpho_result(
    structure: List[Dict],
    bartpho_output: str
) -> str:
    """
    Merge corrected Vietnamese text back into original structure
    """
    corrected_tokens = bartpho_output.split()
    vi_index = 0
    output = []

    for item in structure:
        if item["type"] == "raw":
            output.append(item["text"])
        else:
            # vietnamese
            if vi_index < len(corrected_tokens):
                output.append(corrected_tokens[vi_index])
                vi_index += 1
            else:
                output.append("")  # fallback

    return "".join(output)
