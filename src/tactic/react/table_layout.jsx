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




const TableLayout = React.forwardRef( (props, ref) => {

    React.useImperativeHandle( ref, () => ({
        save(item, column) {
            save(item, column)
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

        get_selected_nodes() {
            return grid_ref.current.get_selected_nodes();
        },
        get_selected_rows() {
           return  grid_ref.current.get_selected_rows();
        },

        show_total() {
           return  grid_ref.current.show_total();
        },

    } ) )

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

    useEffect( () => {
        init();
    }, [] );


    const init = async () => {
        let element_names = props.element_names || ["code"];
        set_element_names([...element_names]);

        let element_definitions = props.element_definitions;
        if (!element_definitions) {
            config_handler = props.config_handler;
            element_definitions = await get_element_definitions(config_handler);
        }
        await set_element_definitions(element_definitions);

        set_search_type(props.search_type);

        build_column_defs(element_names, element_definitions);

        await load_data();

    }


    const load_data = async() => {

        let cmd = props.get_cmd;
        if (!cmd) {
            alert("Get cmd is not defined");
            return;
        }
        let kwargs = props.get_kwargs || {};
        let config_handler = props.config_handler;

        kwargs["config_handler"] = config_handler;


        set_loading(true);

        let server = TACTIC.get();
        server.p_execute_cmd(cmd, kwargs)
        .then( ret => {
            let data = ret.info;
            set_data(data);
            set_loading(false);
            set_first_load(false);

        } )
        .catch( e => {
            set_loading(false);
            alert("TACTIC ERROR: " + e);
        } )
    }


    const get_element_definitions = async (cmd, kwargs) => {

        if (!kwargs) {
            kwargs = {};
        }

        let server = TACTIC.get();
        let ret = await server.p_execute_cmd( cmd, kwargs )
        let info = ret.info;
        let config = info.config;
        let renderer_params = info.renderer_params;

        // convert to AGgrid definitions
        let definitions = spt.react.Config(config, {
            table_ref: ref,
            renderer_params: props.renderer_params || renderer_params
        });

        return definitions;
    }





    const save = (item, column) => {

        //console.log("table: ", item, column)

        let selected = grid_ref.current.get_selected_nodes();

        let items = [];
        if (selected.length) {
            selected.forEach( selected_item => {
                items.push(selected_item.data);
            } )
        }
        else {
            items.push(item);
        }


        let cmd = props.save_cmd;
        if (!cmd) {
            cmd = "tactic.react.TableSaveCmd";
        }


        let updates = [];
        let inserts = [];
        items.forEach( item => {
            let mode = item.code ? "edit" : "insert";

            let update = {
                search_key: item.__search_key__,
                column: column,
                value: item[column],
                mode: mode,
            };

            if (mode == "insert") {
                inserts.push(item)
            }

            updates.push(update);

        } )


        let kwargs = {
            updates: updates,
            config_handler: props.config_handler,
        }


        let server = TACTIC.get();
        server.p_execute_cmd(cmd, kwargs)
        .then( ret => {

            let info = ret.info;
            let updated_sobjects = info.updated_sobjects;
            let new_sobjects = info.new_sobjects || [];

            // add the new items
            new_sobjects.forEach( item => {
                data.push(item);
            } )
            //grid_ref.current.refresh_rows();

        } )
        .catch( e => {
            alert("TACTIC ERROR: " + e);
        } )
    }



    const insert_item = (item) => {

        //console.log("table: ", item, column)

        let cmd = props.save_cmd;
        if (!cmd) {
            //cmd = "tactic.react.EditSaveCmd";
            cmd = "tactic.react.TableSaveCmd"; // use the same save command for everythhing
        }


        let inserts = [];

        let mode = item.__search_key__ ? "edit" : "insert";

        let code = Common.generate_key(12);
        item.code = code;


        let update = {
            search_type: search_type,
            search_key: item.__search_key__,
            mode: mode,
            item: item,
        };

        if (mode == "insert") {
            inserts.push(item)
        }

        let kwargs = {
            updates: [update],
            extra_data: props.extra_data,
            config_handler: props.config_handler,
        }


        let server = TACTIC.get();
        server.p_execute_cmd(cmd, kwargs)
        .then( ret => {

            let info = ret.info;
            let sobjects = info.sobjects || [];

            /*
            // add the new items
            sobjects.forEach( item => {
                data.push(item);
            } )
            set_data([...data]);
            */

            // Brute force
            load_data();

        } )
        .catch( e => {
            alert("TACTIC ERROR: " + e);
        } )
    }

 
    const cell_value_changed = props => {
        let column = props.colDef.field;
        let data = props.data;
        save(data, column);
    }


    const column_moved = () => {
    }




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


        column_defs = [
            { field: '', maxWidth: 50,
                headerCheckboxSelection: true,
                headerCheckboxSelectionFilteredOnly: true,
                checkboxSelection: true,
                pinned: "left",
            },
        ]


        new_element_names.forEach( element => {
            let column_def;
            try {
                column_def = definitions[element];
            } catch(e) {}

            if (!column_def) {
                column_def = {
                    field: element,
                    headerName: Common.capitalize(element),
                    maxWidth: 150,
                    editable: true,
                    onCellValueChanged: cell_value_changed,
                    cellRenderer: SimpleCellRenderer,
                }
            }
            column_defs.push(column_def);
        } )

        set_column_defs(column_defs);
    }





    let property_names = ["title", "name", "type", "width"];
    let property_definitions = {
        title: {
        },
        name: {
        },
        type: {
        },
        width: {
            "type": "number"
        }

    }

    const property_save = (item, column) => {
        let save_cmd = ROOT_CMD + ".TableCreatePropertyCmd";
        let kwargs = {
            name: props.name,
            item: item,
            column: column
        }

        let server = TACTIC.get();
        server.execute_cmd( save_cmd, kwargs )
        .then( ret => {
        } )
        .catch( e => {
            alert("TACTIC ERROR: " + e);
        } )
    }


    //
    // Import Data
    //
    const [import_options, set_import_options] = useState({
        search_type: props.search_type
    } )
    const get_import_data_modal = () => {

        let cmd = props.import_cmd;
        if (!cmd) {
            cmd = ROOT_CMD + ".ImportDataCmd";
        }
        return (
            <spt.react.ImportDataModal
                ref={import_data_modal_ref}
                kwargs={import_options}
                cmd={cmd}
                reload={ () => {
                    load_data();
                } }
                elements={{
                    help: props.elements?.import_help
                }}
            />
        )
    }
    const show_import_data_modal = async () => {
        await set_import_options( {...import_options} );
        import_data_modal_ref.current.show();
    }




    on_select = (selected) => {
    }



    const get_shelf = () => {
        return (
        <>
            <EditModal
                name={props.name}
                ref={edit_modal_ref}
                on_insert={insert_item}
                element_names={props.element_names}
                element_definitions={element_definitions}
            />

            <EditModal
                name={"Custom Property"}
                ref={property_modal_ref}
                on_insert={property_save}
                element_names={property_names}
                element_definitions={property_definitions}
            />


            <DeleteModal
                name={"Delete"}
                ref={delete_modal_ref}
                grid_ref={grid_ref}
                //ondelete={ e => {alert("delete")}}
                element_names={property_names}
                element_definitions={property_definitions}
                load_data={load_data}
            />


            { get_import_data_modal() }



            <div style={{display: "flex", gap: "15px", alignItems: "center"}}>

                { props.get_shelf && props.get_shelf() }


                { props.element_names &&
                <ColumnManagerMenu
                    all_columns={props.all_element_names || props.element_names}
                    columns={element_names}
                    update={build_column_defs}
                    property_modal_ref={property_modal_ref}
                />
                }

                { false &&
                <Button
                    size="small"
                    variant="contained"
                    onClick={ e => {
                        grid_ref.current.set_filter("director", "Jil");
                    } }
                >Filter
                </Button>
                }

                <TableLayoutActionMenu
                    grid_ref={grid_ref}
                    edit_modal_ref={edit_modal_ref}
                    delete_modal_ref={delete_modal_ref}
                    import_data_modal_ref={import_data_modal_ref}
                    on_import={load_data}
                    import_cmd={props.import_cmd }
                    action_menu_items={props.action_menu_items}
                />

            </div>
        </>
        )
    }


    const get_name = () => {

        if (props.name) {
            return props.name;
        }
        else {
            return "TABLE"
        }
    }


    let EmptyWdg = props.empty_wdg;

    return (
    <div>
        { props.show_shelf != false &&
        <div style={{display: "flex", justifyContent: "space-between"}}>
            <div style={{fontSize: "1.2rem"}}>{get_name()}</div>
            { get_shelf() }
        </div>
        }

        { (!first_load && !loading && props.empty_wdg && data?.length == 0) ?
            <div>
                <EmptyWdg
                    edit_modal_ref={edit_modal_ref}
                    import_data_modal_ref={import_data_modal_ref}
                />
            </div>
        :
            <>
            { !loading ?
            <DataGrid
                ref={grid_ref}
                name={get_name()}
                column_defs={column_defs}
                data={data}
                supress_click={true}
                auto_height={props.auto_height}
                height={props.height}
                row_height={props.row_height}
                enable_undo={props.enable_undo}
                on_column_moved={props.on_column_moved}
            />
            :
                <div>Loading ...</div>
            }
            </>
        }
    </div>
    )

} )



