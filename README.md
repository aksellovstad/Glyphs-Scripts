# Glyphs Scripts


## **Alignment** 

`EnableAutoAlignment.py` *activates* auto alignment for all components in all selected glyphs in the current master.

`DisableAutoAlignment.py` *deactivates* auto alignment for all components in all selected glyphs in the current master.

## **Build Glyphs**

`PasteComponent.py` lets you add a specified component to every currently selected glyph in the font. Ideal for creating fallback fonts or when designing additional masters.

## **Build Shapes**

`InsertPolygon.py` generates a regular convex polygon that is symmetrical.

<img src="https://github.com/user-attachments/assets/ece31860-b1ee-4c54-a045-6f3b36663f02" width="600" alt="Insert Polygon demo GIF">

## **Components** 

`TransferComponents.py` lets you copy component across masters, essentially letting you replicate a component structure across other masters. Applies to all selected glyphs.


## **Glyph Names**

`RenameGlyphs.py` works as a find and replace tool for changing the name of Glyphs. Ideal for updating the suffix of multiple glyphs. <br>
<img width="506" height="245" alt="Skjermbilde 2025-09-20 kl  22 49 20" src="https://github.com/user-attachments/assets/f4d75022-a15b-4755-9a03-3c9a3fd94751" />

## **Guides**

`UnlockGuides.py` unlocks *all* guides in selected glyph(s).

## **Layer**

## **Open Glyphs**

`EmptyGlyphs.py`, as the name might suggest, the script opens a new tab with all glyphs that are empty in the current master.

`OpenbyColorLabel.py`lets you open all glyphs with a specified color label(s). <br>

<img width="386" height="419" alt="Skjermbilde 2025-09-20 kl  21 22 37" src="https://github.com/user-attachments/assets/288c967f-3cfb-4e92-8877-a888c824f9be" />

`WordGenerator.py` utilizes the system dictionary to generate word strings using only characters that are available and drawn in the current master. The script lets you define minimum and maximum word lengths, select letter case, and specify required characters. <br>
<img src="https://github.com/user-attachments/assets/e3477cda-8ec4-4546-ae80-13a7ea6ac943" width="800" alt="Word Generator 3.0 demo GIF">

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

