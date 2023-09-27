"use strict";

const store = spt.react.redux.store;
class Common {
  constructor() {}
  static capitalize = str => {
    if (!str) {
      return str;
    }
    let new_str = str.replace("_", " ");
    return new_str.replace(/(?:^|\s|[-_])\w/g, function (match) {
      return match.toUpperCase();
    });
  };
}
spt.react.Common = Common;