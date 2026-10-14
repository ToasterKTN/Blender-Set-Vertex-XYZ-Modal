bl_info = {
    "name": "Set Vertex XYZ Modal",
    "author": "Custom",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "Edit Mode > Vertex Menu / F3",
    "description": "Modal operator to set vertex coordinates with live preview",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector

class MESH_OT_set_vertex_xyz_modal(bpy.types.Operator):
    """Set vertex coordinates with full keyboard control and live preview"""
    bl_idname = "mesh.set_vertex_xyz_modal"
    bl_label = "Set Vertex XYZ (Modal)"
    bl_options = {'REGISTER', 'UNDO'}

    values = {'X': '0', 'Y': '0', 'Z': '0'}
    active = 'X'
    use_global = True
    _handle = None
    mouse_x = 0
    mouse_y = 0
    original_coords = []

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if context.mode != 'EDIT_MESH' or not context.edit_object:
            self.report({'WARNING'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        selected = [v for v in bm.verts if v.select]
        if not selected:
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}

        # Store original positions for cancel
        self.original_coords = [v.co.copy() for v in selected]

        if len(selected) == 1:
            co = selected[0].co.copy()
        else:
            co = sum((v.co for v in selected), Vector()) / len(selected)
        if self.use_global:
            co = obj.matrix_world @ co

        self.values = {
            'X': f"{co.x:.4f}",
            'Y': f"{co.y:.4f}",
            'Z': f"{co.z:.4f}"
        }
        self.active = 'X'
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback, args, 'WINDOW', 'POST_PIXEL'
        )
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        context.area.tag_redraw()

        if event.type == 'ESC' and event.value == 'PRESS':
            self.restore_original(context)
            self.finish(context)
            return {'CANCELLED'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            self.apply(context)
            self.finish(context)
            return {'FINISHED'}

        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}

        changed = False

        if event.type == 'X':
            self.active = 'X'
            self.values['X'] = ''
            changed = True
        elif event.type == 'Y':
            self.active = 'Y'
            self.values['Y'] = ''
            changed = True
        elif event.type == 'Z':
            self.active = 'Z'
            self.values['Z'] = ''
            changed = True
        elif event.type in {'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'}:
            mapping = {'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
                       'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9'}
            self.values[self.active] += mapping[event.type]
            changed = True
        elif event.type in {'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
                            'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9'}:
            self.values[self.active] += event.type[-1]
            changed = True
        elif event.type in {'PERIOD', 'NUMPAD_PERIOD'}:
            if '.' not in self.values[self.active]:
                self.values[self.active] += '.'
                changed = True
        elif event.type == 'MINUS':
            if self.values[self.active].startswith('-'):
                self.values[self.active] = self.values[self.active][1:]
            else:
                self.values[self.active] = '-' + self.values[self.active]
            changed = True
        elif event.type == 'BACK_SPACE':
            val = self.values[self.active]
            self.values[self.active] = val[:-1] if len(val) > 1 else ''
            changed = True

        # Live update
        if changed:
            self.apply(context, preview=True)

        return {'RUNNING_MODAL'}

    def apply(self, context, preview=False):
        try:
            x = float(self.values['X'] or '0')
            y = float(self.values['Y'] or '0')
            z = float(self.values['Z'] or '0')
        except ValueError:
            if not preview:
                self.report({'ERROR'}, "Invalid number")
            return

        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        selected = [v for v in bm.verts if v.select]
        if not selected:
            return

        target = Vector((x, y, z))
        if self.use_global:
            target = obj.matrix_world.inverted() @ target

        if len(selected) == 1:
            selected[0].co = target
        else:
            current = sum((v.co for v in selected), Vector()) / len(selected)
            offset = target - current
            for v in selected:
                v.co += offset

        bmesh.update_edit_mesh(obj.data)

    def restore_original(self, context):
        obj = context.edit_object
        if not obj:
            return
        bm = bmesh.from_edit_mesh(obj.data)
        selected = [v for v in bm.verts if v.select]
        if len(selected) != len(self.original_coords):
            return
        for v, co in zip(selected, self.original_coords):
            v.co = co
        bmesh.update_edit_mesh(obj.data)

    def finish(self, context):
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        context.area.tag_redraw()

    def draw_callback(self, op, context):
        import blf
        font_id = 0
        blf.size(font_id, 16)

        x = op.mouse_x + 20
        y = op.mouse_y + 10

        lines = [
            "X: " + (op.values['X'] or "_") + ("  <-" if op.active == 'X' else ""),
            "Y: " + (op.values['Y'] or "_") + ("  <-" if op.active == 'Y' else ""),
            "Z: " + (op.values['Z'] or "_") + ("  <-" if op.active == 'Z' else ""),
        ]
        for i, line in enumerate(lines):
            blf.position(font_id, x, y - i * 22, 0)
            blf.draw(font_id, line)

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
