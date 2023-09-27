"use strict";

const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;
const useReducer = React.useReducer;
const NotesWdg = React.forwardRef((props, ref) => {
  let this_ref = useRef();
  React.useImperativeHandle(ref, () => ({
    show() {
      let el = this_ref.current.getElement(".spt_discussion_add");
      const event = document.createEvent("Event");
      event.initEvent("click", true, true);
      el.dispatchEvent(event);
    }
  }));
  let process = "publish";
  let search_key = props.search_key;
  useEffect(() => {
    let cmd = "tactic.ui.widget.DiscussionWdg";
    let kwargs = {
      mode: "icon",
      search_key: search_key,
      width: "100%",
      use_dialog: true,
      process: "publish",
      size: 16
    };
    spt.panel.load(this_ref.current, cmd, kwargs);
  }, []);
  return React.createElement("div", {
    style: {
      color: "white !important",
      padding: "3px"
    },
    ref: this_ref
  });
});
if (!spt.react.widget) {
  spt.react.widget = {};
}
spt.react.widget.NotesWdg = NotesWdg;