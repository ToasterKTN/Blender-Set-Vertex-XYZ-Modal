# Set Vertex XYZ Modal

A small Blender addon that lets you set the absolute coordinates of selected vertices using the keyboard, with a live preview that follows your mouse.

No more hunting for number fields in the N-panel or dealing with draggable sliders that steal keyboard focus.

## Features

- Keyboard-driven coordinate input
- Press **X**, **Y**, or **Z** to select a field (clears it so you can type a fresh value)
- Type numbers (including decimals and negatives) while the vertex updates live
- Overlay text follows the mouse cursor
- **Enter** confirms the new position
- **Esc** cancels and restores the original position
- Works with a single vertex or multiple vertices (moves the selection by the median)
- Supports global coordinates

## Installation

1. Download or clone this repository.
2. In Blender go to **Edit → Preferences → Add-ons**.
3. Click **Install…** and select the `set_vertex_xyz.py` file (or the whole folder if you package it as a zip).
4. Enable the checkbox next to **Set Vertex XYZ Modal**.
5. (Optional) Click **Save Preferences**.

The operator is now available permanently.

## Usage

1. Enter **Edit Mode** on a mesh.
2. Select one or more vertices.
3. Start the operator:
   - Press **F3** and search for **Set Vertex XYZ (Modal)**
   - Or open the Vertex menu (**Ctrl+V**) and choose it
   - Or assign a custom shortcut in Preferences → Keymap
4. The overlay appears next to your mouse showing the current X, Y, and Z values.
5. Press **X**, **Y**, or **Z** to choose which value to edit (the field clears).
6. Type the new number. The vertex moves live so you can see where it will land.
7. Press **Enter** to confirm, or **Esc** to cancel and restore the original position.

### Keyboard Controls

| Key              | Action                          |
|------------------|---------------------------------|
| **X** / **Y** / **Z** | Switch to that axis and clear it |
| **0–9**, **.**, **-** | Type a number                   |
| **Backspace**    | Delete last character           |
| **Enter**        | Apply and finish                |
| **Esc**          | Cancel and restore original     |

## Notes

- The overlay only shows the three coordinate lines so it stays out of the way.
- Live preview skips invalid intermediate states (e.g. a trailing decimal point).
- Global coordinates are used by default.
- Multiple selected vertices are moved together based on their median point.

## License

GPL-3.0 or later (same as Blender).
