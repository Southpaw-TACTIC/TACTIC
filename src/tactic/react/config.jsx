const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;

const Common = spt.react.Common;
const SelectEditor = spt.react.SelectEditor;
const InputEditor = spt.react.InputEditor;
const SimpleCellRenderer = spt.react.SimpleCellRenderer;
const PreviewCellRenderer = spt.react.PreviewCellRenderer;


// default save implementation
const on_cell_value_changed = params => {
    //console.log("params: ", params);
    let table_ref = params.table_ref;
    let data = params.data;
    let column = params.column.colId;
    table_ref.current.save(data, column);
}



const Xon_cell_value_changed = params => {

    let table_ref = params.table_ref;

    let item = params.data;
    let column = params.column.colId;


    //let selected = grid_ref.current.get_selected_nodes();
    let selected = [];
    let items = [];
    if (selected.length) {
        selected.forEach( selected_item => {
            items.push(selected_item.data);
        } )
    }
    else {
        items.push(item);
    }


    //let cmd = params.save_cmd;
    let cmd = "tactic.react.TableSaveCmd";

    // FIXME: should call save cmd just once
    updates = [];
    items.forEach( item => {
        let mode = item.code ? "edit" : "insert";
        let update = {
            search_key: item.__search_key__,
            column: column,
        };
        updates.push(update);
    } )


    let kwargs = {
        updates: updates
    }

    let server = TACTIC.get();
    server.p_execute_cmd(cmd, kwargs)
    .then( ret => {
        // TODO: refresh nodes
    } )
    .catch( e => {
        alert("TACTIC ERROR: " + e);
    } )
}



const Config = (config, options) => {

    let cell_value_changed = options.cell_value_changed;

    if (!cell_value_changed) {
        cell_value_changed = on_cell_value_changed;
    }

    let table_ref = options.table_ref;



    // use these definition types as a starting point
    let definition_types = {
        simple: {
            width: 150,
            resizable: true,
            onCellValueChanged: cell_value_changed,
            cellRenderer: SimpleCellRenderer,
        },
        preview: {
            width: 60,
            resizable: true,
            cellRenderer: PreviewCellRenderer,
        },
        select: {
            width: 150,
            editable: true,
            resizable: true,
            onCellValueChanged: cell_value_changed,
            cellEditor: SelectEditor,
            cellRenderer: SimpleCellRenderer,
        }
    }


    // convert to config_def data
    let config_defs = {};
    config.forEach(config_item => {

        let element_type = config_item.type;
        let definition_type = element_type;
        if (element_type == "number") {
            definition_type = "simple";
        }
        else if (element_type == "color") {
            definition_type = "simple";
        }
        else if (element_type == "date") {
            definition_type = "simple";
        }
        else if (element_type == "text") {
            definition_type = "simple";
        }




        let name = config_item.name;
        let title = config_item.title;
        let pinned = config_item.pinned;
        let width = config_item.width;

        if (!name) {
            throw("No name provided in config")
        }

        let config_def = {...definition_types[definition_type]};
        config_defs[name] = config_def;

        config_def["resizable"] = true;

        config_def["field"] = name;
        if (title) {
            config_def["headerName"] = title;
        }
        else {
            config_def["headerName"] = Common.capitalize(name);
        }

        if (pinned) {
            config_def["pinned"] = pinned;
        }

        if (width) {
            config_def["width"] = width;
        }

        if (element_type == "select") {
            let labels = config_item.labels;
            let values = config_item.values || [];
            if (!labels) {
                labels = values;
            }

            if (typeof(labels) == "string" ) {
                labels = labels.split(",")
            }
            if (typeof(values) == "string" ) {
                values = values.split(",")
            }


            let params = {
                table_ref: table_ref,
                labels: labels,
                values: values,
            }

            config_def.cellEditor = SelectEditor;
            config_def.cellEditorParams = params;
            config_def.cellRendererParams = params;

            config_def.editable = true;

            //config_def.onCellValueChanged = cell_value_changed;
            config_def.onCellValueChanged = e => {
                let p = {...e, ...params}
                return cell_value_changed(p);
            }

        }
        else {
            let format = config_item.format;
            if (element_type == "number") {
                format = "number";
            }
            else if (element_type == "color") {
                format = "color";
            }
            else if (element_type == "date") {
                format = "date";
            }


            let params = {
                table_ref: table_ref,
                mode: format
            }

            let editable = config_item.editable;
            if (editable) {
                config_def.editable = true;
                if (format) {
                    config_def.cellDataType = format;
                }
                config_def.cellEditor = InputEditor;
                config_def.cellEditorParams = params;
                config_def.onCellValueChanged = e => {
                    let p = {...e, ...params}
                    return cell_value_changed(p);
                }
            }
            else {
                config_def.editable = false;
            }
            config_def.cellRendererParams = params;
        }

    } );

    return config_defs;

}


// Store this
spt.react.Config = Config;




