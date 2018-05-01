###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ChartWdg', 'ChartData', 'SampleBarChartWdg']

from pyasm.common import Environment, Common, jsonloads
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer, Canvas

from tactic.ui.common import BaseRefreshWdg


class SampleBarChartWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'width': {
        'description': 'Width of widget',
        'category': 'Options',
        'order': 0
    },
    'height': {
        'description': 'Height of widget',
        'category': 'Options',
        'order': 1
    },
    }



    def get_display(self):

        top = self.top

        #top.add_gradient("background", "background", 5, -20)
        top.add_color("background", "background", -5)
        #top.add_style("padding-top: 10px")

        title = "Sample Chart"
        if title:
            date = "@FORMAT(@STRING($TODAY),'Dec 31, 1999')"
            date = Search.eval(date, single=True)

            title_wdg = DivWdg()
            top.add(title_wdg)
            title_wdg.add(title)
            title_wdg.add(" [%s]" % date)
            title_wdg.add_style("font-size: 1.1em")
            title_wdg.add_color("background", "background3")
            title_wdg.add_color("color", "color3")
            title_wdg.add_style("padding: 10px")
            title_wdg.add_style("font-weight: bold")
            title_wdg.add_style("text-align: center")



        #labels = ['chr001', 'chr002', 'chr003', 'chr004', 'prop001', 'prop002', 'cow001']
        labels = ['week 1', 'week 2', 'week 3', 'week 4', 'week 5', 'week 6', 'week 7', 'week 8']
        values = [1,2,4,5,6,7,8]

        width = self.kwargs.get("width")
        if not width:
            width = '800px'
        height = self.kwargs.get("height")
        if not height:
            height = '500px'


        chart_div = DivWdg()
        top.add(chart_div)
        chart_div.add_style("text-align: center")

        chart = ChartWdg(
            height=height,
            width=width,
            chart_type='bar',
            labels=labels
        )
        chart_div.add(chart)

        data = ChartData(
            color="rgba(255, 0, 0, 1.0)",
            data=[1.2, 5.5, 7.5, 14.3, 10.2, 1.1, 3.3],
            x_data=[1,3,3.1,3.2,3.3,3.4,3.5]
        )
        chart.add(data)

        data = ChartData(
            color="rgba(0, 255, 0, 0.5)",
            data=[1.5, 4.3, 8.4, 6.2, 8.4, 2.2],
        )
        chart.add(data)


        data = ChartData(
            color="rgba(0, 0, 255, 0.7)",
            data=[1.1, 3.5, 2.2, 6.6, 1.3, 9.4],
        )
        chart.add(data)


        data = [14.3, 17, 15.5, -3, 17, 16.8, 11.4]
        data = ChartData(data=data, color="rgba(0, 0, 255, 0.3)")
        chart.add(data)


        data = {
            "m": -2.5,
            "b": 17.3
        }
        data = ChartData(chart_type='function', data=data, color="rgba(128, 128, 128, 0.6)")
        chart.add(data)


        data = {
            "m": -3,
            "b": 13.3
        }
        data = ChartData(chart_type='function', data=data, color="rgba(128, 128, 128, 0.6)")
        chart.add(data)


        data = {
            "a": -2,
            "b": 1.3,
            "c": 10 
        }
        data = ChartData(chart_type='polynomial', data=data, color="rgba(128, 128, 128, 0.6)")
        chart.add(data)

        return top





class ChartWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'height': 'Height of the canvas',
    'width': 'Width of the canvas',
    }

    def init(self):
        top = self.top
        #top.add_gradient("background", "background", -5)

    def add_style(self, name, value):
        self.top.add_style(name, value)

    def add_color(self, name, value):
        self.top.add_color(name, value)

    def add_gradient(self, name, value, offset=0, gradient=-10):
        self.top.add_gradient(name, value, offset, gradient)


    def get_display(self):

        top = self.top
        top.add_style("position: relative")

        labels = self.kwargs.get("labels")
        if not labels:
            labels = []
        label_values = self.kwargs.get("label_values")

        width = self.kwargs.get("width")
        height = self.kwargs.get("height")

        default_chart_type = self.kwargs.get("chart_type")
        if not default_chart_type:
            default_chart_type = 'bar'

        canvas = Canvas()
        top.add(canvas)
        canvas.set_id("chart1")
        canvas.add_attr("width", width)
        canvas.add_attr("height", height)
        canvas.add("Your web-browser does not support the HTML 5 canvas element.")

        canvas.add_behavior( {
            'type': 'load',
            'cbjs_action': ONLOAD_JS
        } )


        bar_chart_index = 0
        num_bar_charts = 0
        for widget in self.widgets:
            # count the number of bar charts
            chart_type = widget.get_chart_type()
            if not chart_type:
                chart_type = default_chart_type
                widget.set_chart_type(chart_type)


            if chart_type == 'bar':
                num_bar_charts += 1



        # auto figure out the range
        xmax = 1
        ymax = 0

        for widget in self.widgets:

            # count the number of bar charts
            chart_type = widget.get_chart_type()
            if not chart_type:
                chart_type = default_chart_type
                widget.set_chart_type(chart_type)


            widget.set_index(bar_chart_index, num_bar_charts)
            if chart_type == 'bar':
                bar_chart_index += 1


            # remember the largest value
            data = widget.get_data()
            for value in data:
                if value > ymax:
                    ymax = value


            x_data = widget.get_xdata()
            if not x_data:
                if len(data)-1 > xmax:
                    xmax = len(data)-1
            else:
                last = x_data[-1]
                if last > xmax:
                    xmax = last

            top.add(widget)

        # FIXME: doesn't handle small numbers too well
        ymax += 1

        if len(labels) > xmax:
            xmax = len(labels)
        if not xmax:
            xmax = 1



        # initialize the canvas
        canvas.add_behavior( {
            'type': 'load',
            'xmax': xmax,
            'ymax': ymax,
            'cbjs_action': '''
            spt.chart.top = bvr.src_el;
            spt.chart.set_range(bvr.xmax, bvr.ymax);
            '''
        } )


        # draw the grid
        rotate_x_axis = self.kwargs.get("rotate_x_axis")
        y_axis_mode = self.kwargs.get("y_axis_mode")
        grid = ChartGrid(labels=labels, label_values=label_values, rotate_x_axis=rotate_x_axis, mode=y_axis_mode)
        top.add(grid)


        # draw a legend
        if self.kwargs.get("legend"):
            legend = ChartLegend(labels=self.kwargs.get('legend'))
            legend.add_style("position: absolute")
            legend.add_style("left: %s" % 50)
            legend.add_style("top: %s" % 10)

            top.add(legend)

        return top


