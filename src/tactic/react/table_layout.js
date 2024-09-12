"use strict";

function _extends() { _extends = Object.assign ? Object.assign.bind() : function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; }; return _extends.apply(this, arguments); }
const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;
const useReducer = React.useReducer;
const Box = MaterialUI.Box;
const Button = MaterialUI.Button;
const Modal = MaterialUI.Modal;
const Alert = MaterialUI.Alert;
const Tab = MaterialUI.Tab;
const Tabs = MaterialUI.Tabs;
const MenuItem = MaterialUI.MenuItem;
const Menu = MaterialUI.Menu;
const Select = MaterialUI.Select;
const TextField = MaterialUI.TextField;
const Checkbox = MaterialUI.Checkbox;
const Dialog = MaterialUI.Dialog;
const DialogTitle = MaterialUI.DialogTitle;
const DialogContent = MaterialUI.DialogContent;
const DialogContentText = MaterialUI.DialogContentText;
const DialogActions = MaterialUI.DialogActions;
const Common = spt.react.Common;
const DataGrid = spt.react.DataGrid;
const NotesWdg = spt.react.widget.NotesWdg;
const ROOT_CMD = "tactic.react";
const TableLayout = React.forwardRef((props, ref) => {
  React.useImperativeHandle(ref, () => ({
    save(item, column) {
      save(item, column);
    },
    refresh_cells(nodes) {
      grid_ref.current.refresh_cells(nodes);
    },
    get_grid_ref() {
      return grid_ref;
    },
    group_data(group_column) {
      return group_by(data, group_column);
    },
    export_csv() {
      grid_ref.current.export_csv();
    },
    get_display_data() {
      return grid_ref.current.get_display_data();
    },
    get_selected_nodes() {
      return grid_ref.current.get_selected_nodes();
    },
    get_selected_rows() {
      return grid_ref.current.get_selected_rows();
    },
    show_total() {
      return grid_ref.current.show_total();
    },
    reload() {
      return load_data();
    }
  }));
  const [first_load, set_first_load] = useState(true);
  const [loading, set_loading] = useState(false);
  const [search_type, set_search_type] = useState("");
  const [base_data, set_base_data] = useState([]);
  const [data, set_data] = useState([]);
  const [element_names, set_element_names] = useState([]);
  const [element_definitions, set_element_definitions] = useState({});
  const [column_defs, set_column_defs] = useState([]);
  const edit_modal_ref = useRef();
  const delete_modal_ref = useRef();
  const property_modal_ref = useRef();
  const import_data_modal_ref = useRef();
  const grid_ref = useRef();
  useEffect(() => {
    init();
  }, []);
  const init = async () => {
    let element_names = props.element_names || ["code"];
    set_element_names([...element_names]);
    let element_definitions = props.element_definitions;
    if (!element_definitions) {
      config_handler = props.config_handler;
      if (config_handler) {
        element_definitions = await get_element_definitions(config_handler);
      }
    }
    if (element_definitions) {
      await set_element_definitions(element_definitions);
      build_column_defs(element_names, element_definitions);
    } else if (props.column_defs) {
      set_column_defs(props.column_defs);
    }
    set_search_type(props.search_type);
    if (props.data) {
      set_data(props.data);
    } else {
      await load_data();
    }
  };
  const load_data = async () => {
    let cmd = props.get_cmd;
    if (!cmd) {
      alert("Get cmd is not defined");
      return;
    }
    let kwargs = props.get_kwargs || {};
    let config_handler = props.config_handler;
    kwargs["config_handler"] = config_handler;
    if (props.extra_data) {
      Object.keys(props.extra_data).forEach(key => {
        kwargs[key] = props.extra_data[key];
      });
    }
    set_loading(true);
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, kwargs).then(ret => {
      let data = ret.info;
      set_data(data);
      set_loading(false);
      set_first_load(false);
    }).catch(e => {
      set_loading(false);
      alert("TACTIC ERROR: " + e);
    });
  };
  const get_element_definitions = async (cmd, kwargs) => {
    if (!kwargs) {
      kwargs = {};
    }
    let server = TACTIC.get();
    let ret = await server.p_execute_cmd(cmd, kwargs);
    let info = ret.info;
    let config = info.config;
    let renderer_params = info.renderer_params;
    if (!renderer_params) {
      renderer_params = info.cell_params;
    }

    let definitions = spt.react.Config(config, {
      table_ref: ref,
      renderer_params: props.renderer_params || props.cell_params || renderer_params
    });
    return definitions;
  };
  const save = (item, column) => {

    let selected = grid_ref.current.get_selected_nodes();
    let items = [];
    if (selected.length) {
      selected.forEach(selected_item => {
        items.push(selected_item.data);
      });
    } else {
      items.push(item);
    }
    let cmd = props.save_cmd;
    if (!cmd) {
      cmd = "tactic.react.TableSaveCmd";
    }
    let updates = [];
    let inserts = [];
    items.forEach(item => {
      let mode = item.code ? "edit" : "insert";
      let update = {
        search_key: item.__search_key__,
        column: column,
        value: item[column],
        mode: mode
      };
      if (mode == "insert") {
        inserts.push(item);
      }
      updates.push(update);
    });
    let kwargs = {
      updates: updates,
      config_handler: props.config_handler
    };
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, kwargs).then(ret => {
      let info = ret.info;
      let updated_sobjects = info.updated_sobjects;
      let new_sobjects = info.new_sobjects || [];

      new_sobjects.forEach(item => {
        data.push(item);
      });
    }).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  };
  const insert_item = item => {

    let cmd = props.save_cmd;
    if (!cmd) {
      cmd = "tactic.react.TableSaveCmd";
    }

    let inserts = [];
    let mode = item.__search_key__ ? "edit" : "insert";
    let code = Common.generate_key(12);
    item.code = code;
    let update = {
      search_type: search_type,
      search_key: item.__search_key__,
      mode: mode,
      item: item
    };
    if (mode == "insert") {
      inserts.push(item);
    }
    let kwargs = {
      updates: [update],
      extra_data: props.extra_data,
      config_handler: props.config_handler
    };
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, kwargs).then(ret => {
      let info = ret.info;
      let sobjects = info.sobjects || [];

      load_data();
    }).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  };
  const cell_value_changed = props => {
    let column = props.colDef.field;
    let data = props.data;
    save(data, column);
  };
  const column_moved = () => {};
  const build_column_defs = (new_element_names, definitions) => {
    let column_defs = props.column_defs;
    if (column_defs) {
      return column_defs;
    }
    if (!new_element_names) {
      new_element_names = element_names;
    }
    if (!definitions) {
      definitions = element_definitions;
    }
    column_defs = [{
      field: '',
      maxWidth: 50,
      headerCheckboxSelection: true,
      headerCheckboxSelectionFilteredOnly: true,
      checkboxSelection: true,
      pinned: "left"
    }];
    new_element_names.forEach(element => {
      let column_def;
      try {
        column_def = definitions[element];
      } catch (e) {}
      if (!column_def) {
        column_def = {
          field: element,
          headerName: Common.capitalize(element),
          maxWidth: 150,
          editable: true,
          onCellValueChanged: cell_value_changed,
          cellRenderer: SimpleCellRenderer
        };
      }
      column_defs.push(column_def);
    });
    set_column_defs(column_defs);
  };
  let property_names = ["title", "name", "type", "width"];
  let property_definitions = {
    title: {},
    name: {},
    type: {},
    width: {
      "type": "number"
    }
  };
  const property_save = (item, column) => {
    let save_cmd = ROOT_CMD + ".TableCreatePropertyCmd";
    let kwargs = {
      name: props.name,
      item: item,
      column: column
    };
    let server = TACTIC.get();
    server.execute_cmd(save_cmd, kwargs).then(ret => {}).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  };

  const [import_options, set_import_options] = useState({
    search_type: props.search_type
  });
  const get_import_data_modal = () => {
    let cmd = props.import_cmd;
    if (!cmd) {
      cmd = ROOT_CMD + ".ImportDataCmd";
    }
    return React.createElement(spt.react.ImportDataModal, {
      ref: import_data_modal_ref,
      kwargs: import_options,
      cmd: cmd,
      reload: () => {
        load_data();
      },
      elements: {
        help: props.elements?.import_help
      }
    });
  };
  const show_import_data_modal = async () => {
    await set_import_options({
      ...import_options
    });
    import_data_modal_ref.current.show();
  };
  on_select = selected => {};
  const get_shelf = () => {
    return React.createElement(React.Fragment, null, React.createElement(EditModal, {
      name: props.name,
      ref: edit_modal_ref,
      on_insert: insert_item,
      element_names: props.element_names,
      element_definitions: element_definitions,
      extra_data: props.extra_data
    }), React.createElement(EditModal, {
      name: "Custom Property",
      ref: property_modal_ref,
      on_insert: property_save,
      element_names: property_names,
      element_definitions: property_definitions
    }), React.createElement(DeleteModal, {
      name: "Delete",
      ref: delete_modal_ref,
      grid_ref: grid_ref
      ,
      element_names: property_names,
      element_definitions: property_definitions,
      load_data: load_data
    }), get_import_data_modal(), React.createElement("div", {
      style: {
        display: "flex",
        gap: "15px",
        alignItems: "center"
      }
    }, props.get_shelf && props.get_shelf(), props.element_names && React.createElement(ColumnManagerMenu, {
      all_columns: props.all_element_names || props.element_names,
      columns: element_names,
      update: build_column_defs,
      property_modal_ref: property_modal_ref
    }), false && React.createElement(Button, {
      size: "small",
      variant: "contained",
      onClick: e => {
        grid_ref.current.set_filter("director", "Jil");
      }
    }, "Filter"), React.createElement(TableLayoutActionMenu, {
      grid_ref: grid_ref,
      edit_modal_ref: edit_modal_ref,
      delete_modal_ref: delete_modal_ref,
      import_data_modal_ref: import_data_modal_ref,
      on_import: load_data,
      import_cmd: props.import_cmd,
      action_menu_items: props.action_menu_items
    })));
  };
  const get_name = () => {
    if (props.name) {
      return props.name;
    } else {
      return "TABLE";
    }
  };
  let EmptyWdg = props.empty_wdg;
  return React.createElement("div", null, props.show_shelf != false && React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between"
    }
  }, React.createElement("div", {
    style: {
      fontSize: "1.2rem"
    }
  }, get_name()), get_shelf()), !first_load && !loading && props.empty_wdg && data?.length == 0 ? React.createElement("div", null, React.createElement(EmptyWdg, {
    edit_modal_ref: edit_modal_ref,
    import_data_modal_ref: import_data_modal_ref
  })) : React.createElement(React.Fragment, null, !loading ? React.createElement(DataGrid, {
    ref: grid_ref,
    name: get_name(),
    column_defs: column_defs,
    data: data,
    supress_click: true,
    auto_height: props.auto_height,
    height: props.height,
    row_height: props.row_height,
    enable_undo: props.enable_undo,
    on_column_moved: props.on_column_moved
  }) : React.createElement("div", null, "Loading ...")));
});
const TableLayoutActionMenu = props => {
  const [action_anchorEl, action_setAnchorEl] = React.useState(null);
  const action_is_open = Boolean(action_anchorEl);
  const action_handle_click = event => {
    action_setAnchorEl(event.currentTarget);
  };
  const action_handle_close = async () => {
    action_setAnchorEl(null);
  };
  const action_handle_select = async () => {
    action_setAnchorEl(null);
  };
  const open_edit_modal = () => {
    let selected = props.grid_ref.current.get_selected_nodes();
    if (selected.length == 0) {
      alert("No items selected");
      return;
    }
    let data = selected[0].data;
    props.edit_modal_ref.current.set_item(data);
    props.edit_modal_ref.current.show();
  };
  return React.createElement("div", {
    style: {
      marginRight: "5px"
    }
  }, React.createElement(Button, {
    variant: "outlined",
    id: "action-button",
    onClick: action_handle_click
  }, "ACTION", React.createElement("i", {
    className: "fa-xs fas fa-caret-down"
  })), React.createElement(Menu, {
    id: "action-menu",
    anchorEl: action_anchorEl,
    open: action_is_open,
    onClose: action_handle_close
  }, React.createElement(MenuItem, {
    onClick: e => {
      action_handle_select();
      props.on_import();
    }
  }, "Reload"), React.createElement(MenuItem, {
    onClick: e => {
      action_handle_select();
      props.edit_modal_ref.current.show();
    }
  }, "New"), React.createElement(MenuItem, {
    onClick: e => {
      action_handle_select();
      open_edit_modal();
    }
  }, "Edit Selected"), props.import_cmd && React.createElement(MenuItem, {
    onClick: e => {
      action_handle_select();
      props.import_data_modal_ref.current.show();
    }
  }, "Import Data"), React.createElement(MenuItem, {
    onClick: e => {
      action_handle_select();
      props.grid_ref.current.export_csv();
    }
  }, "Export CSV"), React.createElement("hr", null), React.createElement(MenuItem, {
    onClick: e => {
      action_handle_select();
      let selected = props.grid_ref.current.get_selected_nodes();
      props.delete_modal_ref.current.set_items(selected);
      props.delete_modal_ref.current.show();
    }
  }, "Delete Selected"), props.action_menu_items && React.createElement(React.Fragment, null, React.createElement("hr", null), props.action_menu_items({
    close: action_handle_select
  }))));
};
const EditForm = React.forwardRef((props, ref) => {
  const [element_definitions, set_element_definitions] = useState(null);
  const [element_names, set_element_names] = useState(null);
  const [groups, set_groups] = useState({});
  const [group_names, set_group_names] = useState({});
  React.useImperativeHandle(ref, () => ({
    get_config() {
      return props.config;
    },
    get_sobject() {
      return props.sobject;
    },
    validate() {
      return validate();
    }
  }));
  useEffect(() => {
    init();
  }, []);
  const init = async () => {
    let element_names = props.element_names;
    let element_definitions = props.element_definitions;
    if (!element_definitions) {
      config_handler = props.config_handler;
      if (config_handler) {
        element_definitions = await get_element_definitions(config_handler);
      } else {
        if (!element_names) {
          element_names = [];
          props.config.forEach(item => {
            element_names.push(item.name);
          });
        }
        element_definitions = spt.react.Config(props.config, {});
      }
    }
    element_names.forEach(element_name => {
      let definition = props.config;
    });
    let filtered = [];

    element_names.forEach(element_name => {
      let definition = element_definitions[element_name];
      if (!definition) {
        definition = {};
        element_definitions[element_name] = definition;
      }
      if (!definition.name) definition.name = element_name;
      if (!definition.title) definition.title = Common.capitalize(definition.name);
      if (definition.editable == true) {
        filtered.push(element_name);
      }
    });
    if (props.sobject) {
      element_names.forEach(element_name => {
        let definition = element_definitions[element_name];
        let column = element_name;
        definition.value = props.sobject[column];
        definition.sobject = props.sobject;
      });
    }
    set_element_names(filtered);
    set_element_definitions(element_definitions);

    let groups = {};
    let group_names = [];
    filtered.forEach(element_name => {
      let definition = element_definitions[element_name];
      let group_name = definition.group || Common.generate_key();
      let group = groups[group_name];
      if (!group) {
        group = [];
        groups[group_name] = group;
        group_names.push(group_name);
      }
      if (typeof definition.value == "undefined") {
        definition.value = null;
      }
      group.push(definition);
    });
    set_groups(groups);
    set_group_names(group_names);

  };

  const load_data = async () => {
    let cmd = props.get_cmd;
    if (!cmd) {
      alert("Get cmd is not defined");
      return;
    }
    let kwargs = props.get_kwargs || {};
    let config_handler = props.config_handler;
    kwargs["config_handler"] = config_handler;
    if (props.extra_data) {
      Object.keys(props.extra_data).forEach(key => {
        kwargs[key] = props.extra_data[key];
      });
    }
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, kwargs).then(ret => {
      let data = ret.info;
      set_data(data);
    }).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  };
  const get_element_definitions = async (cmd, kwargs) => {
    if (!kwargs) {
      kwargs = {};
    }
    let server = TACTIC.get();
    let ret = await server.p_execute_cmd(cmd, kwargs);
    let info = ret.info;
    let config = info.config;

    let definitions = spt.react.Config(config, {});
    return definitions;
  };
  const validate = () => {
    let config = props.config;
    if (!config) return true;
    let sobject = props.sobject;
    if (!sobject) return true;
    let form_validated = true;
    element_names.forEach(element_name => {
      let definition = element_definitions[element_name];
      if (definition.required == true) {
        let key = definition.column || definition.name;
        if (!sobject[key]) {
          form_validated = false;
          definition.helper = "ERROR";
          definition.error = true;
        }
      }
    });
    set_element_names([...element_names]);
    return form_validated;
  };
  let style = props.style;
  if (!style) {
    style = {
      display: "flex",
      flexDirection: "column",
      gap: "20px",
      margin: "30px 10px"
    };
  }
  return React.createElement("div", {
    className: "spt_edit_form",
    style: style
  }, element_definitions && group_names?.map((group_name, index) => React.createElement("div", {
    className: "spt_edit_form_row",
    style: {
      display: "flex",
      flexDirection: "row",
      gap: "10px"
    }
  }, groups[group_name].map((definition, index) => {
    let editor = definition?.cellEditor;
    if (editor == SelectEditor) {
      return React.createElement(SelectEditorWdg, _extends({
        key: index,
        onchange: onchange
      }, definition));
    } else if (editor == "NotesEditor") {
      return React.createElement(NotesEditorWdg, _extends({
        key: index,
        onchange: onchange
      }, definition));
    } else if (editor == InputEditor) {
      return React.createElement(InputEditorWdg, _extends({
        key: index,
        onchange: onchange
      }, definition));
    } else {
      return React.createElement(InputEditorWdg, _extends({
        key: index,
        onchange: onchange
      }, definition));
    }
  }))));
});
const EditModal = React.forwardRef((props, ref) => {
  const [show, set_show] = useState(false);
  const [item, set_item] = useState({});
  React.useImperativeHandle(ref, () => ({
    show() {
      set_show(true);
    },
    set_item(item) {
      set_item(item);
    }
  }));
  const handleClickOpen = () => {
    set_show(true);
  };
  const handleClose = () => {
    set_show(false);
  };
  const insert = () => {
    if (props.on_insert) props.on_insert(item);
    handleClose();
    set_item({});
  };
  const onchange = e => {
    let name = e.name;
    let value = e.target.value;
    item[name] = value;
  };
  return React.createElement(React.Fragment, null, false && React.createElement(Modal, {
    open: show,
    onClose: e => set_show(false)
  }, React.createElement("div", {
    className: "spt_modal",
    style: {
      width: "60vw",
      height: "fit-content",
      padding: "20px"
    }
  })), React.createElement(Dialog, {
    open: show,
    onClose: handleClose,
    fullWidth: true,
    maxWidth: "sm"
  }, React.createElement(DialogTitle, null, "New ", props.name), React.createElement(DialogContent, null, React.createElement(DialogContentText, null, "Enter the following data for ", props.name), React.createElement(EditForm, _extends({}, props, {
    sobject: item
  }))), React.createElement(DialogActions, null, React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "center",
      gap: "30px",
      width: "100%"
    }
  }, React.createElement(Button, {
    onClick: handleClose
  }, "Cancel"), React.createElement(Button, {
    variant: "contained",
    onClick: e => {
      insert();
    }
  }, "Insert")))));
});
const DeleteModal = React.forwardRef((props, ref) => {
  const [show, set_show] = useState(false);
  const [items, set_items] = useState([]);
  React.useImperativeHandle(ref, () => ({
    show() {
      set_show(true);
    },
    set_items(items) {
      set_items(items);
    }
  }));
  const handleClickOpen = () => {
    set_show(true);
  };
  const handleClose = () => {
    set_show(false);
  };
  const delete_selected = () => {
    if (props.ondelete) {
      props.ondelete(items);
    } else {
      items.reverse();
      let data = props.grid_ref.current.get_data();
      let search_keys = [];
      items.forEach(item => {
        let item_data = item.data;
        search_keys.push(item_data.__search_key__);
        data.splice(item.rowIndex, 1);
      });

      let server = TACTIC.get();
      let cmd = "tactic.react.DeleteCmd";
      let kwargs = {
        search_keys: search_keys
      };
      server.p_execute_cmd(cmd, kwargs).then(ret => {
        props.load_data();
      }).catch(e => {
        alert("TACTIC Error: " + e);
      });
    }
    handleClose();
  };
  return React.createElement(React.Fragment, null, React.createElement(Dialog, {
    open: show,
    onClose: handleClose,
    fullWidth: true,
    maxWidth: "sm"
  }, React.createElement(DialogTitle, null, "Delete Selected Items"), React.createElement(DialogContent, null, React.createElement(DialogContentText, null, React.createElement(Alert, {
    severity: "error"
  }, "Do you wish to delete the following:")), React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "30px",
      margin: "30px 20px"
    }
  }, items.map((item, index) => React.createElement("h3", {
    key: index
  }, item.data.name || "")))), React.createElement(DialogActions, null, React.createElement(Button, {
    onClick: handleClose
  }, "Cancel"), React.createElement(Button, {
    severity: "error",
    onClick: e => {
      delete_selected();
    }
  }, "Delete"))));
});
class SelectEditor {
  init(params) {
    let column = params.colDef?.field;
    let open;
    if (column) {
      this.value = params.data[column] || "";
      open = true;
    } else {
      this.value = params.value;
      open = false;
    }
    let mode = params.mode || "select";
    let labels = params.labels || [];
    let values = params.values || [];
    let helpers = params.helpers || [];
    let colors = params.colors || {};
    let error = params.error;
    if (typeof labels == "string") {
      labels = labels.split("|");
    }
    if (typeof values == "string") {
      values = values.split("|");
    }
    if (typeof helpers == "string") {
      helpers = helpers.split("|");
    }
    let variant = params.variant || "standard";
    let label = params.label || "";
    let name = params.name;
    let layout = params.layout || "column";
    let el_style;
    let style = {
      width: "100%",
      height: "100%"
    };
    if (!params.is_form) {
      el_style = {
        fontSize: "0.75rem",
        padding: "0px 3px",
        width: "100%",
        height: "100%"
      };
    } else {
      el_style = {};
    }
    this.input = document.createElement("div");
    this.input.style.width = "100%";
    this.root = ReactDOM.createRoot(this.input);
    if (mode == "button") {
      this.el = React.createElement("div", {
        style: {
          display: "flex",
          flexDirection: layout,
          gap: "20px"
        }
      }, values.map((value, index) => React.createElement("div", {
        style: {
          width: "100%"
        }
      }, React.createElement(Button, {
        key: index,
        variant: this.value == value ? "contained" : "outlined",
        style: {
          border: error ? "solid 1px red" : ""
        },
        fullWidth: true,
        onClick: e => {
          this.value = value;

          e.name = name;
          if (params.onchange) {
            params.onchange(e, this.value);
          }
        }
      }, React.createElement("div", {
        style: {
          fontSize: "0.8rem"
        }
      }, labels[index])), helpers.length > 0 && React.createElement("div", {
        style: {
          fontSize: "0.7rem",
          margin: "3px"
        }
      }, helpers[index]))));
      return;
    } else if (mode == "checkbox") {
    }
    if (this.value == null) {
    }
    let value = this.value || values[0] || "";
    this.value = value || "";

    this.el = React.createElement(React.Fragment, null, React.createElement(TextField, {
      label: label,
      variant: variant,
      defaultValue: value,
      size: "small",
      select: true,
      style: style,
      SelectProps: {
        defaultOpen: open,
        style: el_style
      },
      onChange: e => {
        this.value = e.target.value;

        e.name = name;
        if (params.onchange) {
          params.onchange(e, this.value);
        }
        if (params.api?.stopEditing) {
          params.api.stopEditing();
        }
      },
      onKeyUp: e => {
        if (e.key == 13) {
          params.api.stopEditing();
          params.api.tabToNextCell();
        }
      }
    }, values.map((v, index) => React.createElement(MenuItem, {
      key: index,
      value: v
    }, React.createElement("div", {
      style: {
        fontSize: "0.8rem"
      }
    }, labels[index])))));
  }
  getEl() {
    return this.el;
  }

