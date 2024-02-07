"use strict";

const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;
const useReducer = React.useReducer;
const Modal = MaterialUI.Modal;
const Alert = MaterialUI.Alert;
const Button = MaterialUI.Button;
const TextField = MaterialUI.TextField;
const IconButton = MaterialUI.IconButton;
const Menu = MaterialUI.Menu;
const MenuItem = MaterialUI.MenuItem;
const Select = MaterialUI.Select;
const LinearProgress = MaterialUI.LinearProgress;
const ImportDataModal = React.forwardRef((props, ref) => {
  let cmd = props.cmd;
  if (!cmd) {
    return null;
  }
  const [importing, set_importing] = useState(false);
  React.useImperativeHandle(ref, () => ({
    show() {
      set_show(true);
    }
  }));
  const [show, set_show] = useState(false);
  const [data, set_data] = useState({
    dry_run: true,
    header: "",
    data: "",
    extra_data: props.kwargs
  });
  const [headers, set_headers] = useState([]);
  const [rows, set_rows] = useState([]);
  const [severity, set_severity] = useState("error");
  const [error, set_error] = useState("");
  const [line_errors, set_line_errors] = useState({});
  const [extra_data, set_extra_data] = useState([]);
  useEffect(() => {
    if (props.show) {
      set_show(true);
    }
  }, [props]);
  const import_data = () => {
    set_importing(true);
    data.dry_run = false;

    extra_data.forEach(item => {
      if (item[0] == "" || !item[0]) {
        return;
      }
      if (item[1] == "" || !item[1]) {
        return;
      }
      data.extra_data[item[0]] = item[1];
    });
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, data).then(ret => {
      let info = ret.info;
      let data = info?.data;
      let error = info?.error;
      if (error && error != "") {
        set_importing(false);
        set_severity("error");
        set_error(error.replace(/\\n/g, "<br/>"));
        set_error(error);
      } else {
        if (props.reload) {
          props.reload(data);
        }
        set_importing(false);
        set_show(false);
      }
    }).catch(e => {
      set_importing(false);
      set_error(e);
    });
  };
  const dry_run = () => {
    data.dry_run = true;

    extra_data.forEach(item => {
      if (item[0] == "" || !item[0]) {
        return;
      }
      if (item[1] == "" || !item[1]) {
        return;
      }
      data.extra_data[item[0]] = item[1];
    });
    let server = TACTIC.get();
    server.p_execute_cmd(cmd, data).then(ret => {
      let info = ret.info;
      let data = info?.data;
      let error = info?.error;
      let line_errors = info?.line_errors || null;
      if (line_errors) {
        set_line_errors(line_errors);
      }
      if (error && error != "") {
        set_severity("error");
        set_error(error.replace(/\\n/g, "<br/>"));
      } else if (line_errors && Object.keys(line_errors).length > 0) {
        set_severity("error");
        set_error("Found " + Object.keys(line_errors).length + " errors in data.");
      } else {
        if (data.length == 0) {
          set_severity("warning");
          set_error("There are no data entries");
        }
        if (data.length > 0) {
          set_severity("success");
          set_error("Detected " + data.length + " items.");
        }
      }
    }).catch(e => {
      set_severity("error");
      set_error(e.replace(/\\n/g, "<br/>"));
    });
  };
  return React.createElement(Modal, {
    open: show,
    onClose: e => set_show(false)
  }, React.createElement("div", {
    className: "spt_modal",
    style: {
      width: "60vw",
      height: "70vh",
      padding: "20px"
    }
  }, React.createElement(IconButton, {
    style: {
      position: "absolute",
      top: "10px",
      right: "10px"
    },
    onClick: e => {
      data.data = "";
      rows.length = 0;
      set_data({
        ...data
      });
      set_error("");
      set_show(false);
    }
  }, "X"), React.createElement("h3", null, "Import Data"), React.createElement("hr", null), React.createElement("br", null), importing && React.createElement("div", {
    style: {
      margin: "40px auto",
      width: "80%",
      padding: "30px",
      border: "solid 1px #DDD"
    }
  }, React.createElement("h3", null, "Importing ..."), React.createElement("div", {
    style: {
      width: '100%'
    }
  }, React.createElement(LinearProgress, null))), !importing && React.createElement(React.Fragment, null, React.createElement("div", {
    style: {
      margin: "0px 30px"
    }
  }, "Cut and paste rows from a spreadsheet into the text boxes below."), React.createElement("br", null), error != "" && React.createElement(Alert, {
    severity: severity,
    style: {
      margin: "15px 30px"
    }
  }, error), React.createElement("div", {
    style: {
      margin: "10px 30px"
    }
  }, data.header != "" ? React.createElement(React.Fragment, null, React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between"
    }
  }, React.createElement("div", null, React.createElement("b", null, "Found " + headers.length + " headers")), React.createElement(Button, {
    size: "small",
    onClick: e => {
      data.header = "";
      headers.length = 0;
      set_data({
        ...data
      });
    }
  }, "Clear")), React.createElement("div", {
    style: {
      height: "100px",
      overflow: "auto",
      width: "100%",
      border: "solid 1px #DDD",
      padding: "10px"
    }
  }, headers.join(", "))) : React.createElement(TextField, {
    label: "Headers",
    fullWidth: true,
    multiline: true,
    inputProps: {
      style: {
        maxHeight: "100px"
      }
    },
    onBlur: e => {
      let lines = e.target.value.split("\n");
      if (lines.length == 0) {
        return;
      }
      data.header = lines[0];
      let headers = [];
      let parts = data.header.split("\t");
      parts.forEach(part => {
        part = part.trim();
        if (part == "") {
          return;
        }
        headers.push(part);
      });
      set_headers(headers);
      if (lines.length > 0) {
        let parts = [...lines];
        parts.shift();
        let rows = [];
        parts.forEach(part => {
          part = part.trim();
          if (part == "") {
            return;
          }
          rows.push(part);
        });
        set_rows(rows);
        data.data = parts.join("\n");
      }
      set_data({
        ...data
      });
      dry_run();
    }
  })), React.createElement("br", null), headers?.length > 0 && React.createElement("div", {
    style: {
      margin: "10px 30px"
    }
  }, data.data != "" ? React.createElement(React.Fragment, null, React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between"
    }
  }, React.createElement("div", null, React.createElement("b", null, "Found " + rows.length + " rows")), React.createElement(Button, {
    onClick: e => {
      data.data = "";
      rows.length = 0;
      set_data({
        ...data
      });
    }
  }, "Clear")), React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center"
    }
  }, React.createElement("div", {
    style: {
      maxHeight: "200px",
      overflow: "auto",
      width: "100%",
      border: "solid 1px #DDD",
      padding: "10px"
    }
  }, rows.map((row, index) => React.createElement("div", {
    key: index,
    style: {
      borderBottom: "solid 1px #999",
      paddingBottom: "10px",
      marginTop: "10px"
    }
  }, React.createElement("div", null, row.replace(/\t/g, ", ")), React.createElement("div", null, line_errors[index] && React.createElement(Alert, {
    icon: false,
    style: {
      padding: "0px 10px"
    },
    severity: line_errors[index].severity
  }, line_errors[index].severity.toUpperCase(), ": ", line_errors[index].msg))))))) : React.createElement(TextField, {
    multiline: true,
    rows: 1,
    label: "Data",
    fullWidth: true,
    onBlur: e => {
      data.data = e.target.value;
      set_data({
        ...data
      });
      let rows = [];
      let parts = data.data.split("\n");
      parts.forEach(part => {
        part = part.trim();
        if (part == "") {
          return;
        }
        rows.push(part);
      });
      set_rows(rows);
      dry_run();
    }
  })), false && React.createElement("div", {
    style: {
      margin: "30px 30px 50px 30px"
    }
  }, React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between"
    }
  }, React.createElement("div", null, React.createElement("div", null, React.createElement("b", null, "Extra Data")), React.createElement("div", null, "This is data that will be added to every row")), React.createElement(Button, {
    onClick: e => {
      extra_data.push(["", ""]);
      set_extra_data([...extra_data]);
    }
  }, "Add")), extra_data.map((item, index) => React.createElement("div", {
    key: index,
    style: {
      margin: "10px auto",
      width: "50%",
      display: "flex",
      justifyContent: "space-between",
      gap: "15px",
      alignItems: "center"
    }
  }, React.createElement(TextField, {
    value: item[0],
    size: "small",
    label: "Name",
    onChange: e => {
      item[0] = e.target.value;
      set_extra_data([...extra_data]);
    }
  }), React.createElement("div", {
    style: {
      fontSize: "1.0rem"
    }
  }, " = "), React.createElement(TextField, {
    size: "small",
    label: "Value",
    value: item[1],
    onChange: e => {
      item[1] = e.target.value;
      set_extra_data([...extra_data]);
    }
  }), React.createElement(IconButton, {
    onClick: e => {
      extra_data.splice(index, 1);
      set_extra_data([...extra_data]);
    }
  }, "X")))), React.createElement("div", {
    style: {
      width: "100%",
      display: "flex",
      justifyContent: "space-around",
      marginTop: "30px"
    }
  }, React.createElement(Button, {
    variant: "outlined",
    onClick: e => {
      set_show(false);
    }
  }, "Cancel"), React.createElement(Button, {
    variant: "contained",
    disabled: headers?.length == 0 || rows?.length == 0,
    onClick: e => {
      import_data();
      data.data = "";
      rows.length = 0;
      set_data({
        ...data
      });
      set_error("");
    }
  }, "Import")))));
});
if (!spt.react) {
  spt.react = {};
}
spt.react.ImportDataModal = ImportDataModal;