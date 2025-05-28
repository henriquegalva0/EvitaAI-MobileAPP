import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from consulta_api import consultar_analise_gpt

LabelBase.register(name='Roboto-Thin', fn_regular='fonts/Roboto-Thin.ttf')

class RoundedButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text", "Botão")
        self.font_size = kwargs.get("font_size", 30)
        self.size_hint_y = None
        self.height = 50
        self.font_name = 'Roboto-Thin'
        self.color = (0.925, 0.922, 0.871, 1)
        self.radius = [20]

        with self.canvas.before:
            Color(0.843, 0.827, 0.749, 1)  # cor do botão
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

    def on_release(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.843, 0.827, 0.749, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            
class RoundedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Roboto-Thin'
        self.color = (0.647, 0.616, 0.518, 1)
        self.font_size = kwargs.get("font_size", 16)
        self.size_hint_y = None
        self.height = kwargs.get("height", 100)
        self.size_hint_x = kwargs.get("size_hint_x", 1)
        self.halign = 'center'
        self.valign = 'middle'
        self.padding = [15, 15]
        self.markup = True

        # Alinha o texto com base no tamanho do widget
        self.bind(size=self._update_text_size, texture_size=self._update_height)

        with self.canvas.before:
            Color(0.925, 0.922, 0.871, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_text_size(self, *args):
        self.text_size = (self.width - 30, None)  # padding aplicado, allow text to wrap

    def _update_height(self, *args):
        self.height = max(self.texture_size[1] + 30, 100)  # Adjust height based on content

class MyBoxLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.757, 0.729, 0.631, 1) 
            self.bg_rect = Rectangle(size_hint=(1, 1))

        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        self.spacing = 15
        self.orientation = 'vertical'
        self.size_hint = (1, 1)  # Ocupa toda a janela
        self.pos_hint = {'top': 1}  # Alinha no topo

        self.top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=60,
            pos_hint = {'top': 1}
        )

        with self.top_bar.canvas.before:
            Color(0.647, 0.616, 0.518, 1)
            self.top_bar_bg = Rectangle(pos=self.top_bar.pos, size=self.top_bar.size)

        self.top_bar.bind(pos=self.update_top_bar_bg, size=self.update_top_bar_bg)

        self.img = Image(
            source='img/cor_teste_evita.png',
            size_hint=(None, 1),
            width=160,
            allow_stretch=True,
            keep_ratio=True
        )

        self.top_bar.add_widget(self.img)
        self.top_bar.add_widget(Widget())

        self.add_widget(self.top_bar)

        self.site_input = TextInput(
            multiline=False,
            height=60,
            size_hint=(0.67,None),
            padding=[15, 20],
            hint_text=' Insira um site... ',
            hint_text_color=(0.8, 0.78, 0.7, 1),
            foreground_color=(0.647, 0.616, 0.518, 1),
            selection_color=(0.8, 0.78, 0.7, 0.4),
            background_normal='',
            background_active='',
            background_color=(0.925, 0.922, 0.871, 1),
            font_name='Roboto-Thin',
            halign = 'center'
        )
        self.site_input.pos_hint = {'center_x': 0.5, 'top': 0.91}
        self.add_widget(self.site_input)

        self.submit = RoundedButton(
            text="Submeter",
            size_hint=(0.4, None),
            height=50
        )
        self.submit.pos_hint = {'center_x': 0.5, 'top': 0.82}
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=0,
            size_hint=(0.9, None),
            height=400,
            pos_hint={'center_x': 0.5},
            padding=[10, 10, 10, 10]
        )

        classificacao_box = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=100
        )

        classificacao_title = Label(
            text="natureza",
            font_name='Roboto-Thin',
            font_size=16,
            color=(0.925, 0.922, 0.871, 1),
            outline_width=2,
            outline_color=(0.647, 0.616, 0.518, 1),
            size_hint_y=None,
            height=20,
            halign='center',
            valign='middle'
        )
        classificacao_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.classificacao_scroll = ScrollView(
            size_hint=(1, None),
            height=100,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.classificacao_label = RoundedLabel(
            text="confiabilidade do site",
            height=80,
            font_size=16,
            size_hint_y=None
        )
        self.classificacao_scroll.add_widget(self.classificacao_label)
        classificacao_box.add_widget(classificacao_title)
        classificacao_box.add_widget(self.classificacao_scroll)
        self.results_layout.add_widget(classificacao_box)

        self.lower_results_layout = BoxLayout(
            orientation='horizontal',
            spacing=15,
            size_hint=(1, None),
            height=350
        )
    
        dominio_box = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=350,
            size_hint_x=0.33  # Um terço da linha
        )

        dominio_title = Label(
            text="domínio",
            font_name='Roboto-Thin',
            font_size=16,
            color=(0.925, 0.922, 0.871, 1),
            outline_width=2,
            outline_color=(0.647, 0.616, 0.518, 1),
            size_hint_y=None,
            height=20,
            halign='center',
            valign='middle'
        )
        dominio_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.dominio_scroll = ScrollView(
            size_hint=(1, None),
            height=320,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.dominio_label = RoundedLabel(
            text="reputação a respeito do nome do site",
            height=320,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None
        )
        self.dominio_scroll.add_widget(self.dominio_label)
        dominio_box.add_widget(dominio_title)
        dominio_box.add_widget(self.dominio_scroll)
        self.lower_results_layout.add_widget(dominio_box)

        justificativa_box = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=350,
            size_hint_x=0.33  # Um terço da linha
        )

        justificativa_title = Label(
            text="justificativa",
            font_name='Roboto-Thin',
            font_size=16,
            color=(0.925, 0.922, 0.871, 1),
            outline_width=2,
            outline_color=(0.647, 0.616, 0.518, 1),
            size_hint_y=None,
            height=20,
            halign='center',
            valign='middle'
        )
        justificativa_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.justificativa_scroll = ScrollView(
            size_hint=(1, None),
            height=320,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.justificativa_label = RoundedLabel(
            text="relatório da análise da confiabilidade do site",
            height=320,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None
        )
        self.justificativa_scroll.add_widget(self.justificativa_label)
        justificativa_box.add_widget(justificativa_title)
        justificativa_box.add_widget(self.justificativa_scroll)
        self.lower_results_layout.add_widget(justificativa_box)

        medidas_box = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=350,
            size_hint_x=0.33  # Um terço da linha
        )

        medidas_title = Label(
            text="dicas de segurança",
            font_name='Roboto-Thin',
            font_size=16,
            color=(0.925, 0.922, 0.871, 1),
            outline_width=2,
            outline_color=(0.647, 0.616, 0.518, 1),
            size_hint_y=None,
            height=20,
            halign='center',
            valign='middle'
        )
        medidas_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        self.medidas_scroll = ScrollView(
            size_hint=(1, None),
            height=320,
            do_scroll_x=False,
            do_scroll_y=True
        )
        self.medidas_label = RoundedLabel(
            text="recomendações de segurança ao usuário",
            height=320,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None
        )
        self.medidas_scroll.add_widget(self.medidas_label)
        medidas_box.add_widget(medidas_title)
        medidas_box.add_widget(self.medidas_scroll)
        self.lower_results_layout.add_widget(medidas_box)

        self.results_layout.add_widget(self.lower_results_layout)
        self.results_layout.pos_hint = {'center_x': 0.5, 'top': 0.6}
        self.add_widget(self.results_layout)

    def press(self, instance):
        instance.background_color = (0, 0, 0, 0.2)
        instance.color = (0.757, 0.729, 0.631, 1)
        instance.outline_color = (0.647, 0.616, 0.518, 1)

        Clock.schedule_once(lambda dt: self.processar_consulta(instance), 0.05)

    def processar_consulta(self, instance):
        site_input = self.site_input.text
        self.site_input.text = ""

        analise_gpt = consultar_analise_gpt(site_input)

        if isinstance(analise_gpt, int):
            # Volta ao estado inicial
            estilo_padrao = {
                "texto": "A59D84FF",    # cor texto padrão convertida
                "contorno": "736E5CFF"  # cor contorno padrão convertida
            }
            def aplicar_estilo_label(label, texto, estilo):
                cor_texto = estilo.get("texto", "000000FF")
                label.text = f"[color={cor_texto}]{texto}[/color]"

            aplicar_estilo_label(self.classificacao_label, "erro na consulta", estilo_padrao)
            aplicar_estilo_label(self.dominio_label, "reputação a respeito do nome do site", estilo_padrao)
            aplicar_estilo_label(self.justificativa_label, "relatório da análise da confiabilidade do site", estilo_padrao)
            aplicar_estilo_label(self.medidas_label, "recomendações de segurança ao usuário", estilo_padrao)

        else:
            # Processa normalmente
            classificacao = analise_gpt.get('classificacao', 'Não disponível')
            reputacao = analise_gpt.get('reputacao', 'Não disponível')
            justificativa = analise_gpt.get('justificativa', 'Não disponível')
            seguranca = analise_gpt.get('seguranca', 'Não disponível')

            cores_classificacao = {
                "confiável": {
                    "texto": "33975FFF",      # verde
                },
                "malicioso": {
                    "texto": "A65C7FFF",     # vermelho suave (rosa avermelhado claro)
                }
            }

            estilo = cores_classificacao.get(classificacao.lower(), {
                "texto": "000000FF",  # padrão: preto
            })

            def aplicar_estilo_label(label, texto, estilo):
                cor_texto = estilo.get("texto", "000000FF")
                label.text = f"[color={cor_texto}]{texto}[/color]"

            aplicar_estilo_label(self.classificacao_label, classificacao, estilo)
            aplicar_estilo_label(self.dominio_label, reputacao, estilo)
            aplicar_estilo_label(self.justificativa_label, justificativa, estilo)
            aplicar_estilo_label(self.medidas_label, seguranca, estilo)
        Clock.schedule_once(lambda dt: self.reset_button_color(instance), 0.2)

    def reset_button_color(self, button):
        button.background_color = (0.843, 0.827, 0.749, 1)
        button.color = (0.925, 0.922, 0.871, 1)
        button.outline_color = (0.700, 0.674, 0.590, 1)

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