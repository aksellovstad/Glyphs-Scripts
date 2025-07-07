# Glyphs Scripts

## **Word Generator**

`Dictionary.py` utilizes the system dictionary to generate word strings using only characters that are available and drawn in the current master. The script lets you define minimum and maximum word lengths, select letter case, and specify required characters. <br>

<img width="406" alt="Skjermbilde 2025-07-07 kl  00 33 01" src="https://github.com/user-attachments/assets/8de857ce-33d6-4b60-a1b3-c78e56de7f8f" />


## **Spacing**

`BasicSpacingString.py` is simply a shortcut for spacing strings `A–Z`.  
Running the script opens **two separate tabs** with uppercase and lowercase spacing strings, respectively.

`ComplexSpacingString.py` generates every possible combination of uppercase letters, lowercase letters, and uppercase–lowercase pairings from `A-Z` in a comprehensive set of spacing strings, much like `BasicSpacingString.py`. <br>

| Basic    | Complex     |
|----------|-------------|
| HHHAHHH  | HHHAaAHHH   |
| HHHBHHH  | HHHAbAHHH   |
| HHHCHHH  | HHHAcAHHH   |
| HHHDHHH  | HHHAdAHHH   |
| HHHEHHH  | HHHAeAHHH   |
| HHHFHHH  | HHHAfAHHH   |
| …        | …           |
| HHHXHHH  | HHHZxZHHH   |
| HHHYHHH  | HHHZyZHHH   |
| HHHZHHH  | HHHZzZHHH   |


## **Open Glyphs**

`EmptyGlyphs.py`, as the name might suggest, the script opens a new tab with all glyphs that are empty in the current master.

`OpenbyColorLabel.py`lets you open all glyphs with a specified color label(s). <br>

<img width="346" alt="Skjermbilde 2025-07-07 kl  11 47 53" src="https://github.com/user-attachments/assets/2fb23925-8e4e-4a23-a644-69b513a17f6c" />

## **Build Glyphs**

`PasteComponent.py` lets you add a specified component to every currently selected glyph in the font. Ideal for creating fallback fonts or when designing additional masters.