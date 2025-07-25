import bpy


def get_addon_prefs(context):
    for addon_id in context.preferences.addons.keys():
        if 'textify' in addon_id.lower():
            return context.preferences.addons[addon_id].preferences
    return None


def draw_menu(self, context):
    """Append the trim whitespace operator to the context menu if any trailing whitespace exists."""
    prefs = get_addon_prefs(context)
    if not getattr(prefs, "enable_trim_whitespace", False):
        return

    text_block = context.space_data.text
    if not text_block:
        return

    if any(line.body.rstrip() != line.body for line in text_block.lines):
        layout = self.layout
        layout.operator("text.trim_whitespaces", icon="GRIP")
        layout.separator()


class TEXT_OT_trim_whitespaces(bpy.types.Operator):
    """Trim trailing whitespaces in the current text block."""
    bl_idname = "text.trim_whitespaces"
    bl_label = "Trim Whitespaces"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        prefs = get_addon_prefs(context)
        return (
            getattr(prefs, "enable_trim_whitespace", True) and
            context.space_data and
            context.space_data.type == 'TEXT_EDITOR' and
            context.space_data.text
        )

    def execute(self, context):
        text_block = context.space_data.text
        removed_chars = 0

        for line in text_block.lines:
            original = line.body
            trimmed = original.rstrip()
            if trimmed != original:
                removed_chars += len(original) - len(trimmed)
                line.body = trimmed

        if removed_chars:
            self.report({'INFO'}, f"Removed {removed_chars} trailing whitespace character(s).")
        else:
            self.report({'INFO'}, "No trailing whitespace to remove.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(TEXT_OT_trim_whitespaces)
    bpy.types.TEXT_MT_context_menu.prepend(draw_menu)


def unregister():
    bpy.types.TEXT_MT_context_menu.remove(draw_menu)
    bpy.utils.unregister_class(TEXT_OT_trim_whitespaces)
