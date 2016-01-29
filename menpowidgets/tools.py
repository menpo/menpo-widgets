from collections import OrderedDict
import ipywidgets
from traitlets.traitlets import List, Int, Float, Dict
from traitlets import link

from menpo.compatibility import unicode

from .abstract import MenpoWidget
from .style import (map_styles_to_hex_colours, convert_image_to_bytes,
                    format_box, format_font, format_slider, format_text_box,
                    parse_font_awesome_icon)
from .utils import (lists_are_the_same, decode_colour, parse_slicing_command,
                    list_has_constant_step, parse_int_range_command,
                    parse_float_range_command)

# Global variables to try and reduce overhead of loading the logo
MENPO_MINIMAL_LOGO = None
MENPO_DANGER_LOGO = None
MENPO_WARNING_LOGO = None
MENPO_SUCCESS_LOGO = None
MENPO_INFO_LOGO = None
MENPO_LOGO_SCALE = None


class LogoWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget with Menpo's logo image. The widget stores the image in
    `self.image` using `ipywidgets.Image`.

    To set the styling of this widget please refer to the `style()` method.

    Parameters
    ----------
    scale : `float`, optional
        Defines the scale that will be applied to the logo image
        (`logos/menpo_thumbnail.jpg`).
    style : ``{'minimal', 'danger', 'info', 'warning', 'success'}``, optional
        Defines the styling of the logo widget, i.e. the colour around the
        logo image.
    """
    def __init__(self, scale=0.3, style='minimal'):
        from menpowidgets.base import menpowidgets_src_dir_path
        import menpo.io as mio
        # Try to only load the logo once
        global MENPO_LOGO_SCALE
        logos_path = menpowidgets_src_dir_path() / 'logos'
        if style == 'minimal':
            global MENPO_MINIMAL_LOGO
            if MENPO_MINIMAL_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_MINIMAL_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_MINIMAL_LOGO))
        elif style == 'danger':
            global MENPO_DANGER_LOGO
            if MENPO_DANGER_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_DANGER_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_DANGER_LOGO))
        elif style == 'info':
            global MENPO_INFO_LOGO
            if MENPO_INFO_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_INFO_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_INFO_LOGO))
        elif style == 'warning':
            global MENPO_WARNING_LOGO
            if MENPO_WARNING_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_WARNING_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_WARNING_LOGO))
        elif style == 'success':
            global MENPO_SUCCESS_LOGO
            if MENPO_SUCCESS_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_SUCCESS_LOGO = image.rescale(scale)
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_SUCCESS_LOGO))
        else:
            raise ValueError("style must be 'minimal', 'info', 'danger', "
                             "'warning' or 'success'; {} was "
                             "given.".format(style))
        super(LogoWidget, self).__init__(children=[self.image])

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0):
        r"""
        Function that defines the style of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)


class ListWidget(MenpoWidget):
    r"""
    Creates a widget for selecting a list with numbers. It supports both
    integers and floats.

    The selected values are stored in the `self.selected_values` `trait`. To
    set the styling of this widget please refer to the `style()` method. To
    update the state and function of the widget, please refer to the
    `set_widget_state()` and `replace_render_function()` methods.

    Parameters
    ----------
    selected_list : `list`
        The initial list of numbers.
    mode : ``{'int', 'float'}``, optional
        Defines the data type of the list members.
    description : `str`, optional
        The description of the command text box.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    example_visible : `bool`, optional
        If `True`, then a line with command examples is printed below the
        main text box.
    """
    def __init__(self, selected_list, mode='float', description='Command:',
                 render_function=None, example_visible=True):
        # Create children
        selected_cmd = ''
        if mode == 'int':
            for i in selected_list:
                selected_cmd += '{}, '.format(i)
            self.example = ipywidgets.Latex(
                value="e.g. '[1, 2]', '10', '10, 20', 'range(10)', "
                      "'range(1, 8, 2)' etc.",
                font_size=11, font_style='italic', visible=example_visible)
        elif mode == 'float':
            for i in selected_list:
                selected_cmd += '{:.1f}, '.format(i)
            self.example = ipywidgets.Latex(
                value="e.g. '10.', '10., 20.', 'range(10.)', "
                      "'range(2.5, 5., 2.)' etc.",
                font_size=11, font_style='italic', visible=example_visible)
        else:
            raise ValueError("mode must be either int or float.")
        self.cmd_text = ipywidgets.Text(value=selected_cmd[:-2],
                                        description=description)
        self.error_msg = ipywidgets.Latex(value='', font_style='italic',
                                          color='#FF0000')

        # Create final widget
        children = [self.cmd_text, self.example, self.error_msg]
        super(ListWidget, self).__init__(
            children, List, selected_list, render_function=render_function,
            orientation='vertical', align='end')

        # Assign properties
        self.mode = mode

        # Set functionality
        def save_cmd(name):
            self.error_msg.value = ''
            try:
                if self.mode == 'int':
                    self.selected_values = parse_int_range_command(
                        str(self.cmd_text.value))
                else:
                    self.selected_values = parse_float_range_command(
                        str(self.cmd_text.value))
            except ValueError as e:
                self.error_msg.value = str(e)
        self.cmd_text.on_submit(save_cmd)

    def set_widget_state(self, selected_list, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        selected_list : `list`
            The selected list.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if not lists_are_the_same(selected_list, self.selected_values):
            # Assign new options dict to selected_values
            selected_cmd = ''
            if self.mode == 'int':
                for i in selected_list:
                    selected_cmd += '{}, '.format(i)
            elif self.mode == 'float':
                for i in selected_list:
                    selected_cmd += '{}, '.format(i)

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update command text and selected values
            self.cmd_text.value = selected_cmd[:-2]
            self.selected_values = selected_list

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', 0)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, text_box_style=None, text_box_background_colour=None,
              text_box_width=None, font_family='', font_size=None,
              font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        text_box_style : `str` or ``None`` (see below), optional
            Command text box style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        text_box_background_colour : `str`, optional
            The background colour of the command text box.
        text_box_width : `str`, optional
            The width of the command text box.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.cmd_text, font_family, font_size, font_style,
                    font_weight)
        self.cmd_text.color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.background_color = map_styles_to_hex_colours(
            text_box_background_colour, background=True)
        self.cmd_text.border_color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.font_family = 'monospace'
        self.cmd_text.border_width = 1
        self.cmd_text.width = text_box_width


class SlicingCommandWidget(MenpoWidget):
    r"""
    Creates a widget for selecting a slicing command.

    The selected values are stored in `self.selected_values` `trait`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    slice_options : `dict`
        The initial slicing options. Example ::

            slice_options = {'command': ':3', 'length': 68}

    description : `str`, optional
        The description of the command text box.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    example_visible : `bool`, optional
        If ``True``, then a line with command examples is printed below the
        main text box.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the slider's handle. If ``False``, then the the functions are
        called only when the handle (mouse click) is released.
    orientation : ``{'horizontal', 'vertical'}``, optional
        The orientation between the command text box and the sliders.
    """
    def __init__(self, slice_options, description='Command:',
                 render_function=None, example_visible=True,
                 continuous_update=False, orientation='horizontal'):
        # Create children
        indices = parse_slicing_command(slice_options['command'],
                                        slice_options['length'])
        self.cmd_text = ipywidgets.Text(value=slice_options['command'],
                                        description=description)
        self.example = ipywidgets.Latex(
            value="e.g. ':3', '-3:', '1:{}:2', '3::', '0, {}', '7', "
                  "'range({})' etc.".format(slice_options['length'],
                                            slice_options['length'],
                                            slice_options['length']),
            font_size=11, font_style='italic', visible=example_visible)
        self.error_msg = ipywidgets.Latex(value='', font_style='italic',
                                          color='#FF0000')
        self.single_slider = ipywidgets.IntSlider(
            min=0, max=slice_options['length'] - 1, value=0, width='6.8cm',
            visible=self._single_slider_visible(indices),
            continuous_update=continuous_update)
        self.multiple_slider = ipywidgets.IntRangeSlider(
            min=0, max=slice_options['length'] - 1,
            value=(indices[0], indices[-1]),
            width='6.8cm',
            visible=self._multiple_slider_visible(indices)[0],
            continuous_update=continuous_update)
        self.command_error_box = ipywidgets.VBox(
            children=[self.cmd_text, self.example, self.error_msg], align='end',
            margin='0.1cm')
        self.sliders_box = ipywidgets.VBox(
            children=[self.single_slider, self.multiple_slider], align='start',
            margin='0.1cm')

        # Create final widget
        children = [self.command_error_box, self.sliders_box]
        align = 'end'
        if orientation == 'horizontal':
            align = 'start'
        super(SlicingCommandWidget, self).__init__(
            children, List, indices, render_function=render_function,
            orientation=orientation, align=align)

        # Assign properties
        self.length = slice_options['length']

        # Set functionality
        def save_cmd(name):
            self.error_msg.value = ''
            try:
                self.selected_values = parse_slicing_command(
                    str(self.cmd_text.value), self.length)
            except ValueError as e:
                self.error_msg.value = str(e)

            # set single slider visibility and value
            vis = self._single_slider_visible(self.selected_values)
            self.single_slider.visible = vis
            if vis:
                self.single_slider.value = self.selected_values[0]

            # set multiple slider visibility and value
            vis, step = self._multiple_slider_visible(self.selected_values)
            self.multiple_slider.visible = vis
            if vis:
                self.multiple_slider.step = step
                self.multiple_slider.value = (self.selected_values[0],
                                              self.selected_values[-1])
        self.cmd_text.on_submit(save_cmd)

        def single_slider_value(name, value):
            self.selected_values = [value]
            self.cmd_text.value = str(value)
        self.single_slider.observe(single_slider_value, names='value')

        def multiple_slider_value(value):
            self.selected_values = list(range(value[0], value[1]+1,
                                              self.multiple_slider.step))
            self.cmd_text.value = "{}:{}:{}".format(value[0], value[1]+1,
                                                    self.multiple_slider.step)
        self.multiple_slider.observe(multiple_slider_value, names='value')

    def _single_slider_visible(self, selected_values):
        return len(selected_values) == 1

    def _multiple_slider_visible(self, selected_values):
        return list_has_constant_step(selected_values)

    def set_widget_state(self, slice_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        slice_options : `dict`
            The initial slicing options. Example ::

                slice_options = {'command': '10', 'length': 30}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        self.length = slice_options['length']

        # decode command
        indices = parse_slicing_command(slice_options['command'],
                                        slice_options['length'])

        if not lists_are_the_same(indices, self.selected_values):
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update selected values
            self.selected_values = indices

            # update single slider
            vis = self._single_slider_visible(self.selected_values)
            self.single_slider.visible = vis
            self.single_slider.max = self.length - 1
            if vis:
                self.single_slider.value = self.selected_values[0]

            # update multiple slider
            vis, step = self._multiple_slider_visible(self.selected_values)
            self.multiple_slider.visible = vis
            self.multiple_slider.max = self.length - 1
            if vis:
                self.multiple_slider.step = step
                self.multiple_slider.value = (self.selected_values[0],
                                              self.selected_values[-1])

            # update command text
            self.cmd_text.value = slice_options['command']

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', 0)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, text_box_style=None, text_box_background_colour=None,
              text_box_width=None, font_family='', font_size=None,
              font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        text_box_style : `str` or ``None`` (see below), optional
            Command text box style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        text_box_background_colour : `str`, optional
            The background colour of the command text box.
        text_box_width : `str`, optional
            The width of the command text box.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.cmd_text, font_family, font_size, font_style,
                    font_weight)
        self.cmd_text.color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.background_color = map_styles_to_hex_colours(
            text_box_background_colour, background=True)
        self.cmd_text.border_color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.font_family = 'monospace'
        self.cmd_text.border_width = 1
        self.cmd_text.width = text_box_width
        self.single_slider.slider_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.single_slider.background_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.multiple_slider.slider_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.multiple_slider.background_color = map_styles_to_hex_colours(
            box_style, background=False)


