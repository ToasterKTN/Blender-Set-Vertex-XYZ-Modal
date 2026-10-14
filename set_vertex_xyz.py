# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thomas Bucher

bl_info = {
    "name": "Set Vertex XYZ Modal",
    "author": "Thomas Bucher",
    "version": (1, 3, 0),
    "blender": (3, 0, 0),
    "location": "Edit Mode > Vertex Menu / F3",
    "description": "Type world coordinates for selected vertices, with a live preview",
    "doc_url": "https://github.com/ToasterKTN/Blender-Set-Vertex-XYZ-Modal",
    "tracker_url": "https://github.com/ToasterKTN/Blender-Set-Vertex-XYZ-Modal/issues",
    "category": "Mesh",
}

import blf
import bmesh
import bpy
from mathutils import Vector

_AXES = ("X", "Y", "Z")
_INCOMPLETE = {"", "-", ".", "-.", "+"}
_DIGITS = {
    "ZERO": "0",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
    "NUMPAD_0": "0",
    "NUMPAD_1": "1",
    "NUMPAD_2": "2",
    "NUMPAD_3": "3",
    "NUMPAD_4": "4",
    "NUMPAD_5": "5",
    "NUMPAD_6": "6",
    "NUMPAD_7": "7",
    "NUMPAD_8": "8",
    "NUMPAD_9": "9",
}
# Passed through so orbit, pan, and zoom keep working during the modal.
_VIEW_EVENTS = {
    "MIDDLEMOUSE",
    "WHEELUPMOUSE",
    "WHEELDOWNMOUSE",
    "WHEELINMOUSE",
    "WHEELOUTMOUSE",
    "TRACKPADPAN",
    "TRACKPADZOOM",
    "MOUSEROTATE",
    "MOUSESMARTZOOM",
    "MOUSEMOVE",
}


def _blf_size(font_id, size):
    # Blender 4.0 removed the dpi argument. Older releases require it.
    try:
        blf.size(font_id, size)
    except TypeError:
        blf.size(font_id, size, 72)


def _format_component(value):
    # Enough digits that confirming without typing does not nudge the vertex.
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        return "0"
    return text


def _parse_values(values):
    coords = []
    for axis in _AXES:
        text = values[axis]
        if text in _INCOMPLETE:
            raise ValueError(axis)
        coords.append(float(text))
    return Vector(coords)


def _selected_verts(obj):
    bm = bmesh.from_edit_mesh(obj.data)
    # vert.index is only valid after the lookup table is built.
    bm.verts.ensure_lookup_table()
    return bm, [v for v in bm.verts if v.select]


def _selection_world(obj, selected):
    if len(selected) == 1:
        local = selected[0].co.copy()
    else:
        local = sum((v.co for v in selected), Vector()) / len(selected)
    return obj.matrix_world @ local


def _move_selection(obj, world):
    """Move the selected verts so their median sits on the world point."""
    local = obj.matrix_world.inverted() @ world
    bm, selected = _selected_verts(obj)
    if not selected:
        return False
    if len(selected) == 1:
        selected[0].co = local
    else:
        current = sum((v.co for v in selected), Vector()) / len(selected)
        offset = local - current
        for vert in selected:
            vert.co += offset
    bmesh.update_edit_mesh(obj.data)
    return True


def _draw_overlay(op, context):
    region = context.region
    if region is None:
        return
    started = getattr(op, "_region", None)
    if started is not None and region != started:
        return

    font_id = 0
    scale = context.preferences.system.ui_scale
    _blf_size(font_id, max(12, int(round(15 * scale))))
    blf.enable(font_id, blf.SHADOW)
    try:
        blf.shadow(font_id, 3, 0.0, 0.0, 0.0, 0.9)
        blf.shadow_offset(font_id, 1, -1)

        pad = 16 * scale
        line_h = 22 * scale
        rows = []
        for axis in _AXES:
            shown = op.values[axis] or "_"
            mark = "  <-" if op.active == axis else ""
            rows.append((axis, f"{axis}: {shown}{mark}"))

        widths = [blf.dimensions(font_id, text)[0] for _, text in rows]
        block_w = max(widths) if widths else 0.0
        block_h = line_h * len(rows)

        x = op.mouse_x + pad
        y = op.mouse_y + pad
        if x + block_w > region.width:
            x = max(pad, op.mouse_x - pad - block_w)
        if y - block_h < 0:
            y = min(region.height - pad, op.mouse_y + block_h)

        for i, (axis, text) in enumerate(rows):
            if axis == op.active:
                blf.color(font_id, 1.0, 0.86, 0.35, 1.0)
            else:
                blf.color(font_id, 0.93, 0.93, 0.93, 1.0)
            blf.position(font_id, x, y - i * line_h, 0)
            blf.draw(font_id, text)
    finally:
        blf.disable(font_id, blf.SHADOW)


