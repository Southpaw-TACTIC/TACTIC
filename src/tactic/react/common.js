"use strict";

class Common {
  constructor() {}
  static capitalize = str => {
    if (!str) {
      return str;
    }
    let new_str = str.replace(/_/g, " ");
    return new_str.replace(/(?:^|\s|[-_])\w/g, function (match) {
      return match.toUpperCase();
    });
  };
  static generate_key = length => {
    if (!length) {
      length = 20;
    }
    let code = "";
    let possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    for (let i = 0; i < length; i++) {
      if (i != 0 && i % 4 == 0) {
        code += "-";
      }
      code += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return code;
  };
}
spt.react.Common = Common;