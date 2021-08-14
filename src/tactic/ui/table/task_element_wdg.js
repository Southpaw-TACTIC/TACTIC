"use strict";

class StatusWdg extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.task = props.task;
  }

  render() {
    return React.createElement("div", {
      style: {
        display: "flex"
      }
    }, React.createElement("select", {
      className: "form-control",
      style: {
        textAlignLast: "center",
        background: "transparent"
      }
    }, React.createElement("option", {
      value: this.task.status
    }, this.task.status), React.createElement("option", {
      value: "cow"
    }, "Cow"), React.createElement("option", {
      value: "pig"
    }, "Pig"), React.createElement("option", {
      value: "horse"
    }, "Horse")));
  }

}

spt.task_element.StatusWdg = StatusWdg;