# Glyphs Scripts

## **Open Glyphs**

`WordGenerator.py` utilizes the system dictionary to generate word strings using only characters that are available and drawn in the current master. The script lets you define minimum and maximum word lengths, select letter case, and specify required characters. <br>
<img src="https://github.com/user-attachments/assets/e3477cda-8ec4-4546-ae80-13a7ea6ac943" width="800" alt="Word Generator 3.0 demo GIF">

`EmptyGlyphs.py`, as the name might suggest, the script opens a new tab with all glyphs that are empty in the current master.

`OpenbyColorLabel.py`lets you open all glyphs with a specified color label(s). <br>

<img width="386" height="419" alt="Skjermbilde 2025-09-20 kl  21 22 37" src="https://github.com/user-attachments/assets/288c967f-3cfb-4e92-8877-a888c824f9be" />


## **Build Glyphs**

`PasteComponent.py` lets you add a specified component to every currently selected glyph in the font. Ideal for creating fallback fonts or when designing additional masters.

## **Components** 

`TransferComponents.py` lets you copy component across masters, essentially letting you replicate a component structure across other masters. Applies to all selected glyphs.

## **Alignment** 

`EnableAutoAlignment.py` *activates* auto alignment for all components in all selected glyphs in the current master.

`DisableAutoAlignment.py` *deactivates* auto alignment for all components in all selected glyphs in the current master.

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

