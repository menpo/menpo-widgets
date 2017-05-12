from menpo.base import MenpoMissingDependencyError

try:
    import menpo3d
except ImportError:
    raise MenpoMissingDependencyError('menpo3d')

# Continue with imports if we have menpo3d
import sys
from collections import Sized, OrderedDict
import matplotlib.pyplot as plt

import ipywidgets
import IPython.display as ipydisplay

from menpo.visualize import print_dynamic
from menpo.base import name_of_callable

from ..style import map_styles_to_hex_colours
from ..checks import check_n_parameters
from ..options import (RendererOptionsWidget, TextPrintWidget,
                       LinearModelParametersWidget, LogoWidget,
                       SaveMayaviFigureOptionsWidget)


def visualize_morphable_model(mm, n_shape_parameters=5, n_texture_parameters=5,
                              mode='multiple', parameters_bounds=(-15.0, 15.0),
                              style='coloured'):
    r"""
    Widget that allows the dynamic visualization of a 3D Morphable Model.

    Parameters
    ----------
    mm : `menpo3d.morhpablemodel.ColouredMorphableModel` or `subclass`
        The multi-scale 3D Morphable Model to be visualized.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    n_texture_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the tecture
        parameters sliders. If `int`, then the number of sliders per level is
        the minimum between `n_parameters` and the number of active components
        per level. If `list` of `int`, then a number of sliders is defined per
        level. If ``None``, all the active components per level will have a
        slider.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, then only a single slider is constructed along with a
        drop down menu. If ``'multiple'``, then a slider is constructed for each
        parameter.
    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    print('Initializing...')
    sys.stdout.flush()

    # Ensure that the code is being run inside a Jupyter kernel!
    from ..utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()

    # Define the styling options
    if style == 'coloured':
        model_tab_style = 'danger'
        model_parameters_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_tab_style = ''
        model_parameters_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Check the given number of parameters
    n_shape_parameters = check_n_parameters(
        n_shape_parameters, 1, [mm.shape_model.n_active_components])
    n_texture_parameters = check_n_parameters(
        n_texture_parameters, 1, [mm.texture_model.n_active_components])

    # Define render function
    def render_function(change):
        # Compute weights
        shape_weights = shape_model_parameters_wid.selected_values
        shape_weights = (
            shape_weights *
            mm.shape_model.eigenvalues[:len(shape_weights)] ** 0.5)
        texture_weights = texture_model_parameters_wid.selected_values
        texture_weights = (
            texture_weights *
            mm.texture_model.eigenvalues[:len(texture_weights)] ** 0.5)
        instance = mm.instance(shape_weights=shape_weights,
                               texture_weights=texture_weights)
        instance = instance.with_clipped_texture()

        # Render shape instance with selected options
        options = renderer_options_wid.selected_values['coloured_trimesh']

        # Clear figure
        save_figure_wid.renderer.clear_figure()

        # Render instance
        renderer = instance.view(figure_id=save_figure_wid.renderer.figure_id,
                                 new_figure=False, **options)

        # Save the current figure id
        save_figure_wid.renderer = renderer

        # Update info
        update_info(mm, instance)

        # Force rendering
        renderer.force_draw()

    # Define function that updates the info text
    def update_info(mm, instance):
        text_per_line = [
            "> {} vertices, {} triangles".format(mm.n_vertices,
                                                 mm.n_triangles),
            "> {} shape components ({:.2f}% of variance)".format(
                mm.shape_model.n_components,
                mm.shape_model.variance_ratio() * 100),
            "> {} texture channels".format(mm.n_channels),
            "> {} texture components ({:.2f}% of variance)".format(
                mm.texture_model.n_components,
                mm.texture_model.variance_ratio() * 100),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.colours.min(), instance.colours.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot shape variance function
    def plot_shape_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Render
        plt.subplot(121)
        mm.shape_model.plot_eigenvalues_ratio()
        plt.subplot(122)
        mm.shape_model.plot_eigenvalues_cumulative_ratio()
        plt.show()

    # Plot texture variance function
    def plot_texture_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Render
        plt.subplot(121)
        mm.texture_model.plot_eigenvalues_ratio()
        plt.subplot(122)
        mm.texture_model.plot_eigenvalues_cumulative_ratio()
        plt.show()

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
        n_shape_parameters[0], render_function, params_str='Parameter ',
        mode=mode, params_bounds=parameters_bounds, params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_shape_variance,
        style=model_parameters_style, animation_step=0.5, interval=0.,
        loop_enabled=True)
    texture_model_parameters_wid = LinearModelParametersWidget(
        n_texture_parameters[0], render_function, params_str='Parameter ',
        mode=mode, params_bounds=parameters_bounds, params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_texture_variance,
        style=model_parameters_style, animation_step=0.5, interval=0.,
        loop_enabled=True)
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['coloured_trimesh'], labels=None,
        render_function=render_function, style=renderer_style,
        tabs_style=renderer_tabs_style)
    info_wid = TextPrintWidget(text_per_line=[''] * 5, style=info_style)
    save_figure_wid = SaveMayaviFigureOptionsWidget(renderer=None,
                                                    style=save_figure_style)

    # Group widgets
    model_parameters_wid = ipywidgets.Tab(
        children=[shape_model_parameters_wid, texture_model_parameters_wid])
    model_parameters_wid.set_title(0, 'Shape')
    model_parameters_wid.set_title(1, 'Texture')
    model_parameters_wid = ipywidgets.FlexBox(children=[model_parameters_wid],
                                              margin='0.2cm', padding='0.1cm',
                                              box_style=model_tab_style)
    options_box = ipywidgets.Tab(children=[model_parameters_wid,
                                           renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Renderer', 'Info', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})
    ipydisplay.clear_output()
