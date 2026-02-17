# Glyphs Scripts

## **Alignment** 
`DisableAutoAlignment.py` *deactivates* auto alignment for all components in all selected glyphs in the *current* master.

`EnableAutoAlignment.py` *activates* auto alignment for all components in all selected glyphs in the *current* master.

`OpenGlyphsWithoutAutoAlignment.py` opens all glyphs that contain component(s) with automatic alignment disabled.


## **Build Glyphs**

`PasteComponent.py` lets you *add* a specified component to every currently selected glyph in the font. 

`RemoveComponent.py` lets you *remove* a specified component from every currently selected glyph in the font. 


## **Build Shapes**

`InsertPolygon.py` generates a regular convex polygon.

<img src="https://github.com/user-attachments/assets/7b9e4775-8961-48f3-a266-b19252d2216d" width="600" alt="Word Generator 3.0 demo GIF">


## **Components** 

`TransferComponents.py` lets you copy components across masters, letting you replicate the component structure from a source to a target master. Applies to all selected glyphs.

`TransferComponents.py` lets you copy paths across masters, from a source to a target master. Applies to all selected glyphs. Optional: Clears target glyph(s), includes anchors and inherit sidebearings.

`TransferPathsAndComponents.py` is an all in one tool that does all of the above as well as letting you transfer paths and components across documents.


## **Glyph Names**

`RenameGlyphs.py` works as a find and replace tool for changing the name of Glyphs. Ideal for updating the suffix of multiple glyphs. <br>
<img width="506" height="245" alt="Skjermbilde 2025-09-20 kl  22 49 20" src="https://github.com/user-attachments/assets/f4d75022-a15b-4755-9a03-3c9a3fd94751" />


## **Guides**

`UnlockGuides.py` unlocks all locked guides in selected glyph(s) in the *current* master.


## **Layer**

`AddBackupLayer.py` can be utilized for adding a backup layer via a shortcut (e. g. **control** + **L**). Follows the system syntax for date and time and works on multiple characters at once without creating duplicates

`AddCustomBackupLayer.py` works much the same as `AddBackupLayer.py`, but additionally lets you add a custom name for the new layer and is applicable to multiple charcters at once. Suggested shortcut: **control** + **shift** + **L**.


## **Open Glyphs**

`WordGenerator.py` utilizes the system dictionary to generate word strings using only characters that are available and drawn in the *current* master. The script lets you define minimum and maximum word lengths, select letter case, and specify required characters. <br>
<img src="https://github.com/user-attachments/assets/e3477cda-8ec4-4546-ae80-13a7ea6ac943" width="800" alt="Word Generator 3.0 demo GIF">

`CloseNodes.py` opens glyphs that include nodes that are less than 5 pt. apart.

`EmptyGlyphs.py`, as the name might suggest, the script opens a new tab with all glyphs that are empty in the *current* master.

`OpenGlyphsWithoutAutoAlignment.py` opens glyphs that icludes components that have automatic alignment *disabled*.

`OpenIncompatibleGlyphs.py` opens a new tab with all glyphs with incompatibilities on a asigned variable axis.

`OpenbyColorLabel.py` lets you open all glyphs with a specified color label. <br>

<img width="386" height="419" alt="Skjermbilde 2025-09-20 kl  21 22 37" src="https://github.com/user-attachments/assets/288c967f-3cfb-4e92-8877-a888c824f9be" />


## **Lookups**

`ClassSuggester.py` scans for glyphs that share a base name with one or more suffixed variants (e.g. .alt, .ss01, .case, etc.), and prints suggested OpenType class definitions to the Macro Panel. Script is *read only*. For example a file containing ``hyphen``, ``hyphen.case``, ``colon``, ``colon.case``, ``a``, ``a.alt``, ``a.ss01`` will print a suggested @class: 


```text
@a      = [a a.alt a.ss01];
@colon  = [colon colon.case];
@hyphen = [hyphen hyphen.case];
```



## **Spacing**

`BasicSpacingString.py` is simply a shortcut for spacing strings `A–Z`.  
Running the script opens **two separate tabs** with uppercase and lowercase spacing strings, respectively.

`ComplexSpacingString.py` generates every possible combination of uppercase letters, lowercase letters, and uppercase–lowercase pairings from `A-Z` in a comprehensive set of spacing strings.. 