  getGui() {
    this.root.render(this.el);
    return this.input;
  }

  getValue() {
    return this.value;
  }

  afterGuiAttached() {}
}
const SelectEditorWdg = props => {
  const [value, set_value] = useState();
  const [label, set_label] = useState();
  const [el, set_el] = useState();
  const [ignored, forceUpdate] = useReducer(x => x + 1, 0);
  useEffect(() => {
    let value = props.value;
    set_value(value);
    let label = props.headerName || props.label || props.title;
    if (label == null || typeof label == "undefined") {
      label = props.field;
    }
    label = Common.capitalize(label);
    set_label(label);
  }, []);
  useEffect(() => {
    if (!props.error) {
      return;
    }
    init();
  }, [props.error]);
  useEffect(() => {
    if (typeof value == "undefined") return;
    init();
  }, [value]);
  const init = () => {
    let name = props.name;
    let mode = props.mode;
    let cellEditorParams = props.cellEditorParams || {};
    let props2 = {
      is_form: true,
      name: name,
      label: "",
      variant: "outlined",
      values: cellEditorParams.values || [],
      labels: cellEditorParams.labels || [],
      helpers: cellEditorParams.helpers || [],
      layout: props.layout,
      onchange: (e, new_value) => {
        set_value(new_value);
        if (props.onchange) {
          props.onchange(e, new_value);
        }
        if (props.sobject) {
          props.sobject[name] = new_value;
        }
      },
      value: value,
      mode: mode,
      error: props.error
    };
    let select = new SelectEditor();
    select.init(props2);
    let el = select.getEl();
    set_el(el);
    forceUpdate();
  };
  return React.createElement("div", {
    style: {
      width: "100%"
    }
  }, props.show_title != false && React.createElement("div", {
    className: "spt_form_label"
  }, label, " ", props.required == true ? "*" : ""), el && React.createElement("div", {
    className: "spt_form_input"
  }, el), props.helper && React.createElement("div", null, props.helper));
};
class InputEditor {
  init(params) {
    this.value = params.value;
    let mode = params.mode || "text";
    this.mode = mode;
    let variant = params.variant || "standard";
    let name = params.name;
    let label = params.label || "";
    let rows = params.rows || 1;
    let helper = params.helper;
    let error = params.error;
    let is_form = params.is_form;
    let el_style;
    let style = {
      width: "100%",
      height: "100%"
    };
    if (!is_form) {
      if (mode == "color") {} else {
        el_style = {
          fontSize: "0.75rem",
          padding: "3px 3px",
          height: "100%",
          width: "100%",
          boxSizing: "border-box"
        };
        style.padding = "0px 15px";
        style.width = "max-width";
      }
    } else {
      el_style = {};
    }
    this.input = document.createElement("div");
    this.input.style.width = "100%";
    this.root = ReactDOM.createRoot(this.input);
    this.el = React.createElement(TextField, {
      label: label,
      variant: variant,
      defaultValue: this.value,
      multiline: rows > 1 ? true : false,
      error: error,
      helperText: helper,
      rows: rows,
      fullWidth: true,
      size: "small",
      type: mode,
      style: style,
      InputProps: {
        disableunderline: true
      },
      inputProps: {
        className: "input",
        style: el_style
      },
      onChange: e => {
        this.value = e.target.value;

        e.name = name;
        if (params.onchange) {
          params.onchange(e, this.value);
        }
      },
      onBlur: e => {
        if (params.api?.stopEditing) {
          params.api.stopEditing();
        }
      },
      onKeyUp: e => {
        this.value = e.target.value;
        if (e.code == "Tab" && params.api) {
          params.api.tabToNextCell();
        } else if (e.code == "Enter" && params.api) {
          params.api.stopEditing();
        }
      }
    });
  }
  getEl() {
    return this.el;
  }
  getGui() {
    this.root.render(this.el);
    return this.input;
  }