const TableLayoutActionMenu = props => {

    //
    // Action Menu
    //
    const [action_anchorEl, action_setAnchorEl] = React.useState(null);
    const action_is_open = Boolean(action_anchorEl);

    const action_handle_click = (event) => {
        action_setAnchorEl(event.currentTarget);
    };
    const action_handle_close =  async () => {
        action_setAnchorEl(null);
    }
    const action_handle_select = async () => {
        action_setAnchorEl(null);
    };



    const open_edit_modal = () => {
        let selected = props.grid_ref.current.get_selected_nodes();
        if (selected.length == 0) {
            alert("No items selected")
            return;
        }
        let data = selected[0].data;

        props.edit_modal_ref.current.set_item(data);
        props.edit_modal_ref.current.show()
    }




    return (
    <div style={{marginRight: "5px"}}>
      <Button
        variant="outlined"
        id="action-button"
        onClick={action_handle_click}
      >
        ACTION
        <i className="fa-xs fas fa-caret-down"></i>
      </Button>
      <Menu
        id="action-menu"
        anchorEl={action_anchorEl}
        open={action_is_open}
        onClose={action_handle_close}
      >

        <MenuItem onClick={e => {
            action_handle_select();
            props.on_import();
        }}>Reload</MenuItem>


        <MenuItem onClick={e => {
            action_handle_select();
            props.edit_modal_ref.current.show()
        }}>New</MenuItem>


        <MenuItem onClick={e => {
            action_handle_select();
            open_edit_modal()
        }}>Edit Selected</MenuItem>


        { props.import_cmd &&
        <MenuItem onClick={e => {
            action_handle_select();
            props.import_data_modal_ref.current.show();
        }}>Import Data</MenuItem>
        }



        <MenuItem onClick={e => {
            action_handle_select();
            props.grid_ref.current.export_csv();
        }}>Export CSV</MenuItem>

        <hr/>

        <MenuItem onClick={e => {
            action_handle_select();
            let selected = props.grid_ref.current.get_selected_nodes();
            props.delete_modal_ref.current.set_items(selected)
            props.delete_modal_ref.current.show()
        }}>Delete Selected</MenuItem>


        { props.action_menu_items &&
            <>
            <hr/>
            { props.action_menu_items({close: action_handle_select}) }
            </>
        }


      </Menu>
    </div>
    )

}



