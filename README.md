
  * This is based off [Schwaffle's Encounter Sheet](https://www.dmsguild.com/product/210262/5e-Encounter-Sheet?site=).

I retyped the fonts using the Asana Math font inside Gimp at a few pixel heights: 6, 10, 11, 14, 18

# Manual work

## Set auto-size fields

The following fields must be updated to have a font size of 0:
- monster_#_size
- monster_#_race
- monster_#_armortype
- monster_#_alignment
- monster_#_hitdice
- monster_#_speed
- monster_#_attack_#_description
- monster_#_traits

To make this simpler, these fields are saved as having a 2pt font (the smallest size LibreOffice Draw lets me set). So we can easily search and replace the string ` 2 Tf)` -> ` 0 Tf)`. 

# How-tos

## Set auto-size font

Open the PDF as text and find the control you want. E.g., if looking for `monster_1_speed`, search for `/T(monster_1_speed)`. This should be within a /Type/Annot/Subtype/Widget/F object.

Within this object, we need to look for the Default Appearance string, designed by `/DA(...)`. Within that string is an operator called `Tf`. PDF using a stack notation for operators, so the arguments come immediately before the operator name. The first will be a font identified by `/F#` where `#` is any number. The second is the font size.

By changing the font size to `0`, the field will use an auto-size font.
