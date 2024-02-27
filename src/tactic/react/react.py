
__all__ = ["React"]

import tacticenv

class React():

    @classmethod
    def load_libraries(widget):
        tactic_src_dir = tacticenv.get_install_dir()
        react_dir = "%s/src/tactic/ui/react" % tactic_src_dir

        jsx_path = "%s/redux/store.jsx" % dirname
        self.init_react(widget, jsx_path)


        # Resource central components
        jsx_path = "%s/common.jsx" % react_dir
        self.init_react(widget, jsx_path)


        jsx_path = "%s/data_grid.jsx" % react_dir
        self.init_react(widget, jsx_path)

        jsx_path = "%s/widget/notes.jsx" % react_dir
        self.init_react(widget, jsx_path)

        jsx_path = "%s/import_data.jsx" % tactic_react_dir
        self.init_react(widget, jsx_path)

        jsx_path = "%s/table_layout.jsx" % react_dir
        self.init_react(widget, jsx_path)

        jsx_path = "%s/config.jsx" % react_dir
        self.init_react(widget, jsx_path)