const EditForm = React.forwardRef( (props, ref) => {

    const [element_definitions, set_element_definitions] = useState(null);
    const [element_names, set_element_names] = useState(null);

    const [groups, set_groups] = useState({});
    const [group_names, set_group_names] = useState({});



    React.useImperativeHandle( ref, () => ({
        get_config() {
            return props.config;
        },
        get_sobject() {
            return props.sobject;
        },
        validate() {
            return validate();
        }
    } ) )

    useEffect( () => {
        init();
    }, [] )


    const init = async () => {

        let element_names = props.element_names;

        let element_definitions = props.element_definitions;
        if (!element_definitions) {
            config_handler = props.config_handler;
            if (config_handler) {
                element_definitions = await get_element_definitions(config_handler);
            }
            else {
                if (!element_names) {
                    element_names = [];
                    props.config.forEach( item => {
                        element_names.push(item.name)
                    } )
                }
                element_definitions = spt.react.Config(props.config, {});
            }
        }

        element_names.forEach( element_name => {
            let definition = props.config
        } )
        


        let filtered = [];

        // make sure all the element names have definitions
        element_names.forEach( element_name => {
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
        } )


        if (props.sobject) {
            element_names.forEach( element_name => {
                let definition = element_definitions[element_name];
                let column = element_name;
                definition.value = props.sobject[column];
                definition.sobject = props.sobject;
            } )
        }

        set_element_names(filtered);
        set_element_definitions(element_definitions);

        // Group the definitions
        let groups = {};
        let group_names = [];
        filtered.forEach( element_name => {
            let definition = element_definitions[element_name];
            let group_name = definition.group || Common.generate_key();
            let group = groups[group_name];
            if (!group) {
                group = [];
                groups[group_name] = group;
                group_names.push(group_name);
            }
            group.push(definition);
        } )

        set_groups(groups);
        set_group_names(group_names);

        //console.log("groups: ", groups, group_names)
    }



    const load_data = async() => {

        let cmd = props.get_cmd;
        if (!cmd) {
            alert("Get cmd is not defined");
            return;
        }
        let kwargs = props.get_kwargs || {};
        let config_handler = props.config_handler;

        kwargs["config_handler"] = config_handler;


        let server = TACTIC.get();
        server.p_execute_cmd(cmd, kwargs)
        .then( ret => {
            let data = ret.info;
            set_data(data);

        } )
        .catch( e => {
            alert("TACTIC ERROR: " + e);
        } )
    }


    const get_element_definitions = async (cmd, kwargs) => {

        if (!kwargs) {
            kwargs = {};
        }

        let server = TACTIC.get();
        let ret = await server.p_execute_cmd( cmd, kwargs )
        let info = ret.info;
        let config = info.config;
        let renderer_params = info.renderer_params;

        // convert to AGgrid definitions
        let definitions = spt.react.Config(config, {});

        return definitions;
    }


    const validate = () => {

        let config = props.config;
        if (!config) return true;

        let sobject = props.sobject;
        if (!sobject) return true;

        let form_validated = true;

        element_names.forEach( element_name => {
            let definition = element_definitions[element_name];
            if (definition.required == true) {
                let key = definition.column || definition.name;
                if (!sobject[key]) {
                    form_validated = false;
                    definition.helper = "ERROR";
                    definition.error = true;
                }
            }

        } )

        set_element_names([...element_names]);

        return form_validated;
    }


    let style = props.style;
    if (!style) {
        style = {
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            margin: "30px 10px"
        }
    }




    return (

        <div className="spt_edit_form" style={style}>


            { element_definitions && group_names?.map( (group_name, index) => (

              <div className="spt_edit_form_row" style={{
                  display: "flex", flexDirection: "row", gap: "10px"
              }}>

              { groups[group_name].map( (definition, index) => {

                let editor = definition?.cellEditor;
                if (editor == SelectEditor) {
                    return ( <SelectEditorWdg key={index} onchange={onchange} {...definition}/>)
                }
                else if (editor == "NotesEditor") {
                    return ( <NotesEditorWdg key={index} onchange={onchange} {...definition}/>)
                }
                else if (editor == InputEditor) {
                    return ( <InputEditorWdg key={index} onchange={onchange} {...definition}/>)
                }
                else {
                    return ( <InputEditorWdg key={index} onchange={onchange} {...definition}/>)
                }
              } ) }

              </div>
            ) ) }


        </div>

    )
} )