class MESH_OT_set_vertex_xyz_modal(bpy.types.Operator):
    """Type world coordinates for the selected vertices"""

    bl_idname = "mesh.set_vertex_xyz_modal"
    bl_label = "Set Vertex XYZ (Modal)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.edit_object
        return (
            context.mode == "EDIT_MESH"
            and obj is not None
            and obj.type == "MESH"
            and obj.data.total_vert_sel > 0
        )

    def invoke(self, context, event):
        obj = context.edit_object
        if context.mode != "EDIT_MESH" or obj is None or obj.type != "MESH":
            self.report({"WARNING"}, "Must be in Edit Mode on a mesh")
            return {"CANCELLED"}

        _bm, selected = _selected_verts(obj)
        if not selected:
            self.report({"WARNING"}, "No vertices selected")
            return {"CANCELLED"}

        world = _selection_world(obj, selected)
        self.values = {axis: _format_component(world[i]) for i, axis in enumerate(_AXES)}
        self.active = "X"
        self._original = [(v.index, v.co.copy()) for v in selected]
        self._region = context.region
        self._handle = None
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y

        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_overlay, (self, context), "WINDOW", "POST_PIXEL"
        )
        context.window_manager.modal_handler_add(self)
        if context.area is not None:
            context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        if context.area is not None:
            context.area.tag_redraw()

        if event.type == "ESC" and event.value == "PRESS":
            self._restore(context)
            self._finish(context)
            return {"CANCELLED"}

        if event.type in {"RET", "NUMPAD_ENTER"} and event.value == "PRESS":
            if self._apply(context, preview=False):
                self._finish(context)
                return {"FINISHED"}
            return {"RUNNING_MODAL"}

        if event.type in _VIEW_EVENTS:
            return {"PASS_THROUGH"}

        if event.value != "PRESS":
            return {"RUNNING_MODAL"}

        if event.ctrl or event.alt or event.oskey:
            return {"RUNNING_MODAL"}

        changed = False
        if event.type in {"X", "Y", "Z"}:
            self.active = event.type
            self.values[self.active] = ""
            changed = True
        elif event.type in _DIGITS:
            self.values[self.active] += _DIGITS[event.type]
            changed = True
        elif event.type in {"PERIOD", "NUMPAD_PERIOD", "COMMA"}:
            if "." not in self.values[self.active]:
                self.values[self.active] += "."
                changed = True
        elif event.type in {"MINUS", "NUMPAD_MINUS"}:
            current = self.values[self.active]
            if current.startswith("-"):
                self.values[self.active] = current[1:]
            else:
                self.values[self.active] = "-" + current
            changed = True
        elif event.type == "BACK_SPACE":
            self.values[self.active] = self.values[self.active][:-1]
            changed = True

        if changed:
            self._apply(context, preview=True)

        return {"RUNNING_MODAL"}

    def _apply(self, context, preview):
        obj = context.edit_object
        if obj is None:
            return False
        try:
            world = _parse_values(self.values)
        except ValueError:
            if not preview:
                self.report({"WARNING"}, "Enter a complete number for X, Y, and Z")
            return False
        try:
            moved = _move_selection(obj, world)
        except ValueError:
            moved = False
        if not moved and not preview:
            self.report({"WARNING"}, "Could not apply that position")
        return moved

    def _restore(self, context):
        obj = context.edit_object
        if obj is None:
            return
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        for index, co in self._original:
            if 0 <= index < len(bm.verts):
                bm.verts[index].co = co
        bmesh.update_edit_mesh(obj.data)

    def _finish(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            self._handle = None
        if getattr(context, "area", None) is not None:
            context.area.tag_redraw()


def menu_func(self, context):
    self.layout.operator(MESH_OT_set_vertex_xyz_modal.bl_idname)


def register():
    bpy.utils.register_class(MESH_OT_set_vertex_xyz_modal)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_func)
    bpy.utils.unregister_class(MESH_OT_set_vertex_xyz_modal)


if __name__ == "__main__":
    register()
