import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, PushMatrix, PopMatrix, Rotate
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView

from consulta_api_classficacao import classificacao_analise_gpt
from consulta_api_relatorio import consultar_analise_gpt_relatorio
import math

LabelBase.register(name='Roboto-Thin', fn_regular='fonts/Roboto-Thin.ttf')

class LoadingSpinner(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 60)
        self.angle = 0
        
        with self.canvas:
            PushMatrix()
            self.rotate = Rotate()
            self.rotate.angle = 0
            self.rotate.origin = (30, 30)  # Center of the 60x60 widget
            
            # Create multiple dots for spinner effect
            Color(0.4, 0.6, 0.9, 1)
            self.dot1 = Ellipse(pos=(45, 25), size=(10, 10))
            Color(0.4, 0.6, 0.9, 0.8)
            self.dot2 = Ellipse(pos=(35, 45), size=(8, 8))
            Color(0.4, 0.6, 0.9, 0.6)
            self.dot3 = Ellipse(pos=(15, 35), size=(6, 6))
            Color(0.4, 0.6, 0.9, 0.4)
            self.dot4 = Ellipse(pos=(25, 15), size=(4, 4))
            
            PopMatrix()
            
        self.bind(pos=self._update_spinner, size=self._update_spinner)
        self.animation_event = None
        
    def _update_spinner(self, *args):
        # Update rotation origin when position changes
        self.rotate.origin = (self.x + 30, self.y + 30)
        
        # Update dot positions relative to widget position
        self.dot1.pos = (self.x + 45, self.y + 25)
        self.dot2.pos = (self.x + 35, self.y + 45)
        self.dot3.pos = (self.x + 15, self.y + 35)
        self.dot4.pos = (self.x + 25, self.y + 15)
        
    def start_animation(self):
        if self.animation_event is None:
            self.animation_event = Clock.schedule_interval(self._animate, 1/30.0)  # 30 FPS
        
    def stop_animation(self):
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
            
    def _animate(self, dt):
        self.angle += 5  # Rotate 5 degrees per frame
        if self.angle >= 360:
            self.angle = 0
        self.rotate.angle = self.angle

class LoadingOverlay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Semi-transparent background
        with self.canvas.before:
            Color(0, 0, 0, 0.7)  # Dark overlay
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Loading content
        loading_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(200, 150),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=20
        )
        
        # Spinner container
        spinner_container = Widget(
            size_hint=(None, None),
            size=(60, 60),
            pos_hint={'center_x': 0.5}
        )
        
        self.spinner = LoadingSpinner()
        self.spinner.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        spinner_container.add_widget(self.spinner)
        
        # Loading text
        self.loading_label = Label(
            text="Analisando...",
            font_name='Roboto-Thin',
            font_size=24,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=40
        )
        
        loading_box.add_widget(spinner_container)
        loading_box.add_widget(self.loading_label)
        self.add_widget(loading_box)
        
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
        self.font_size = kwargs.get("font_size", 28)
        self.size_hint_y = None
        self.height = 50
        self.font_name = 'Roboto-Thin'
        self.color = (1, 1, 1, 1)  # Pure white text
        self.radius = [25]

        with self.canvas.before:
            Color(0.4, 0.6, 0.9, 1)  # Clean modern blue
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.3, 0.5, 0.8, 1)  # Slightly darker on press
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

    def on_release(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.4, 0.6, 0.9, 1)  # Restore button color
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            
class RoundedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Roboto-Thin'
        self.color = (0.2, 0.2, 0.2, 1)  # Dark gray text for better readability
        self.font_size = kwargs.get("font_size", 16)
        self.size_hint_y = None
        self.height = kwargs.get("height", 100)
        self.size_hint_x = kwargs.get("size_hint_x", 1)
        self.halign = 'center'
        self.valign = 'middle'
        self.padding = [20, 20]
        self.markup = True

        self.bind(size=self._update_text_size, texture_size=self._update_height)

        with self.canvas.before:
            Color(1, 1, 1, 1)  # Pure white background for boxes
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_text_size(self, *args):
        self.text_size = (self.width - 40, None)

    def _update_height(self, *args):
        self.height = max(self.texture_size[1] + 40, 100)

class MyBoxLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.94, 0.95, 0.96, 1)  # Slightly darker background for contrast
            self.bg_rect = Rectangle(size_hint=(1, 1))

        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        self.spacing = 20
        self.orientation = 'vertical'
        self.size_hint = (1, 1)
        self.pos_hint = {'top': 1}
        
        # Track if detailed results are visible and store last analyzed site
        self.detailed_results_visible = False
        self.last_analyzed_site = ""

        # Top bar
        self.top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=70,
            pos_hint = {'top': 1}
        )

        with self.top_bar.canvas.before:
            Color(1, 1, 1, 1)  # Pure white top bar
            self.top_bar_bg = Rectangle(pos=self.top_bar.pos, size=self.top_bar.size)

        self.top_bar.bind(pos=self.update_top_bar_bg, size=self.update_top_bar_bg)

        self.img = Image(
            source='img/cor_teste_evita.png',
            size_hint=(None, 1),
            width=180,
            allow_stretch=True,
            keep_ratio=True
        )

        self.top_bar.add_widget(self.img)
        self.top_bar.add_widget(Widget())
        self.add_widget(self.top_bar)

        # Input field
        self.site_input = TextInput(
            multiline=False,
            height=55,
            size_hint=(0.85, None),
            padding=[20, 18],
            hint_text=' Digite o URL do site... ',
            hint_text_color=(0.6, 0.6, 0.6, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            selection_color=(0.4, 0.6, 0.9, 0.3),
            background_normal='',
            background_active='',
            background_color=(1, 1, 1, 1),
            font_name='Roboto-Thin',
            font_size=18,
            halign='center'
        )
        self.site_input.pos_hint = {'center_x': 0.5, 'top': 0.89}
        self.add_widget(self.site_input)

        # Submit button
        self.submit = RoundedButton(
            text="Analisar",
            size_hint=(0.5, None),
            height=55
        )
        self.submit.pos_hint = {'center_x': 0.5, 'top': 0.79}
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

        # Classification box (always visible)
        self.classificacao_box = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint=(0.85, None),
            height=150,
            pos_hint={'center_x': 0.5, 'top': 0.68}
        )

        classificacao_title = Label(
            text="CLASSIFICAÇÃO",
            font_name='Roboto-Thin',
            font_size=24,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=35,
            halign='center',
            valign='middle'
        )
        classificacao_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.classificacao_scroll = ScrollView(
            size_hint=(1, None),
            height=110,
            do_scroll_x=False,
            do_scroll_y=False
        )
        self.classificacao_label = RoundedLabel(
            text="Aguardando análise...",
            height=100,
            font_size=28,
            size_hint_y=None
        )
        self.classificacao_scroll.add_widget(self.classificacao_label)
        self.classificacao_box.add_widget(classificacao_title)
        self.classificacao_box.add_widget(self.classificacao_scroll)
        self.add_widget(self.classificacao_box)

        # Report button (initially hidden)
        self.relatorio_button = RoundedButton(
            text="Relatório",
            size_hint=(0.4, None),
            height=50,
            font_size=24
        )
        self.relatorio_button.pos_hint = {'center_x': 0.5, 'top': 0.48}
        self.relatorio_button.bind(on_press=self.generate_detailed_report)
        self.relatorio_button.opacity = 0  # Initially hidden
        self.add_widget(self.relatorio_button)

        # Detailed results layout (initially hidden)
        self.detailed_results_layout = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(0.92, None),
            height=350,
            pos_hint={'center_x': 0.5, 'top': 0.4},
            padding=[15, 15, 15, 15]
        )
        self.detailed_results_layout.opacity = 0  # Initially hidden

        # Domain box
        dominio_box = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None,
            height=320,
            size_hint_x=0.33
        )

        dominio_title = Label(
            text="DOMÍNIO",
            font_name='Roboto-Thin',
            font_size=20,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30,
            halign='center',
            valign='middle'
        )
        dominio_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.dominio_scroll = ScrollView(
            size_hint=(1, None),
            height=280,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.dominio_label = RoundedLabel(
            text="Clique em 'Relatório' para gerar análise detalhada",
            height=280,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None
        )
        self.dominio_scroll.add_widget(self.dominio_label)
        dominio_box.add_widget(dominio_title)
        dominio_box.add_widget(self.dominio_scroll)
        self.detailed_results_layout.add_widget(dominio_box)

        # Analysis box
        justificativa_box = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None,
            height=320,
            size_hint_x=0.33
        )

        justificativa_title = Label(
            text="ANÁLISE",
            font_name='Roboto-Thin',
            font_size=20,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30,
            halign='center',
            valign='middle'
        )
        justificativa_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.justificativa_scroll = ScrollView(
            size_hint=(1, None),
            height=280,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.justificativa_label = RoundedLabel(
            text="Clique em 'Relatório' para gerar análise detalhada",
            height=280,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None
        )
        self.justificativa_scroll.add_widget(self.justificativa_label)
        justificativa_box.add_widget(justificativa_title)
        justificativa_box.add_widget(self.justificativa_scroll)
        self.detailed_results_layout.add_widget(justificativa_box)

        # Security box
        medidas_box = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None,
            height=320,
            size_hint_x=0.33
        )

        medidas_title = Label(
            text="SEGURANÇA",
            font_name='Roboto-Thin',
            font_size=20,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30,
            halign='center',
            valign='middle'
        )
        medidas_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.medidas_scroll = ScrollView(
            size_hint=(1, None),
            height=280,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.medidas_label = RoundedLabel(
            text="Clique em 'Relatório' para gerar análise detalhada",
            height=280,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None
        )
        self.medidas_scroll.add_widget(self.medidas_label)
        medidas_box.add_widget(medidas_title)
        medidas_box.add_widget(self.medidas_scroll)
        self.detailed_results_layout.add_widget(medidas_box)

        self.add_widget(self.detailed_results_layout)

        # Loading overlay (initially hidden)
        self.loading_overlay = LoadingOverlay()
        self.loading_overlay.opacity = 0
        self.add_widget(self.loading_overlay)


    def generate_detailed_report(self, instance):
        """Generate detailed report by calling gerar_relatorio function"""
        # Always generate report (no toggle behavior)
        self.show_loading_report()
        Clock.schedule_once(lambda dt: self._process_report_generation(), 0.1)
        
    def _process_report_generation(self):
        """Process the report generation in background"""
        try:
            # Call the gerar_relatorio function with the last analyzed site
            relatorio_data = consultar_analise_gpt_relatorio(self.last_analyzed_site)
            
            # Update the labels with the generated report data
            def aplicar_estilo_relatorio(label, texto):
                label.text = f"[color=333333FF]{texto}[/color]"
            
            aplicar_estilo_relatorio(self.dominio_label, relatorio_data.get('dominio', 'Dados não disponíveis'))
            aplicar_estilo_relatorio(self.justificativa_label, relatorio_data.get('justificativa', 'Dados não disponíveis'))
            aplicar_estilo_relatorio(self.medidas_label, relatorio_data.get('seguranca', 'Dados não disponíveis'))
            
            # Show the detailed results
            self.detailed_results_layout.opacity = 1
            self.detailed_results_visible = True
            
            # Properly remove the report button after generating the report
            self.remove_widget(self.relatorio_button)
            
        except Exception as e:
            # Handle errors in report generation
            error_message = f"Erro ao gerar relatório: {str(e)}"
            self.dominio_label.text = f"[color=D32F2FFF]{error_message}[/color]"
            self.justificativa_label.text = f"[color=D32F2FFF]{error_message}[/color]"
            self.medidas_label.text = f"[color=D32F2FFF]{error_message}[/color]"
            
            self.detailed_results_layout.opacity = 1
            self.detailed_results_visible = True
            
            # Remove the report button even on error
            self.remove_widget(self.relatorio_button)
        
        finally:
            # Hide loading screen
            Clock.schedule_once(lambda dt: self.hide_loading_report(), 0.2)

    def show_loading_report(self):
        """Show loading screen for report generation"""
        self.loading_overlay.opacity = 1
        self.loading_overlay.show("Gerando relatório...")
        self.relatorio_button.disabled = True

    def hide_loading_report(self):
        """Hide loading screen for report generation"""
        self.loading_overlay.opacity = 0
        self.loading_overlay.hide()
        self.relatorio_button.disabled = False

    def show_loading(self):
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
        self.last_analyzed_site = site_input  # Store the analyzed site
        self.site_input.text = ""

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
        else:
            classificacao = analise_gpt.get('classificacao', 'Não disponível')

            cores_classificacao = {
                "confiável": {"texto": "2E7D32FF"},
                "malicioso": {"texto": "D32F2FFF"}
            }

            estilo = cores_classificacao.get(classificacao.lower(), {"texto": "333333FF"})

            def aplicar_estilo_label(label, texto, estilo):
                cor_texto = estilo.get("texto", "333333FF")
                label.text = f"[color={cor_texto}]{texto}[/color]"

            aplicar_estilo_label(self.classificacao_label, classificacao, estilo)

        # Re-add the report button after analysis is complete (in case it was removed)
        if self.relatorio_button not in self.children:
            self.add_widget(self.relatorio_button)
        
        # Reset button properties
        self.relatorio_button.opacity = 1
        self.relatorio_button.disabled = False
        self.relatorio_button.text = "Relatório"
        
        # Hide detailed results from previous analysis
        self.detailed_results_layout.opacity = 0
        self.detailed_results_visible = False
        
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

class MyApp(App):
    def build(self):
        self.title = "EvitaABC"
        return MyBoxLayout()

if __name__ == '__main__':
    MyApp().run()