const EditModal = React.forwardRef( (props, ref) => {

    const [show, set_show] = useState(false);
    const [item, set_item] = useState({});

    React.useImperativeHandle( ref, () => ({
        show() {
            set_show(true);
        },
        set_item(item) {
            set_item(item)
        }
    } ) )
   
    const handleClickOpen = () => {
        set_show(true);
    };
   
    const handleClose = () => {
        set_show(false);
    };


    const insert = () => {
        if (props.on_insert) props.on_insert(item);

        handleClose()
        set_item( {} );
    }

    const onchange = e => {
        let name = e.name;
        let value = e.target.value;

        item[name] = value;
    }




    return (
    <>
        { false &&
        <Modal
           open={show}
           onClose={ e => set_show(false) }
        >
        <div
           className="spt_modal"
           style={{
               width: "60vw",
               height: "fit-content",
               padding: "20px",
           }}
        >

        </div>
        </Modal>
        }

        <Dialog open={show} onClose={handleClose}
                fullWidth={true}
                maxWidth={"sm"}>
          <DialogTitle>New {props.name}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Enter the following data for {props.name}
            </DialogContentText>


            <EditForm {...props} sobject={item}/>

   
          </DialogContent>
          <DialogActions>
            <div style={{
                display: "flex",
                justifyContent: "center",
                gap: "30px",
                width: "100%",
            }}>
                <Button 
                    onClick={handleClose}
                >Cancel</Button>
                <Button
                    variant="contained"
                    onClick={ e => {
                        insert();
                }}>Insert</Button>
            </div>
          </DialogActions>
        </Dialog>
    </>
    )

} )



