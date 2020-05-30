# -*- coding: utf-8 -*-
from gi.repository import GObject, Gedit, Gio

# ToDo:
# - Corregir fallo al activar el plugin
# - Comentar los logs (print)

actions = [
    ("fold", "<Alt>Z", "Fold / Unfold")
]

class FoldingPyPluginAppActivatable(GObject.Object, Gedit.AppActivatable):

    app = GObject.property(type=Gedit.App)

    # Se ejecuta al habilitar el plugin en las preferencias de Gedit
    def do_activate(self):
        print("FoldingPyPluginAppActivatable.do_activate")
        self.menu_ext = self.extend_menu("tools-section")
        for (action_name, key, menu_name) in actions:
            fullname = "win." + action_name
            self.app.add_accelerator(key, fullname, None)
            item = Gio.MenuItem.new(_(menu_name), fullname)
            self.menu_ext.append_menu_item(item)

    # Se ejecuta al desabilitar el plugin en las preferencias de Gedit
    def do_deactivate(self):
        print("FoldingPyPluginAppActivatable.do_deactivate")
        for (action_name, key, menu_name) in actions:
            self.app.remove_accelerator("win." + action_name, None)
        self.menu_ext = None


class FoldingPyPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = 'FoldingPyPlugin'
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        print("FoldingPyPlugin.__init__")
        GObject.Object.__init__(self)

    # Se ejecuta al iniciar Gedit, cuando el plugin está habilitado
    def do_activate(self):
        print("FoldingPyPlugin.do_activate")
        self.do_update_state()
        for (action_name, key, menu_name) in actions:
            action = Gio.SimpleAction(name=action_name)
            action.connect('activate', getattr(self, action_name))
            self.window.add_action(action)

    def do_update_state(self):
        self.doc = self.window.get_active_document()
        if self.doc:
            self.view = self.window.get_active_view()
            table = self.doc.get_tag_table()
            self.fld = table.lookup('fld')
            if self.fld is None:
                self.fld = self.doc.create_tag('fld',foreground="#28784b",paragraph_background="#FBFF7E")
            self.inv = table.lookup('inv')
            if self.inv is None:
                self.inv = self.doc.create_tag('inv', invisible=True)


    def fold(self, action, a=None):
        print("Gedit: Folding. Function: fold")
        cursor_pos = self.doc.get_iter_at_mark(self.doc.get_insert())   # Crea un TextIter apartir de la posición del cursor de inserción
        cursor_pos.set_line_offset(0)                                  # Ponermos el cursor al comienzo de la línea
        if self.is_header_line(cursor_pos):
            header_start = cursor_pos.copy()
            # print("Header level:", self.get_header_level(cursor_pos))

            if header_start.has_tag(self.fld):     # Comprueba si el TextIter "a" tiene la etiqueta "fld"
                # print("* Unfolding...")
                section_end = header_start.copy()
                self.get_header_content_end(section_end)
                self.doc.remove_tag(self.fld, header_start, section_end)
                self.doc.remove_tag(self.inv, header_start, section_end)

                #self.doc.remove_tag(self.fld, header_start, header_end)
                #header_start.forward_to_tag_toggle(self.inv)
                #header_end.forward_to_tag_toggle(self.inv)
                #self.doc.remove_tag(self.inv, header_start, header_end)

            else:
                # print("* Folding...")
                # print("header_start:", header_start.get_line())
                header_end = header_start.copy()
                header_end.forward_line()
                # print("header_end:", header_end.get_line())
                section_end = header_start.copy()
                self.get_header_content_end(section_end)
                # print("section_end:", section_end.get_line())
                if section_end.get_line() > header_start.get_line():
                    self.doc.apply_tag(self.fld, header_start, header_end)
                    self.doc.apply_tag(self.inv, header_end, section_end)


    def is_header_line(self, position):
        if position.get_char() == "#":
            return True
        else:
            return False

    def get_header_level(self, position):
        position.set_line_offset(0)     # Ponermos el cursor al comienzo de la línea
        header = 0
        while position.get_char() == "#":
            header = header + 1
            position.forward_char()
        position.set_line_offset(0)
        return header

    def get_header_content_end(self, position):
        header_level = self.get_header_level(position)
        last_line = position.copy()
        last_line.forward_to_end()
        # print("Text last line:", last_line.get_line())
        position.forward_line()

        while ( (position.get_line() < last_line.get_line())
                and ((self.is_header_line(position) == False)
                or (self.get_header_level(position) > header_level)) ):
            position.forward_line()
            # print("Current position:",position.get_line())

        # Por alguna razón cuando hay que plegar la última línea hay que añadir esto:
        if position.get_line() == last_line.get_line():
            position.forward_to_line_end()
        return position
