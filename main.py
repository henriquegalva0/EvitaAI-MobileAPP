from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, PushMatrix, PopMatrix, Rotate, Line
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup

import webbrowser

from consulta_api_classficacao import classificacao_analise_gpt
from consulta_api_relatorio import consultar_analise_gpt_relatorio

LabelBase.register(name='Roboto-Thin', fn_regular='fonts/Roboto-Thin.ttf')

try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
except Exception:
    # Se não estiver rodando no Android (ex: desenvolvimento no PC)
    PythonActivity = None
    Intent = None
    print("Pyjnius e classes Android não disponíveis. Rodando em ambiente não-Android.")

from jnius import autoclass, cast
from android.permissions import request_permissions, Permission

request_permissions([Permission.POST_NOTIFICATIONS])

class AccessibilityButton(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 60)
        
        with self.canvas:
            # Background circle with transparency
            Color(0.4, 0.6, 0.9, 0.3)  # Blue with transparency
            self.bg_circle = Ellipse(pos=self.pos, size=self.size)
            
            # Border circle
            Color(0.4, 0.6, 0.9, 0.8)  # Less transparent border
            self.border_line = Line(circle=(self.center_x, self.center_y, 30), width=2)
        
        # Add the "A" label
        self.label = Label(
            text="A",
            font_size=30,
            color=(0.4, 0.6, 0.9, 1),
            pos=self.pos,
            size=self.size,
            font_name='Roboto-Thin'
        )
        self.add_widget(self.label)
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size
        self.border_line.circle = (self.center_x, self.center_y, self.width/2)
        self.label.pos = self.pos
        self.label.size = self.size