const DeleteModal = React.forwardRef( (props, ref) => {

    const [show, set_show] = useState(false);
    const [items, set_items] = useState([]);

    React.useImperativeHandle( ref, () => ({
        show() {
            set_show(true);
        },
        set_items(items) {
            set_items(items)
        }
    } ) )
   
    const handleClickOpen = () => {
        set_show(true);
    };
   
    const handleClose = () => {
        set_show(false);
    };


    const delete_selected = () => {

        if (props.ondelete) {
            props.ondelete(items);
        }
        else {

            items.reverse()

            let data = props.grid_ref.current.get_data();


            let search_keys = [];
            items.forEach( item => {
                let item_data = item.data;
                search_keys.push( item_data.__search_key__ );

                data.splice(item.rowIndex, 1);
            } )

            // TODO: make row disappear


            let server = TACTIC.get();
            let cmd = "tactic.react.DeleteCmd";
            let kwargs = {
                search_keys: search_keys
            };
            server.p_execute_cmd(cmd, kwargs)
            .then( ret => {
                props.load_data();
            } )
            .catch( e => {
                alert("TACTIC Error: " + e);
            } )

        }


        handleClose()
    }


    return (
    <>
        <Dialog open={show} onClose={handleClose}
                fullWidth={true}
                maxWidth={"sm"}>
          <DialogTitle>Delete Selected Items</DialogTitle>
          <DialogContent>
            <DialogContentText>
              <Alert severity="error">
              Do you wish to delete the following:
              </Alert>
            </DialogContentText>

            <div style={{display: "flex", flexDirection: "column", gap: "30px", margin: "30px 20px"}}>
                { items.map( (item, index) => (
                    <h3 key={index}>{item.data.name || ""}</h3>
                ) ) }
            </div>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button severity="error" onClick={ e => {
                delete_selected();
            }}>Delete</Button>
          </DialogActions>
        </Dialog>
    </>
    )

} )




class SelectEditor {

