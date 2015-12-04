import ipywidgets
from traitlets.traitlets import Int, Dict

from .abstract import MenpoWidget
from .tools import IndexSliderWidget, IndexButtonsWidget, SlicingCommandWidget
from .style import map_styles_to_hex_colours, format_box, format_font


class AnimationOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for animating through a list of objects. The widget
    consists of the following parts from `ipywidgets` and `menpowidgets.tools`:

    == ================== ===================== ====================
    No Object             Variable (`self.`)    Description
    == ================== ===================== ====================
    1  ToggleButton       `play_stop_toggle`    The play/stop button
    2  ToggleButton       `play_options_toggle` Button that toggles

                                                the options menu
    3  Checkbox           `loop_checkbox`       Repeat mode
    4  FloatText          `interval_text`       Interval (secs)
    5  VBox               `loop_interval_box`   Contains 3, 4
    6  VBox               `play_options_box`    Contains 2, 5
    7  HBox               `animation_box`       Contains 1, 6
    8  IndexButtonsWidget `index_wid`           The index selector

       IndexSliderWidget                        widget
    == ================== ===================== ====================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` and ``replace_update_function()`` methods.

    Parameters
    ----------
    index : `dict`
        The dictionary with the initial options. For example
        ::

            index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    index_style : ``{'buttons', 'slider'}``, optional
        If ``'buttons'``, then `IndexButtonsWidget()` class is called. If
        ``'slider'``, then 'IndexSliderWidget()' class is called.
    interval : `float`, optional
        The interval between the animation progress.
    description : `str`, optional
        The title of the widget.
    loop_enabled : `bool`, optional
        If ``True``, then after reach the minimum (maximum) index values, the
        counting will continue from the end (beginning). If ``False``, the
        counting will stop at the minimum (maximum) value.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    continuous_update : `bool`, optional
        If ``True`` and `index_style` is set to ``'slider'``, then the render
        and update functions are called while moving the slider's handle. If
        ``False``, then the the functions are called only when the handle
        (mouse click) is released.

    Example
    -------
    Let's create an animation widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import AnimationOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Selected index: {}".format(wid.selected_values)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}
        >>> wid = AnimationOptionsWidget(index, index_style='buttons',
        >>>                              render_function=render_function,
        >>>                              style='info')
        >>> wid

    By pressing the buttons (or simply pressing the Play button), the printed
    message gets updated. Finally, let's change the widget status with a new
    dictionary of options:

        >>> new_options = {'min': 0, 'max': 20, 'step': 2, 'index': 16}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, index, render_function=None, index_style='buttons',
                 interval=0.2, description='Index: ', loop_enabled=True,
                 style='minimal', continuous_update=False):
        from time import sleep
        from IPython import get_ipython

        # Get the kernel to use it later in order to make sure that the widgets'
        # traits changes are passed during a while-loop
        kernel = get_ipython().kernel

        # Create index widget
        if index_style == 'slider':
            self.index_wid = IndexSliderWidget(
                index, description=description,
                continuous_update=continuous_update)
        elif index_style == 'buttons':
            self.index_wid = IndexButtonsWidget(
                index, description=description, minus_description='fa-minus',
                plus_description='fa-plus', loop_enabled=loop_enabled,
                text_editable=True)
        else:
            raise ValueError('index_style should be either slider or buttons')
        self.index_wid.style(box_style=None, border_visible=False,
                             padding=0, margin='0.1cm')

        # Create other widgets
        self.play_stop_toggle = ipywidgets.ToggleButton(
            icon='fa-play', description='', value=False, margin='0.1cm')
        self._toggle_play_style = 'success'
        self._toggle_stop_style = 'danger'
        if style == 'minimal':
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
        self.play_options_toggle = ipywidgets.ToggleButton(
            icon='fa-wrench', description='', value=False, margin='0.1cm')
        self.loop_checkbox = ipywidgets.Checkbox(
            description='Loop', value=loop_enabled)
        self.interval_text = ipywidgets.FloatText(description='Interval (sec)',
                                                  value=interval, width='1.4cm')
        self.loop_interval_box = ipywidgets.VBox(
            children=[self.interval_text, self.loop_checkbox], visible=False,
            margin='0.1cm', padding='0.1cm', border_color='black',
            border_style='solid', border_width=1)
        self.play_options_box = ipywidgets.HBox(
            children=[self.play_options_toggle, self.loop_interval_box])
        self.animation_box = ipywidgets.HBox(
            children=[self.play_stop_toggle, self.play_options_box])

        # Create final widget
        children = [self.index_wid, self.animation_box]
        super(AnimationOptionsWidget, self).__init__(
            children, Int, index['index'], render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']
        self.loop_enabled = loop_enabled
        self.index_style = index_style
        self.continuous_update = continuous_update

        # Set style
        self.predefined_style(style)

        # Set functionality
        def play_stop_pressed(name, value):
            if value:
                # Animation was not playing, so Play was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_stop_style
                # Change the description to Stop
                self.play_stop_toggle.icon = 'fa-stop'
                # Make sure that play options are off
                self.play_options_toggle.value = False
            else:
                # Animation was playing, so Stop was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_play_style
                # Change the description to Play
                self.play_stop_toggle.icon = 'fa-play'
            self.play_options_toggle.disabled = value
        self.play_stop_toggle.on_trait_change(play_stop_pressed, 'value')

        def play_options_visibility(name, value):
            self.loop_interval_box.visible = value
        self.play_options_toggle.on_trait_change(play_options_visibility,
                                                 'value')

        def animate(name, value):
            if self.loop_checkbox.value:
                # loop is enabled
                i = self.selected_values
                if i < self.max:
                    i += self.step
                else:
                    i = self.min

                while i <= self.max and self.play_stop_toggle.value:
                    # update index value
                    if index_style == 'slider':
                        self.index_wid.slider.value = i
                    else:
                        self.index_wid.index_text.value = i

                    # Run IPython iteration.
                    # This is the code that makes this operation non-blocking.
                    # This allows widget messages and callbacks to be processed.
                    kernel.do_one_iteration()

                    # update counter
                    if i < self.max:
                        i += self.step
                    else:
                        i = self.min

                    # wait
                    sleep(self.interval_text.value)
            else:
                # loop is disabled
                i = self.selected_values
                i += self.step
                while i <= self.max and self.play_stop_toggle.value:
                    # update index value
                    if index_style == 'slider':
                        self.index_wid.slider.value = i
                    else:
                        self.index_wid.index_text.value = i

                    # Run IPython iteration.
                    # This is the code that makes this operation non-blocking.
                    # This allows widget messages and callbacks to be processed.
                    kernel.do_one_iteration()

                    # update counter
                    i += self.step

                    # wait
                    sleep(self.interval_text.value)
                if i > self.max:
                    self.play_stop_toggle.value = False
        self.play_stop_toggle.on_trait_change(animate, 'value')

        def save_value(name, value):
            self.selected_values = self.index_wid.selected_values
        self.index_wid.on_trait_change(save_value, 'selected_values')

    def style(self, box_style=None, border_visible=False, border_color='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_color : `str`, optional
            The color of the border around the widget.
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

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_color, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.play_stop_toggle, font_family, font_size, font_style,
                    font_weight)
        format_font(self.play_options_toggle, font_family, font_size,
                    font_style, font_weight)
        format_font(self.loop_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.interval_text, font_family, font_size, font_style,
                    font_weight)
        if self.index_style == 'buttons':
            self.index_wid.style(
                box_style=None, border_visible=False, padding=0,
                margin='0.1cm', font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)
        else:
            self.index_wid.style(
                box_style=None, border_visible=False, padding=0,
                margin='0.1cm', font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style='', border_visible=False)
            self.play_stop_toggle.button_style = ''
            self.play_stop_toggle.font_weight = 'normal'
            self.play_options_toggle.button_style = ''
            format_box(self.loop_interval_box, '', False, 'black', 'solid', 1,
                       10, '0.1cm', '0.1cm')
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = ''
                self.index_wid.button_plus.font_weight = 'normal'
                self.index_wid.button_minus.button_style = ''
                self.index_wid.button_minus.font_weight = 'normal'
                self.index_wid.index_text.background_color = None
            elif self.index_style == 'slider':
                self.index_wid.slider.slider_color = None
                self.index_wid.slider.background_color = None
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
        elif (style == 'info' or style == 'success' or style == 'danger' or
              style == 'warning'):
            self.style(box_style=style, border_visible=False)
            self.play_stop_toggle.button_style = 'success'
            self.play_stop_toggle.font_weight = 'bold'
            self.play_options_toggle.button_style = 'info'
            format_box(self.loop_interval_box, 'info', True,
                       map_styles_to_hex_colours('info'), 'solid', 1, 10,
                       '0.1cm', '0.1cm')
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = 'primary'
                self.index_wid.button_plus.font_weight = 'bold'
                self.index_wid.button_minus.button_style = 'primary'
                self.index_wid.button_minus.font_weight = 'bold'
                self.index_wid.index_text.background_color = \
                    map_styles_to_hex_colours(style, True)
            elif self.index_style == 'slider':
                self.index_wid.slider.slider_color = \
                    map_styles_to_hex_colours(style)
                self.index_wid.slider.background_color = \
                    map_styles_to_hex_colours(style)
            self._toggle_play_style = 'success'
            self._toggle_stop_style = 'danger'
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, index, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        index : `dict`
            The dictionary with the new options to be used. For example
            ::

                index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update
        if self.play_stop_toggle.value:
            self.play_stop_toggle.value = False
        if self.index_style == 'slider':
            self.index_wid.set_widget_state(
                index, continuous_update=self.continuous_update,
                allow_callback=False)
        else:
            self.index_wid.set_widget_state(
                index, loop_enabled=self.loop_checkbox.value,
                text_editable=True, allow_callback=False)
        self.selected_values = index['index']
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', 0)


class ChannelOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting channel options when rendering an image. The
    widget consists of the following parts from `IPython.html.widgets`:

    == ============== ================================== =======================
    No Object         Variable (`self.`)                 Description
    == ============== ================================== =======================
    1  RadioButtons   `mode_radiobuttons`                The mode selector

                                                         'Single' or 'Multiple'
    2  Checkbox       `masked_checkbox`                  Controls masked mode
    3  IntSlider      `single_slider`                    Single channel selector
    4  IntRangeSlider `multiple_slider`                  Channels range selector
    5  Checkbox       `rgb_checkbox`                     View as RGB
    6  Checkbox       `sum_checkbox`                     View sum of channels
    7  Checkbox       `glyph_checkbox`                   View glyph
    8  BoundedIntText `glyph_block_size_text`            Glyph block size
    9  Checkbox       `glyph_use_negative_checkbox`      Use negative values
    10 VBox           `glyph_options_box`                Contains 8, 9
    11 VBox           `glyph_box`                        Contains 7, 10
    12 HBox           `multiple_options_box`             Contains 6, 11, 5
    13 Box            `sliders_box`                      Contains 3, 4
    14 Box            `sliders_and_multiple_options_box` Contains 13, 12
    15 VBox           `mode_and_masked_box`              Contains 1, 2
    == ============== ================================== =======================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` method.

    Parameters
    ----------
    channel_options : `dict`
        The dictionary with the initial options. For example
        ::

            channel_options = {'n_channels': 10,
                               'image_is_masked': True,
                               'channels': 0,
                               'glyph_enabled': False,
                               'glyph_block_size': 3,
                               'glyph_use_negative': False,
                               'sum_enabled': False,
                               'masked_enabled': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    Example
    -------
    Let's create a channels widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options_old import ChannelOptionsWidget
        >>> from IPython.display import display

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected channels and masked flag:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Channels: {}, Masked: {}".format(
        >>>         wid.selected_values['channels'],
        >>>         wid.selected_values['masked_enabled'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> channel_options = {'n_channels': 30,
        >>>                    'image_is_masked': True,
        >>>                    'channels': [0, 10],
        >>>                    'glyph_enabled': False,
        >>>                    'glyph_block_size': 3,
        >>>                    'glyph_use_negative': False,
        >>>                    'sum_enabled': True,
        >>>                    'masked_enabled': True}
        >>> wid = ChannelOptionsWidget(channel_options,
        >>>                            render_function=render_function,
        >>>                            style='warning')
        >>> display(wid)

    By playing around with the widget, printed message gets updated. Finally,
    let's change the widget status with a new dictionary of options:

        >>> new_options = {'n_channels': 10,
        >>>                'image_is_masked': True,
        >>>                'channels': [7, 8, 9],
        >>>                'glyph_enabled': True,
        >>>                'glyph_block_size': 3,
        >>>                'glyph_use_negative': True,
        >>>                'sum_enabled': False,
        >>>                'masked_enabled': False}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, channel_options, render_function=None, style='minimal'):
        # If image_is_masked is False, then masked_enabled should be False too
        if not channel_options['image_is_masked']:
            channel_options['masked_enabled'] = False

        # Parse channels
        if channel_options['channels'] is None:
            channels = str(range(channel_options['n_channels'])).strip('[]')
        elif isinstance(channel_options['channels'], list):
            channels = str(channel_options['channels']).strip('[]')
        else:
            channels = str(channel_options['channels'])

        # Parse sum, glyph
        if channel_options['sum_enabled'] and channel_options['glyph_enabled']:
            channel_options['sum_enabled'] = False
            channel_options['glyph_enabled'] = False

        # Create children
        slice_options = {'command': channels,
                         'length': channel_options['n_channels']}
        self.channels_wid = SlicingCommandWidget(
            slice_options, description='Channels:', render_function=None,
            example_visible=True, continuous_update=False)
        self.masked_checkbox = ipywidgets.Checkbox(
            value=channel_options['masked_enabled'], description='Masked',
            visible=channel_options['image_is_masked'])
        self.rgb_checkbox = ipywidgets.Checkbox(
            value=(channel_options['n_channels'] == 3 and
                   channel_options['channels'] is None),
            description='RGB')
        self.sum_checkbox = ipywidgets.Checkbox(
            value=channel_options['sum_enabled'], description='Sum')
        self.glyph_checkbox = ipywidgets.Checkbox(
            value=channel_options['glyph_enabled'], description='Glyph')
        self.glyph_block_size_text = ipywidgets.BoundedIntText(
            description='Block size', min=1, max=25,
            value=channel_options['glyph_block_size'], width='1.5cm')
        self.glyph_use_negative_checkbox = ipywidgets.Checkbox(
            description='Negative', value=channel_options['glyph_use_negative'])

        # Group widgets
        self.glyph_options_box = ipywidgets.VBox(
            children=[self.glyph_block_size_text,
                      self.glyph_use_negative_checkbox])
        self.glyph_box = ipywidgets.HBox(children=[self.glyph_checkbox,
                                                   self.glyph_options_box],
                                         align='start')
        self.glyph_sum_options_box = ipywidgets.VBox(
            children=[self.sum_checkbox, self.glyph_box])
        self.rgb_masked_options_box = ipywidgets.VBox(
            children=[self.rgb_checkbox, self.masked_checkbox])

        # Create final widget
        if channel_options['n_channels'] == 1:
            if channel_options['image_is_masked']:
                children = [self.masked_checkbox]
            else:
                children = [ipywidgets.Latex(value='No options available')]
        else:
            children = [self.channels_wid, self.rgb_masked_options_box,
                        self.glyph_sum_options_box]
        super(ChannelOptionsWidget, self).__init__(
            children, Dict, channel_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set style
        #self.predefined_style(style)

    #     # Set functionality
    #     def mode_selection(name, value):
    #         # Temporarily remove render function
    #         self.sum_checkbox.on_trait_change(self._render_function, 'value',
    #                                           remove=True)
    #         self.glyph_checkbox.on_trait_change(self._render_function, 'value',
    #                                             remove=True)
    #         # Control visibility of widgets
    #         if value == 'Single':
    #             self.multiple_slider.visible = False
    #             self.single_slider.visible = True
    #             self.sum_checkbox.visible = False
    #             self.sum_checkbox.value = False
    #             self.glyph_checkbox.visible = False
    #             self.glyph_checkbox.value = False
    #             self.glyph_options_box.visible = False
    #             self.rgb_checkbox.visible = \
    #                 self.selected_values['n_channels'] == 3
    #         else:
    #             self.single_slider.visible = False
    #             self.multiple_slider.visible = True
    #             self.sum_checkbox.visible = True
    #             self.sum_checkbox.value = False
    #             self.glyph_checkbox.visible = \
    #                 self.selected_values['n_channels'] > 1
    #             self.glyph_checkbox.value = False
    #             self.glyph_options_box.visible = False
    #             self.rgb_checkbox.visible = False
    #         # Add render function
    #         if self._render_function is not None:
    #             self.sum_checkbox.on_trait_change(self._render_function,
    #                                               'value')
    #             self.glyph_checkbox.on_trait_change(self._render_function,
    #                                                 'value')
    #     self.mode_radiobuttons.on_trait_change(mode_selection, 'value')
    #
    #     def glyph_options_visibility(name, value):
    #         # Temporarily remove render function
    #         self.sum_checkbox.on_trait_change(self._render_function, 'value',
    #                                           remove=True)
    #         # Check value of sum checkbox
    #         if value:
    #             self.sum_checkbox.value = False
    #         # Add render function
    #         if self._render_function is not None:
    #             self.sum_checkbox.on_trait_change(self._render_function,
    #                                               'value')
    #         # Control glyph options visibility
    #         self.glyph_options_box.visible = value
    #     self.glyph_checkbox.on_trait_change(glyph_options_visibility, 'value')
    #
    #     self.link_rgb_checkbox_and_single_slider = link(
    #         (self.rgb_checkbox, 'value'), (self.single_slider, 'disabled'))
    #
    #     def sum_fun(name, value):
    #         # Temporarily remove render function
    #         self.glyph_checkbox.on_trait_change(self._render_function, 'value',
    #                                             remove=True)
    #         # Check value of glyph checkbox
    #         if value:
    #             self.glyph_checkbox.value = False
    #         # Add render function
    #         if self._render_function is not None:
    #             self.glyph_checkbox.on_trait_change(self._render_function,
    #                                                 'value')
    #     self.sum_checkbox.on_trait_change(sum_fun, 'value')
    #
    #     def get_glyph_options(name, value):
    #         self.selected_values['glyph_enabled'] = self.glyph_checkbox.value
    #         self.selected_values['sum_enabled'] = self.sum_checkbox.value
    #         self.selected_values['glyph_use_negative'] = \
    #             self.glyph_use_negative_checkbox.value
    #         self.selected_values['glyph_block_size'] = \
    #             self.glyph_block_size_text.value
    #     self.glyph_checkbox.on_trait_change(get_glyph_options, 'value')
    #     self.sum_checkbox.on_trait_change(get_glyph_options, 'value')
    #     self.glyph_use_negative_checkbox.on_trait_change(get_glyph_options,
    #                                                      'value')
    #     self.glyph_block_size_text.on_trait_change(get_glyph_options, 'value')
    #
    #     def get_channels(name, value):
    #         if self.mode_radiobuttons.value == "Single":
    #             if self.rgb_checkbox.value:
    #                 self.selected_values['channels'] = None
    #             else:
    #                 self.selected_values['channels'] = self.single_slider.value
    #         else:
    #             self.selected_values['channels'] = range(
    #                 self.multiple_slider.lower, self.multiple_slider.upper + 1)
    #     self.single_slider.on_trait_change(get_channels, 'value')
    #     self.multiple_slider.on_trait_change(get_channels, 'value')
    #     self.rgb_checkbox.on_trait_change(get_channels, 'value')
    #     self.mode_radiobuttons.on_trait_change(get_channels, 'value')
    #
    #     def get_masked(name, value):
    #         self.selected_values['masked_enabled'] = value
    #     self.masked_checkbox.on_trait_change(get_masked, 'value')
    #
    # def _parse_options(self, channels):
    #     if isinstance(channels, list):
    #         if len(channels) == 1:
    #             mode_value = 'Single'
    #             single_slider_value = channels[0]
    #             multiple_slider_value = (0, 1)
    #         else:
    #             mode_value = 'Multiple'
    #             single_slider_value = 0
    #             multiple_slider_value = (min(channels), max(channels))
    #     elif channels is None:
    #         mode_value = 'Single'
    #         single_slider_value = 0
    #         multiple_slider_value = (0, 1)
    #     else:
    #         mode_value = 'Single'
    #         single_slider_value = channels
    #         multiple_slider_value = (0, 1)
    #     return mode_value, single_slider_value, multiple_slider_value
    #
    # def _parse_sum_glyph(self, mode_value, sum_enabled, glyph_enabled):
    #     if mode_value == 'Single' or (sum_enabled and glyph_enabled):
    #         sum_enabled = False
    #         glyph_enabled = False
    #     return sum_enabled, glyph_enabled
    #
    # def _single_slider_visible(self, mode):
    #     return mode == 'Single'
    #
    # def _multiple_slider_visible(self, mode):
    #     return mode == 'Multiple'
    #
    # def _rgb_checkbox_visible(self, mode, n_channels):
    #     return mode == 'Single' and n_channels == 3
    #
    # def _sum_checkbox_visible(self, mode, n_channels):
    #     return mode == 'Multiple' and n_channels > 1
    #
    # def _glyph_checkbox_visible(self, mode, n_channels):
    #     return mode == 'Multiple' and n_channels > 1
    #
    # def _glyph_options_visible(self, mode, n_channels, glyph_value):
    #     return mode == 'Multiple' and n_channels > 1 and glyph_value
    #
    # def style(self, box_style=None, border_visible=False, border_color='black',
    #           border_style='solid', border_width=1, border_radius=0, padding=0,
    #           margin=0, font_family='', font_size=None, font_style='',
    #           font_weight='', slider_width='', slider_colour=None):
    #     r"""
    #     Function that defines the styling of the widget.
    #
    #     Parameters
    #     ----------
    #     box_style : See Below, optional
    #         Style options
    #
    #             ========= ============================
    #             Style     Description
    #             ========= ============================
    #             'success' Green-based style
    #             'info'    Blue-based style
    #             'warning' Yellow-based style
    #             'danger'  Red-based style
    #             ''        Default style
    #             None      No style
    #             ========= ============================
    #
    #     border_visible : `bool`, optional
    #         Defines whether to draw the border line around the widget.
    #     border_color : `str`, optional
    #         The color of the border around the widget.
    #     border_style : `str`, optional
    #         The line style of the border around the widget.
    #     border_width : `float`, optional
    #         The line width of the border around the widget.
    #     border_radius : `float`, optional
    #         The radius of the corners of the box.
    #     padding : `float`, optional
    #         The padding around the widget.
    #     margin : `float`, optional
    #         The margin around the widget.
    #     font_family : See Below, optional
    #         The font family to be used.
    #         Example options ::
    #
    #             {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
    #              'helvetica'}
    #
    #     font_size : `int`, optional
    #         The font size.
    #     font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
    #         The font style.
    #     font_weight : See Below, optional
    #         The font weight.
    #         Example options ::
    #
    #             {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
    #              'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
    #              'extra bold', 'black'}
    #
    #     slider_width : `str`, optional
    #         The width of the slider.
    #     slider_colour : `str`, optional
    #         The colour of the sliders.
    #     """
    #     format_box(self, box_style, border_visible, border_color, border_style,
    #                border_width, border_radius, padding, margin)
    #     self.single_slider.width = slider_width
    #     self.multiple_slider.width = slider_width
    #     format_font(self, font_family, font_size, font_style, font_weight)
    #     format_font(self.mode_radiobuttons, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.single_slider, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.multiple_slider, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.masked_checkbox, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.rgb_checkbox, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.sum_checkbox, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.glyph_checkbox, font_family, font_size, font_style,
    #                 font_weight)
    #     format_font(self.glyph_use_negative_checkbox, font_family, font_size,
    #                 font_style, font_weight)
    #     format_font(self.glyph_block_size_text, font_family, font_size,
    #                 font_style, font_weight)
    #     self.single_slider.slider_color = slider_colour
    #     self.single_slider.background_color = slider_colour
    #     self.multiple_slider.slider_color = slider_colour
    #     self.multiple_slider.background_color = slider_colour
    #
    # def predefined_style(self, style):
    #     r"""
    #     Function that sets a predefined style on the widget.
    #
    #     Parameters
    #     ----------
    #     style : `str` (see below)
    #         Style options
    #
    #             ========= ============================
    #             Style     Description
    #             ========= ============================
    #             'minimal' Simple black and white style
    #             'success' Green-based style
    #             'info'    Blue-based style
    #             'warning' Yellow-based style
    #             'danger'  Red-based style
    #             ''        No style
    #             ========= ============================
    #     """
    #     if style == 'minimal':
    #         self.style(box_style=None, border_visible=True,
    #                    border_color='black', border_style='solid',
    #                    border_width=1, border_radius=0, padding='0.2cm',
    #                    margin='0.3cm', font_family='', font_size=None,
    #                    font_style='', font_weight='', slider_width='5cm',
    #                    slider_colour=None)
    #         format_box(self.glyph_options_box, box_style='',
    #                    border_visible=False, border_color='',
    #                    border_style='solid', border_width=1, border_radius=0,
    #                    padding='0.1cm', margin=0)
    #     elif (style == 'info' or style == 'success' or style == 'danger' or
    #                   style == 'warning'):
    #         self.style(box_style=style, border_visible=True,
    #                    border_color=map_styles_to_hex_colours(style),
    #                    border_style='solid', border_width=1, border_radius=10,
    #                    padding='0.2cm', margin='0.3cm', font_family='',
    #                    font_size=None, font_style='', font_weight='',
    #                    slider_width='5cm',
    #                    slider_colour=map_styles_to_hex_colours(style))
    #         format_box(self.glyph_options_box, box_style=style,
    #                    border_visible=True,
    #                    border_color=map_styles_to_hex_colours(style),
    #                    border_style='solid', border_width=1, border_radius=10,
    #                    padding='0.1cm', margin=0)
    #     else:
    #         raise ValueError('style must be minimal or info or success or '
    #                          'danger or warning')
    #
    # def set_widget_state(self, channel_options, allow_callback=True):
    #     r"""
    #     Method that updates the state of the widget with a new set of values.
    #
    #     Parameters
    #     ----------
    #     channel_options : `dict`
    #         The dictionary with the new options to be used. For example
    #         ::
    #
    #             channel_options = {'n_channels': 10,
    #                                'image_is_masked': True,
    #                                'channels': 0,
    #                                'glyph_enabled': False,
    #                                'glyph_block_size': 3,
    #                                'glyph_use_negative': False,
    #                                'sum_enabled': False,
    #                                'masked_enabled': True}
    #
    #     allow_callback : `bool`, optional
    #         If ``True``, it allows triggering of any callback functions.
    #     """
    #     # temporarily remove render callback
    #     render_function = self._render_function
    #     self.remove_render_function()
    #
    #     # If image_is_masked is False, then masked_enabled should be False too
    #     if not channel_options['image_is_masked']:
    #         channel_options['masked_enabled'] = False
    #
    #     # Parse channels
    #     mode_default, single_slider_default, multiple_slider_default = \
    #         self._parse_options(channel_options['channels'])
    #
    #     # Check sum and glyph options
    #     channel_options['sum_enabled'], channel_options['glyph_enabled'] = \
    #         self._parse_sum_glyph(mode_default, channel_options['sum_enabled'],
    #                               channel_options['glyph_enabled'])
    #
    #     # Update widgets' state
    #     self.mode_radiobuttons.value = mode_default
    #     self.mode_radiobuttons.disabled = channel_options['n_channels'] == 1
    #
    #     self.masked_checkbox.value = channel_options['masked_enabled']
    #     self.masked_checkbox.visible = channel_options['image_is_masked']
    #
    #     self.single_slider.max = channel_options['n_channels'] - 1
    #     self.single_slider.value = single_slider_default
    #     self.single_slider.visible = self._single_slider_visible(mode_default)
    #     self.single_slider.disabled = channel_options['n_channels'] == 1
    #
    #     self.multiple_slider.max = channel_options['n_channels'] - 1
    #     self.multiple_slider.value = multiple_slider_default
    #     self.multiple_slider.visible = self._multiple_slider_visible(
    #         mode_default)
    #
    #     self.rgb_checkbox.value = (channel_options['n_channels'] == 3 and
    #                                channel_options['channels'] is None)
    #     self.rgb_checkbox.visible = self._rgb_checkbox_visible(
    #         mode_default, channel_options['n_channels'])
    #
    #     self.sum_checkbox.value = channel_options['sum_enabled']
    #     self.sum_checkbox.visible = self._sum_checkbox_visible(
    #         mode_default, channel_options['n_channels'])
    #
    #     self.glyph_checkbox.value = channel_options['glyph_enabled']
    #     self.glyph_checkbox.visible = self._glyph_checkbox_visible(
    #         mode_default, channel_options['n_channels'])
    #
    #     self.glyph_block_size_text.value = channel_options['glyph_block_size']
    #
    #     self.glyph_use_negative_checkbox.value = \
    #         channel_options['glyph_use_negative']
    #
    #     self.glyph_options_box.visible = self._glyph_options_visible(
    #         mode_default, channel_options['n_channels'],
    #         channel_options['glyph_enabled'])
    #
    #     # Re-assign render callback
    #     self.add_render_function(render_function)
    #
    #     # Assign new options dict to selected_values
    #     self.selected_values = channel_options
    #
    #     # trigger render function if allowed
    #     if allow_callback:
    #         self._render_function('', True)