class AccessibilityPopup(Popup):
    def __init__(self, main_layout, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = main_layout
        self.title = ""
        self.size_hint = (0.8, 0.4)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.separator_height = 0
        self.title_size = 0
        self.background = ''
        self.background_color = (0, 0, 0, 0)

        # Main content layout
        content = BoxLayout(orientation='vertical', padding=20, spacing=45)
        
        # Close button (X)
        close_layout = BoxLayout(size_hint_y=None, height=40)
        close_layout.add_widget(Widget())  # Spacer
        close_btn = Label(
            text="X",
            size_hint=(None, None),
            size=(40, 40),
            font_size=40,
            color=(0.9, 0.9, 0.9, 1)
        )
        close_btn.bind(on_touch_down=self._close_popup)
        close_layout.add_widget(close_btn)
        content.add_widget(close_layout)
        
        # Font size section
        font_label = Label(
            text="Tamanho da escrita",
            size_hint_y=None,
            height=40,
            font_size=30,
            color=(0.8, 0.8, 0.8, 1),
            font_name='Roboto-Thin'
        )
        content.add_widget(font_label)
        
        # Font size slider
        self.font_slider = Slider(
            min=0.8,
            max=2,
            value=1.4,
            size_hint_y=None,
            height=40
        )
        self.font_slider.bind(value=self._on_font_size_change)
        content.add_widget(self.font_slider)
        
        # Theme section
        theme_label = Label(
            text="Escolha o tema",
            size_hint_y=None,
            height=40,
            font_size=30,
            color=(0.8, 0.8, 0.8, 1),
            font_name='Roboto-Thin'
        )
        content.add_widget(theme_label)
        
        # Theme buttons
        theme_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.dark_btn = RoundedButton(text="Escuro", size_hint_y=None, height=50)
        self.dark_btn.bind(on_press=lambda x: self._set_theme('dark'))
        
        self.light_btn = RoundedButton(text="Claro", size_hint_y=None, height=50)
        self.light_btn.bind(on_press=lambda x: self._set_theme('light'))
        
        theme_layout.add_widget(self.dark_btn)
        theme_layout.add_widget(self.light_btn)
        content.add_widget(theme_layout)
        
        self.content = content
    
    def _close_popup(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.dismiss()
            return True
        return False
    
    def _on_font_size_change(self, instance, value):
        self.main_layout.set_font_scale(value)
    
    def _set_theme(self, theme):
        self.main_layout.set_theme(theme)

class LoadingSpinner(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.angle = 0
        
        # Bind to window size changes for responsive sizing
        Window.bind(on_resize=self._update_size)
        self._update_size()
        
        with self.canvas:
            PushMatrix()
            self.rotate = Rotate()
            self.rotate.angle = 0
            
            # Create multiple dots for spinner effect
            Color(0.4, 0.6, 0.9, 1)
            self.dot1 = Ellipse()
            Color(0.4, 0.6, 0.9, 0.8)
            self.dot2 = Ellipse()
            Color(0.4, 0.6, 0.9, 0.6)
            self.dot3 = Ellipse()
            Color(0.4, 0.6, 0.9, 0.4)
            self.dot4 = Ellipse()
            
            PopMatrix()
            
        self.bind(pos=self._update_spinner, size=self._update_spinner)
        self.animation_event = None
        
    def _update_size(self, *args):
        # Responsive sizing based on window dimensions
        min_dimension = min(Window.width, Window.height)
        spinner_size = max(40, min_dimension * 0.08)
        self.size = (spinner_size, spinner_size)
        
    def _update_spinner(self, *args):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        # Update rotation origin when position changes
        self.rotate.origin = (center_x, center_y)
        
        # Update dot positions and sizes relative to widget size
        dot_size_1 = self.width * 0.16
        dot_size_2 = self.width * 0.13
        dot_size_3 = self.width * 0.10
        dot_size_4 = self.width * 0.07
        
        radius = self.width * 0.3
        
        self.dot1.pos = (center_x + radius - dot_size_1/2, center_y - dot_size_1/2)
        self.dot1.size = (dot_size_1, dot_size_1)
        
        self.dot2.pos = (center_x - dot_size_2/2, center_y + radius - dot_size_2/2)
        self.dot2.size = (dot_size_2, dot_size_2)
        
        self.dot3.pos = (center_x - radius - dot_size_3/2, center_y - dot_size_3/2)
        self.dot3.size = (dot_size_3, dot_size_3)
        
        self.dot4.pos = (center_x - dot_size_4/2, center_y - radius - dot_size_4/2)
        self.dot4.size = (dot_size_4, dot_size_4)
        
    def start_animation(self):
        if self.animation_event is None:
            self.animation_event = Clock.schedule_interval(self._animate, 1/30.0)
        
    def stop_animation(self):
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
            
    def _animate(self, dt):
        self.angle += 5
        if self.angle >= 360:
            self.angle = 0
        self.rotate.angle = self.angle

class LoadingOverlay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Semi-transparent background
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self._update_bg, size=self._update_bg)
        Window.bind(on_resize=self._update_responsive_elements)
        
        # Loading content
        self.loading_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Spinner container
        self.spinner_container = Widget(
            size_hint=(None, None),
            pos_hint={'center_x': 0.5}
        )
        
        self.spinner = LoadingSpinner()
        self.spinner.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.spinner_container.add_widget(self.spinner)
        
        # Loading text
        self.loading_label = Label(
            text="Analisando...",
            font_name='Roboto-Thin',
            color=(1, 1, 1, 1),
            size_hint_y=None
        )
        
        self.loading_box.add_widget(self.spinner_container)
        self.loading_box.add_widget(self.loading_label)
        self.add_widget(self.loading_box)
        
        self._update_responsive_elements()
        
    def _update_responsive_elements(self, *args):
        # Responsive sizing for loading elements
        min_dimension = min(Window.width, Window.height)
        
        # Loading box size
        box_width = max(200, Window.width * 0.3)
        box_height = max(150, Window.height * 0.2)
        self.loading_box.size = (box_width, box_height)
        
        # Spinner container size
        spinner_size = max(60, min_dimension * 0.08)
        self.spinner_container.size = (spinner_size, spinner_size)
        
        # Loading label font size and height
        # Increased font size by 25%
        font_size = max(22, min_dimension * 0.038)
        self.loading_label.font_size = font_size
        self.loading_label.height = font_size * 2
        
        # Loading box spacing
        self.loading_box.spacing = max(15, min_dimension * 0.02)
        
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
    def show(self, text="Analisando..."):
        self.loading_label.text = text
        self.spinner.start_animation()
        
    def hide(self):
        self.spinner.stop_animation()

class RoundedButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text", "Botão")
        self.size_hint_y = None
        self.font_name = 'Roboto-Thin'
        self.color = (1, 1, 1, 1)  # Changed to pure white text
        self.default_bg_color = (0.4, 0.6, 0.9, 0.3)  # Changed to transparent (0.3 alpha)
        self.current_bg_color = self.default_bg_color  # Track current background color
        self.border_color = (0.4, 0.6, 0.9, 0.8)  # More visible border color
        
        # Bind to window resize for responsive sizing
        Window.bind(on_resize=self._update_responsive_size)
        self._update_responsive_size()

        with self.canvas.before:
            # Background
            Color(*self.default_bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
            
            # Border
            Color(*self.border_color)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], self.height/2), width=1.5)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_responsive_size(self, *args):
        # Responsive font size and height
        # Increased font size by 25%
        min_dimension = min(Window.width, Window.height)
        self.font_size = max(20, min_dimension * 0.031)
        self.height = max(50, min_dimension * 0.075)
        
        # Update radius based on height
        self.radius = [self.height / 2]

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rect.radius = self.radius
        
        # Update border
        self.border.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], self.radius[0])

    def set_background_color(self, color):
        """Set the background color of the button"""
        # Make the background transparent but keep the color hue
        transparent_color = (color[0], color[1], color[2], 0.3)
        border_color = (color[0], color[1], color[2], 0.8)
        
        self.current_bg_color = transparent_color
        self.border_color = border_color
        
        self.canvas.before.clear()
        with self.canvas.before:
            # Background
            Color(*transparent_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            
            # Border
            Color(*border_color)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], self.radius[0]), width=1.5)

    def on_press(self):
        # Darken the current color on press
        darker_bg = tuple(max(0, c - 0.1) for c in self.current_bg_color[:3]) + (self.current_bg_color[3] + 0.1,)
        darker_border = tuple(max(0, c - 0.1) for c in self.border_color[:3]) + (self.border_color[3],)
        
        self.canvas.before.clear()
        with self.canvas.before:
            # Background
            Color(*darker_bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            
            # Border
            Color(*darker_border)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], self.radius[0]), width=1.5)

    def on_release(self):
        # Restore current color on release
        self.canvas.before.clear()
        with self.canvas.before:
            # Background
            Color(*self.current_bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            
            # Border
            Color(*self.border_color)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], self.radius[0]), width=1.5)
            
class RoundedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Roboto-Thin'
        self.color = (0.2, 0.2, 0.2, 1)
        self.size_hint_y = None
        self.size_hint_x = kwargs.get("size_hint_x", 1)
        self.halign = 'center'
        self.valign = 'middle'
        self.markup = True

        # Bind to window resize for responsive sizing
        Window.bind(on_resize=self._update_responsive_size)
        self._update_responsive_size()

        self.bind(size=self._update_text_size, texture_size=self._update_height)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_responsive_size(self, *args):
        # Responsive font size, padding, and minimum height
        # Increased font size by 25%
        min_dimension = min(Window.width, Window.height)
        self.font_size = max(15, min_dimension * 0.025)
        self.padding_x = max(15, Window.width * 0.02)
        self.padding_y = max(15, Window.height * 0.02)
        self.padding = [self.padding_x, self.padding_y]
        self.min_height = max(80, min_dimension * 0.1)
        
        # Update radius
        self.radius = [max(10, min_dimension * 0.015)]
        
        # Update height if needed
        if hasattr(self, 'height'):
            self.height = max(self.min_height, self.height)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rect.radius = self.radius

    def _update_text_size(self, *args):
        self.text_size = (self.width - 2 * self.padding_x, None)

    def _update_height(self, *args):
        self.height = max(self.texture_size[1] + 2 * self.padding_y, self.min_height)

class MyBoxLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Theme colors
        self.light_theme = {
            'bg_color': (0.94, 0.95, 0.96, 1),
            'top_bar_color': (1, 1, 1, 1),
            'input_bg_color': (1, 1, 1, 1),
            'input_text_color': (0.2, 0.2, 0.2, 1),
            'label_bg_color': (1, 1, 1, 1),
            'label_text_color': (0.2, 0.2, 0.2, 1),
            'title_text_color': (0.3, 0.3, 0.3, 1),
            'button_bg_color': (0.4, 0.6, 0.9, 0.3),
            'button_border_color': (0.4, 0.6, 0.9, 0.8),
            'button_text_color': (1, 1, 1, 1)
        }
        
        self.dark_theme = {
            'bg_color': (0.14, 0.15, 0.31, 1),
            'top_bar_color': (0.28, 0.32, 0.50, 1),  # Brighter than bg
            'input_bg_color': (0.28, 0.32, 0.50, 1),
            'input_text_color': (0.9, 0.9, 0.9, 1),  # Light text
            'label_bg_color': (0.28, 0.32, 0.50, 1),  # Brighter than bg
            'label_text_color': (0.9, 0.9, 0.9, 1),  # Light text
            'title_text_color': (0.8, 0.8, 0.8, 1),  # Light text
            'button_bg_color': (0.5, 0.7, 1.0, 0.4),  # Lighter button
            'button_border_color': (0.5, 0.7, 1.0, 0.9),
            'button_text_color': (1, 1, 1, 1)
        }
        
        self.current_theme = 'light'
        self.font_scale = 1.0
        
        with self.canvas.before:
            Color(*self.light_theme['bg_color'])
            self.bg_rect = Rectangle(size_hint=(1, 1))

        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        Window.bind(on_resize=self._update_responsive_layout)

        self.size_hint = (1, 1)
        self.pos_hint = {'top': 1}

        # Track if detailed results are visible and store last analyzed site
        self.detailed_results_visible = False
        self.last_analyzed_site = ""
        self.current_classification_color = None  # Track current classification color
        self.current_classification_rgb = None  # Track RGB values for classification color
        self.report_button_visible = False  # Track if report button is visible
        self.is_malicious = False  # Track if current site is malicious
        self.report_generated = False  # Track if report has been generated
        self.analysis_state = None  # Track analysis state: 'safe', 'malicious', 'error', None
        self.access_button_visible = False  # Track if access button is visible

        self._create_widgets()
        self._update_responsive_layout()

        # NOVO: Chame a função para processar a Intent de inicialização
        Clock.schedule_once(self._process_initial_intent, 0) # Agenda para rodar no próximo frame

    def _create_widgets(self):
        # Top bar
        self.top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            pos_hint={'top': 1}
        )

        with self.top_bar.canvas.before:
            Color(*self.light_theme['top_bar_color'])
            self.top_bar_bg = Rectangle(pos=self.top_bar.pos, size=self.top_bar.size)

        self.top_bar.bind(pos=self.update_top_bar_bg, size=self.update_top_bar_bg)

        self.img = Image(
            source='img/cor_teste_evita.png',
            size_hint=(None, 1),
            allow_stretch=True,
            keep_ratio=True
        )

        # Add accessibility button to top bar
        self.accessibility_btn = AccessibilityButton()
        self.accessibility_btn.bind(on_press=self._show_accessibility_popup)
        
        # Add accessibility button to top bar with positioning
        accessibility_container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            width=Window.width * 0.07  # Adjust this value to control position
        )
        
        # Add spacer to push button to the left
        right_spacer = Widget(size_hint=(0.7, 1))
        
        self.accessibility_btn = AccessibilityButton()
        self.accessibility_btn.pos_hint = {'center_y': 0.5}  # Centers vertically
        self.accessibility_btn.bind(on_press=self._show_accessibility_popup)
        # Add button and spacer to container
        accessibility_container.add_widget(self.accessibility_btn)
        accessibility_container.add_widget(right_spacer)
        
        self.top_bar.add_widget(self.img)
        self.top_bar.add_widget(Widget())  # Flexible spacer
        self.top_bar.add_widget(accessibility_container)
        self.add_widget(self.top_bar)

        # Input field
        self.site_input = TextInput(
            multiline=False,
            size_hint=(0.85, None),
            hint_text=' Digite o URL do site... ',
            hint_text_color=(0.6, 0.6, 0.6, 1),
            foreground_color=self.light_theme['input_text_color'],
            selection_color=(0.4, 0.6, 0.9, 0.3),
            background_normal='',
            background_active='',
            background_color=self.light_theme['input_bg_color'],
            font_name='Roboto-Thin',
            halign='center'
        )
        self.site_input.pos_hint = {'center_x': 0.5, 'top': 0.89}
        self.add_widget(self.site_input)

        # Submit button
        self.submit = RoundedButton(
            text="Analisar",
            size_hint=(0.5, None)
        )
        self.submit.pos_hint = {'center_x': 0.5, 'top': 0.79}
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

        # Classification box
        self.classificacao_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, None),
            pos_hint={'center_x': 0.5, 'top': 0.68}
        )

        self.classificacao_title = Label(
            text="CLASSIFICAÇÃO",
            font_name='Roboto-Thin',
            color=self.light_theme['title_text_color'],
            size_hint_y=None,
            halign='center',
            valign='middle'
        )
        self.classificacao_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.classificacao_scroll = ScrollView(
            size_hint=(1, None),
            do_scroll_x=False,
            do_scroll_y=False
        )
        self.classificacao_label = RoundedLabel(
            text="Aguardando análise...",
            size_hint_y=None
        )
        self.classificacao_scroll.add_widget(self.classificacao_label)
        self.classificacao_box.add_widget(self.classificacao_title)
        self.classificacao_box.add_widget(self.classificacao_scroll)
        self.add_widget(self.classificacao_box)

        # Detailed results layout
        self.detailed_results_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.92, None),
            pos_hint={'center_x': 0.5, 'top': 0.4}
        )
        self.detailed_results_layout.opacity = 0

        # Create the three detail boxes
        self._create_detail_boxes()
        self.add_widget(self.detailed_results_layout)

        # Loading overlay (add at the end to ensure it's on top)
        self.loading_overlay = LoadingOverlay()
        self.loading_overlay.opacity = 0
        self.add_widget(self.loading_overlay)

    def _show_accessibility_popup(self, instance):
        popup = AccessibilityPopup(self)
        popup.open()

    def set_font_scale(self, scale):
        """Set font scale for all text elements"""
        self.font_scale = scale
        self._apply_font_scale()

    def _apply_font_scale(self):
        """Apply font scale to all text elements"""
        # Update input field
        base_font_size = max(14, min(Window.width, Window.height) * 0.025)
        self.site_input.font_size = base_font_size * self.font_scale
        
        # Update classification title
        base_title_size = max(22, min(Window.width, Window.height) * 0.031)
        self.classificacao_title.font_size = base_title_size * self.font_scale
        
        # Update submit button
        if hasattr(self.submit, 'font_size'):
            base_button_size = max(20, min(Window.width, Window.height) * 0.031)
            self.submit.font_size = base_button_size * self.font_scale
        
        # Update report button if it exists
        if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
            base_button_size = max(20, min(Window.width, Window.height) * 0.031)
            self.relatorio_button.font_size = base_button_size * self.font_scale
        
        # Update access button if it exists
        if hasattr(self, 'acessar_site_button') and self.acessar_site_button in self.children:
            base_button_size = max(20, min(Window.width, Window.height) * 0.031)
            self.acessar_site_button.font_size = base_button_size * self.font_scale
        
        # Update labels
        for widget in [self.classificacao_label, self.dominio_label, self.justificativa_label, self.medidas_label]:
            if hasattr(widget, 'font_size'):
                base_label_size = max(15, min(Window.width, Window.height) * 0.025)
                widget.font_size = base_label_size * self.font_scale
        
        # Update detail titles
        for title in [self.dominio_title, self.justificativa_title, self.medidas_title]:
            base_detail_title_size = max(20, min(Window.width, Window.height) * 0.028)
            title.font_size = base_detail_title_size * self.font_scale

    def set_theme(self, theme_name):
        """Set the app theme"""
        self.current_theme = theme_name
        theme = self.dark_theme if theme_name == 'dark' else self.light_theme
        
        # Update background
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*theme['bg_color'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        # Update top bar
        self.top_bar.canvas.before.clear()
        with self.top_bar.canvas.before:
            Color(*theme['top_bar_color'])
            self.top_bar_bg = Rectangle(pos=self.top_bar.pos, size=self.top_bar.size)
        
        # Update input field
        self.site_input.background_color = theme['input_bg_color']
        self.site_input.foreground_color = theme['input_text_color']
        
        # Update classification title
        self.classificacao_title.color = theme['title_text_color']
        
        # Update labels background and text color
        for label in [self.classificacao_label, self.dominio_label, self.justificativa_label, self.medidas_label]:
            label.canvas.before.clear()
            with label.canvas.before:
                Color(*theme['label_bg_color'])
                label.rect = RoundedRectangle(pos=label.pos, size=label.size, radius=label.radius)
            label.color = theme['label_text_color']
        
        # Update detail titles
        for title in [self.dominio_title, self.justificativa_title, self.medidas_title]:
            title.color = theme['title_text_color']
        
        # Update buttons based on analysis state - only if analysis has been performed
        if self.analysis_state is not None:
            self._update_all_button_colors()
        else:
            # Only update submit button if no analysis has been performed
            self.submit.set_background_color(theme['button_bg_color'][:3] + (1,))
            self.submit.color = theme['button_text_color']

    def _update_all_button_colors(self):
        """Update all button colors based on current analysis state and theme"""
        theme = self.dark_theme if self.current_theme == 'dark' else self.light_theme
        
        # Update submit button
        self.submit.set_background_color(theme['button_bg_color'][:3] + (1,))
        self.submit.color = theme['button_text_color']
        
        # Update analysis-specific buttons based on state
        if self.analysis_state == 'safe':
            # Green color for safe sites - much lighter for dark theme
            if self.current_theme == 'dark':
                button_color = (0.5, 0.9, 0.5, 1)  # Much lighter green for dark theme
            else:
                button_color = (0.18, 0.49, 0.20, 1)  # Original green for light theme
        elif self.analysis_state == 'malicious':
            # Red color for malicious sites - much lighter for dark theme
            if self.current_theme == 'dark':
                button_color = (1.0, 0.5, 0.5, 1)  # Much lighter red for dark theme
            else:
                button_color = (0.83, 0.18, 0.18, 1)  # Original red for light theme
        elif self.analysis_state == 'error':
            # Red color for error state - much lighter for dark theme
            if self.current_theme == 'dark':
                button_color = (1.0, 0.5, 0.5, 1)  # Much lighter red for dark theme
            else:
                button_color = (0.83, 0.18, 0.18, 1)  # Original red for light theme
        else:
            # Default blue color
            button_color = theme['button_bg_color'][:3] + (1,)
        
        # Update report button if it exists
        if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
            self.relatorio_button.set_background_color(button_color)
            self.relatorio_button.color = theme['button_text_color']
        
        # Update access button if it exists
        if hasattr(self, 'acessar_site_button') and self.acessar_site_button in self.children:
            if self.analysis_state == 'error':
                # Red color for error, but keep it functional
                self.acessar_site_button.set_background_color(button_color)
                self.acessar_site_button.color = theme['button_text_color']
                self.acessar_site_button.opacity = 1
                self.acessar_site_button.disabled = False
            elif self.is_malicious and not self.report_generated:
                # Grey out for malicious sites until report is generated
                self.acessar_site_button.set_background_color((0.5, 0.5, 0.5, 1))
                self.acessar_site_button.color = (0.5, 0.5, 0.5, 1)
                self.acessar_site_button.opacity = 0.5
                self.acessar_site_button.disabled = True
            else:
                # Normal state
                self.acessar_site_button.set_background_color(button_color)
                self.acessar_site_button.color = theme['button_text_color']
                self.acessar_site_button.opacity = 1
                self.acessar_site_button.disabled = False

    def _create_detail_boxes(self):
        # Domain box
        dominio_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=0.33
        )

        self.dominio_title = Label(
            text="NOME",
            font_name='Roboto-Thin',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            halign='center',
            valign='middle'
        )
        self.dominio_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.dominio_scroll = ScrollView(
            size_hint=(1, None),
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.dominio_label = RoundedLabel(
            text="Clique em 'Relatório' para gerar análise detalhada",
            size_hint_x=1,
            size_hint_y=None
        )
        self.dominio_scroll.add_widget(self.dominio_label)
        dominio_box.add_widget(self.dominio_title)
        dominio_box.add_widget(self.dominio_scroll)
        self.detailed_results_layout.add_widget(dominio_box)

        # Analysis box
        justificativa_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=0.33
        )

        self.justificativa_title = Label(
            text="ANÁLISE",
            font_name='Roboto-Thin',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            halign='center',
            valign='middle'
        )
        self.justificativa_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.justificativa_scroll = ScrollView(
            size_hint=(1, None),
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.justificativa_label = RoundedLabel(
            text="Clique em 'Relatório' para gerar análise detalhada",
            size_hint_x=1,
            size_hint_y=None
        )
        self.justificativa_scroll.add_widget(self.justificativa_label)
        justificativa_box.add_widget(self.justificativa_title)
        justificativa_box.add_widget(self.justificativa_scroll)
        self.detailed_results_layout.add_widget(justificativa_box)

        # Security box
        medidas_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=0.33
        )

        self.medidas_title = Label(
            text="DICAS",
            font_name='Roboto-Thin',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            halign='center',
            valign='middle'
        )
        self.medidas_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.medidas_scroll = ScrollView(
            size_hint=(1, None),
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.medidas_label = RoundedLabel(
            text="Clique em 'Relatório' para gerar análise detalhada",
            size_hint_x=1,
            size_hint_y=None
        )
        self.medidas_scroll.add_widget(self.medidas_label)
        medidas_box.add_widget(self.medidas_title)
        medidas_box.add_widget(self.medidas_scroll)
        self.detailed_results_layout.add_widget(medidas_box)

    def _calculate_access_button_position(self):
        """Calculate the optimal position for the access button based on screen size and content"""
        min_dimension = min(Window.width, Window.height)
        
        # Base position calculation
        if self.detailed_results_visible:
            # When detailed results are visible, position button below them with safe margin
            detailed_results_bottom = self.detailed_results_layout.pos_hint['top'] - (self.detailed_results_layout.height / Window.height)
            # Add a responsive margin based on screen size
            margin = max(0.03, min_dimension * 0.00008)  # Responsive margin
            button_top = max(0.08, detailed_results_bottom - margin)  # Minimum 8% from bottom
        else:
            # When no detailed results, use responsive positioning
            if Window.height < 600:  # Small screens
                button_top = 0.12
            elif Window.height < 800:  # Medium screens
                button_top = 0.10
            else:  # Large screens
                button_top = 0.08
                
        return button_top

    def _update_responsive_layout(self, *args):
        # Update responsive sizing for all elements
        min_dimension = min(Window.width, Window.height)
        
        # Top bar height
        self.top_bar.height = max(50, Window.height * 0.08)
        
        # Logo width
        self.img.width = max(120, Window.width * 0.15)
        
        # Input field - increased font size by 25%
        input_height = max(100, min_dimension * 0.075)
        self.site_input.height = input_height
        self.site_input.font_size = max(18, min_dimension * 0.025) * self.font_scale
        self.site_input.padding = [max(15, Window.width * 0.02), input_height * 0.3]
        
        # Classification box
        classification_height = max(120, Window.height * 0.18)
        self.classificacao_box.height = classification_height
        self.classificacao_box.spacing = max(5, min_dimension * 0.01)
        
        # Classification title - increased font size by 25%
        title_height = max(30, Window.height * 0.05)
        self.classificacao_title.height = title_height
        self.classificacao_title.font_size = max(22, min_dimension * 0.031) * self.font_scale
        
        # Classification scroll
        scroll_height = classification_height - title_height - self.classificacao_box.spacing
        self.classificacao_scroll.height = scroll_height
        
        # Detailed results layout
        detail_height = max(250, Window.height * 0.35)
        self.detailed_results_layout.height = detail_height
        self.detailed_results_layout.spacing = max(15, Window.width * 0.02)
        self.detailed_results_layout.padding = [max(10, Window.width * 0.015)] * 4
        
        # Update detail boxes
        for box in self.detailed_results_layout.children:
            box.height = detail_height - 2 * self.detailed_results_layout.padding[1]
            box.spacing = max(5, min_dimension * 0.01)
            
            # Update title and scroll heights for each box
            if len(box.children) >= 2:
                title = box.children[1]  # Title is second child (added first)
                scroll = box.children[0]  # Scroll is first child (added second)
                
                # Increased title font size by 25%
                title_height = max(25, Window.height * 0.038)
                title.height = title_height
                title.font_size = max(20, min_dimension * 0.028) * self.font_scale
                
                scroll.height = box.height - title_height - box.spacing
                
        # Adjust positions when report button is hidden
        if self.detailed_results_visible and not self.report_button_visible:
            # Move detailed results up to fill the space
            self.detailed_results_layout.pos_hint = {'center_x': 0.5, 'top': 0.48}
        else:
            # Default position
            self.detailed_results_layout.pos_hint = {'center_x': 0.5, 'top': 0.4}
            
        # Update access button position if it exists
        if hasattr(self, 'acessar_site_button') and self.acessar_site_button in self.children:
            access_button_top = self._calculate_access_button_position()
            self.acessar_site_button.pos_hint = {'center_x': 0.5, 'top': access_button_top}
        
        # Apply font scale
        self._apply_font_scale()

    def _hex_to_rgb(self, hex_color):
        """Convert hex color code to RGB tuple"""
        if len(hex_color) == 8:  # Format: RRGGBBAA
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            a = int(hex_color[6:8], 16) / 255.0
            return (r, g, b, a)
        return (0.4, 0.6, 0.9, 1)  # Default blue if conversion fails

    def _get_theme_adjusted_color(self, classification_color):
        """Get theme-adjusted color for report text"""
        if classification_color == "43A047FF":  # Green for confiável
            if self.current_theme == 'dark':
                return "81C784FF"  # Much lighter green for dark theme
            else:
                return "43A047FF"  # Original green for light theme
        elif classification_color == "E53935FF":  # Red for malicioso
            if self.current_theme == 'dark':
                return "EF5350FF"  # Much lighter red for dark theme
            else:
                return "E53935FF"  # Original red for light theme
        else:
            return "333333FF"  # Default dark gray

    def open_website(self, instance):
        """Open the analyzed website in the default browser"""
        if self.last_analyzed_site and not instance.disabled:
            # Ensure URL has http/https prefix
            url = self.last_analyzed_site
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
                
            # Open URL in default browser
            webbrowser.open(url)

    def generate_detailed_report(self, instance):
        """Generate detailed report by calling gerar_relatorio function"""
        self.show_loading_report()
        Clock.schedule_once(lambda dt: self._process_report_generation(), 0.1)
        
    def _process_report_generation(self):
        """Process the report generation in background"""
        try:
            relatorio_data = consultar_analise_gpt_relatorio(self.last_analyzed_site)
            
            # Use theme-adjusted colors for report text
            text_color = self._get_theme_adjusted_color(self.current_classification_color)
            
            def aplicar_estilo_relatorio(label, texto, cor):
                label.text = f"[color={cor}]{texto}[/color]"
            
            aplicar_estilo_relatorio(self.dominio_label, relatorio_data.get('dominio', 'Dados não disponíveis'), text_color)
            aplicar_estilo_relatorio(self.justificativa_label, relatorio_data.get('justificativa', 'Dados não disponíveis'), text_color)
            aplicar_estilo_relatorio(self.medidas_label, relatorio_data.get('seguranca', 'Dados não disponíveis'), text_color)
            
            # Mark report as generated
            self.report_generated = True
            
            # Update access button state (enable if it was disabled due to malicious content)
            self._update_all_button_colors()
            
            # REMOVE the report button completely (not just hide it)
            if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
                self.remove_widget(self.relatorio_button)
            self.report_button_visible = False
            
            # Show detailed results and adjust their position
            self.detailed_results_layout.opacity = 1
            self.detailed_results_visible = True
            self.detailed_results_layout.pos_hint = {'center_x': 0.5, 'top': 0.48}
            
            # Update access button position after showing detailed results
            self._update_responsive_layout()
            
        except Exception as e:
            error_message = f"Erro ao gerar relatório: {str(e)}"
            error_color = self._get_theme_adjusted_color("E53935FF")  # Use theme-adjusted red
            self.dominio_label.text = f"[color={error_color}]Erro na consulta.\nTente novamente.[/color]"
            self.justificativa_label.text = f"[color={error_color}]Erro na consulta.\nTente novamente.[/color]"
            self.medidas_label.text = f"[color={error_color}]Erro na consulta.\nTente novamente.[/color]"
            
            # Mark report as generated even on error
            self.report_generated = True
            
            # Update access button state
            self._update_all_button_colors()
            
            # REMOVE the report button completely (not just hide it)
            if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
                self.remove_widget(self.relatorio_button)
            self.report_button_visible = False
            
            # Show detailed results and adjust their position
            self.detailed_results_layout.opacity = 1
            self.detailed_results_visible = True
            self.detailed_results_layout.pos_hint = {'center_x': 0.5, 'top': 0.48}
            
            # Update access button position after showing detailed results
            self._update_responsive_layout()
            
        finally:
            Clock.schedule_once(lambda dt: self.hide_loading_report(), 0.2)

    def show_loading_report(self):
        """Show loading screen for report generation"""
        # Ensure loading overlay is on top by removing and re-adding it
        if self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)
        self.add_widget(self.loading_overlay)
        
        self.loading_overlay.opacity = 1
        self.loading_overlay.show("Gerando relatório...")
        if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
            self.relatorio_button.disabled = True

    def hide_loading_report(self):
        """Hide loading screen for report generation"""
        self.loading_overlay.opacity = 0
        self.loading_overlay.hide()
        if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
            self.relatorio_button.disabled = False

    def show_loading(self):
        # Ensure loading overlay is on top by removing and re-adding it
        if self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)
        self.add_widget(self.loading_overlay)
        
        self.loading_overlay.opacity = 1
        self.loading_overlay.show("Analisando...")
        self.submit.disabled = True

    def hide_loading(self):
        self.loading_overlay.opacity = 0
        self.loading_overlay.hide()
        self.submit.disabled = False

    def press(self, instance):
        self.show_loading()
        instance.background_color = (0.3, 0.5, 0.8, 1)
        instance.color = (1, 1, 1, 1)
        Clock.schedule_once(lambda dt: self.processar_consulta(instance), 0.1)

    def processar_consulta(self, instance):
        site_input = self.site_input.text
        self.last_analyzed_site = site_input
        self.site_input.text = ""

        # Reset states for new analysis
        self.is_malicious = False
        self.report_generated = False
        self.analysis_state = None

        try:
            analise_gpt = classificacao_analise_gpt(site_input)
        except:
            analise_gpt = 0

        if isinstance(analise_gpt, int):
            estilo_padrao = {"texto": "666666FF"}
            def aplicar_estilo_label(label, texto, estilo):
                cor_texto = estilo.get("texto", "333333FF")
                label.text = f"[color={cor_texto}]{texto}[/color]"

            aplicar_estilo_label(self.classificacao_label, "Erro na consulta", estilo_padrao)
            self.current_classification_color = None
            self.analysis_state = 'error'
            
            # Don't show report button on error
            if hasattr(self, 'relatorio_button') and self.relatorio_button in self.children:
                self.remove_widget(self.relatorio_button)
            self.report_button_visible = False
        else:
            classificacao = analise_gpt.get('classificacao', 'Não disponível')

            cores_classificacao = {
                "confiável": {"texto": "43A047FF"},
                "malicioso": {"texto": "E53935FF"}
            }

            estilo = cores_classificacao.get(classificacao.lower(), {"texto": "333333FF"})
            self.current_classification_color = estilo.get("texto", "333333FF")

            # Check if the site is malicious
            self.is_malicious = classificacao.lower() == "malicioso"
            
            # Set analysis state
            if classificacao.lower() == "confiável":
                self.analysis_state = 'safe'
            elif classificacao.lower() == "malicioso":
                self.analysis_state = 'malicious'
            else:
                self.analysis_state = None

            def aplicar_estilo_label(label, texto, estilo):
                cor_texto = estilo.get("texto", "333333FF")
                label.text = f"[color={cor_texto}]{texto}[/color]"

            aplicar_estilo_label(self.classificacao_label, classificacao, estilo)
            
            # Create and add a new report button ONLY after analysis
            if not self.report_button_visible:
                # Create a new report button
                self.relatorio_button = RoundedButton(
                    text="Relatório",
                    size_hint=(0.4, None)
                )
                self.relatorio_button.pos_hint = {'center_x': 0.5, 'top': 0.48}
                self.relatorio_button.bind(on_press=self.generate_detailed_report)
                self.add_widget(self.relatorio_button)
                self.report_button_visible = True

        # Create and add access site button ONLY after analysis
        if not self.access_button_visible:
            self.acessar_site_button = RoundedButton(
                text="Acessar Site",
                size_hint=(0.4, None)
            )
            self.acessar_site_button.bind(on_press=self.open_website)
            self.add_widget(self.acessar_site_button)
            self.access_button_visible = True

        # Update all button colors based on analysis state
        self._update_all_button_colors()
        
        # Show the access site button
        if self.last_analyzed_site:
            self.acessar_site_button.opacity = 1
        
        # Hide detailed results from previous analysis
        self.detailed_results_layout.opacity = 0
        self.detailed_results_visible = False
        
        # Reset detailed results position
        self.detailed_results_layout.pos_hint = {'center_x': 0.5, 'top': 0.4}
        
        # Update layout to recalculate access button position
        self._update_responsive_layout()
        
        Clock.schedule_once(lambda dt: self.finish_processing(instance), 0.2)
        
    def finish_processing(self, button):
        self.hide_loading()
        self.reset_button_color(button)

    def reset_button_color(self, button):
        button.background_color = (0.4, 0.6, 0.9, 1)
        button.color = (1, 1, 1, 1)

    def _update_bg_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_top_bar_bg(self, instance, value):
        self.top_bar_bg.pos = instance.pos
        self.top_bar_bg.size = instance.size

    def _process_initial_intent(self, dt):
        if PythonActivity and Intent:
            current_activity = PythonActivity.mActivity
            intent = current_activity.getIntent()
            action = intent.getAction()

            if action == Intent.ACTION_VIEW:
                data_uri = intent.getData()
                if data_uri:
                    link_recebido = str(data_uri.toString())
                    print(f"Link recebido via Intent: {link_recebido}") # Para depuração

                    # Adiciona o link recebido ao seu site_input e dispara a análise
                    self.site_input.text = link_recebido
                    self.press(self.submit) # Chama o método 'press' como se o botão 'Analisar' tivesse sido clicado
                else:
                    print("Intent VIEW recebida, mas sem dados de URL.")
            else:
                print("Nenhuma Intent VIEW na inicialização.")
        else:
            print("Não rodando no Android ou Pyjnius/Intent indisponível. Ignorando processamento de Intent.")

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        Clock.schedule_once(self._process_initial_intent, 0)

class EvitaAIApp(App):
    def build(self):
        self.title = "EvitaAI"
        return MyBoxLayout()

if __name__ == '__main__':
    EvitaAIApp().run()