    init(params) {
        let column = params.colDef?.field;
        let open;
        if (column) {
            this.value = params.data[column] || "";
            open = true;
        }
        else {
            this.value = params.value;
            open = false;
        }

        let mode = params.mode || "select";
        let labels = params.labels || [];
        let values = params.values || [];
        let helpers = params.helpers || [];
        let colors = params.colors || {};

        let error = params.error;

        if (typeof(labels) == "string") {
            labels = labels.split("|")
        }
        if (typeof(values) == "string") {
            values = values.split("|")
        }
        if (typeof(helpers) == "string") {
            helpers = helpers.split("|")
        }

        let variant = params.variant || "standard";
        let label = params.label || "";
        let name = params.name;

        let layout = params.layout || "column";


        let el_style;
        let style = {
            width: "100%",
            height: "100%"
        }
        if (!params.is_form) {
            el_style = {
                fontSize: "0.75rem",
                padding: "0px 3px",
                width: "100%",
                height: "100%"
            }
        }
        else {
            el_style = {
            }
        }


        this.input = document.createElement("div")
        this.input.style.width = "100%";
        this.root = ReactDOM.createRoot( this.input );


        if (mode == "button") {
            this.el = (
            <div style={{display: "flex", flexDirection: layout, gap: "20px"}}>
                { values.map( (value, index) => (
                <div style={{width: "100%"}}>
                    <Button key={index}
                        variant={this.value == value ? "contained" : "outlined"}
                        style={{
                            border: error ? "solid 1px red" : "",
                        }}
                        fullWidth
                        onClick={ e => {
                            this.value = value;

                            // Need to add this
                            e.name = name;

                            if (params.onchange) {
                                params.onchange(e, this.value);
                            }
                        }}
                    >
                        <div style={{
                            fontSize: "0.8rem",
                        }}
                        >{labels[index]}</div>
                    </Button>
                    { helpers.length > 0 &&
                    <div style={{fontSize: "0.7rem", margin: "3px"}}>{ helpers[index] }</div>
                    }
                </div>
                ) ) }
            </div>
            )
            return;
        }

        else if (mode == "checkbox") {
            //Default to not checked
            if (this.value == null && labels.length > 1) {
                this.value = values[2];
            }
            else if (this.value == null) {
                this.value = values[1];
            }
            

            

            this.el = (
                <div style={{display: "flex", flexDirection: layout, gap: "20px"}}>
                    <div style={{width: "100%", display: "flex", alignItems: "center"}}>
                        {labels.length > 1 ? <><Checkbox
                            checked={this.value === values[0]}
                            onChange={ e => {
                                if (this.value === values[0]){
                                    this.value = values[2];
                                }
                                else if (this.value === values[1]){
                                    this.value = values[0];
                                }
                                else if (this.value === values[2]){
                                    this.value = values[0];
                                }
                                // Need to add this
                                e.name = name;
        
                                if (params.onchange) {
                                    params.onchange(e, this.value);
                                }
                            }}
                            style={{
                                cursor: "pointer",
                                alignSelf: "flex-start"
                            }}
                        /> 
                        <div style={{
                            fontSize: "0.8rem",
                            textAlign: "center",
                        }}>{labels[0]}</div>
                        <Checkbox
                            checked={this.value === values[1]}
                            onChange={ e => {
                                if (this.value === values[0]){
                                    this.value = values[1];
                                }
                                else if (this.value === values[1]){
                                    this.value = values[2];
                                }
                                else if (this.value === values[2]){
                                    this.value = values[1];
                                }
                                // Need to add this
                                e.name = name;
        
                                if (params.onchange) {
                                    params.onchange(e, this.value);
                                }
                            }}
                            style={{
                                cursor: "pointer",
                                alignSelf: "flex-start"
                            }}
                        /></>:
                        <Checkbox
                            checked={this.value === values[0]}
                            onChange={ e => {
                                if (this.value === values[0]){
                                    this.value = values[1];
                                }
                                else if (this.value === values[1]){
                                    this.value = values[0];
                                }
                                // Need to add this
                                e.name = name;
        
                                if (params.onchange) {
                                    params.onchange(e, this.value);
                                }
                            }}
                            style={{
                                cursor: "pointer",
                                alignSelf: "flex-start"
                            }}
                        />
                    }
                        <div style={{
                            fontSize: "0.8rem",
                            textAlign: "center",
                        }}>{labels.length > 1 ? labels[1] : labels[0]}</div>
                    </div>
                </div>
            )
            return;
            
        }



        this.el = (
            <TextField
                label={label}
                variant={variant}
                defaultValue={this.value}
                size="small"
                select
                style={style}
                SelectProps={{
                    defaultOpen: open,
                    style: el_style,
                }}
                onChange={ e => {
                    this.value = e.target.value;

                    // Need to add this
                    e.name = name;

                    if (params.onchange) {
                        params.onchange(e, this.value);
                    }
                    if (params.api?.stopEditing) {
                        params.api.stopEditing();
                    }
                }}
                onKeyUp={ e => {
                    if (e.key == 13) {
                        params.api.stopEditing();
                        params.api.tabToNextCell();
                    }
                }}
            >
                { values.map( (value, index) => (
                    <MenuItem key={index} value={value}>
                        <div style={{
                            fontSize: "0.8rem",
                        }}
                        >{labels[index]}</div>
                    </MenuItem>
                ) ) }
            </TextField>
        );

    }


    getEl() {
        return this.el
    }

    /* Component Editor Lifecycle methods */
    // gets called once when grid ready to insert the element
    getGui() {
        this.root.render(this.el);
        return this.input;
    }

    // the final value to send to the grid, on completion of editing
    getValue() {
        return this.value;
    }

    // Gets called once before editing starts, to give editor a chance to
    // cancel the editing before it even starts.
    /*
    isCancelBeforeStart() {
        return false;
    }
    */

    // Gets called once when editing is finished (eg if Enter is pressed).
    // If you return true, then the result of the edit will be ignored.
    /*
    isCancelAfterEnd() {
    }
    */

    // after this component has been created and inserted into the grid
    afterGuiAttached() {
    }
}