class ChartGrid(BaseRefreshWdg):

    def get_display(self):


        labels = self.kwargs.get("labels")
        if not labels:
            labels = None

        xmax = self.kwargs.get("xmax")
        ymax = self.kwargs.get("ymax")

        mode = self.kwargs.get("mode")
        if not mode:
            #mode = 'integer'
            mode = 'float'


        self.label_values = self.kwargs.get("label_values")
        if not self.label_values:
            self.label_values = [0]

        top = self.top

        font_color = top.get_color("color")
        #font = '12px san-serif';
        font = '12px arial';
        grid_color = top.get_color("border")

        rotate_x_axis = self.kwargs.get("rotate_x_axis") 
        if rotate_x_axis in [True, 'true']:
            rotate_x_axis = True
        else:
            rotate_x_axis = False

        top.add_behavior( {
            'type': 'load',
            'mode': mode,
            'font': font,
            'font_color': font_color,
            'grid_color': grid_color,
            'rotate_x_axis': rotate_x_axis,
            'labels': labels,
            'label_values': self.label_values,
            'cbjs_action': '''

            var size = spt.chart.get_size();
            var color = bvr.grid_color;


            var origin = spt.chart.get_origin();
            var outer = spt.chart.get_outer();

            var interval = spt.chart.get_interval();

            // draw the main grid lines
            spt.chart.draw_line( origin, {x: origin.x, y: outer.y}, color );
            spt.chart.draw_line( origin, {x: outer.x, y: origin.y}, color );

            // draw lines on the x axis
            var last_x = 0;
            var last_label = null;
            for (var i = 0; ; i++) {
                if (i > 1000) break;

                var label_value = bvr.label_values[i];
                var x;
                if (typeof(label_value) == 'undefined') {
                    x = last_x + interval.x;
                }
                else {
                    x = origin.x + label_value*interval.x;
                }


                var y = origin.y;
                if (x > outer.x) break;

                var start = {x: x, y: y};
                var end = {x: x, y: y+5};
                spt.chart.draw_line( start, end, color );

                var label = null;
                if (bvr.labels == null) {
                    label = i + "";
                }
                else {
                    if (i < bvr.labels.length)
                        label = bvr.labels[i];
                }


                // if diff is too small, don't draw it
                var diff = x - last_x;
                if (diff < 20) {
                    continue;
                }
                last_x = x;



                var ctx = spt.chart.get_ctx();
                ctx.fillStyle = bvr.font_color;
                ctx.font = bvr.font;
                ctx.textBaseline = 'bottom';

                if (label && label != last_label) {
                    var length = (label+"").length;
                    //var offset = length * 2;
                    var offset_x = 5;
                    if (bvr.rotate_x_axis)
                        var offset_y = 5;
                    else
                        var offset_y = 10;
                    

                    ctx.save();
                    ctx.translate(+(x-offset_x), +(origin.y+offset_y));
                    if (bvr.rotate_x_axis)
                        ctx.rotate(3*Math.PI/16);
                    ctx.translate(-(x-offset_x), -(origin.y+offset_y));
                    ctx.translate(0, 15);
                    ctx.fillText(label, x - offset_x, origin.y + offset_y);
                    ctx.restore();
                }
                last_label = label;
            }

            // draw the  axis titles
            /*
            ctx.font = '14px san-serif';
            var title = "Wow";
            ctx.fillText(title, (origin.x+outer.x)/2, origin.y+40);
            var title = "MB";
            var x = origin.x-30;
            var y = (origin.y+outer.y)/2;

            ctx.save();
            ctx.translate(+x, +y);
            ctx.rotate(-Math.PI/2);
            ctx.translate(-x, -y);
            ctx.fillText(title, +x, +y);
            ctx.restore();
            */



            // draw the vertical grid lines
            var multiplier = 1;

            var too_big = false;
            while (1) {
                var num_lines = (origin.y - outer.y) / (interval.y * multiplier);
                if (num_lines > 10) {
                    multiplier = multiplier * 10;
                }
                else if (num_lines < 5) {
                    multiplier = multiplier / 2;
                }
                else {
                    break;
                }
            }

            if (bvr.mode == 'integer') {
                multiplier = parseInt(multiplier);
            }
            if (multiplier == 0) {
                multiplier = 1;
            }

            interval.y = interval.y * multiplier;

            var color2 = 'rgba(240, 240, 240, 0.5)';
            for (var i = 0; ; i++) {
                if (i > 1000) break;

                var label = i*multiplier

                var y = origin.y - i*interval.y;
                if (y < outer.y) break;

                var start = {x: origin.x-1, y: y};
                var end = {x: origin.x-5, y: y};
                spt.chart.draw_line( start, end, "#999" );

                if (i == 0) continue;

                var start = {x: origin.x+1, y: y};
                var end = {x: outer.x, y: y};
                spt.chart.draw_line( start, end, color2 );

                // draw the label
                var ctx = spt.chart.get_ctx();
                ctx.fillStyle = bvr.font_color;
                ctx.font = bvr.font;
                ctx.textBaseline = 'bottom';
                var length = (label+"").length;
                var offset = (length-1) * 3;
                ctx.fillText(label, origin.x - 20 - offset, origin.y - i*interval.y+8);

            }

            '''
        } )

        return top




