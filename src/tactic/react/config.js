"use strict";

const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;
const SelectEditor = spt.react.SelectEditor;
const InputEditor = spt.react.InputEditor;
const SimpleCellRenderer = spt.react.SimpleCellRenderer;
const PreviewCellRenderer = spt.react.PreviewCellRenderer;
const Config = (config, options) => {
  let cell_value_changed = options.cell_value_changed;

  let definition_types = {
    simple: {
      width: 150,
      onCellValueChanged: cell_value_changed,
      cellRenderer: SimpleCellRenderer
    },
    preview: {
      width: 60,
      cellRenderer: PreviewCellRenderer
    },
    select: {
      width: 150,
      editable: true,
      onCellValueChanged: cell_value_changed,
      cellEditor: SelectEditor,
      cellRenderer: SimpleCellRenderer
    }
  };

  let config_defs = {};
  config.forEach(config_item => {
    let element_type = config_item.type;
    if (!element_type) {
      element_type = "simple";
    }
    if (element_type == "number") {
      element_type = "simple";
    }
    let name = config_item.name;
    let title = config_item.title;
    let pinned = config_item.pinned;
    let width = config_item.width;
    let config_def = {
      ...definition_types[element_type]
    };
    config_defs[name] = config_def;
    config_def["resizable"] = true;
    config_def["field"] = name;
    if (title) {
      config_def["headerName"] = title;
    }
    if (pinned) {
      config_def["pinned"] = pinned;
    }
    if (width) {
      config_def["width"] = width;
    }
    if (element_type == "select") {
      let params = {
        labels: config_item.labels || [],
        values: config_item.values || []
      };
      config_def.cellEditorParams = params;
      config_def.cellRendererParams = params;
      config_def.editable = true;
      config_def.onCellValueChanged = cell_value_changed;
    } else {
      let format = config_item.format;
      if (element_type == "number") {
        format = "number";
      }
      let params = {
        mode: format
      };
      let editable = config_item.editable;
      if (editable) {
        config_def.editable = true;
        if (format) {
          config_def.cellDataType = format;
        }
        config_def.cellEditor = InputEditor;
        config_def.cellEditorParams = params;
        config_def.onCellValueChanged = cell_value_changed;
      } else {
        config_def.editable = false;
      }
      config_def.cellRendererParams = params;
    }
  });
  return config_defs;
};

spt.react.Config = Config;