const SelectEditorWdg = (props) => {

    const [value, set_value] = useState();
    const [label, set_label] = useState();
    const [el, set_el] = useState();

    const [ignored, forceUpdate] = useReducer(x => x + 1, 0);

    useEffect( () => {
        let value = props.value;
        set_value(value);

        let label = props.headerName || props.label || props.title;
        if (label == null || typeof(label) == "undefined") {
            label = props.field;
        }
        label = Common.capitalize(label);
        set_label(label);

        init();
    }, [] );


    useEffect( () => {
        init();
    }, [props.error] );


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
            error: props.error,
        }

        let select = new SelectEditor()
        select.init(props2);
        let el = select.getEl();
        set_el(el);

    }


    useEffect( () => {
        init();
        forceUpdate();
    }, [value] );


    return (
        <div style={{width: "100%"}}>
            { props.show_title != false &&
            <div className="spt_form_label">{label} {props.required == true ? "*" : ""}</div>
            }
            { el &&
            <div className="spt_form_input">{el}</div>
            }
            { props.helper &&
                <div>{props.helper}</div>
            }
        </div>
 
    );
}



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
            height: "100%",
        }
        if (!is_form) {
            if (mode == "color") {
            }
            else {
                el_style = {
                    fontSize: "0.75rem",
                    padding: "3px 3px",
                    height: "100%",
                    width: "100%",
                    boxSizing: "border-box",
                }
                style.padding = "0px 15px";
                style.width = "max-width";
            }
        }
        else {
            el_style = {};
        }

        this.input = document.createElement("div")
        this.input.style.width = "100%";
        this.root = ReactDOM.createRoot( this.input );
        this.el = (
                <TextField
                    label={label}
                    variant={variant}
                    defaultValue={this.value}
                    multiline={rows > 1 ? true : false}
                    error={error}
                    helperText={helper}
                    rows={rows}
                    fullWidth
                    size="small"
                    type={mode}
                    style={style}
                    InputProps={{ disableUnderline: true }}
                    inputProps={{
                        className: "input",
                        style: el_style,
                    }}
                    onChange={ e => {
                        this.value = e.target.value;

                        // Need to add this
                        e.name = name;

                        if (params.onchange) {
                            params.onchange(e, this.value);
                        }

                    }}
                    onBlur={ e => {

                        if (params.api?.stopEditing) {
                            params.api.stopEditing();
                        }
                    } }
                    onKeyUp={ e => {
                        this.value = e.target.value;
                        if (e.code == "Tab" && params.api) {
                            params.api.tabToNextCell();
                        }
                        else if (e.code == "Enter" && params.api) {
                            params.api.stopEditing();
                        }
                    }}
 
                >
                </TextField>
        );

    }


    getEl() {
        return this.el
    }

    getGui() {
        this.root.render(this.el);
        return this.input;
    }

    // the final value to send to the grid, on completion of editing
    getValue() {
        if (this.mode == "date") {
            this.value = Date.parse(this.value);
        }
        return this.value;
    }



    // after this component has been created and inserted into the grid
    afterGuiAttached() {
        setTimeout( () => {
            let x = document.id(this.input);
            let input = x.getElement(".input");
            input.focus();
            //input.click();
        }, 250 );
    }

}



const InputEditorWdg = (props) => {

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
                props.onchange(e, new_value)
            }
        },
        value: props.value,
        helper: props.helper,
        error: props.error,
    }

    let input = new InputEditor();
    input.init(props2);
    let el = input.getEl();

    return (
        <div style={{width: "100%"}}>
            <div className="spt_form_label">{label}{props.required == true ? " *" : ""}</div>
            <div className="spt_form_input">{el}</div>
        </div>
    );
}



const SimpleCellRenderer = (params) => {

    let value = params.value;
    let label = value;
    let onClick = params.onClick;
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
            let month = (date.getMonth() + 1) + "";
            let year = date.getFullYear() + "";
            label = year + "-" + month.padStart(2, "0") + "-" + day.padStart(2, "0");
        }
        catch(e) {
            label = "";
        }

    }
    else if (mode == "%") {
        try {
            let display_value = value * 100;
            label = display_value + "%";
        }
        catch(e) {
            label = "";
        }

    }

    else if (mode == "$") {

        function numberWithCommasAndDecimals(x) {
            const parts = x.toString().split(".");
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            return parts.join(".");
        }

        try {
            label = "$" + numberWithCommasAndDecimals(value);
        }
        catch(e) {
            label = "";
        }
    }


    else {
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


    // default behavior
    let el = document.createElement("div");
    let inner;

    if (renderer) {
        inner = renderer(params);
        el.appendChild(inner);
    }
    else {
        inner = document.createElement("div");
        el.appendChild(inner);
        inner.style.width = "100%";
        inner.style.height = "100%";
        inner.style.padding = "0px 3px";

        inner.style.whiteSpace = "normal";

        // if the mode is color, the set the background color
        if (params.mode == "color") {
            inner.style.background = value;
        }

        let color = colors[value];
        if (color) {
            inner.style.background = color;
        }


        if (label == "") label = "&nbsp;";
        inner.appendChild( document.createTextNode(label) );
        if (onClick) {
            inner.style.textDecoration = "underline";
            inner.style.cursor = "pointer";

            // provide a link
            inner.addEventListener( "click", e => {
                onClick(params);
            } )
        }

    }


    // Edit icon
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

        icon.addEventListener( "click", e => {
            //params.show_notes();
            params.api.startEditingCell({
                rowIndex: params.rowIndex,
                colKey: params.colDef.field,
            });
            e.stopPropagation();
        } );
        el.addEventListener( "mouseenter", e => {
            icon.style.display = "";
        } );
        el.addEventListener( "mouseleave", e => {
            icon.style.display = "none";
        } );
    }
    else {
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
        el.addEventListener( "mouseenter", e => {
            icon.style.display = "";
        } );
        el.addEventListener( "mouseleave", e => {
            icon.style.display = "none";
        } );

    }


    return el;

}




