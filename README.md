# Set Vertex XYZ Modal

A Blender add-on for typing the world position of selected vertices. An overlay follows the mouse, and the mesh updates as soon as the number is valid.

## Features

- Type absolute world coordinates from the keyboard
- Press **X**, **Y**, or **Z** to choose an axis (the field clears)
- Digits, a decimal point, and a sign, from the main keyboard or the numpad
- Live preview while X, Y, and Z are all valid numbers
- **Enter** applies the position
- **Esc** restores the original positions
- One vertex moves to the typed point. Several vertices move together so their median lands on that point
- Middle mouse and the scroll wheel still orbit, pan, and zoom

## Requirements

Blender 3.0 or newer.

## Install

The add-on is the single file `set_vertex_xyz.py`.

### Blender 4.2 and later

1. Open **Edit → Preferences → Add-ons**.
2. Open the menu in the top-right corner and choose **Install from Disk…**.
3. Select `set_vertex_xyz.py`.
4. Enable **Set Vertex XYZ Modal**.
5. Optional: choose **Save Preferences**.

### Blender 3.x and 4.0–4.1

1. Open **Edit → Preferences → Add-ons**.
2. Click **Install…** and select `set_vertex_xyz.py`.
3. Enable **Set Vertex XYZ Modal**.

## Usage

1. Enter **Edit Mode** on a mesh.
2. Select one or more vertices.
3. Run **Set Vertex XYZ (Modal)**:
   - Press **F3** and search for the name
   - Open the Vertex menu (**Ctrl+V**) and choose it
   - Or bind a shortcut to `mesh.set_vertex_xyz_modal`
4. The overlay shows the current world X, Y, and Z beside the cursor.
5. Press **X**, **Y**, or **Z**, then type the new number.
6. Press **Enter** to apply, or **Esc** to restore the original positions.

### Keyboard

| Key | Action |
| --- | --- |
| **X** / **Y** / **Z** | Edit that axis and clear it |
| **0–9**, numpad digits | Append a digit |
| **.** or **,** or numpad **.** | Decimal point |
| **-** or numpad **-** | Toggle the sign |
| **Backspace** | Delete the last character |
| **Enter** | Apply when every axis is a valid number |
| **Esc** | Cancel and restore the original positions |
| **Middle mouse**, **scroll** | Orbit, pan, and zoom |

An empty field, `-`, or `.` leaves the mesh where it is. **Enter** stays in the operator until every axis is a complete number.

Coordinates are world space on the active object. With several vertices selected, the whole group keeps its shape and shifts so the median matches the typed point.

## License

[GNU General Public License v3.0 or later](LICENSE).

Blender requires this license for add-ons. The full text is in `LICENSE`, and the source file carries the SPDX identifier `GPL-3.0-or-later`.
