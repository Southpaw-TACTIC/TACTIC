"use strict";

function _extends() { _extends = Object.assign ? Object.assign.bind() : function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; }; return _extends.apply(this, arguments); }
const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;
const Box = MaterialUI.Box;
const Button = MaterialUI.Button;
const Modal = MaterialUI.Modal;
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
    }
  }));
  const [search_type, set_search_type] = useState("");
  const [data, set_data] = useState([]);
  const [element_names, set_element_names] = useState([]);
  const [column_defs, set_column_defs] = useState([]);
  const edit_modal_ref = useRef();
  const property_modal_ref = useRef();
  const grid_ref = useRef();
  useEffect(() => {
    let element_names = props.element_names;
    set_element_names([...element_names]);
    set_search_type(props.search_type);
    build_column_defs(element_names);
    let cmd = props.get_cmd;
    let kwargs = props.get_kwargs;
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, kwargs).then(ret => {
      let data = ret.info;
      set_data(data);
    }).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  }, []);
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
      let new_sobjects = info.new_sobjects;
      new_sobjects.forEach(item => {
        data.push(item);
      });
      set_data([...data]);
    }).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  };
  const insert_item = item => {
    let cmd = props.save_cmd;
    if (!cmd) {
      cmd = "tactic.react.EditSaveCmd";
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
      sobjects.forEach(item => {
        data.push(item);
      });
      set_data([...data]);
    }).catch(e => {
      alert("TACTIC ERROR: " + e);
    });
  };
  const cell_value_changed = props => {
    let column = props.colDef.field;
    let data = props.data;
    save(data, column);
  };
  const build_column_defs = new_element_names => {
    let column_defs = props.column_defs;
    if (column_defs) {
      return column_defs;
    }
    if (!new_element_names) {
      new_element_names = element_names;
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
      let column_def = props.element_definitions[element];
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
  const get_shelf = () => {
    return React.createElement(React.Fragment, null, React.createElement(EditModal, {
      name: props.name,
      ref: edit_modal_ref,
      on_insert: insert_item,
      element_names: props.element_names,
      element_definitions: props.element_definitions
    }), React.createElement(EditModal, {
      name: "Custom Property",
      ref: property_modal_ref,
      on_insert: property_save,
      element_names: property_names,
      element_definitions: property_definitions
    }), React.createElement("div", {
      style: {
        display: "flex",
        gap: "15px"
      }
    }, props.element_names && React.createElement(ColumnManagerMenu, {
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
    }, "Filter"), React.createElement(Button, {
      size: "small",
      variant: "contained",
      onClick: e => {
        let selected = grid_ref.current.get_selected_nodes();
        if (selected.length == 0) {
          alert("No items selected");
          return;
        }
        let data = selected[0].data;
        edit_modal_ref.current.set_item(data);
        edit_modal_ref.current.show();
      }
    }, "Edit"), React.createElement(Button, {
      size: "small",
      variant: "contained",
      onClick: e => {
        edit_modal_ref.current.show();
      }
    }, "New ", props.name)));
  };
  return React.createElement("div", null, React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between"
    }
  }, React.createElement("div", {
    style: {
      fontSize: "1.2rem"
    }
  }, props.name, " List"), get_shelf()), React.createElement(DataGrid, {
    ref: grid_ref,
    name: props.name,
    column_defs: column_defs,
    data: data,
    supress_click: true,
    auto_height: true,
    row_height: props.row_height,
    enable_undo: props.enable_undo
  }));
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
  }, React.createElement(DialogTitle, null, "New ", props.name), React.createElement(DialogContent, null, React.createElement(DialogContentText, null, "Enter the following data for ", props.name), React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "30px",
      margin: "30px 0px"
    }
  }, props.element_names?.map((element_name, index) => {
    let definition = props.element_definitions && props.element_definitions[element_name];
    if (!definition) definition = {};
    if (!definition.name) definition.name = element_name;
    if (!definition.title) definition.title = Common.capitalize(element_name);
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
    return React.createElement(TextField, {
      key: index,
      label: Common.capitalize(element_name),
      size: "small",
      variant: "outlined",
      defaultValue: item[element_name],
      onChange: e => {
        item[element_name] = e.target.value;
      }
    });
  }))), React.createElement(DialogActions, null, React.createElement(Button, {
    onClick: handleClose
  }, "Cancel"), React.createElement(Button, {
    onClick: e => {
      insert();
    }
  }, "Insert"))));
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
    let labels = params.labels || [];
    let values = params.values || [];
    let colors = params.colors || {};
    if (typeof labels == "string") {
      labels = labels.split("|");
    }
    if (typeof values == "string") {
      values = values.split("|");
    }
    let variant = params.variant || "standard";
    let label = params.label || "";
    let name = params.name;
    let el_style;
    if (!params.is_form) {
      el_style = {
        fontSize: "0.75rem",
        padding: "0px 3px",
        width: "100%",
        height: "40px"
      };
    } else {
      el_style = null;
    }
    this.input = document.createElement("div");
    this.root = ReactDOM.createRoot(this.input);
    this.el = React.createElement("div", null, React.createElement(TextField, {
      label: label,
      variant: variant,
      defaultValue: this.value,
      size: "small",
      select: true,
      style: {
        width: "100%",
        height: "100%",
        padding: "0px 15px",
        fontSize: "0.8rem"
      },
      SelectProps: {
        defaultOpen: open,
        style: el_style
      },
      onChange: e => {
        this.value = e.target.value;
        e.name = name;
        if (params.onchange) {
          params.onchange(e);
        }
      },
      onKeyUp: e => {
        if (e.key == 13) {
          params.api.stopEditing();
          params.api.tabToNextCell();
        }
      }
    }, values.map((value, index) => React.createElement(MenuItem, {
      key: index,
      value: value
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
  let cellEditorParams = props.cellEditorParams || {};
  let label = props.label || props.field;
  label = Common.capitalize(label);
  let name = props.name;
  let props2 = {
    is_form: true,
    name: name,
    label: label,
    variant: "outlined",
    values: cellEditorParams.values || [],
    labels: cellEditorParams.labels || [],
    onchange: props.onchange
  };
  let select = new SelectEditor();
  select.init(props2);
  let el = select.getEl();
  return React.createElement("div", null, el);
};
class InputEditor {
  init(params) {
    this.value = params.value;
    let mode = params.mode || "text";
    this.mode = mode;
    let variant = params.variant || "standard";
    let name = params.name;
    let label = params.label || "";
    let is_form = params.is_form;
    let el_style;
    let style = {
      width: "100%",
      height: "100%"
    };
    if (!is_form) {
      el_style = {
        fontSize: "0.75rem",
        padding: "3px 3px"
      };
      style.padding = "0px 15px";
    } else {
      el_style = {};
    }
    this.input = document.createElement("div");
    this.root = ReactDOM.createRoot(this.input);
    this.el = React.createElement("div", null, React.createElement(TextField, {
      label: label,
      variant: variant,
      defaultValue: this.value,
      size: "small",
      type: mode,
      style: style,
      inputProps: {
        className: "input",
        style: el_style
      },
      onChange: e => {
        this.value = e.target.value;
        e.name = name;
        if (params.onchange) {
          params.onchange(e);
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
    }));
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
  let cellEditorParams = props.cellEditorParams || {};
  let label = props.label || props.field || props.name;
  label = Common.capitalize(label);
  let props2 = {
    is_form: true,
    name: props.name,
    label: label,
    variant: "outlined",
    mode: cellEditorParams.mode,
    onchange: props.onchange
  };
  let input = new InputEditor();
  input.init(props2);
  let el = input.getEl();
  return React.createElement("div", null, el);
};
const SimpleCellRenderer = params => {
  let value = params.value;
  let label = value;
  if (label == null) {
    label = "";
  }
  let mode = params.mode;
  let onClick = params.onClick;
  let values = params.values;
  if (values != null) {
    let labels = params.labels;
    let index = values.indexOf(value);
    if (index != -1) {
      label = labels[index];
    }
  }
  let colors = params.colors || {};
  let el = document.createElement("div");
  el.setAttribute("class", "resource-cell");
  let inner = document.createElement("div");
  el.appendChild(inner);
  inner.style.width = "100%";
  inner.style.padding = "0px 3px";
  if (true) {
    let icon = document.createElement("i");
    el.appendChild(icon);
    icon.classList.add("fas");
    icon.classList.add("fa-edit");
    icon.classList.add("btn");
    icon.classList.add("btn-default");
    icon.style.display = "none";
    icon.style.position = "absolute";
    icon.style.opacity = 0.4;
    icon.style.right = "5px";
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
  }
  if (params.mode == "color") {
    inner.style.background = value;
  }
  let color = colors[value];
  if (color) {
    inner.style.background = color;
  }
  if (typeof value != "undefined") {
    inner.appendChild(document.createTextNode(label));
    if (onClick) {
      inner.style.textDecoration = "underline";
      inner.style.cursor = "pointer";
      inner.addEventListener("click", e => {
        onClick(params);
      });
    }
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
spt.react.EditModal = EditModal;
spt.react.SelectEditor = SelectEditor;
spt.react.InputEditor = InputEditor;
spt.react.SimpleCellRenderer = SimpleCellRenderer;
spt.react.PreviewCellRenderer = PreviewCellRenderer;