  getValue() {
    if (this.mode == "date") {
      this.value = Date.parse(this.value);
    }
    return this.value;
  }

  afterGuiAttached() {
    setTimeout(() => {
      let x = document.id(this.input);
      let input = x.getElement(".input");
      input.focus();
    }, 250);
  }
}
const InputEditorWdg = props => {
  const [value, set_value] = useState();
  let cellEditorParams = props.cellEditorParams || {};
  let label = props.label || props.headerName || props.field || props.name;
  label = Common.capitalize(label);
  let props2 = {
    is_form: true,
    name: props.name,
    label: "",
    rows: props.rows,
    variant: "outlined",
    mode: cellEditorParams.mode,
    onchange: (e, new_value) => {
      set_value(new_value);
      if (props.sobject) {
        props.sobject[props.name] = new_value;
      }
      if (props.onchange) {
        props.onchange(e, new_value);
      }
    },
    value: props.value,
    helper: props.helper,
    error: props.error
  };
  let input = new InputEditor();
  input.init(props2);
  let el = input.getEl();
  return React.createElement("div", {
    style: {
      width: "100%"
    }
  }, React.createElement("div", {
    className: "spt_form_label"
  }, label, props.required == true ? " *" : ""), React.createElement("div", {
    className: "spt_form_input"
  }, el));
};
const SimpleCellRenderer = params => {
  let value = params.value;
  let label = value;
  let onClick = params.onClick;
  let onclick = params.onclick;
  let mode = params.mode;
  let renderer = params.renderer;
  let editable = params.colDef.editable;
  if (label == null) {
    label = "";
  }
  if (mode == "date") {
    try {
      let date = Date.parse(value);
      let day = date.getDate() + "";
      let month = date.getMonth() + 1 + "";
      let year = date.getFullYear() + "";
      label = year + "-" + month.padStart(2, "0") + "-" + day.padStart(2, "0");
    } catch (e) {
      label = "";
    }
  } else if (mode == "%") {
    try {
      let display_value = value * 100;
      label = display_value + "%";
    } catch (e) {
      label = "";
    }
  } else if (mode == "$") {
    function numberWithCommasAndDecimals(x) {
      const parts = x.toString().split(".");
      parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      return parts.join(".");
    }
    try {
      label = "$" + numberWithCommasAndDecimals(value);
    } catch (e) {
      label = "";
    }
  } else {
    let values = params.values;
    if (values != null) {
      let labels = params.labels;
      let index = values.indexOf(value);
      if (index != -1) {
        label = labels[index];
      }
    }
  }
  let colors = params.colors || {};

  let el = document.createElement("div");
  let inner;
  if (renderer) {
    inner = renderer(params);
    el.appendChild(inner);
  } else {
    inner = document.createElement("div");
    el.appendChild(inner);
    inner.style.width = "100%";
    inner.style.height = "100%";
    inner.style.padding = "0px 3px";
    inner.style.whiteSpace = "normal";

    if (params.mode == "color") {
      inner.style.background = value;
    }
    let color = colors[value];
    if (color) {
      inner.style.background = color;
    }
    if (label == "") label = "&nbsp;";
    inner.appendChild(document.createTextNode(label));
    if (onClick || onclick) {
      inner.style.textDecoration = "underline";
      inner.style.cursor = "pointer";

      inner.addEventListener("click", e => {
        if (onclick) onclick(params);
        if (onClick) onClick(params);
      });
    }
  }

  if (editable) {
    let icon = document.createElement("i");
    el.appendChild(icon);
    icon.classList.add("fas");
    icon.classList.add("fa-edit");
    icon.classList.add("btn");
    icon.classList.add("btn-default");
    icon.style.display = "none";
    icon.style.position = "absolute";
    icon.style.opacity = 0.4;
    icon.style.right = "-5px";
    icon.style.top = "-3px";
    icon.style.fontSize = "0.8rem";
    icon.addEventListener("click", e => {
      params.api.startEditingCell({
        rowIndex: params.rowIndex,
        colKey: params.colDef.field
      });
      e.stopPropagation();
    });
    el.addEventListener("mouseenter", e => {
      icon.style.display = "";
    });
    el.addEventListener("mouseleave", e => {
      icon.style.display = "none";
    });
  } else {
    let icon = document.createElement("i");
    el.appendChild(icon);
    icon.classList.add("fas");
    icon.classList.add("fa-ban");
    icon.classList.add("btn");
    icon.classList.add("btn-link");
    icon.style.display = "none";
    icon.style.position = "absolute";
    icon.style.opacity = 0.4;
    icon.style.right = "-5px";
    icon.style.top = "-3px";
    icon.style.fontSize = "0.8rem";
    el.addEventListener("mouseenter", e => {
      icon.style.display = "";
    });
    el.addEventListener("mouseleave", e => {
      icon.style.display = "none";
    });
  }
  return el;
};
const PreviewCellRenderer = props => {
  let data = props.data;
  let cell = props.eGridCell;
  let column = props.column.colId;
  let root = cell.root;
  if (!root) {
    root = ReactDOM.createRoot(cell);
    cell.root = root;
  }
  let src = "/plugins/spt/modules/workflow/apps/Resource/media/materials.png";
  let el = React.createElement("div", null, React.createElement("img", {
    style: {
      width: "auto",
      height: "100%"
    },
    src: src
  }));
  return root.render(el);
};
const ColumnManagerMenu = React.forwardRef((props, ref) => {
  const [column_anchorEl, column_setAnchorEl] = React.useState(null);
  const column_is_open = Boolean(column_anchorEl);
  let column_create_ref = useRef();
  const column_handle_click = event => {
    column_setAnchorEl(event.currentTarget);
  };
  const column_handle_close = async () => {
    column_setAnchorEl(null);
  };
  const column_handle_select = async column => {
    let index = props.columns.indexOf(column);
    if (index == -1) {
      props.columns.push(column);
    } else {
      props.columns.splice(index, 1);
    }
    if (props.update) {
      props.update();
    }
  };
  const get_column_menu = () => {
    return React.createElement(React.Fragment, null, React.createElement(Button, {
      variant: "outlined",
      id: "column-button",
      onClick: column_handle_click,
      title: "Column Manager"
    }, React.createElement("i", {
      className: "fas fa-columns"
    }), "\xA0", React.createElement("i", {
      className: "fa-xs fas fa-caret-down"
    })), React.createElement(Menu, {
      id: "column-menu",
      anchorEl: column_anchorEl,
      open: column_is_open,
      onClose: column_handle_close,
      MenuListProps: {
        'aria-labelledby': 'column-menu'
      }
    }, React.createElement(MenuItem, {
      value: "custom",
      onClick: e => {
        props.property_modal_ref.current.show();
      },
      style: {
        height: "40px"
      }
    }, "Custom"), React.createElement("hr", null), props.all_columns.map((column, index) => React.createElement(MenuItem, {
      key: index,
      value: column,
      onClick: e => {
        column_handle_select(column);
      },
      style: {
        height: "30px"
      }
    }, React.createElement(Checkbox, {
      checked: props.columns.includes(column)
    }), Common.capitalize(column)))));
  };
  return React.createElement(React.Fragment, null, React.createElement(ColumnCreateModal, {
    ref: column_create_ref
  }), get_column_menu());
});
const ColumnCreateModal = React.forwardRef((props, ref) => {
  const [show, set_show] = useState(false);
  const [item, set_item] = useState({});
  React.useImperativeHandle(ref, () => ({
    show() {
      set_show(true);
    },
    set_item(item) {
      set_item(item);
    }
  }));
  const handleClickOpen = () => {
    set_show(true);
  };
  const handleClose = () => {
    set_show(false);
  };
  const create = () => {
    alert("CREATE");
  };
  return React.createElement(React.Fragment, null, React.createElement(Dialog, {
    open: show,
    onClose: handleClose,
    fullWidth: true,
    maxWidth: "sm"
  }, React.createElement(DialogTitle, null, "Create Custom Column"), React.createElement(DialogContent, null, React.createElement(DialogContentText, null, "Enter the properties for custom column"), React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "20px",
      margin: "20px 0px"
    }
  })), React.createElement(DialogActions, null, React.createElement(Button, {
    onClick: handleClose
  }, "Cancel"), React.createElement(Button, {
    onClick: e => {
      create();
    }
  }, "Create"))));
});

spt.react.TableLayout = TableLayout;
spt.react.EditForm = EditForm;
spt.react.EditModal = EditModal;
spt.react.SelectEditor = SelectEditor;
spt.react.InputEditor = InputEditor;
spt.react.SimpleCellRenderer = SimpleCellRenderer;
spt.react.PreviewCellRenderer = PreviewCellRenderer;