class ChartData(BaseRefreshWdg):

    def init(self):
        self.index = 0
        self.total_index = 0

    def get_chart_type(self):
        return self.chart_type

    def set_chart_type(self, chart_type):
        self.chart_type = chart_type


    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_xdata(self):
        return self.x_data

    def set_index(self, index, total_index):
        self.index = index
        self.total_index = total_index


    def init(self):
        self.chart_type = self.kwargs.get("chart_type")
        self.index = self.kwargs.get("index")
        self.data = self.kwargs.get("data")
        self.x_data = self.kwargs.get("x_data")

        if self.chart_type == 'function':
            self.data = self.handle_func(self.data)
            self.chart_type = 'line'
        elif self.chart_type == 'polynomial':
            self.data = self.handle_polynomial(self.data)
            self.chart_type = 'line'


    def get_display(self):

        labels = self.kwargs.get("labels")
        color = self.kwargs.get("color")

        if not self.chart_type:
            self.chart_type = 'bar'


        self.x_data = self.kwargs.get("x_data")
        if not self.x_data:
            self.x_data = [0]

        top = self.top

        top.add_behavior( {
        'type': 'load',
        'color': color,
        'index': str(self.index),
        'total_index': str(self.total_index),
        'chart_type': self.chart_type,
        'data': self.data,
        'x_data': self.x_data,
        'cbjs_action': '''
        var size = spt.chart.get_size();
        var index = parseInt(bvr.index);
        var total_index = parseInt(bvr.total_index);

        var type = bvr.chart_type;

        var origin = spt.chart.get_origin();
        var outer = spt.chart.get_outer();

        var interval = spt.chart.get_interval();

        var last = null;
        var last_x = 0;
        for (var i = 0; i < bvr.data.length; i++) {

            var x_value = bvr.x_data[i];
            var x;
            if (typeof(x_value) == 'undefined') {
                x = last_x + interval.x;
            }
            else {
                x = x_value*interval.x;
            }
            last_x = x;


            var y = bvr.data[i]*interval.y;
            var cur = spt.chart.get_pos(x, y);

            // skip first
            if (type != 'bar') {
                if (i == 0) {
                    last = cur;
                    //spt.chart.draw_dot( x, y, 3, "#000" );
                    continue;
                }
            }


            if (type == 'area') {
                spt.chart.draw_area( last, cur, bvr.color );
                //spt.chart.draw_dot( x, y, 3, "#000" );
            }
            else if (type == 'line') {
                spt.chart.draw_line( last, cur, bvr.color );
                //spt.chart.draw_dot( x, y, 3, "#000" );
            }
            else {
                var width = interval.x * 0.5 / bvr.total_index;
                var pos = {x: cur.x - (bvr.total_index*width/2), y: cur.y};
                spt.chart.draw_bar( pos, index, bvr.color, width );
            }


            last = cur;
        }

        '''
        } )

        return top



    def handle_func(self, data):
        # take the data and fit it?
        """
        data = [10, 8, 5, 3, 1.5]
        slope = 0
        last = 0
        for i, item in enumerate(data):
            if i == 0:
                last = item
                continue

            slope += item - last
            last = item

        slope = slope / i
        print "slope: ", slope
        """

        # find b: this isn't so necessary here because we have point 0
        m = data.get("m")
        b = data.get("b")
        start = data.get("start")
        end = data.get("end")

        # linear
        func = 'm*x + b'
        func = func.replace("m", str(m))
        func = func.replace("b", str(b))
        data = []
        for x in range(0, 10):
            y = eval(func)
            if y < 0:
                break
            data.append(y)

        return data


    def handle_polynomial(self, data):
        func = 'a*x*x + b*x *c'

        # find b: this isn't so necessary here because we have point 0
        a = data.get("a")
        b = data.get("b")
        c = data.get("c")
        start = data.get("start")
        end = data.get("end")

        # linear
        func = func.replace("a", str(a))
        func = func.replace("b", str(b))
        func = func.replace("c", str(c))
        data = []
        for x in range(0, 10):
            x = float(x)
            y = eval(func)
            if y < 0:
                break
            data.append(y)

        return data


