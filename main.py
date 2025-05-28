import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.text import LabelBase

from consulta_api import consultar_analise_gpt

LabelBase.register(name='Roboto-Thin', fn_regular='fonts/Roboto-Thin.ttf')

class MyBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.757, 0.729, 0.631, 1) 
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        # Atualizar tamanho/posição do fundo quando a janela for redimensionada
        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        self.orientation = 'vertical'
        self.size_hint = (1, 1)

        self.top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50,
            padding=0,
            spacing=0
        )

        with self.top_bar.canvas.before:
            Color(0.647, 0.616, 0.518, 1)  # cor da barra
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
            size_hint_y=None,
            padding=[10, 20],
            hint_text=' Insira um site... ( exemplo: https://evita-ai.com.br/ )',
            hint_text_color=(0.8, 0.78, 0.7, 1),
            foreground_color=(0.647, 0.616, 0.518, 1),
            selection_color=(0.8, 0.78, 0.7, 0.4),
            background_normal='',
            background_active='',
            background_color=(0.925, 0.922, 0.871, 1),
            font_name='Roboto-Thin'
            )
        self.add_widget(self.site_input)

        self.submit = Button(
            text="Submeter",
            font_size=30,
            size_hint_y=None,
            height=50,
            background_normal='',
            background_down='',
            color=(0.925, 0.922, 0.871, 1),
            outline_color=(0.700, 0.674, 0.590, 1),
            outline_width=2,
            background_color=(0.843, 0.827, 0.749, 1),
            font_name='Roboto-Thin'
        )
        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

        self.resultado_consulta = Label(
            text="Pendente",
            font_size=16,
            size_hint_y=1,  # Expandir para preencher espaço vertical
            halign='center',
            valign='middle',
            color=(0.925, 0.922, 0.871, 1),
            outline_color=(0.647, 0.616, 0.518, 1),
            outline_width=3,
            markup=True,
            font_name='Roboto-Thin'
        )
        self.resultado_consulta.bind(width=self._update_text_size)
        self._update_text_size(self.resultado_consulta, self.resultado_consulta.width)
        self.add_widget(self.resultado_consulta)


    def press(self, instance):
        # Mudar cor imediatamente
        instance.background_color = (0,0,0, 0.2)
        instance.color=(0.757, 0.729, 0.631, 1)
        instance.outline_color=(0.647, 0.616, 0.518, 1)

        # Aguardar 0.05s antes de continuar com a lógica (deixa a UI atualizar)
        Clock.schedule_once(lambda dt: self.processar_consulta(instance), 0.05)

    def processar_consulta(self, instance):
        site_input = self.site_input.text
        self.site_input.text = ""

        analise_gpt = consultar_analise_gpt(site_input)

        if isinstance(analise_gpt, dict):
            texto_formatado = ""
            for chave, valor in analise_gpt.items():
                texto_formatado += f"\n[b]{chave}:[/b]\n{valor}\n"
            self.resultado_consulta.markup = True
            self.resultado_consulta.text = texto_formatado
        else:
            self.resultado_consulta.text = 'Erro na consulta. Tente Novamente.'

        # Voltar à cor original após 0.2s
        Clock.schedule_once(lambda dt: self.reset_button_color(instance), 0.2)

    def reset_button_color(self, button):
        button.background_color = (0.843, 0.827, 0.749, 1)
        button.color=(0.925, 0.922, 0.871, 1)
        button.outline_color=(0.700, 0.674, 0.590, 1)

    def _update_text_size(self, instance, width):
        instance.text_size = (width, None)

    def _update_bg_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_title_text_size(self, instance, value):
        instance.text_size = (instance.width, None)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def update_top_bar_bg(self, instance, value):
        self.top_bar_bg.pos = instance.pos
        self.top_bar_bg.size = instance.size


# iniciar app
class MyApp(App):
    def build(self):
        self.title = "EvitaAI"
        return MyBoxLayout()
    
if __name__ == '__main__':
    MyApp().run()