import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class MyGridLayout(GridLayout): # montar grid
    def __init__(self,**kwargs):
        super(MyGridLayout,self).__init__(**kwargs)

        self.cols=3
        
        self.add_widget(Label(text="Site: "))
        self.name = TextInput(multiline=False)
        self.add_widget(self.name)

class MyApp(App): # iniciar app
    def build(self):
        return Label(text="EvitaAi")
    
if __name__ == '__main__':
    MyApp().run()