class ChartLegend(BaseRefreshWdg):

    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def set_labels(self, labels):
        self.kwargs['labels'] = labels

    def set_colors(self, colors):
        self.kwargs['colors'] = colors

    def get_display(self):

        top = self.top
        labels = self.kwargs.get("labels")
        if not labels:
            return top

        if isinstance(labels, basestring):
            labels = labels.split("|")


        top.add_style("padding: 3px")
        top.add_color("background", "background3")
        top.add_border()


        colors = self.kwargs.get("colors")


        # draw a legend
        for i, label in enumerate(labels):

            label_div = DivWdg()
            top.add(label_div)
            label_div.add_style("float: left")

            #label_div.set_round_corners()
            label_div.add_style("padding: 0 15 3 15")

            color_div = DivWdg()
            color_div.add_style("width: 12px")
            color_div.add_style("height: 12px")

            if colors:
                color_div.add_style("background: %s" % colors[i])
                label_div.add(color_div)
                color_div.add_style("float: left")
                color_div.add_style("margin-right: 10px")
                color_div.add_style("margin-top: 2px")
            else:
                label_div.add("+ ")
            label_div.add(label)

        top.add("<br/>")

        return top



ONLOAD_JS = '''

spt.chart = {}

spt.chart.top = null;

spt.chart.data = {};
spt.chart.data.scale = {x: 1.0, y: 1.0};

spt.chart.get_top = function() {
    return spt.chart.top;
}


spt.chart.get_data = function() {
    return spt.chart.data;
}


spt.chart.set_range = function(x, y) {
    var data = spt.chart.get_data();
    data.xmax = x;
    data.ymax = y;
}



spt.chart.get_size = function() {
    var top = spt.chart.get_top();
    return top.getSize();
}


spt.chart.set_scale = function(x, y) {
    spt.chart.data.scale = {x: x, y: y};

}

spt.chart.get_scale = function() {
    return spt.chart.data.scale;
}




spt.chart.get_origin = function() {
    var size = spt.chart.get_size();
    var x_offset = 50;
    var y_offset = 50;
    var origin = {
        x: x_offset,
        y: size.y - y_offset
    }
    return origin;
}


spt.chart.get_outer = function() {
    var size = spt.chart.get_size();
    var x_offset = 50;
    var y_offset = 15;
    var outer = {
        x: size.x - x_offset,
        y: y_offset 
    }
    return outer;
}


spt.chart.get_pos = function(x, y) {
    var origin = spt.chart.get_origin();
    var pos = {
        x: origin.x + x,
        y: origin.y - y
    }
    return pos;
}


spt.chart.get_interval = function() {
    var origin = spt.chart.get_origin();
    var outer = spt.chart.get_outer();

    var data = spt.chart.get_data();

    var interval = {};

    var grid_height = origin.y - outer.y;

    if (data.ymax == 0) {
        interval.y = 1;
    }
    else {
        interval.y = grid_height / data.ymax;
    }


    var grid_width = outer.x - origin.x;

    if (data.xmax == 0) {
        interval.x = 1;
    }
    else {
        interval.x = grid_width / data.xmax;
    }


    return interval;
}



spt.chart.get_ctx = function() {
    var top = spt.chart.get_top();
    //var chart = top.getElement(".spt_chart");
    var ctx = top.getContext('2d');
    return ctx;
}
 
spt.chart.draw_line = function(start, end, color, width) {
    var origin = spt.chart.get_origin();

    var ctx = spt.chart.get_ctx();
    ctx.strokeStyle = color;  
    if (!width) width = 1;
    ctx.lineWidth = width;
    ctx.beginPath();

    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.stroke();
}


spt.chart.draw_area = function(start, end, color) {
    var origin = spt.chart.get_origin();

    var ctx = spt.chart.get_ctx();
    ctx.strokeStyle = color;  

    //ctx.fillStyle = color;  
    var gradient = ctx.createLinearGradient(0,0,0,origin.y);
    gradient.addColorStop(0, '#FFF');
    //gradient.addColorStop(0.75, color);
    gradient.addColorStop(1, color);
    ctx.fillStyle = gradient;
 

    ctx.beginPath();

    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.lineTo(end.x, origin.y-1);
    ctx.lineTo(start.x, origin.y-1);
    ctx.closePath();

    ctx.fill();

    var width = 1;
    spt.chart.draw_line(start, end, 'rgba(100,145,164,1)', width);

}


spt.chart.draw_bar = function(pos, index, color, width) {
    var origin = spt.chart.get_origin();

    var ctx = spt.chart.get_ctx();

    ctx.strokeStyle = spt.css.modify_color_value(color, -5);
    //ctx.strokeStyle = color;

    //var gradient = ctx.createLinearGradient(0,pos.y,0,origin.y);
    var gradient = ctx.createLinearGradient(0,0,0,origin.y);
    gradient.addColorStop(0, '#FFF');
    gradient.addColorStop(0.75, color);
    gradient.addColorStop(1, color);
    ctx.fillStyle = gradient;
    //ctx.fillStyle = color;  



    ctx.lineWidth = 2;
    ctx.beginPath();

    var width;
    if (!width) {
        width = 10;
    }

    var offset = index * (width+3);

    ctx.moveTo(pos.x+offset, origin.y-1);
    ctx.lineTo(pos.x+offset, pos.y);
    ctx.lineTo(pos.x+offset+width, pos.y);
    ctx.lineTo(pos.x+offset+width, origin.y-1);
    ctx.closePath();
    ctx.stroke();

    ctx.fill();

}



spt.chart.draw_dot = function(x, y, size, color) {

    var pos = spt.chart.get_pos(x, y);

    var ctx = spt.chart.get_ctx();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, size, 0, Math.PI*2, true);
    ctx.closePath();
    ctx.fill();
}


        '''