const PreviewCellRenderer = (props) => {

    let data = props.data;
    let cell = props.eGridCell;
    let column = props.column.colId;

    let root = cell.root;
    if (!root) {
        root = ReactDOM.createRoot( cell );
        cell.root = root;
    }


    let src = "/plugins/spt/modules/workflow/apps/Resource/media/materials.png";

    let el = (
        <div>
            <img style={{width: "auto", height: "100%"}} src={src}/>
        </div>
    );

    return root.render(el);


}




const ColumnManagerMenu = React.forwardRef( (props, ref) => {

    //
    // Column Menu
    //
    const [column_anchorEl, column_setAnchorEl] = React.useState(null);
    const column_is_open = Boolean(column_anchorEl);

    let column_create_ref = useRef();


    const column_handle_click = (event) => {
        column_setAnchorEl(event.currentTarget);
    };
    const column_handle_close =  async () => {
        column_setAnchorEl(null);
    }
    const column_handle_select = async (column) => {
        //column_setAnchorEl(null);
        let index = props.columns.indexOf(column);
        if (index == -1) {
            props.columns.push(column);
        }
        else {
            props.columns.splice(index,1)
        }
        if (props.update) {
            props.update();
        }
    };



    const get_column_menu = () => {
        return (
        <>
            <Button
              variant="outlined"
              id="column-button"
              onClick={column_handle_click}
              title="Column Manager"
            >
              <i className="fas fa-columns"></i>
              &nbsp;
              <i className="fa-xs fas fa-caret-down"></i>
            </Button>
            <Menu
              id="column-menu"
              anchorEl={column_anchorEl}
              open={column_is_open}
              onClose={column_handle_close}
              MenuListProps={{
                'aria-labelledby': 'column-menu',
              }}
            >
                <MenuItem
                    value={"custom"}
                    onClick={e => {
                        //column_create_ref.current.show();
                        //column_handle_close();
                        props.property_modal_ref.current.show();
                    }}
                    style={{
                        height: "40px"
                    }}
                >Custom</MenuItem>
                <hr/>


                { props.all_columns.map( (column, index) => (
                    <MenuItem
                        key={index}
                        value={column}
                        onClick={e => {
                            column_handle_select(column);
                        }}
                        style={{
                            height: "30px"
                        }}
                    >
                    <Checkbox
                        checked={props.columns.includes(column)}
                    />
                    {Common.capitalize(column)}
                    </MenuItem>
                ) ) }
            </Menu>
        </>
        )
    }

    return (
        <>
        <ColumnCreateModal ref={column_create_ref}/>
        { get_column_menu() }
        </>
    )

} )


const ColumnCreateModal = React.forwardRef( (props, ref) => {

    const [show, set_show] = useState(false);
    const [item, set_item] = useState({});

    React.useImperativeHandle( ref, () => ({
        show() {
            set_show(true);
        },
        set_item(item) {
            set_item(item)
        }
    } ) )
   
    const handleClickOpen = () => {
        set_show(true);
    };
   
    const handleClose = () => {
        set_show(false);
    };

    const create = () => {
        alert("CREATE")
    }





    return (
    <>
        <Dialog open={show} onClose={handleClose}
                fullWidth={true}
                maxWidth={"sm"}>
          <DialogTitle>Create Custom Column</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Enter the properties for custom column
            </DialogContentText>

            <div style={{display: "flex", flexDirection: "column", gap: "20px", margin: "20px 0px"}}>
            </div>


   
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={ e => {
                create();
            }}>Create</Button>
          </DialogActions>
        </Dialog>
    </>
    )

} )






// Store this
spt.react.TableLayout = TableLayout;
spt.react.EditForm = EditForm;
spt.react.EditModal = EditModal;
spt.react.SelectEditor = SelectEditor;
spt.react.InputEditor = InputEditor;
spt.react.SimpleCellRenderer = SimpleCellRenderer;
spt.react.PreviewCellRenderer = PreviewCellRenderer;



