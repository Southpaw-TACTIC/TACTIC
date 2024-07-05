
__all__ = ["React"]

import tacticenv

class React():

    @classmethod
    def load_libraries(cls, widget):

        from tactic.ui.tools import BaseReactWdg as ReactWdg

        tactic_src_dir = tacticenv.get_install_dir()
        react_dir = "%s/src/tactic/react" % tactic_src_dir

        #jsx_path = "%s/redux/store.jsx" % react_dir
        #ReactWdg.init_react(widget, jsx_path)


        # React central components
        jsx_path = "%s/common.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)


        jsx_path = "%s/data_grid.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)

        jsx_path = "%s/widget/notes.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)

        jsx_path = "%s/import_data.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)

        jsx_path = "%s/table_layout.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)

        jsx_path = "%s/config.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)

        jsx_path = "%s/pages.jsx" % react_dir
        ReactWdg.init_react(widget, jsx_path)