"""
<config>
  <burndown_chart_wdg>
<html>
  <style type="text/css">
    table {color:#000;}
  </style>


  <div class="spt_top" style="background:none; padding:10px; width:100%; text-align:center">
    <h4>Burndown Report</h4>
    <![CDATA[

    <canvas class="spt_canvas" id="canvas" width="1000" height="300" style="background:#FFF;">No HTML5 Canvas Support</canvas>


    ]]>

  </div>
</html>



   <behavior class='spt_top'>{
      "type": "load",
      "cbjs_action": <![CDATA['''
        try {

            // Options
            var x_pad = 30;
            var y_pad = 30;
            var label_pad = 10;           

            // Setup
            var server = TacticServerStub.get();

            var canvas;
            var ctx;
            var x_spacing;
            var max_value;
            var x = 0;
            var y = 0;
            var x_vals = [];
            var WIDTH;
            var HEIGHT;


          // Init
          function init() {
              // Get the top elements
              var top_el = bvr.src_el;
              var canvas = top_el.getElement(".spt_canvas");
              WIDTH = canvas.getAttribute("width") - x_pad*2;
              HEIGHT = canvas.getAttribute("height") - y_pad*2;
              ctx = canvas.getContext("2d");
              draw();
          }



          // Draw the graph
          function draw() {
              clear();
              
              // Get the x-axis values
              x_vals = server.eval("@GET(project/burndown.code)")
              x_spacing = WIDTH / x_vals.length;
              max_value = server.eval("@COUNT(sthpw/task['project_code', $PROJECT])")

              // Setup the base graph
              drawaxes();
              addlabels();
              drawgrid();

              // Get the Data
              var y_proj_vals = server.eval("@GET(project/burndown.tasks_due)");
              var y_curr_vals = server.eval("@GET(project/burndown['tasks_remaining', '>', 0].tasks_remaining)");
              var y_velo_vals = server.eval("@GET(project/burndown.velocity)");

              // Draw the date 
              plotdata(y_proj_vals, "#000", "rgba(255,100,100, 0.5)", 1)
              plotdata(y_curr_vals, "#000","rgba(100,255,100, 0.5)", 1)
              plotdata(y_velo_vals, "red", "rgba(0,0,0, 0)", 0)
          }



          // Clear Rect
          function clear() {
              ctx.clearRect(0, 0, WIDTH, HEIGHT);
          }


          // Get the Max value for the y-axis
          function getmax(values) {
              var curr = 0;
              for (i=0; i<values.length; i++) {
                  if (values[i] > curr) {
                      curr = values[i];
                  }
              }
              return curr;
          }



          // Draw the axes
          function drawaxes(){
              ctx.strokeStyle = "black";

              /* y axis along the left edge of the canvas*/

              ctx.beginPath();
              ctx.moveTo(x_pad, HEIGHT+y_pad*2);
              ctx.lineTo(x_pad,0);
              ctx.stroke();

              /* x axis along the bottom edge of the canvas*/
              ctx.moveTo(0,HEIGHT+y_pad);
              ctx.lineTo(WIDTH+x_pad*2,HEIGHT+y_pad);
              ctx.stroke();
          }


          // Draw the Grid
          function drawgrid() {
              /* y axis grid */
              ctx.strokeStyle = "rgba(100, 100, 100, 0.25)";
              ctx.beginPath();
              var y_spacing = HEIGHT / 10;
              for (i=0; i<10; i++) {
                  var y_pos = HEIGHT+y_pad - (y_spacing * i);
                  ctx.moveTo(x_pad, y_pos);
                  ctx.lineTo(WIDTH, y_pos);                
              }                
              ctx.stroke();
          }


          // Add Labels to the graph
          function addlabels(){
              ctx.font = '12px san-serif';
  
              /* y axis labels */
              var y_spacing = HEIGHT / 10;
              var y_units = max_value / 10;
              for (i=0; i<10; i++) {
                  var y_val = Math.round(y_units * i);
                  var y_pos = HEIGHT+y_pad - (y_spacing * i);
                  ctx.fillText(y_val, label_pad, y_pos);                
              }                

              /* x axis labels */
              for (i=0; i<x_vals.length; i++) {
                  var x_val =x_vals[i];
                  var x_pos = x_pad +(x_spacing * i);
                  ctx.fillText(x_val, x_pos, (HEIGHT+y_pad*2) - label_pad);                
              } 
          }  


          // Draw a graph dot 
          function drawdot(x, y, size) {
              ctx.fillStyle = "rgba(0, 0, 0, 1)"
              ctx.beginPath();
              ctx.arc(x, y, size, 0, Math.PI*2, true);
              ctx.closePath();
              ctx.fill();
          }


          // Plot Data
          function plotdata(values, stroke_color, fill_style, has_dots){
              ctx.strokeStyle = stroke_color;
              ctx.fillStyle = fill_style;
              ctx.beginPath();
              ctx.moveTo(x_pad, HEIGHT+y_pad);
            
              for (j=0; j<values.length; j++){
                  x = x_pad + (j*x_spacing);
                  y = (HEIGHT+y_pad) -((HEIGHT+y_pad) * (values[j]/max_value));
                  ctx.lineTo(x,y);
              }
              ctx.lineTo(x, HEIGHT+y_pad);
              ctx.closePath();
              ctx.stroke();
              ctx.fill();
              if (has_dots == 1) {
                  for (j=0; j<values.length; j++){
                      var x = x_pad + (j*x_spacing);
                      var y = (HEIGHT+y_pad) -((HEIGHT+y_pad) * (values[j]/max_value));
                      drawdot(x, y, 3);
                  }
              }
          }


        init();



        }
        catch(err) {
          alert(err)
          spt.app_busy.hide();
        }
        
      ''']]>
    }</behavior>



 </burndown_chart_wdg>
</config>
"""