class IndexSliderWidget(MenpoWidget):
    r"""
    Creates a widget for selecting an index using a slider.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `set_render_function()` methods.

    Parameters
    ----------
    index : `dict`
        The dictionary with the default options. For example ::

            index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

    description : `str`, optional
        The title of the widget.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while moving
        the slider's handle. If ``False``, then the the functions are called only
        when the handle (mouse click) is released.
    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, index, description='Index: ', continuous_update=False,
                 render_function=None):
        # Create children
        self.slider = ipywidgets.IntSlider(
            min=index['min'], max=index['max'], value=index['index'],
            step=index['step'], description=description, width='5cm',
            continuous_update=continuous_update)

        # Create final widget
        children = [self.slider]
        super(IndexSliderWidget, self).__init__(
            children, Int, index['index'], render_function=render_function,
            orientation='vertical', align='start')

        # Set functionality
        def save_index(name, value):
            self.selected_values = value
        self.slider.observe(save_index, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='6cm', slider_bar_colour=None,
              slider_handle_colour=None, slider_text_visible=True):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        slider_width : `float`, optional
            The width of the slider
        slider_bar_colour : `str`, optional
            The colour of the slider's bar.
        slider_handle_colour : `str`, optional
            The colour of the slider's handle.
        slider_text_visible : `bool`, optional
            Whether the selected value of the slider is visible.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style,
                    font_weight)
        format_slider(self.slider, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=slider_text_visible)

    def set_widget_state(self, index, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        index : `dict`
            The dictionary with the selected options. For example ::

                index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (index['index'] != self.selected_values or
                index['min'] != self.slider.min or
                index['max'] != self.slider.max or
                index['step'] != self.slider.step):
            # temporarily remove render function
            render_function = self._render_function
            self.remove_render_function()

            # set values to slider
            self.slider.min = index['min']
            self.slider.max = index['max']
            self.slider.step = index['step']
            self.slider.value = index['index']

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', 0)


class IndexButtonsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting an index using plus/minus buttons.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    index : `dict`
        The dictionary with the default options. For example ::

            index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that decreases the index. If the `str`
        starts with `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that increases the index. If the `str` starts
        with `'fa-'`, then a font-awesome icon is defined.
    loop_enabled : `bool`, optional
        If ``True``, then if by pressing the buttons we reach the minimum
        (maximum) index values, then the counting will continue from the end
        (beginning). If ``False``, the counting will stop at the minimum
        (maximum) value.
    text_editable : `bool`, optional
        Flag that determines whether the index text will be editable.
    """
    def __init__(self, index, render_function=None, description='Index: ',
                 minus_description='fa-minus', plus_description='fa-plus',
                 loop_enabled=True, text_editable=True):
        # Create children
        self.title = ipywidgets.Latex(value=description, padding=6, margin=6)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.button_minus = ipywidgets.Button(description=m_description,
                                              icon=m_icon, width='1cm')
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.button_plus = ipywidgets.Button(description=p_description,
                                             icon=p_icon, width='1cm')
        self.index_text = ipywidgets.BoundedIntText(
            value=index['index'], min=index['min'], max=index['max'],
            disabled=not text_editable)

        # Create final widget
        children = [self.title, self.button_minus, self.index_text,
                    self.button_plus]
        super(IndexButtonsWidget, self).__init__(
            children, Int, index['index'], render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']
        self.loop_enabled = loop_enabled
        self.text_editable = text_editable

        # Set functionality
        def value_plus(name):
            tmp_val = int(self.index_text.value) + self.step
            if tmp_val > self.max:
                if self.loop_enabled:
                    self.index_text.value = str(self.min)
                else:
                    self.index_text.value = str(self.max)
            else:
                self.index_text.value = str(tmp_val)
        self.button_plus.on_click(value_plus)

        def value_minus(name):
            tmp_val = int(self.index_text.value) - self.step
            if tmp_val < self.min:
                if self.loop_enabled:
                    self.index_text.value = str(self.max)
                else:
                    self.index_text.value = str(self.min)
            else:
                self.index_text.value = str(tmp_val)
        self.button_minus.on_click(value_minus)

        def save_index(name, value):
            self.selected_values = int(value)
        self.index_text.observe(save_index, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', minus_style='', plus_style='',
              text_colour=None, text_background_colour=None):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        minus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        plus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        text_colour : `str`, optional
            The text colour of the index text.
        text_background_colour : `str`, optional
            The background colour of the index text.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.index_text, font_family, font_size, font_style,
                    font_weight)
        self.button_minus.button_style = minus_style
        self.button_plus.button_style = plus_style
        format_text_box(self.index_text, text_colour, text_background_colour)

    def set_widget_state(self, index, loop_enabled, text_editable,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        index : `dict`
            The dictionary with the selected options. For example ::

                index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

        loop_enabled : `bool`, optional
            If ``True``, then if by pressing the buttons we reach the minimum
            (maximum) index values, then the counting will continue from the end
            (beginning). If ``False``, the counting will stop at the minimum
            (maximum) value.
        text_editable : `bool`, optional
            Flag that determines whether the index text will be editable.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Update loop_enabled and text_editable
        self.loop_enabled = loop_enabled
        self.text_editable = text_editable
        self.index_text.disabled = not text_editable

        # Check if update is required
        if (index['index'] != self.selected_values or
            index['min'] != self.min or index['max'] != self.max or
            index['step'] != self.step):
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # set value to index text
            self.min = index['min']
            self.max = index['max']
            self.step = index['step']
            self.index_text.min = index['min']
            self.index_text.max = index['max']
            self.index_text.value = str(index['index'])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', 0)


class ColourSelectionWidget(MenpoWidget):
    r"""
    Creates a widget for colour selection of a single or multiple objects.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    colours_list : `list` of `str` or [`float`, `float`, `float`]
        If `str`, it must either a hex code or a colour name, such as ::

            {'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black',
            'white', 'pink', 'orange'}

        If [`float`, `float`, `float`], it defines an RGB value and must have
        length 3.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The description of the widget.
    labels : `list` or ``None``, optional
        A `list` with the labels' names. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined.
    """
    def __init__(self, colours_list, render_function=None, description='Colour',
                 labels=None):
        # Check if multiple mode should be enabled
        if isinstance(colours_list, str) or isinstance(colours_list, unicode):
            colours_list = [colours_list]
        n_labels = len(colours_list)
        multiple = n_labels > 1

        # Decode the colour of the first label
        default_colour = decode_colour(colours_list[0])

        # Create children
        labels_dict = OrderedDict()
        if labels is None:
            labels = []
            for k in range(n_labels):
                labels_dict["label {}".format(k)] = k
                labels.append("label {}".format(k))
        else:
            for k, l in enumerate(labels):
                labels_dict[l] = k
        self.label_dropdown = ipywidgets.Dropdown(description=description,
                                                  options=labels_dict, value=0)
        self.apply_to_all_button = ipywidgets.Button(
            description=' Apply to all', icon='fa-paint-brush')
        self.labels_box = ipywidgets.VBox(
            children=[self.label_dropdown, self.apply_to_all_button],
            visible=multiple, align='end')
        colour_description = ''
        if not multiple:
            colour_description = description
        self.colour_widget = ipywidgets.ColorPicker(
            value=default_colour, description=colour_description)

        # Create final widget
        children = [self.labels_box, self.colour_widget]
        super(ColourSelectionWidget, self).__init__(
            children, List, colours_list, render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.labels = labels
        self.description = description

        # Set functionality
        def apply_to_all_function(name):
            tmp = str(self.colour_widget.value)
            self.selected_values = [tmp] * len(self.selected_values)
            self.label_dropdown.value = 0
        self.apply_to_all_button.on_click(apply_to_all_function)

        def update_colour_wrt_label(name, value):
            self.colour_widget.value = decode_colour(
                self.selected_values[value])
        self.label_dropdown.observe(update_colour_wrt_label, names='value')

        def save_colour(name, value):
            idx = self.label_dropdown.value
            tmp = [v for v in self.selected_values]
            tmp[idx] = str(self.colour_widget.value)
            self.selected_values = tmp
        self.colour_widget.observe(save_colour, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', label_colour=None, label_background_colour=None,
              picker_colour=None, picker_background_colour=None,
              apply_to_all_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the cornerns of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        label_colour : `str`, optional
            The text colour of the labels dropdown selection.
        label_background_colour : `str`, optional
            The background colour of the labels dropdown selection.
        picker_colour : `str`, optional
            The text colour of the colour picker.
        picker_background_colour : `str`, optional
            The background colour of the colour picker.
        apply_to_all_style : `str`,
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.label_dropdown, font_family, font_size, font_style,
                    font_weight)
        format_font(self.apply_to_all_button, font_family, font_size,
                    font_style, font_weight)
        format_font(self.colour_widget, font_family, font_size, font_style,
                    font_weight)
        format_text_box(self.label_dropdown, label_colour,
                        label_background_colour)
        format_text_box(self.colour_widget, picker_colour,
                        picker_background_colour)
        self.apply_to_all_button.button_style = apply_to_all_style

    def set_widget_state(self, colours_list, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided
        `colours_list` and `labels` values are different than
        `self.selected_values()`.

        Parameters
        ----------
        colours_list : `list` of `str` or [`float`, `float`, `float`]
            If `str`, it must either a hex code or a colour name, such as ::

                {'blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
                'black', 'white'}

            If [`float`, `float`, `float`], it defines an RGB value and must have
            length 3.
        labels : `list` or ``None``, optional
            A `list` with the labels' names. If ``None``, then a `list` of the
            form ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if labels is None:
            labels = ["label {}".format(k) for k in range(len(colours_list))]

        sel_colours = self.selected_values
        sel_labels = self.labels
        if (lists_are_the_same(sel_colours, colours_list) and
                not lists_are_the_same(sel_labels, labels)):
            # the provided colours are the same, but the labels changed, so
            # update the labels
            self.labels = labels
            labels_dict = OrderedDict()
            for k, l in enumerate(labels):
                labels_dict[l] = k
            self.label_dropdown.options = labels_dict
            if len(labels) > 1:
                if self.label_dropdown.value > 0:
                    self.label_dropdown.value = 0
                else:
                    self.label_dropdown.value = 1
                    self.label_dropdown.value = 0
        elif (not lists_are_the_same(sel_colours, colours_list) and
              lists_are_the_same(sel_labels, labels)):
            # the provided labels are the same, but the colours are different
            # temporarily remove render_function from r, g, b traits
            render_function = self._render_function
            self.remove_render_function()
            # assign colour
            self.selected_values = colours_list
            k = self.label_dropdown.value
            self.colour_widget.value = decode_colour(colours_list[k])
            # re-assign render_function
            self.add_render_function(render_function)
            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)
        elif (not lists_are_the_same(sel_colours, colours_list) and
              not lists_are_the_same(sel_labels, labels)):
            # temporarily remove render_function from r, g, b traits
            render_function = self._render_function
            self.remove_render_function()
            # both the colours and the labels are different
            self.labels_box.visible = len(labels) > 1
            if len(labels) > 1:
                self.colour_widget.description = ''
            else:
                self.colour_widget.description = self.description
            self.selected_values = colours_list
            self.labels = labels
            labels_dict = OrderedDict()
            for k, l in enumerate(labels):
                labels_dict[l] = k
            self.label_dropdown.options = labels_dict
            if len(labels) > 1:
                if self.label_dropdown.value > 0:
                    self.label_dropdown.value = 0
                else:
                    self.label_dropdown.value = 1
                    self.label_dropdown.value = 0
            else:
                self.label_dropdown.value = 0
            # update colour widgets
            self.colour_widget.value = decode_colour(colours_list[0])
            # re-assign render_function
            self.add_render_function(render_function)
            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class ZoomOneScaleWidget(MenpoWidget):
    r"""
    Creates a widget for selecting zoom options with a single scale.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    zoom_options : `dict`
        The dictionary with the default options. For example ::

            zoom_options = {'min': 0.1, 'max': 4., 'step': 0.05, 'zoom': 1.}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that zooms_out. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that zooms in. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the zoom slider's handle. If ``False``, then the the functions
        are called only when the handle (mouse click) is released.
    """
    def __init__(self, zoom_options, render_function=None,
                 description='Figure scale: ',
                 minus_description='fa-search-minus',
                 plus_description='fa-search-plus', continuous_update=False):
        # Create children
        self.title = ipywidgets.Latex(value=description, padding=6, margin=6)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.button_minus = ipywidgets.Button(description=m_description,
                                              icon=m_icon, width='1cm')
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.button_plus = ipywidgets.Button(description=p_description,
                                             icon=p_icon, width='1cm')
        self.zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options['zoom'], min=zoom_options['min'],
            max=zoom_options['max'], step=zoom_options['step'], readout=False,
            width='6cm', continuous_update=continuous_update)
        self.zoom_text = ipywidgets.BoundedFloatText(
            value=zoom_options['zoom'], min=zoom_options['min'],
            max=zoom_options['max'], width='1.5cm')

        # Create final widget
        children = [self.title, self.button_minus, self.zoom_slider,
                    self.button_plus, self.zoom_text]
        super(ZoomOneScaleWidget, self).__init__(
            children, Float, zoom_options['zoom'],
            render_function=render_function, orientation='horizontal',
            align='start')

        # Link the zoom text and slider
        link((self.zoom_slider, 'value'), (self.zoom_text, 'value'))

        # Set functionality
        def value_plus(name):
            tmp_val = float(self.zoom_text.value) + self.zoom_slider.step
            if tmp_val > self.zoom_slider.max:
                self.zoom_text.value = "{:.2f}".format(self.zoom_slider.max)
            else:
                self.zoom_text.value = "{:.2f}".format(tmp_val)
        self.button_plus.on_click(value_plus)

        def value_minus(name):
            tmp_val = float(self.zoom_text.value) - self.zoom_slider.step
            if tmp_val < self.zoom_slider.min:
                self.zoom_text.value = "{:.2f}".format(self.zoom_slider.min)
            else:
                self.zoom_text.value = "{:.2f}".format(tmp_val)
        self.button_minus.on_click(value_minus)

        def save_zoom_slider(name, value):
            self.selected_values = value
        self.zoom_slider.observe(save_zoom_slider, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='6cm'):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        slider_width : `float`, optional
            The width of the slider
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.zoom_text, font_family, font_size, font_style,
                    font_weight)
        if box_style not in ['', None]:
            self.button_minus.button_style = 'primary'
            self.button_plus.button_style = 'primary'
        else:
            self.button_minus.button_style = None
            self.button_plus.button_style = None
        format_slider(self.zoom_slider, slider_width=slider_width,
                      slider_handle_colour=map_styles_to_hex_colours(box_style),
                      slider_bar_colour=map_styles_to_hex_colours(box_style),
                      slider_text_visible=False)

    def set_widget_state(self, zoom_options, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        zoom_options : `dict`
            The dictionary with the selected options. For example ::

                zoom_options = {'min': 0.1, 'max': 4., 'step': 0.05, 'zoom': 1.}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (zoom_options['zoom'] != self.selected_values or
            zoom_options['min'] != self.zoom_slider.min or
            zoom_options['max'] != self.zoom_slider.max or
                zoom_options['step'] != self.zoom_slider.step):
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update widgets
            self.zoom_text.min = zoom_options['min']
            self.zoom_slider.min = zoom_options['min']
            self.zoom_text.max = zoom_options['max']
            self.zoom_slider.max = zoom_options['max']
            self.zoom_slider.step = zoom_options['step']
            self.zoom_text.value = "{:.2f}".format(zoom_options['zoom'])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class ZoomTwoScalesWidget(MenpoWidget):
    r"""
    Creates a widget for selecting zoom options with a single scale.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    zoom_options : `dict`
        The dictionary with the default options. For example ::

            zoom_options = {'zoom': [1., 1.], 'min': 0.1, 'max': 4.,
                            'step': 0.05, 'lock_aspect_ratio': False}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that zooms_out. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that zooms in. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the zoom slider's handle. If ``False``, then the the functions
        are called only when the handle (mouse click) is released.
    """
    def __init__(self, zoom_options, render_function=None,
                 description='Figure scale: ',
                 minus_description='fa-search-minus',
                 plus_description='fa-search-plus', continuous_update=False):
        # Create children
        self.title = ipywidgets.Latex(value=description, padding=6, margin=6)
        self.x_title = ipywidgets.Latex(value='X', padding=6, margin=6)
        self.y_title = ipywidgets.Latex(value='Y', padding=6, margin=6)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.x_button_minus = ipywidgets.Button(description=m_description,
                                                icon=m_icon, width='1cm')
        self.y_button_minus = ipywidgets.Button(description=m_description,
                                                icon=m_icon, width='1cm')
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.x_button_plus = ipywidgets.Button(description=p_description,
                                               icon=p_icon, width='1cm')
        self.y_button_plus = ipywidgets.Button(description=p_description,
                                               icon=p_icon, width='1cm')
        self.x_zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options['zoom'][0], min=zoom_options['min'],
            max=zoom_options['max'], readout=False, width='6cm',
            continuous_update=continuous_update)
        self.y_zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options['zoom'][1], min=zoom_options['min'],
            max=zoom_options['max'], readout=False, width='6cm',
            continuous_update=continuous_update)
        self.x_zoom_text = ipywidgets.BoundedFloatText(
            value=zoom_options['zoom'][0], min=zoom_options['min'],
            max=zoom_options['max'], width='1.5cm')
        self.y_zoom_text = ipywidgets.BoundedFloatText(
            value=zoom_options['zoom'][1], min=zoom_options['min'],
            max=zoom_options['max'], width='1.5cm')
        self.x_box = ipywidgets.HBox(
            children=[self.x_title, self.x_button_minus, self.x_zoom_slider,
                      self.x_button_plus, self.x_zoom_text], margin='0.05cm')
        self.y_box = ipywidgets.HBox(
            children=[self.y_title, self.y_button_minus, self.y_zoom_slider,
                      self.y_button_plus, self.y_zoom_text], margin='0.05cm')
        self.x_y_box = ipywidgets.VBox(children=[self.x_box, self.y_box])
        self.lock_link = ipywidgets.jslink((self.x_zoom_slider, 'value'),
                                           (self.y_zoom_slider, 'value'))
        lock_icon = 'fa-link'
        if not zoom_options['lock_aspect_ratio']:
            lock_icon = 'fa-unlink'
            self.lock_link.unlink()
        self.lock_aspect_button = ipywidgets.ToggleButton(
            value=zoom_options['lock_aspect_ratio'], description='',
            icon=lock_icon)
        self.options_box = ipywidgets.HBox(
            children=[self.lock_aspect_button, self.x_y_box], align='center')

        # Create final widget
        children = [self.title, self.options_box]
        super(ZoomTwoScalesWidget, self).__init__(
            children, List, zoom_options['zoom'],
            render_function=render_function, orientation='horizontal',
            align='center')

        # Link the zoom texts and sliders
        link((self.x_zoom_slider, 'value'), (self.x_zoom_text, 'value'))
        link((self.y_zoom_slider, 'value'), (self.y_zoom_text, 'value'))

        # Assign properties
        self.lock_aspect_ratio = zoom_options['lock_aspect_ratio']

        # Set functionality
        def x_value_plus(name):
            tmp_val = float(self.x_zoom_text.value) + self.x_zoom_slider.step
            if tmp_val > self.x_zoom_slider.max:
                self.x_zoom_text.value = "{:.2f}".format(
                    self.x_zoom_slider.max)
            else:
                self.x_zoom_text.value = "{:.2f}".format(tmp_val)
        self.x_button_plus.on_click(x_value_plus)

        def x_value_minus(name):
            tmp_val = float(self.x_zoom_text.value) - self.x_zoom_slider.step
            if tmp_val < self.x_zoom_slider.min:
                self.x_zoom_text.value = "{:.2f}".format(
                    self.x_zoom_slider.min)
            else:
                self.x_zoom_text.value = "{:.2f}".format(tmp_val)
        self.x_button_minus.on_click(x_value_minus)

        def y_value_plus(name):
            tmp_val = float(self.y_zoom_text.value) + self.y_zoom_slider.step
            if tmp_val > self.y_zoom_slider.max:
                self.y_zoom_text.value = "{:.2f}".format(
                    self.y_zoom_slider.max)
            else:
                self.y_zoom_text.value = "{:.2f}".format(tmp_val)
        self.y_button_plus.on_click(y_value_plus)

        def y_value_minus(name):
            tmp_val = float(self.y_zoom_text.value) - self.y_zoom_slider.step
            if tmp_val < self.y_zoom_slider.min:
                self.y_zoom_text.value = "{:.2f}".format(
                    self.y_zoom_slider.min)
            else:
                self.y_zoom_text.value = "{:.2f}".format(tmp_val)
        self.y_button_minus.on_click(y_value_minus)

        def save_zoom(name, value):
            if self.lock_aspect_ratio:
                self.selected_values = [value, value]
            else:
                self.selected_values = [self.x_zoom_slider.value,
                                        self.y_zoom_slider.value]
        self.x_zoom_slider.observe(save_zoom, names='value')
        self.y_zoom_slider.observe(save_zoom, names='value')

        def link_button(name, value):
            self.lock_aspect_ratio = value
            if value:
                self.lock_aspect_button.icon = 'fa-link'
                self.lock_link = link((self.x_zoom_slider, 'value'),
                                      (self.y_zoom_slider, 'value'))
                self.selected_values = [self.x_zoom_slider.value,
                                        self.x_zoom_slider.value]
            else:
                self.lock_aspect_button.icon = 'fa-unlink'
                self.lock_link.unlink()
        self.lock_aspect_button.observe(link_button, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='6cm'):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        slider_width : `float`, optional
            The width of the slider
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_zoom_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_zoom_text, font_family, font_size, font_style,
                    font_weight)
        if box_style not in ['', None]:
            self.x_button_minus.button_style = 'primary'
            self.x_button_plus.button_style = 'primary'
            self.y_button_minus.button_style = 'primary'
            self.y_button_plus.button_style = 'primary'
            self.lock_aspect_button.button_style = 'warning'
        else:
            self.x_button_minus.button_style = None
            self.x_button_plus.button_style = None
            self.y_button_minus.button_style = None
            self.y_button_plus.button_style = None
            self.lock_aspect_button.button_style = None
        format_slider(self.x_zoom_slider, slider_width=slider_width,
                      slider_handle_colour=map_styles_to_hex_colours(box_style),
                      slider_bar_colour=map_styles_to_hex_colours(box_style),
                      slider_text_visible=False)
        format_slider(self.y_zoom_slider, slider_width=slider_width,
                      slider_handle_colour=map_styles_to_hex_colours(box_style),
                      slider_bar_colour=map_styles_to_hex_colours(box_style),
                      slider_text_visible=False)

    def set_widget_state(self, zoom_options, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        zoom_options : `dict`
            The dictionary with the selected options. For example ::

            zoom_options = {'zoom_x': 1., 'zoom_y': 1.,
                            'min': 0.1, 'max': 4., 'step': 0.05}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (not lists_are_the_same(zoom_options['zoom'],
                                   self.selected_values) or
                zoom_options['min'] != self.x_zoom_slider.min or
                zoom_options['max'] != self.x_zoom_slider.max or
                zoom_options['step'] != self.x_zoom_slider.step):
            # temporarily remove render and update functions
            render_function = self._render_function
            self.remove_render_function()

            # update widgets
            self.x_zoom_text.min = zoom_options['min']
            self.x_zoom_slider.min = zoom_options['min']
            self.y_zoom_text.min = zoom_options['min']
            self.y_zoom_slider.min = zoom_options['min']
            self.x_zoom_text.max = zoom_options['max']
            self.x_zoom_slider.max = zoom_options['max']
            self.y_zoom_text.max = zoom_options['max']
            self.y_zoom_slider.max = zoom_options['max']
            self.x_zoom_slider.step = zoom_options['step']
            self.y_zoom_slider.step = zoom_options['step']
            self.x_zoom_text.value = "{:.2f}".format(zoom_options['zoom'][0])
            self.y_zoom_text.value = "{:.2f}".format(zoom_options['zoom'][1])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class ImageOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting image rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    image_options : `dict`
        The initial image options. Example ::

            image_options = {'alpha': 1.,
                             'interpolation': 'bilinear',
                             'cmap_name': 'gray'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, image_options, render_function=None):
        # Create children
        self.interpolation_checkbox = ipywidgets.Checkbox(
            description='Pixelated',
            value=image_options['interpolation'] == 'none')
        self.alpha_slider = ipywidgets.FloatSlider(
            description='Alpha', value=image_options['alpha'],
            min=0.0, max=1.0, step=0.05, width='4cm', continuous_update=False)
        cmap_dict = OrderedDict()
        cmap_dict['None'] = None
        cmap_dict['afmhot'] = 'afmhot'
        cmap_dict['autumn'] = 'autumn'
        cmap_dict['binary'] = 'binary'
        cmap_dict['bone'] = 'bone'
        cmap_dict['brg'] = 'brg'
        cmap_dict['bwr'] = 'bwr'
        cmap_dict['cool'] = 'cool'
        cmap_dict['coolwarm'] = 'coolwarm'
        cmap_dict['copper'] = 'copper'
        cmap_dict['cubehelix']= 'cubehelix'
        cmap_dict['flag'] = 'flag'
        cmap_dict['gist_earth'] = 'gist_earth'
        cmap_dict['gist_heat'] = 'gist_heat'
        cmap_dict['gist_gray'] = 'gist_gray'
        cmap_dict['gist_ncar'] = 'gist_ncar'
        cmap_dict['gist_rainbow'] = 'gist_rainbow'
        cmap_dict['gist_stern'] = 'gist_stern'
        cmap_dict['gist_yarg'] = 'gist_yarg'
        cmap_dict['gnuplot'] = 'gnuplot'
        cmap_dict['gnuplot2'] = 'gnuplot2'
        cmap_dict['gray'] = 'gray'
        cmap_dict['hot'] = 'hot'
        cmap_dict['hsv'] = 'hsv'
        cmap_dict['jet'] = 'jet'
        cmap_dict['nipy_spectral'] = 'nipy_spectral'
        cmap_dict['ocean'] = 'ocean'
        cmap_dict['pink'] = 'pink'
        cmap_dict['prism'] = 'prism'
        cmap_dict['rainbow'] = 'rainbow'
        cmap_dict['seismic'] = 'seismic'
        cmap_dict['spectral'] = 'spectral'
        cmap_dict['spring'] = 'spring'
        cmap_dict['summer'] = 'summer'
        cmap_dict['terrain'] = 'terrain'
        cmap_dict['winter'] = 'winter'
        self.cmap_select = ipywidgets.Select(
            options=cmap_dict, value='gray', description='Colourmap',
            width='3cm', height='2cm')
        self.alpha_interpolation_box = ipywidgets.VBox(children=[
            self.alpha_slider, self.interpolation_checkbox])

        # Create final widget
        children = [self.cmap_select, self.alpha_interpolation_box]
        super(ImageOptionsWidget, self).__init__(
            children, Dict, image_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def save_interpolation(name, value):
            if value:
                interpolation = 'none'
            else:
                interpolation = 'bilinear'
            tmp = self.selected_values
            self.selected_values = {'interpolation': interpolation,
                                    'alpha': tmp['alpha'],
                                    'cmap_name': tmp['cmap_name']}
        self.interpolation_checkbox.observe(save_interpolation, names='value')

        def save_alpha(name, value):
            tmp = self.selected_values
            self.selected_values = {'interpolation': tmp['interpolation'],
                                    'alpha': value,
                                    'cmap_name': tmp['cmap_name']}
        self.alpha_slider.observe(save_alpha, names='value')

        def save_cmap(name, value):
            tmp = self.selected_values
            self.selected_values = {'interpolation': tmp['interpolation'],
                                    'alpha': tmp['alpha'],
                                    'cmap_name': value}
        self.cmap_select.observe(save_cmap, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.alpha_slider, font_family, font_size, font_style,
                    font_weight)
        format_font(self.interpolation_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.cmap_select, font_family, font_size, font_style,
                    font_weight)
        format_slider(self.alpha_slider, slider_width='4cm',
                      slider_handle_colour=map_styles_to_hex_colours(box_style),
                      slider_bar_colour=map_styles_to_hex_colours(box_style),
                      slider_text_visible=True)

    def set_widget_state(self, image_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        image_options : `dict`
            The image options. Example ::

                image_options = {'alpha': 1.,
                                 'interpolation': 'bilinear',
                                 'cmap_name': 'gray'}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if image_options != self.selected_values:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.alpha_slider.value = image_options['alpha']
            self.interpolation_checkbox.value = \
                image_options['interpolation'] == 'none'
            self.cmap_select.value = image_options['cmap_name']

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class LineOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting line rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    line_options : `dict`
        The initial line options. Example ::

            line_options = {'render_lines': True, 'line_width': 1,
                            'line_colour': ['blue'], 'line_style': '-'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    labels : `list` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """
    def __init__(self, line_options, render_function=None,
                 render_checkbox_title='Render lines', labels=None):
        # Create children
        self.render_lines_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=line_options['render_lines'])
        self.line_width_text = ipywidgets.BoundedFloatText(
            description='Width', value=line_options['line_width'], min=0.,
            max=10**6)
        line_style_dict = OrderedDict()
        line_style_dict['solid'] = '-'
        line_style_dict['dashed'] = '--'
        line_style_dict['dash-dot'] = '-.'
        line_style_dict['dotted'] = ':'
        self.line_style_dropdown = ipywidgets.Dropdown(
            options=line_style_dict, value=line_options['line_style'],
            description='Style')
        self.line_colour_widget = ColourSelectionWidget(
            line_options['line_colour'], description='Colour', labels=labels,
            render_function=None)
        self.line_options_box = ipywidgets.Box(
            children=[self.line_style_dropdown, self.line_width_text,
                      self.line_colour_widget])

        # Create final widget
        children = [self.render_lines_checkbox, self.line_options_box]
        super(LineOptionsWidget, self).__init__(
            children, Dict, line_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def line_options_visible(name, value):
            self.line_options_box.visible = value
        line_options_visible('', line_options['render_lines'])
        self.render_lines_checkbox.observe(line_options_visible,
                                                   names='value')

        def save_options(name, value):
            self.selected_values = {
                'render_lines': self.render_lines_checkbox.value,
                'line_width': float(self.line_width_text.value),
                'line_colour': self.line_colour_widget.selected_values,
                'line_style': self.line_style_dropdown.value}
        self.render_lines_checkbox.observe(save_options, names='value')
        self.line_width_text.observe(save_options, names='value')
        self.line_colour_widget.observe(save_options, names='selected_values')
        self.line_style_dropdown.observe(save_options, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_lines_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.line_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.line_width_text, font_family, font_size, font_style,
                    font_weight)
        self.line_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')

    def set_widget_state(self, line_options, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        line_options : `dict`
            The new set of options. For example ::

                line_options = {'render_lines': True,
                                'line_width': 2,
                                'line_colour': ['red'],
                                'line_style': '-'}

        labels : `list` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != line_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_lines_checkbox.value = line_options['render_lines']
            self.line_style_dropdown.value = line_options['line_style']
            self.line_width_text.value = float(line_options['line_width'])
            self.line_colour_widget.set_widget_state(
                line_options['line_colour'], labels=labels,
                allow_callback=False)

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class MarkerOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting marker rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    marker_options : `dict`
        The initial marker options. Example ::

            marker_options = {'render_markers': True,
                              'marker_size': 20,
                              'marker_face_colour': ['red'],
                              'marker_edge_colour': ['black'],
                              'marker_style': 'o',
                              'marker_edge_width': 1}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render marker checkbox.
    labels : `list` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """
    def __init__(self, marker_options, render_function=None,
                 render_checkbox_title='Render markers', labels=None):
        # Create children
        self.render_markers_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=marker_options['render_markers'])
        self.marker_size_text = ipywidgets.BoundedIntText(
            description='Size', value=marker_options['marker_size'], min=0,
            max=10**6)
        self.marker_edge_width_text = ipywidgets.BoundedFloatText(
            description='Edge width', min=0., max=10**6,
            value=marker_options['marker_edge_width'])
        marker_style_dict = OrderedDict()
        marker_style_dict['point'] = '.'
        marker_style_dict['pixel'] = ','
        marker_style_dict['circle'] = 'o'
        marker_style_dict['triangle down'] = 'v'
        marker_style_dict['triangle up'] = '^'
        marker_style_dict['triangle left'] = '<'
        marker_style_dict['triangle right'] = '>'
        marker_style_dict['tri down'] = '1'
        marker_style_dict['tri up'] = '2'
        marker_style_dict['tri left'] = '3'
        marker_style_dict['tri right'] = '4'
        marker_style_dict['octagon'] = '8'
        marker_style_dict['square'] = 's'
        marker_style_dict['pentagon'] = 'p'
        marker_style_dict['star'] = '*'
        marker_style_dict['hexagon 1'] = 'h'
        marker_style_dict['hexagon 2'] = 'H'
        marker_style_dict['plus'] = '+'
        marker_style_dict['x'] = 'x'
        marker_style_dict['diamond'] = 'D'
        marker_style_dict['thin diamond'] = 'd'
        self.marker_style_dropdown = ipywidgets.Dropdown(
            options=marker_style_dict, value=marker_options['marker_style'],
            description='Style')
        self.marker_box_1 = ipywidgets.VBox(
            children=[self.marker_style_dropdown, self.marker_size_text,
                      self.marker_edge_width_text], margin='0.1cm')
        self.marker_face_colour_widget = ColourSelectionWidget(
            marker_options['marker_face_colour'], description='Face colour',
            labels=labels, render_function=None)
        self.marker_edge_colour_widget = ColourSelectionWidget(
            marker_options['marker_edge_colour'], description='Edge colour',
            labels=labels, render_function=None)
        self.marker_box_2 = ipywidgets.VBox(
            children=[self.marker_face_colour_widget,
                      self.marker_edge_colour_widget], margin='0.1cm',
            align='end')
        self.marker_options_box = ipywidgets.HBox(
            children=[self.marker_box_1, self.marker_box_2])

        # Create final widget
        children = [self.render_markers_checkbox, self.marker_options_box]
        super(MarkerOptionsWidget, self).__init__(
            children, Dict, marker_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def marker_options_visible(name, value):
            self.marker_options_box.visible = value
        marker_options_visible('', marker_options['render_markers'])
        self.render_markers_checkbox.observe(marker_options_visible,
                                                     names='value')

        def save_options(name, value):
            self.selected_values = {
                'render_markers': self.render_markers_checkbox.value,
                'marker_size': int(self.marker_size_text.value),
                'marker_face_colour':
                    self.marker_face_colour_widget.selected_values,
                'marker_edge_colour':
                    self.marker_edge_colour_widget.selected_values,
                'marker_style': self.marker_style_dropdown.value,
                'marker_edge_width': float(self.marker_edge_width_text.value)}
        self.render_markers_checkbox.observe(save_options, names='value')
        self.marker_size_text.observe(save_options, names='value')
        self.marker_face_colour_widget.observe(save_options,
                                                       names='selected_values')
        self.marker_edge_colour_widget.observe(save_options,
                                                       names='selected_values')
        self.marker_style_dropdown.observe(save_options, names='value')
        self.marker_edge_width_text.observe(save_options, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_markers_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.marker_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.marker_size_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.marker_edge_width_text, font_family, font_size,
                    font_style, font_weight)
        self.marker_edge_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')
        self.marker_face_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')

    def set_widget_state(self, marker_options, labels=None,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        marker_options : `dict`
            The new set of options. For example ::

                marker_options = {'render_markers': True,
                                  'marker_size': 20,
                                  'marker_face_colour': ['red'],
                                  'marker_edge_colour': ['black'],
                                  'marker_style': 'o',
                                  'marker_edge_width': 1}

        labels : `list` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != marker_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_markers_checkbox.value = marker_options['render_markers']
            self.marker_style_dropdown.value = marker_options['marker_style']
            self.marker_size_text.value = int(marker_options['marker_size'])
            self.marker_edge_width_text.value = \
                float(marker_options['marker_edge_width'])
            self.marker_face_colour_widget.set_widget_state(
                marker_options['marker_face_colour'], labels=labels,
                allow_callback=False)
            self.marker_edge_colour_widget.set_widget_state(
                marker_options['marker_edge_colour'], labels=labels,
                allow_callback=False)

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class NumberingOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting numbering rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    numbers_options : `dict`
        The initial numbering options. Example ::

            numbers_options = {'render_numbering': True,
                               'numbers_font_name': 'serif',
                               'numbers_font_size': 10,
                               'numbers_font_style': 'normal',
                               'numbers_font_weight': 'normal',
                               'numbers_font_colour': ['black'],
                               'numbers_horizontal_align': 'center',
                               'numbers_vertical_align': 'bottom'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render numbering checkbox.
    """
    def __init__(self, numbers_options, render_function=None,
                 render_checkbox_title='Render numbering'):
        # Create children
        self.render_numbering_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=numbers_options['render_numbering'])
        numbers_font_name_dict = OrderedDict()
        numbers_font_name_dict['serif'] = 'serif'
        numbers_font_name_dict['sans-serif'] = 'sans-serif'
        numbers_font_name_dict['cursive'] = 'cursive'
        numbers_font_name_dict['fantasy'] = 'fantasy'
        numbers_font_name_dict['monospace'] = 'monospace'
        self.numbers_font_name_dropdown = ipywidgets.Dropdown(
            options=numbers_font_name_dict,
            value=numbers_options['numbers_font_name'], description='Font')
        self.numbers_font_size_text = ipywidgets.BoundedIntText(
            description='Size', min=0, max=10**6,
            value=numbers_options['numbers_font_size'])
        numbers_font_style_dict = OrderedDict()
        numbers_font_style_dict['normal'] = 'normal'
        numbers_font_style_dict['italic'] = 'italic'
        numbers_font_style_dict['oblique'] = 'oblique'
        self.numbers_font_style_dropdown = ipywidgets.Dropdown(
            options=numbers_font_style_dict,
            value=numbers_options['numbers_font_style'], description='Style')
        numbers_font_weight_dict = OrderedDict()
        numbers_font_weight_dict['normal'] = 'normal'
        numbers_font_weight_dict['ultralight'] = 'ultralight'
        numbers_font_weight_dict['light'] = 'light'
        numbers_font_weight_dict['regular'] = 'regular'
        numbers_font_weight_dict['book'] = 'book'
        numbers_font_weight_dict['medium'] = 'medium'
        numbers_font_weight_dict['roman'] = 'roman'
        numbers_font_weight_dict['semibold'] = 'semibold'
        numbers_font_weight_dict['demibold'] = 'demibold'
        numbers_font_weight_dict['demi'] = 'demi'
        numbers_font_weight_dict['bold'] = 'bold'
        numbers_font_weight_dict['heavy'] = 'heavy'
        numbers_font_weight_dict['extra bold'] = 'extra bold'
        numbers_font_weight_dict['black'] = 'black'
        self.numbers_font_weight_dropdown = ipywidgets.Dropdown(
            options=numbers_font_weight_dict,
            value=numbers_options['numbers_font_weight'], description='Weight')
        self.numbers_font_colour_widget = ColourSelectionWidget(
            numbers_options['numbers_font_colour'], description='Colour',
            render_function=None)
        numbers_horizontal_align_dict = OrderedDict()
        numbers_horizontal_align_dict['center'] = 'center'
        numbers_horizontal_align_dict['right'] = 'right'
        numbers_horizontal_align_dict['left'] = 'left'
        self.numbers_horizontal_align_dropdown = ipywidgets.Dropdown(
            options=numbers_horizontal_align_dict,
            value=numbers_options['numbers_horizontal_align'],
            description='Align hor.')
        numbers_vertical_align_dict = OrderedDict()
        numbers_vertical_align_dict['center'] = 'center'
        numbers_vertical_align_dict['top'] = 'top'
        numbers_vertical_align_dict['bottom'] = 'bottom'
        numbers_vertical_align_dict['baseline'] = 'baseline'
        self.numbers_vertical_align_dropdown = ipywidgets.Dropdown(
            options=numbers_vertical_align_dict,
            value=numbers_options['numbers_vertical_align'],
            description='Align ver.')
        self.name_size_style_weight = ipywidgets.VBox(
            children=[self.numbers_font_name_dropdown,
                      self.numbers_font_size_text,
                      self.numbers_font_style_dropdown,
                      self.numbers_font_weight_dropdown])
        self.colour_horizontal_vertical_align = ipywidgets.VBox(
            children=[self.numbers_font_colour_widget,
                      self.numbers_horizontal_align_dropdown,
                      self.numbers_vertical_align_dropdown])
        self.numbering_options_box = ipywidgets.HBox(
            children=[self.name_size_style_weight,
                      self.colour_horizontal_vertical_align])

        # Create final widget
        children = [self.render_numbering_checkbox, self.numbering_options_box]
        super(NumberingOptionsWidget, self).__init__(
            children, Dict, numbers_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def numbering_options_visible(name, value):
            self.numbering_options_box.visible = value
        numbering_options_visible('', numbers_options['render_numbering'])
        self.render_numbering_checkbox.observe(
            numbering_options_visible, names='value')

        def save_options(name, value):
            self.selected_values = {
                'render_numbering': self.render_numbering_checkbox.value,
                'numbers_font_name': self.numbers_font_name_dropdown.value,
                'numbers_font_size': int(self.numbers_font_size_text.value),
                'numbers_font_style': self.numbers_font_style_dropdown.value,
                'numbers_font_weight': self.numbers_font_weight_dropdown.value,
                'numbers_font_colour':
                    self.numbers_font_colour_widget.selected_values[0],
                'numbers_horizontal_align':
                    self.numbers_horizontal_align_dropdown.value,
                'numbers_vertical_align':
                    self.numbers_vertical_align_dropdown.value}
        self.render_numbering_checkbox.observe(save_options, names='value')
        self.numbers_font_name_dropdown.observe(save_options, names='value')
        self.numbers_font_size_text.observe(save_options, names='value')
        self.numbers_font_style_dropdown.observe(save_options, names='value')
        self.numbers_font_weight_dropdown.observe(save_options, names='value')
        self.numbers_font_colour_widget.observe(save_options,
                                                        names='selected_values')
        self.numbers_horizontal_align_dropdown.observe(save_options,
                                                               names='value')
        self.numbers_vertical_align_dropdown.observe(save_options,
                                                             names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_numbering_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_horizontal_align_dropdown, font_family,
                    font_size, font_style, font_weight)
        format_font(self.numbers_vertical_align_dropdown, font_family,
                    font_size, font_style, font_weight)
        self.numbers_font_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')

    def set_widget_state(self, numbers_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        numbers_options : `dict`
            The new set of options. For example ::

                numbers_options = {'render_numbering': True,
                                   'numbers_font_name': 'serif',
                                   'numbers_font_size': 10,
                                   'numbers_font_style': 'normal',
                                   'numbers_font_weight': 'normal',
                                   'numbers_font_colour': ['white'],
                                   'numbers_horizontal_align': 'center',
                                   'numbers_vertical_align': 'bottom'}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != numbers_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_numbering_checkbox.value = \
                numbers_options['render_numbering']
            self.numbers_font_name_dropdown.value = \
                numbers_options['numbers_font_name']
            self.numbers_font_size_text.value = \
                int(numbers_options['numbers_font_size'])
            self.numbers_font_style_dropdown.value = \
                numbers_options['numbers_font_style']
            self.numbers_font_weight_dropdown.value = \
                numbers_options['numbers_font_weight']
            self.numbers_horizontal_align_dropdown.value = \
                numbers_options['numbers_horizontal_align']
            self.numbers_vertical_align_dropdown.value = \
                numbers_options['numbers_vertical_align']
            self.numbers_font_colour_widget.set_widget_state(
                numbers_options['numbers_font_colour'],
                allow_callback=False)

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class AxesLimitsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting the axes limits.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    axes_x_limits : `float` or [`float`, `float`] or ``None``
        The limits of the x axis.
    axes_y_limits : `float` or [`float`, `float`] or ``None``
        The limits of the y axis.
    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, axes_x_limits, axes_y_limits, render_function=None):
        # Create children
        # x limits
        if axes_x_limits is None:
            toggles_initial_value = 'auto'
            percentage_initial_value = [0.]
            percentage_visible = False
            range_initial_value = [0., 100.]
            range_visible = False
        elif isinstance(axes_x_limits, float):
            toggles_initial_value = 'percentage'
            percentage_initial_value = [axes_x_limits]
            percentage_visible = True
            range_initial_value = [0., 100.]
            range_visible = False
        else:
            toggles_initial_value = 'range'
            percentage_initial_value = [0.]
            percentage_visible = False
            range_initial_value = axes_x_limits
            range_visible = True
        self.axes_x_limits_toggles = ipywidgets.ToggleButtons(
            description='X limits:', value=toggles_initial_value,
            options=['auto', 'percentage', 'range'], margin='0.2cm')
        self.axes_x_limits_percentage = ListWidget(
            percentage_initial_value, mode='float', description='',
            render_function=None, example_visible=False)
        self.axes_x_limits_percentage.visible = percentage_visible
        self.axes_x_limits_range = ListWidget(
            range_initial_value, mode='float', description='',
            render_function=None, example_visible=False)
        self.axes_x_limits_range.visible = range_visible
        self.axes_x_limits_options_box = ipywidgets.VBox(
            children=[self.axes_x_limits_percentage, self.axes_x_limits_range])
        self.axes_x_limits_box = ipywidgets.HBox(
            children=[self.axes_x_limits_toggles,
                      self.axes_x_limits_options_box], align='center')

        # y limits
        if axes_y_limits is None:
            toggles_initial_value = 'auto'
            percentage_initial_value = [0.]
            percentage_visible = False
            range_initial_value = [0., 100.]
            range_visible = False
        elif isinstance(axes_y_limits, float):
            toggles_initial_value = 'percentage'
            percentage_initial_value = [axes_y_limits]
            percentage_visible = True
            range_initial_value = [0., 100.]
            range_visible = False
        else:
            toggles_initial_value = 'range'
            percentage_initial_value = [0.]
            percentage_visible = False
            range_initial_value = axes_y_limits
            range_visible = True
        self.axes_y_limits_toggles = ipywidgets.ToggleButtons(
            description='Y limits:', value=toggles_initial_value,
            options=['auto', 'percentage', 'range'], margin='0.2cm')
        self.axes_y_limits_percentage = ListWidget(
            percentage_initial_value, mode='float', description='',
            render_function=None, example_visible=False)
        self.axes_y_limits_percentage.visible = percentage_visible
        self.axes_y_limits_range = ListWidget(
            range_initial_value, mode='float', description='',
            render_function=None, example_visible=False)
        self.axes_y_limits_range.visible = range_visible
        self.axes_y_limits_options_box = ipywidgets.VBox(
            children=[self.axes_y_limits_percentage, self.axes_y_limits_range])
        self.axes_y_limits_box = ipywidgets.HBox(
            children=[self.axes_y_limits_toggles,
                      self.axes_y_limits_options_box], align='center')

        # Create final widget
        children = [self.axes_x_limits_box, self.axes_y_limits_box]
        super(AxesLimitsWidget, self).__init__(
            children, Dict, {'x': axes_x_limits, 'y': axes_y_limits},
            render_function=render_function, orientation='vertical',
            align='start')

        # Set functionality
        def x_visibility(name, value):
            if value == 'auto':
                self.axes_x_limits_percentage.visible = False
                self.axes_x_limits_range.visible = False
            elif value == 'percentage':
                self.axes_x_limits_percentage.visible = True
                self.axes_x_limits_range.visible = False
            else:
                self.axes_x_limits_percentage.visible = False
                self.axes_x_limits_range.visible = True
        self.axes_x_limits_toggles.observe(x_visibility, names='value')

        def y_visibility(name, value):
            if value == 'auto':
                self.axes_y_limits_percentage.visible = False
                self.axes_y_limits_range.visible = False
            elif value == 'percentage':
                self.axes_y_limits_percentage.visible = True
                self.axes_y_limits_range.visible = False
            else:
                self.axes_y_limits_percentage.visible = False
                self.axes_y_limits_range.visible = True
        self.axes_y_limits_toggles.observe(y_visibility, names='value')

        def save_options(name, value):
            if self.axes_x_limits_toggles.value == 'auto':
                x_val = None
            elif self.axes_x_limits_toggles.value == 'percentage':
                x_val = self.axes_x_limits_percentage.selected_values[0]
            else:
                x_val = self.axes_x_limits_range.selected_values
            if self.axes_y_limits_toggles.value == 'auto':
                y_val = None
            elif self.axes_y_limits_toggles.value == 'percentage':
                y_val = self.axes_y_limits_percentage.selected_values[0]
            else:
                y_val = self.axes_y_limits_range.selected_values
            self.selected_values = {'x': x_val, 'y': y_val}
        self.axes_x_limits_toggles.observe(save_options, names='value')
        self.axes_x_limits_percentage.observe(save_options,
                                                      names='selected_values')
        self.axes_x_limits_range.observe(save_options,
                                                 names='selected_values')
        self.axes_y_limits_toggles.observe(save_options, names='value')
        self.axes_y_limits_percentage.observe(save_options,
                                                      names='selected_values')
        self.axes_y_limits_range.observe(save_options,
                                                 names='selected_values')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', toggles_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        toggles_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.axes_x_limits_toggles, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_toggles, font_family, font_size,
                    font_style, font_weight)
        self.axes_x_limits_toggles.button_style = toggles_style
        self.axes_y_limits_toggles.button_style = toggles_style
        self.axes_x_limits_percentage.style(
            box_style=box_style, border_visible=False, padding=0,
            margin=0, text_box_style=box_style, text_box_width=None,
            font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)
        self.axes_x_limits_range.style(
            box_style=box_style, border_visible=False, padding=0,
            margin=0, text_box_style=box_style, text_box_width=None,
            font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)
        self.axes_y_limits_percentage.style(
            box_style=box_style, border_visible=False, padding=0,
            margin=0, text_box_style=box_style, text_box_width=None,
            font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)
        self.axes_y_limits_range.style(
            box_style=box_style, border_visible=False, padding=0,
            margin=0, text_box_style=box_style, text_box_width=None,
            font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)

    def set_widget_state(self, axes_x_limits, axes_y_limits,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        axes_x_limits : `float` or [`float`, `float`] or ``None``
            The limits of the x axis.
        axes_y_limits : `float` or [`float`, `float`] or ``None``
            The limits of the y axis.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if self.selected_values != {'x': axes_x_limits, 'y': axes_y_limits}:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            if axes_x_limits is None:
                self.axes_x_limits_toggles.value = 'auto'
            elif isinstance(axes_x_limits, float):
                self.axes_x_limits_toggles.value = 'percentage'
                self.axes_x_limits_percentage.set_widget_state(
                    [axes_x_limits], allow_callback=False)
            else:
                self.axes_x_limits_toggles.value = 'range'
                self.axes_x_limits_range.set_widget_state(
                    axes_x_limits, allow_callback=False)
            if axes_y_limits is None:
                self.axes_y_limits_toggles.value = 'auto'
            elif isinstance(axes_y_limits, float):
                self.axes_y_limits_toggles.value = 'percentage'
                self.axes_y_limits_percentage.set_widget_state(
                    [axes_y_limits], allow_callback=False)
            else:
                self.axes_y_limits_toggles.value = 'range'
                self.axes_y_limits_range.set_widget_state(
                    axes_y_limits, allow_callback=False)

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class AxesTicksWidget(MenpoWidget):
    r"""
    Creates a widget for selecting the axes ticks.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    axes_ticks : `dict`
        The dictionary with the default options. For example ::

            axes_ticks = {'x': [10, 20], 'y': None}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, axes_ticks, render_function=None):
        # Create children
        # x ticks
        if axes_ticks['x'] is None:
            toggles_initial_value = 'auto'
            list_visible = False
            list_value = []
        else:
            toggles_initial_value = 'list'
            list_visible = True
            list_value = axes_ticks['x']
        self.axes_x_ticks_toggles = ipywidgets.ToggleButtons(
            description='X ticks:', value=toggles_initial_value,
            options=['auto', 'list'], margin='0.1cm')
        self.axes_x_ticks_list = ListWidget(
            list_value, mode='float', description='', render_function=None,
            example_visible=False)
        self.axes_x_ticks_list.margin = '0.1cm'
        self.axes_x_ticks_list.visible = list_visible
        self.axes_x_ticks_box = ipywidgets.HBox(
            children=[self.axes_x_ticks_toggles, self.axes_x_ticks_list],
            align='start')

        # y ticks
        if axes_ticks['y'] is None:
            toggles_initial_value = 'auto'
            list_visible = False
            list_value = []
        else:
            toggles_initial_value = 'list'
            list_visible = True
            list_value = axes_ticks['y']
        self.axes_y_ticks_toggles = ipywidgets.ToggleButtons(
            description='Y ticks:', value=toggles_initial_value,
            options=['auto', 'list'], margin='0.1cm')
        self.axes_y_ticks_list = ListWidget(
            list_value, mode='float', description='', render_function=None,
            example_visible=False)
        self.axes_y_ticks_list.margin = '0.1cm'
        self.axes_y_ticks_list.visible = list_visible
        self.axes_y_ticks_box = ipywidgets.HBox(
            children=[self.axes_y_ticks_toggles, self.axes_y_ticks_list],
            align='start')

        # Create final widget
        children = [self.axes_x_ticks_box, self.axes_y_ticks_box]
        super(AxesTicksWidget, self).__init__(
            children, Dict, axes_ticks, render_function=render_function,
            orientation='vertical', align='start')

        # Set functionality
        def x_visibility(name, value):
            self.axes_x_ticks_list.visible = value == 'list'
        self.axes_x_ticks_toggles.observe(x_visibility, names='value')

        def y_visibility(name, value):
            self.axes_y_ticks_list.visible = value == 'list'
        self.axes_y_ticks_toggles.observe(y_visibility, names='value')

        def save_options(name, value):
            if self.axes_x_ticks_toggles.value == 'auto':
                x_val = None
            else:
                x_val = self.axes_x_ticks_list.selected_values
            if self.axes_y_ticks_toggles.value == 'auto':
                y_val = None
            else:
                y_val = self.axes_y_ticks_list.selected_values
            self.selected_values = {'x': x_val, 'y': y_val}
        self.axes_x_ticks_toggles.observe(save_options, names='value')
        self.axes_x_ticks_list.observe(save_options, names='selected_values')
        self.axes_y_ticks_toggles.observe(save_options, names='value')
        self.axes_y_ticks_list.observe(save_options, names='selected_values')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', toggles_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        toggles_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.axes_x_ticks_toggles, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_ticks_toggles, font_family, font_size,
                    font_style, font_weight)
        self.axes_x_ticks_toggles.button_style = toggles_style
        self.axes_y_ticks_toggles.button_style = toggles_style
        self.axes_x_ticks_list.style(
            box_style=None, border_visible=False, text_box_style=None,
            text_box_background_colour=None, font_family=font_family,
            margin='0.1cm', font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        self.axes_y_ticks_list.style(
            box_style=None, border_visible=False, text_box_style=None,
            text_box_background_colour=None, font_family=font_family,
            margin='0.1cm', font_size=font_size, font_style=font_style,
            font_weight=font_weight)

    def set_widget_state(self, axes_ticks, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        axes_ticks : `dict`
            The dictionary with the selected options. For example ::

                axes_ticks = {'x': [10, 20], 'y': None}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if axes_ticks != self.selected_values:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            if axes_ticks['x'] is None:
                self.axes_x_ticks_toggles.value = 'auto'
            else:
                self.axes_x_ticks_toggles.value = 'list'
                self.axes_x_ticks_list.set_widget_state(axes_ticks['x'],
                                                        allow_callback=False)
            if axes_ticks['y'] is None:
                self.axes_y_ticks_toggles.value = 'auto'
            else:
                self.axes_y_ticks_toggles.value = 'list'
                self.axes_y_ticks_list.set_widget_state(axes_ticks['y'],
                                                        allow_callback=False)

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class AxesOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting axes rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    axes_options : `dict`
        The initial axes options. Example ::

            axes_options = {'render_axes': True, 'axes_font_name': 'serif',
                            'axes_font_size': 10, 'axes_font_style': 'normal',
                            'axes_font_weight': 'normal',
                            'axes_x_ticks': [0, 100], 'axes_y_ticks': None,
                            'axes_x_limits': None, 'axes_y_limits': 1.}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    """
    def __init__(self, axes_options, render_function=None,
                 render_checkbox_title='Render axes'):
        # Create children
        # render checkbox
        self.render_axes_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=axes_options['render_axes'])
        # axes font options
        axes_font_name_dict = OrderedDict()
        axes_font_name_dict['serif'] = 'serif'
        axes_font_name_dict['sans-serif'] = 'sans-serif'
        axes_font_name_dict['cursive'] = 'cursive'
        axes_font_name_dict['fantasy'] = 'fantasy'
        axes_font_name_dict['monospace'] = 'monospace'
        self.axes_font_name_dropdown = ipywidgets.Dropdown(
            options=axes_font_name_dict, value=axes_options['axes_font_name'],
            description='Font')
        self.axes_font_size_text = ipywidgets.BoundedIntText(
            description='Size', value=axes_options['axes_font_size'],
            min=0, max=10**6)
        axes_font_style_dict = OrderedDict()
        axes_font_style_dict['normal'] = 'normal'
        axes_font_style_dict['italic'] = 'italic'
        axes_font_style_dict['oblique'] = 'oblique'
        self.axes_font_style_dropdown = ipywidgets.Dropdown(
            options=axes_font_style_dict, description='Style',
            value=axes_options['axes_font_style'])
        axes_font_weight_dict = OrderedDict()
        axes_font_weight_dict['normal'] = 'normal'
        axes_font_weight_dict['ultralight'] = 'ultralight'
        axes_font_weight_dict['light'] = 'light'
        axes_font_weight_dict['regular'] = 'regular'
        axes_font_weight_dict['book'] = 'book'
        axes_font_weight_dict['medium'] = 'medium'
        axes_font_weight_dict['roman'] = 'roman'
        axes_font_weight_dict['semibold'] = 'semibold'
        axes_font_weight_dict['demibold'] = 'demibold'
        axes_font_weight_dict['demi'] = 'demi'
        axes_font_weight_dict['bold'] = 'bold'
        axes_font_weight_dict['heavy'] = 'heavy'
        axes_font_weight_dict['extra bold'] = 'extra bold'
        axes_font_weight_dict['black'] = 'black'
        self.axes_font_weight_dropdown = ipywidgets.Dropdown(
            options=axes_font_weight_dict,
            value=axes_options['axes_font_weight'], description='Weight')
        self.axes_font_box_1 = ipywidgets.VBox(
            children=[self.axes_font_name_dropdown, self.axes_font_size_text],
            margin='0.2cm')
        self.axes_font_box_2 = ipywidgets.VBox(
            children=[self.axes_font_style_dropdown,
                      self.axes_font_weight_dropdown], margin='0.2cm')
        self.axes_font_options_box = ipywidgets.HBox(
            children=[self.axes_font_box_1, self.axes_font_box_2])

        # axes ticks options
        axes_ticks = {'x': axes_options['axes_x_ticks'],
                      'y': axes_options['axes_y_ticks']}
        self.axes_ticks_widget = AxesTicksWidget(axes_ticks,
                                                 render_function=None)

        # axes font and ticks options box
        self.axes_font_ticks_options = ipywidgets.VBox(
            children=[self.axes_font_options_box, self.axes_ticks_widget])

        # axes font, ticks and render checkbox box
        self.axes_options_box = ipywidgets.HBox(
            children=[self.render_axes_checkbox, self.axes_font_ticks_options],
            margin='0.2cm')

        # axes limits options
        self.axes_limits_widget = AxesLimitsWidget(
            axes_options['axes_x_limits'], axes_options['axes_y_limits'],
            render_function=None)

        # options tab
        self.axes_options_tab = ipywidgets.Tab(
            children=[self.axes_options_box, self.axes_limits_widget])
        self.axes_options_tab.set_title(0, 'Font & Ticks')
        self.axes_options_tab.set_title(1, 'Limits')

        # Create final widget
        children = [self.axes_options_tab]
        super(AxesOptionsWidget, self).__init__(
            children, Dict, axes_options, render_function=render_function,
            orientation='vertical', align='start')

        # Set functionality
        def axes_options_visible(name, value):
            self.axes_font_ticks_options.visible = value
        axes_options_visible('', axes_options['render_axes'])
        self.render_axes_checkbox.observe(axes_options_visible,
                                                  names='value')

        def save_options(name, value):
            self.selected_values = {
                'render_axes': self.render_axes_checkbox.value,
                'axes_font_name': self.axes_font_name_dropdown.value,
                'axes_font_size': int(self.axes_font_size_text.value),
                'axes_font_style': self.axes_font_style_dropdown.value,
                'axes_font_weight': self.axes_font_weight_dropdown.value,
                'axes_x_ticks': self.axes_ticks_widget.selected_values['x'],
                'axes_y_ticks': self.axes_ticks_widget.selected_values['y'],
                'axes_x_limits': self.axes_limits_widget.selected_values['x'],
                'axes_y_limits': self.axes_limits_widget.selected_values['y']}
        self.render_axes_checkbox.observe(save_options, names='value')
        self.axes_font_name_dropdown.observe(save_options, names='value')
        self.axes_font_size_text.observe(save_options, names='value')
        self.axes_font_style_dropdown.observe(save_options, names='value')
        self.axes_font_weight_dropdown.observe(save_options, names='value')
        self.axes_ticks_widget.observe(save_options, names='selected_values')
        self.axes_limits_widget.observe(save_options, names='selected_values')

    def set_widget_state(self, axes_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        axes_options : `dict`
            The new axes options. Example ::

                axes_options = {'render_axes': True, 'axes_font_name': 'serif',
                                'axes_font_size': 10,
                                'axes_font_style': 'normal',
                                'axes_font_weight': 'normal',
                                'axes_x_ticks': [0, 100], 'axes_y_ticks': None,
                                'axes_x_limits': None, 'axes_y_limits': 1.}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        if self.selected_values != axes_options:
            # update
            self.render_axes_checkbox.value = axes_options['render_axes']
            self.axes_font_name_dropdown.value = axes_options['axes_font_name']
            self.axes_font_size_text.value = axes_options['axes_font_size']
            self.axes_font_style_dropdown.value = \
                axes_options['axes_font_style']
            self.axes_font_weight_dropdown.value = \
                axes_options['axes_font_weight']
            axes_ticks = {'x': axes_options['axes_x_ticks'],
                          'y': axes_options['axes_y_ticks']}
            self.axes_ticks_widget.set_widget_state(axes_ticks,
                                                    allow_callback=False)
            axes_limits = {'x': axes_options['axes_x_limits'],
                           'y': axes_options['axes_y_limits']}
            self.axes_limits_widget.set_widget_state(
                axes_options['axes_x_limits'], axes_options['axes_y_limits'],
                allow_callback=False)

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_axes_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        self.axes_ticks_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_style=font_style,
            font_weight=font_weight, toggles_style='')
        self.axes_limits_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_style=font_style,
            font_weight=font_weight, toggles_style='')


class LegendOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting legend rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    legend_options : `dict`
        The initial legend options. Example ::

            legend_options = {'render_legend': True,
                              'legend_title': '',
                              'legend_font_name': 'serif',
                              'legend_font_style': 'normal',
                              'legend_font_size': 10,
                              'legend_font_weight': 'normal',
                              'legend_marker_scale': 1.,
                              'legend_location': 2,
                              'legend_bbox_to_anchor': (1.05, 1.),
                              'legend_border_axes_pad': 1.,
                              'legend_n_columns': 1,
                              'legend_horizontal_spacing': 1.,
                              'legend_vertical_spacing': 1.,
                              'legend_border': True,
                              'legend_border_padding': 0.5,
                              'legend_shadow': False,
                              'legend_rounded_corners': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render legend checkbox.
    """
    def __init__(self, legend_options, render_function=None,
                 render_checkbox_title='Render legend'):
        # Create children
        # render checkbox
        self.render_legend_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=legend_options['render_legend'], margin='0.2cm')

        # font-related options and title
        legend_font_name_dict = OrderedDict()
        legend_font_name_dict['serif'] = 'serif'
        legend_font_name_dict['sans-serif'] = 'sans-serif'
        legend_font_name_dict['cursive'] = 'cursive'
        legend_font_name_dict['fantasy'] = 'fantasy'
        legend_font_name_dict['monospace'] = 'monospace'
        self.legend_font_name_dropdown = ipywidgets.Dropdown(
            options=legend_font_name_dict,
            value=legend_options['legend_font_name'], description='Font')
        self.legend_font_size_text = ipywidgets.BoundedIntText(
            description='Size', min=0, max=10**6,
            value=legend_options['legend_font_size'])
        legend_font_style_dict = OrderedDict()
        legend_font_style_dict['normal'] = 'normal'
        legend_font_style_dict['italic'] = 'italic'
        legend_font_style_dict['oblique'] = 'oblique'
        self.legend_font_style_dropdown = ipywidgets.Dropdown(
            options=legend_font_style_dict,
            value=legend_options['legend_font_style'], description='Style')
        legend_font_weight_dict = OrderedDict()
        legend_font_weight_dict['normal'] = 'normal'
        legend_font_weight_dict['ultralight'] = 'ultralight'
        legend_font_weight_dict['light'] = 'light'
        legend_font_weight_dict['regular'] = 'regular'
        legend_font_weight_dict['book'] = 'book'
        legend_font_weight_dict['medium'] = 'medium'
        legend_font_weight_dict['roman'] = 'roman'
        legend_font_weight_dict['semibold'] = 'semibold'
        legend_font_weight_dict['demibold'] = 'demibold'
        legend_font_weight_dict['demi'] = 'demi'
        legend_font_weight_dict['bold'] = 'bold'
        legend_font_weight_dict['heavy'] = 'heavy'
        legend_font_weight_dict['extra bold'] = 'extra bold'
        legend_font_weight_dict['black'] = 'black'
        self.legend_font_weight_dropdown = ipywidgets.Dropdown(
            options=legend_font_weight_dict,
            value=legend_options['legend_font_weight'], description='Weight')
        self.legend_title_text = ipywidgets.Text(
            description='Title', value=legend_options['legend_title'],
            margin='0.1cm')
        self.legend_font_name_and_size_box = ipywidgets.HBox(
            children=[self.legend_font_name_dropdown,
                      self.legend_font_size_text])
        self.legend_font_style_and_weight_box = ipywidgets.HBox(
            children=[self.legend_font_style_dropdown,
                      self.legend_font_weight_dropdown])
        self.legend_font_box = ipywidgets.Box(
            children=[self.legend_font_name_and_size_box,
                      self.legend_font_style_and_weight_box], margin='0.1cm')
        self.font_related_box = ipywidgets.Box(
            children=[self.legend_title_text, self.legend_font_box])

        # location-related options
        legend_location_dict = OrderedDict()
        legend_location_dict['best'] = 0
        legend_location_dict['upper right'] = 1
        legend_location_dict['upper left'] = 2
        legend_location_dict['lower left'] = 3
        legend_location_dict['lower right'] = 4
        legend_location_dict['right'] = 5
        legend_location_dict['center left'] = 6
        legend_location_dict['center right'] = 7
        legend_location_dict['lower center'] = 8
        legend_location_dict['upper center'] = 9
        legend_location_dict['center'] = 10
        self.legend_location_dropdown = ipywidgets.Dropdown(
            options=legend_location_dict,
            value=legend_options['legend_location'],
            description='Anchor')
        if legend_options['legend_bbox_to_anchor'] is None:
            tmp1 = False
            tmp2 = 0.
            tmp3 = 0.
        else:
            tmp1 = True
            tmp2 = legend_options['legend_bbox_to_anchor'][0]
            tmp3 = legend_options['legend_bbox_to_anchor'][1]
        self.bbox_to_anchor_enable_checkbox = ipywidgets.Checkbox(
            value=tmp1, description='Offset', margin='0.1cm')
        self.bbox_to_anchor_x_text = ipywidgets.FloatText(
            value=tmp2, description='', width='3cm')
        self.bbox_to_anchor_y_text = ipywidgets.FloatText(
            value=tmp3, description='', width='3cm')
        self.legend_bbox_to_anchor_x_y_box = ipywidgets.VBox(
            children=[self.bbox_to_anchor_x_text, self.bbox_to_anchor_y_text],
            margin='0.1cm')
        self.legend_bbox_to_anchor_box = ipywidgets.HBox(
            children=[self.bbox_to_anchor_enable_checkbox,
                      self.legend_bbox_to_anchor_x_y_box], align='start')
        self.legend_border_axes_pad_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_border_axes_pad'],
            description='Padding', min=0.)
        self.legend_location_border_axes_pad_box = ipywidgets.VBox(
            children=[self.legend_location_dropdown,
                      self.legend_border_axes_pad_text], margin='0.1cm')
        self.location_related_box = ipywidgets.HBox(
            children=[self.legend_location_border_axes_pad_box,
                      self.legend_bbox_to_anchor_box])

        # formatting related
        self.legend_n_columns_text = ipywidgets.BoundedIntText(
            value=legend_options['legend_n_columns'], description='Columns',
            min=0, width='1.6cm')
        self.legend_marker_scale_text = ipywidgets.BoundedFloatText(
            description='Marker scale', width='1.6cm',
            value=legend_options['legend_marker_scale'], min=0.)
        self.legend_horizontal_spacing_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_horizontal_spacing'],
            description='Horizontal space', min=0., width='1.6cm')
        self.legend_vertical_spacing_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_vertical_spacing'],
            description='Vertical space', min=0., width='1.6cm')
        self.legend_n_columns_and_marker_scale_box = ipywidgets.VBox(
            children=[self.legend_n_columns_text,
                      self.legend_horizontal_spacing_text], align='end')
        self.legend_horizontal_and_vertical_spacing_box = ipywidgets.VBox(
            children=[self.legend_marker_scale_text,
                      self.legend_vertical_spacing_text], align='end')
        self.location_box = ipywidgets.HBox(
            children=[self.legend_n_columns_and_marker_scale_box,
                      self.legend_horizontal_and_vertical_spacing_box],
            margin='0.1cm')
        self.legend_border_checkbox = ipywidgets.Checkbox(
            description='Border', value=legend_options['legend_border'])
        self.legend_border_padding_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_border_padding'],
            description='Padding', min=0., width='1.5cm')
        self.border_box = ipywidgets.HBox(
            children=[self.legend_border_checkbox,
                      self.legend_border_padding_text])
        self.legend_shadow_checkbox = ipywidgets.Checkbox(
            description='Shadow', value=legend_options['legend_shadow'])
        self.legend_rounded_corners_checkbox = ipywidgets.Checkbox(
            description='Fancy',
            value=legend_options['legend_rounded_corners'])
        self.shadow_fancy_border_box = ipywidgets.VBox(
            children=[self.border_box, self.legend_shadow_checkbox,
                      self.legend_rounded_corners_checkbox], margin='0.1cm')
        self.formatting_related_box = ipywidgets.HBox(
            children=[self.location_box, self.shadow_fancy_border_box])

        # Options widget
        self.tab_box = ipywidgets.Tab(
            children=[self.location_related_box, self.font_related_box,
                      self.formatting_related_box])
        self.tab_box.set_title(0, 'Location')
        self.tab_box.set_title(1, 'Font')
        self.tab_box.set_title(2, 'Formatting')

        # Create final widget
        children = [self.render_legend_checkbox, self.tab_box]
        super(LegendOptionsWidget, self).__init__(
            children, Dict, legend_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def legend_options_visible(name, value):
            self.tab_box.visible = value
        legend_options_visible('', legend_options['render_legend'])
        self.render_legend_checkbox.observe(legend_options_visible,
                                                    names='value')

        def border_pad_visible(name, value):
            self.legend_border_padding_text.visible = value
        self.legend_border_checkbox.observe(border_pad_visible, names='value')

        def bbox_to_anchor_visible(name, value):
            self.bbox_to_anchor_x_text.visible = value
            self.bbox_to_anchor_y_text.visible = value
        bbox_to_anchor_visible('', not legend_options['legend_bbox_to_anchor']
                               is None)
        self.bbox_to_anchor_enable_checkbox.observe(
            bbox_to_anchor_visible, names='value')

        def save_options(name, value):
            legend_bbox_to_anchor = None
            if self.bbox_to_anchor_enable_checkbox.value:
                legend_bbox_to_anchor = (self.bbox_to_anchor_x_text.value,
                                         self.bbox_to_anchor_y_text.value)
            self.selected_values = {
                'render_legend': self.render_legend_checkbox.value,
                'legend_title': str(self.legend_title_text.value),
                'legend_font_name': self.legend_font_name_dropdown.value,
                'legend_font_style': self.legend_font_style_dropdown.value,
                'legend_font_size': int(self.legend_font_size_text.value),
                'legend_font_weight': self.legend_font_weight_dropdown.value,
                'legend_marker_scale':
                    float(self.legend_marker_scale_text.value),
                'legend_location': self.legend_location_dropdown.value,
                'legend_bbox_to_anchor': legend_bbox_to_anchor,
                'legend_border_axes_pad':
                    float(self.legend_border_axes_pad_text.value),
                'legend_n_columns': int(self.legend_n_columns_text.value),
                'legend_horizontal_spacing':
                    float(self.legend_horizontal_spacing_text.value),
                'legend_vertical_spacing':
                    float(self.legend_vertical_spacing_text.value),
                'legend_border': self.legend_border_checkbox.value,
                'legend_border_padding':
                    float(self.legend_border_padding_text.value),
                'legend_shadow': self.legend_shadow_checkbox.value,
                'legend_rounded_corners':
                    self.legend_rounded_corners_checkbox.value}
        self.render_legend_checkbox.observe(save_options, names='value')
        self.legend_title_text.observe(save_options, names='value')
        self.legend_font_name_dropdown.observe(save_options, names='value')
        self.legend_font_size_text.observe(save_options, names='value')
        self.legend_font_style_dropdown.observe(save_options, names='value')
        self.legend_font_weight_dropdown.observe(save_options, names='value')
        self.legend_location_dropdown.observe(save_options, names='value')
        self.bbox_to_anchor_enable_checkbox.observe(save_options,
                                                            names='value')
        self.bbox_to_anchor_x_text.observe(save_options, names='value')
        self.bbox_to_anchor_y_text.observe(save_options, names='value')
        self.legend_border_axes_pad_text.observe(save_options, names='value')
        self.legend_n_columns_text.observe(save_options, names='value')
        self.legend_marker_scale_text.observe(save_options, names='value')
        self.legend_horizontal_spacing_text.observe(save_options,
                                                            names='value')
        self.legend_vertical_spacing_text.observe(save_options, names='value')
        self.legend_border_checkbox.observe(save_options, names='value')
        self.legend_border_padding_text.observe(save_options, names='value')
        self.legend_shadow_checkbox.observe(save_options, names='value')
        self.legend_rounded_corners_checkbox.observe(save_options,
                                                             names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_legend_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_title_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.legend_location_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.bbox_to_anchor_enable_checkbox, font_family,
                    font_size, font_style, font_weight)
        format_font(self.bbox_to_anchor_x_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.bbox_to_anchor_y_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_border_axes_pad_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_n_columns_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_marker_scale_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_horizontal_spacing_text, font_family,
                    font_size, font_style, font_weight)
        format_font(self.legend_vertical_spacing_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_border_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_border_padding_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_shadow_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_rounded_corners_checkbox, font_family,
                    font_size, font_style, font_weight)

    def set_widget_state(self, legend_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        legend_options : `dict`
            The new set of options. For example ::

                legend_options = {'render_legend': True,
                                  'legend_title': '',
                                  'legend_font_name': 'serif',
                                  'legend_font_style': 'normal',
                                  'legend_font_size': 10,
                                  'legend_font_weight': 'normal',
                                  'legend_marker_scale': 1.,
                                  'legend_location': 2,
                                  'legend_bbox_to_anchor': (1.05, 1.),
                                  'legend_border_axes_pad': 1.,
                                  'legend_n_columns': 1,
                                  'legend_horizontal_spacing': 1.,
                                  'legend_vertical_spacing': 1.,
                                  'legend_border': True,
                                  'legend_border_padding': 0.5,
                                  'legend_shadow': False,
                                  'legend_rounded_corners': True}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != legend_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update render legend checkbox
            self.render_legend_checkbox.value = legend_options['render_legend']

            # update legend_title
            self.legend_title_text.value = legend_options['legend_title']

            # update legend_font_name dropdown menu
            self.legend_font_name_dropdown.value = \
                legend_options['legend_font_name']

            # update legend_font_size text box
            self.legend_font_size_text.value = \
                int(legend_options['legend_font_size'])

            # update legend_font_style dropdown menu
            self.legend_font_style_dropdown.value = \
                legend_options['legend_font_style']

            # update legend_font_weight dropdown menu
            self.legend_font_weight_dropdown.value = \
                legend_options['legend_font_weight']

            # update legend_location dropdown menu
            self.legend_location_dropdown.value = \
                legend_options['legend_location']

            # update legend_bbox_to_anchor
            if legend_options['legend_bbox_to_anchor'] is None:
                tmp1 = False
                tmp2 = 0.
                tmp3 = 0.
            else:
                tmp1 = True
                tmp2 = legend_options['legend_bbox_to_anchor'][0]
                tmp3 = legend_options['legend_bbox_to_anchor'][1]
            self.bbox_to_anchor_enable_checkbox.value = tmp1
            self.bbox_to_anchor_x_text.value = tmp2
            self.bbox_to_anchor_y_text.value = tmp3

            # update legend_border_axes_pad
            self.legend_border_axes_pad_text.value = \
                legend_options['legend_border_axes_pad']

            # update legend_n_columns text box
            self.legend_n_columns_text.value = \
                int(legend_options['legend_n_columns'])

            # update legend_marker_scale text box
            self.legend_marker_scale_text.value = \
                float(legend_options['legend_marker_scale'])

            # update legend_horizontal_spacing text box
            self.legend_horizontal_spacing_text.value = \
                float(legend_options['legend_horizontal_spacing'])

            # update legend_vertical_spacing text box
            self.legend_vertical_spacing_text.value = \
                float(legend_options['legend_vertical_spacing'])

            # update legend_border
            self.legend_border_checkbox.value = legend_options['legend_border']

            # update legend_border_padding text box
            self.legend_border_padding_text.value = \
                float(legend_options['legend_border_padding'])

            # update legend_shadow
            self.legend_shadow_checkbox.value = legend_options['legend_shadow']

            # update legend_rounded_corners
            self.legend_rounded_corners_checkbox.value = \
                legend_options['legend_rounded_corners']

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class GridOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting grid rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    grid_options : `dict`
        The initial grid options. Example ::

            grid_options = {'render_grid': True,
                            'grid_line_width': 1,
                            'grid_line_style': '-'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    """
    def __init__(self, grid_options, render_function=None,
                 render_checkbox_title='Render grid'):
        # Create children
        self.render_grid_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=grid_options['render_grid'])
        self.grid_line_width_text = ipywidgets.BoundedFloatText(
            description='Width', value=grid_options['grid_line_width'],
            min=0., max=10**6)
        grid_line_style_dict = OrderedDict()
        grid_line_style_dict['solid'] = '-'
        grid_line_style_dict['dashed'] = '--'
        grid_line_style_dict['dash-dot'] = '-.'
        grid_line_style_dict['dotted'] = ':'
        self.grid_line_style_dropdown = ipywidgets.Dropdown(
            value=grid_options['grid_line_style'], description='Style',
            options=grid_line_style_dict,)
        self.grid_options_box = ipywidgets.VBox(
            children=[self.grid_line_style_dropdown, self.grid_line_width_text])

        # Create final widget
        children = [self.render_grid_checkbox, self.grid_options_box]
        super(GridOptionsWidget, self).__init__(
            children, Dict, grid_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def grid_options_visible(name, value):
            self.grid_options_box.visible = value
        grid_options_visible('', grid_options['render_grid'])
        self.render_grid_checkbox.observe(grid_options_visible, names='value')

        def save_options(name, value):
            self.selected_values = {
                'render_grid': self.render_grid_checkbox.value,
                'grid_line_width': float(self.grid_line_width_text.value),
                'grid_line_style': self.grid_line_style_dropdown.value}
        self.render_grid_checkbox.observe(save_options, names='value')
        self.grid_line_width_text.observe(save_options, names='value')
        self.grid_line_style_dropdown.observe(save_options, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_grid_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.grid_line_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.grid_line_width_text, font_family, font_size,
                    font_style, font_weight)

    def set_widget_state(self, grid_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        grid_options : `dict`
            The new set of options. For example ::

                grid_options = {'render_grid': True,
                                'grid_line_width': 2,
                                'grid_line_style': '-'}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != grid_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_grid_checkbox.value = grid_options['render_grid']
            self.grid_line_style_dropdown.value = \
                grid_options['grid_line_style']
            self.grid_line_width_text.value = \
                float(grid_options['grid_line_width'])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class HOGOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting HOG options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    hog_options : `dict`
        The initial options. Example ::

            hog_options = {'mode': 'dense',
                           'algorithm': 'dalaltriggs',
                           'num_bins': 9,
                           'cell_size': 8,
                           'block_size': 2,
                           'signed_gradient': True,
                           'l2_norm_clip': 0.2,
                           'window_height': 1,
                           'window_width': 1,
                           'window_unit': 'blocks',
                           'window_step_vertical': 1,
                           'window_step_horizontal': 1,
                           'window_step_unit': 'pixels',
                           'padding': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, hog_options, render_function=None):
        # Window related options
        tmp = OrderedDict()
        tmp['Dense'] = 'dense'
        tmp['Sparse'] = 'sparse'
        self.mode_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description='Mode', value=hog_options['mode'])
        self.padding_checkbox = ipywidgets.Checkbox(
            description='Padding', value=hog_options['padding'])
        self.mode_padding_box = ipywidgets.HBox(
            children=[self.mode_radiobuttons, self.padding_checkbox])
        self.window_height_text = ipywidgets.BoundedIntText(
            value=hog_options['window_height'], description='Height',
            min=1, width='2cm')
        self.window_width_text = ipywidgets.BoundedIntText(
            value=hog_options['window_width'], description='Width',
            min=1, width='2cm')
        tmp = OrderedDict()
        tmp['Blocks'] = 'blocks'
        tmp['Pixels'] = 'pixels'
        self.window_size_unit_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description=' Size unit',
            value=hog_options['window_unit'])
        self.window_size_box = ipywidgets.VBox(
            children=[self.window_height_text, self.window_width_text,
                      self.window_size_unit_radiobuttons])
        self.window_vertical_text = ipywidgets.BoundedIntText(
            value=hog_options['window_step_vertical'],
            description='Step Y', min=1, width='2cm')
        self.window_horizontal_text = ipywidgets.BoundedIntText(
            value=hog_options['window_step_horizontal'],
            description='Step X', min=1, width='2cm')
        tmp = OrderedDict()
        tmp['Pixels'] = 'pixels'
        tmp['Cells'] = 'cells'
        self.window_step_unit_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description='Step unit',
            value=hog_options['window_step_unit'])
        self.window_step_box = ipywidgets.VBox(
            children=[self.window_vertical_text, self.window_horizontal_text,
                      self.window_step_unit_radiobuttons])
        self.window_size_step_box = ipywidgets.HBox(
            children=[self.window_size_box, self.window_step_box])
        self.window_box = ipywidgets.Box(children=[self.mode_padding_box,
                                                   self.window_size_step_box])

        # Algorithm related options
        tmp = OrderedDict()
        tmp['Dalal & Triggs'] = 'dalaltriggs'
        tmp['Zhu & Ramanan'] = 'zhuramanan'
        self.algorithm_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, value=hog_options['algorithm'],
            description='Algorithm')
        self.cell_size_text = ipywidgets.BoundedIntText(
            value=hog_options['cell_size'],
            description='Cell size (in pixels)', min=1, width='1.5cm')
        self.block_size_text = ipywidgets.BoundedIntText(
            value=hog_options['block_size'],
            description='Block size (in cells)', min=1, width='1.5cm')
        self.num_bins_text = ipywidgets.BoundedIntText(
            value=hog_options['num_bins'],
            description='Orientation bins', min=1, width='1.5cm')
        self.algorithm_sizes_box = ipywidgets.VBox(
            children=[self.cell_size_text, self.block_size_text,
                      self.num_bins_text])
        self.signed_gradient_checkbox = ipywidgets.Checkbox(
            value=hog_options['signed_gradient'],
            description='Gradient sign')
        self.l2_norm_clipping_text = ipywidgets.BoundedFloatText(
            value=hog_options['l2_norm_clip'],
            description='L2 norm clipping', min=0., width='1.5cm')
        self.algorithm_other_box = ipywidgets.Box(
            children=[self.signed_gradient_checkbox,
                      self.l2_norm_clipping_text], align='end')
        self.algorithm_options_box = ipywidgets.HBox(
            children=[self.algorithm_sizes_box, self.algorithm_other_box])
        self.algorithm_box = ipywidgets.Box(
            children=[self.algorithm_radiobuttons, self.algorithm_options_box])

        # Final widget
        self.options_box = ipywidgets.Tab(children=[self.window_box,
                                                    self.algorithm_box])
        self.options_box.set_title(0, 'Window')
        self.options_box.set_title(1, 'Algorithm')

        # Create final widget
        children = [self.options_box]
        super(HOGOptionsWidget, self).__init__(
            children, Dict, hog_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def window_mode(name, value):
            self.window_horizontal_text.disabled = value == 'sparse'
            self.window_vertical_text.disabled = value == 'sparse'
            self.window_step_unit_radiobuttons.disabled = value == 'sparse'
            self.window_height_text.disabled = value == 'sparse'
            self.window_width_text.disabled = value == 'sparse'
            self.window_size_unit_radiobuttons.disabled = value == 'sparse'
        self.mode_radiobuttons.observe(window_mode, names='value')

        # algorithm function
        def algorithm_mode(name, value):
            self.l2_norm_clipping_text.disabled = value == 'zhuramanan'
            self.signed_gradient_checkbox.disabled = value == 'zhuramanan'
            self.block_size_text.disabled = value == 'zhuramanan'
            self.num_bins_text.disabled = value == 'zhuramanan'
        self.algorithm_radiobuttons.observe(algorithm_mode, names='value')

        # get options
        def save_options(name, value):
            self.selected_values = {
                'mode': self.mode_radiobuttons.value,
                'algorithm': self.algorithm_radiobuttons.value,
                'num_bins': self.num_bins_text.value,
                'cell_size': self.cell_size_text.value,
                'block_size': self.block_size_text.value,
                'signed_gradient': self.signed_gradient_checkbox.value,
                'l2_norm_clip': self.l2_norm_clipping_text.value,
                'window_height': self.window_height_text.value,
                'window_width': self.window_width_text.value,
                'window_unit': self.window_size_unit_radiobuttons.value,
                'window_step_vertical': self.window_vertical_text.value,
                'window_step_horizontal': self.window_horizontal_text.value,
                'window_step_unit': self.window_step_unit_radiobuttons.value,
                'padding': self.padding_checkbox.value}
        self.mode_radiobuttons.observe(save_options, names='value')
        self.padding_checkbox.observe(save_options, names='value')
        self.window_height_text.observe(save_options, names='value')
        self.window_width_text.observe(save_options, names='value')
        self.window_size_unit_radiobuttons.observe(save_options,
                                                           names='value')
        self.window_vertical_text.observe(save_options, names='value')
        self.window_horizontal_text.observe(save_options, names='value')
        self.window_step_unit_radiobuttons.observe(save_options,
                                                           names='value')
        self.algorithm_radiobuttons.observe(save_options, names='value')
        self.num_bins_text.observe(save_options, names='value')
        self.cell_size_text.observe(save_options, names='value')
        self.block_size_text.observe(save_options, names='value')
        self.signed_gradient_checkbox.observe(save_options, names='value')
        self.l2_norm_clipping_text.observe(save_options, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.options_box, font_family, font_size, font_style,
                    font_weight)
        format_font(self.mode_radiobuttons, font_family, font_size, font_style,
                    font_weight)
        format_font(self.padding_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_height_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_width_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_size_unit_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_step_unit_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.algorithm_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.cell_size_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.block_size_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.num_bins_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.signed_gradient_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.l2_norm_clipping_text, font_family, font_size,
                    font_style, font_weight)


class DSIFTOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting desnse SIFT options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    dsift_options : `dict`
        The initial options. Example ::

            dsift_options = {'window_step_horizontal': 1,
                             'window_step_vertical': 1,
                             'num_bins_horizontal': 2,
                             'num_bins_vertical': 2,
                             'num_or_bins': 9,
                             'cell_size_horizontal': 6,
                             'cell_size_vertical': 6,
                             'fast': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, dsift_options, render_function=None):
        # Create widgets
        self.window_vertical_text = ipywidgets.BoundedIntText(
            value=dsift_options['window_step_vertical'],
            description='Step Y', min=1, width='2cm')
        self.window_horizontal_text = ipywidgets.BoundedIntText(
            value=dsift_options['window_step_horizontal'],
            description='Step X', min=1, width='2cm')
        self.fast_checkbox = ipywidgets.Checkbox(
            value=dsift_options['fast'],
            description='Fast computation')
        self.cell_size_vertical_text = ipywidgets.BoundedIntText(
            value=dsift_options['cell_size_vertical'],
            description='Cell size Y', min=1, width='2cm')
        self.cell_size_horizontal_text = ipywidgets.BoundedIntText(
            value=dsift_options['cell_size_horizontal'],
            description='Cell size X', min=1, width='2cm')
        self.num_bins_vertical_text = ipywidgets.BoundedIntText(
            value=dsift_options['num_bins_vertical'],
            description='Bins Y', min=1, width='2cm')
        self.num_bins_horizontal_text = ipywidgets.BoundedIntText(
            value=dsift_options['num_bins_horizontal'],
            description='Bins X', min=1, width='2cm')
        self.num_or_bins_text = ipywidgets.BoundedIntText(
            value=dsift_options['num_or_bins'],
            description='Orientation bins', min=1, width='2cm')

        # Final widget
        self.window_step_box = ipywidgets.VBox(
            children=[self.window_vertical_text, self.window_horizontal_text,
                      self.fast_checkbox])
        self.cell_size_box = ipywidgets.VBox(
            children=[self.cell_size_vertical_text,
                      self.cell_size_horizontal_text])
        self.num_bins_box = ipywidgets.VBox(
            children=[self.num_bins_vertical_text,
                      self.num_bins_horizontal_text, self.num_or_bins_text])
        self.options_box = ipywidgets.HBox(children=[self.window_step_box,
                                                     self.cell_size_box,
                                                     self.num_bins_box])

        # Create final widget
        children = [self.options_box]
        super(DSIFTOptionsWidget, self).__init__(
            children, Dict, dsift_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Get options
        def save_options(name, value):
            self.selected_values = {
                'window_step_horizontal': self.window_horizontal_text.value,
                'window_step_vertical': self.window_vertical_text.value,
                'num_bins_horizontal': self.num_bins_horizontal_text.value,
                'num_bins_vertical': self.num_bins_vertical_text.value,
                'num_or_bins': self.num_or_bins_text.value,
                'cell_size_horizontal': self.cell_size_horizontal_text.value,
                'cell_size_vertical': self.cell_size_vertical_text.value,
                'fast': self.fast_checkbox.value}
        self.window_vertical_text.observe(save_options, names='value')
        self.window_horizontal_text.observe(save_options, names='value')
        self.num_bins_vertical_text.observe(save_options, names='value')
        self.num_bins_horizontal_text.observe(save_options, names='value')
        self.num_or_bins_text.observe(save_options, names='value')
        self.cell_size_vertical_text.observe(save_options, names='value')
        self.cell_size_horizontal_text.observe(save_options, names='value')
        self.fast_checkbox.observe(save_options, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.options_box, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.num_bins_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.num_bins_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.num_or_bins_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.cell_size_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.cell_size_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.fast_checkbox, font_family, font_size, font_style,
                    font_weight)


class DaisyOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting Daisy options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    daisy_options : `dict`
        The initial options. Example ::

            daisy_options = {'step': 1,
                             'radius': 15,
                             'rings': 2,
                             'histograms': 2,
                             'orientations': 8,
                             'normalization': 'l1',
                             'sigmas': None,
                             'ring_radii': None}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, daisy_options, render_function=None):
        self.step_text = ipywidgets.BoundedIntText(
            value=daisy_options['step'], description='Step', min=1,
            max=10**6, width='1.6cm')
        self.radius_text = ipywidgets.BoundedIntText(
            value=daisy_options['radius'], description='Radius', min=1,
            max=10**6, width='1.6cm')
        self.rings_text = ipywidgets.BoundedIntText(
            value=daisy_options['rings'], description='Rings', min=1,
            max=10**6, width='1.6cm')
        self.histograms_text = ipywidgets.BoundedIntText(
            value=daisy_options['histograms'], description='Histograms',
            min=1, max=10**6, width='1.6cm')
        self.orientations_text = ipywidgets.BoundedIntText(
            value=daisy_options['orientations'], description='Orientations',
            min=1, max=10**6, width='1.6cm')
        tmp = OrderedDict()
        tmp['L1'] = 'l1'
        tmp['L2'] = 'l2'
        tmp['Daisy'] = 'daisy'
        tmp['None'] = None
        self.normalization_dropdown = ipywidgets.Dropdown(
            value=daisy_options['normalization'], options=tmp,
            description='Normalisation')
        init_sigmas = daisy_options['sigmas']
        if init_sigmas is None:
            init_sigmas = []
        self.sigmas_wid = ListWidget(
            init_sigmas, mode='float', description='Sigmas',
            render_function=None, example_visible=False)
        init_ring = daisy_options['ring_radii']
        if init_ring is None:
            init_ring = []
        self.ring_radii_wid = ListWidget(
            init_ring, mode='float', description='Ring radii',
            render_function=None, example_visible=False)
        self.step_radius_rings_histograms_box = ipywidgets.VBox(
            children=[self.step_text, self.radius_text, self.rings_text,
                      self.histograms_text])
        self.orientations_normalization_sigmas_radii_box = ipywidgets.VBox(
            children=[self.orientations_text, self.normalization_dropdown,
                      self.sigmas_wid, self.ring_radii_wid])

        # Create final widget
        children = [self.step_radius_rings_histograms_box,
                    self.orientations_normalization_sigmas_radii_box]
        super(DaisyOptionsWidget, self).__init__(
            children, Dict, daisy_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def save_options(name, value):
            sigmas_val = self.sigmas_wid.selected_values
            if len(sigmas_val) == 0:
                sigmas_val = None
            ring_radii_val = self.ring_radii_wid.selected_values
            if len(ring_radii_val) == 0:
                ring_radii_val = None
            self.selected_values = {
                'step': self.step_text.value,
                'radius': self.radius_text.value,
                'rings': self.rings_text.value,
                'histograms': self.histograms_text.value,
                'orientations': self.orientations_text.value,
                'normalization': self.normalization_dropdown.value,
                'sigmas': sigmas_val,
                'ring_radii': ring_radii_val}
        self.step_text.observe(save_options, names='value')
        self.radius_text.observe(save_options, names='value')
        self.rings_text.observe(save_options, names='value')
        self.histograms_text.observe(save_options, names='value')
        self.orientations_text.observe(save_options, names='value')
        self.normalization_dropdown.observe(save_options, names='value')
        self.sigmas_wid.observe(save_options, names='selected_values')
        self.ring_radii_wid.observe(save_options, names='selected_values')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.step_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.radius_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.rings_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.histograms_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.orientations_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.normalization_dropdown, font_family, font_size,
                    font_style, font_weight)
        self.sigmas_wid.style(box_style=None, border_visible=False,
                              font_family=font_family, font_size=font_size,
                              font_style=font_style, font_weight=font_weight)
        self.ring_radii_wid.style(box_style=None, border_visible=False,
                                  font_family=font_family, font_size=font_size,
                                  font_style=font_style,
                                  font_weight=font_weight)


class LBPOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting LBP options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    lbp_options : `dict`
        The initial options. Example ::

        lbp_options = {'radius': range(1, 5),
                       'samples': [8] * 4,
                       'mapping_type': 'u2',
                       'window_step_vertical': 1,
                       'window_step_horizontal': 1,
                       'window_step_unit': 'pixels',
                       'padding': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, lbp_options, render_function=None):
        # Create children
        tmp = OrderedDict()
        tmp['Uniform-2'] = 'u2'
        tmp['Rotation-Invariant'] = 'ri'
        tmp['Both'] = 'riu2'
        tmp['None'] = 'none'
        self.mapping_type_dropdown = ipywidgets.Dropdown(
            value=lbp_options['mapping_type'], options=tmp,
            description='Mapping')
        self.radius_wid = ListWidget(
            lbp_options['radius'], mode='int', description='Radius',
            render_function=None, example_visible=False)
        self.samples_wid = ListWidget(
            lbp_options['samples'], mode='int', description='Samples',
            render_function=None, example_visible=False)
        self.radius_samples_mapping_type_box = ipywidgets.VBox(
            children=[self.radius_wid, self.samples_wid,
                      self.mapping_type_dropdown])
        self.window_vertical_text = ipywidgets.BoundedIntText(
            value=lbp_options['window_step_vertical'], description='Step Y',
            min=1, max=10**6, width='1.5cm')
        self.window_horizontal_text = ipywidgets.BoundedIntText(
            value=lbp_options['window_step_horizontal'], description='Step X',
            min=1, max=10**6, width='1.5cm')
        tmp = OrderedDict()
        tmp['Pixels'] = 'pixels'
        tmp['Windows'] = 'cells'
        self.window_step_unit_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description='Step unit',
            value=lbp_options['window_step_unit'])
        self.padding_checkbox = ipywidgets.Checkbox(
            value=lbp_options['padding'], description='Padding')
        self.window_box = ipywidgets.Box(
            children=[self.window_vertical_text, self.window_horizontal_text,
                      self.window_step_unit_radiobuttons,
                      self.padding_checkbox])

        # Create final widget
        children = [self.window_box, self.radius_samples_mapping_type_box]
        super(LBPOptionsWidget, self).__init__(
            children, Dict, lbp_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def save_options(name, value):
            self.selected_values = {
                'radius': self.radius_wid.selected_values,
                'samples': self.samples_wid.selected_values,
                'mapping_type': self.mapping_type_dropdown.value,
                'window_step_vertical': self.window_vertical_text.value,
                'window_step_horizontal': self.window_horizontal_text.value,
                'window_step_unit': self.window_step_unit_radiobuttons.value,
                'padding': self.padding_checkbox.value}
        self.mapping_type_dropdown.observe(save_options, names='value')
        self.window_vertical_text.observe(save_options, names='value')
        self.window_horizontal_text.observe(save_options, names='value')
        self.window_step_unit_radiobuttons.observe(save_options,
                                                           names='value')
        self.padding_checkbox.observe(save_options, names='value')
        self.radius_wid.observe(save_options, names='selected_values')
        self.samples_wid.observe(save_options, names='selected_values')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.mapping_type_dropdown, font_family, font_size,
                    font_style, font_weight)
        self.radius_wid.style(box_style=None, border_visible=False,
                              font_family=font_family, font_size=font_size,
                              font_style=font_style, font_weight=font_weight)
        self.samples_wid.style(box_style=None, border_visible=False,
                               font_family=font_family, font_size=font_size,
                               font_style=font_style, font_weight=font_weight)
        format_font(self.window_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_step_unit_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.padding_checkbox, font_family, font_size, font_style,
                    font_weight)


class IGOOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting IGO options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    igo_options : `dict`
        The initial options. Example ::

        igo_options = {'double_angles': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, igo_options, render_function=None):
        self.double_angles_checkbox = ipywidgets.Checkbox(
            value=igo_options['double_angles'], description='Double angles')

        # Create final widget
        children = [self.double_angles_checkbox]
        super(IGOOptionsWidget, self).__init__(
            children, Dict, igo_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set functionality
        def save_options(name, value):
            self.selected_values = {'double_angles': value}
        self.double_angles_checkbox.observe(save_options, names='value')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.double_angles_checkbox, font_family, font_size,
                    font_style, font_weight)
