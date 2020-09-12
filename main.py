from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel
import random


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self._score_label = CoreLabel(text="Score: 0")
        self._score_label.refresh()
        self._score = 0

        self.register_event_type("on_frame")

        with self.canvas:
            self._score_instruction = Rectangle(texture=self._score_label.texture, pos=(Window.width / 2, Window.height - 25), size=self._score_label.texture.size)

        self.keysPressed = set()
        self._entities = set()

        Clock.schedule_interval(self._on_frame, 0)
        Clock.schedule_interval(self.spawn_enemies, 3)

    def spawn_enemies(self,dt):
        random_x = random.randint(0, Window.width)
        y = 50
        #random_speed = random.randint(100,300)
        self.add_entity(Enemy(pos=(random_x, y),size=(100,50)))


    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass


    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

    def collides(self, e1, e2):
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[1]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y:
            return True
        else:
            return False

    def colliding_entities(self, entity):
        result = set()
        for e in self._entities:
            if self.collides(e, entity) and e != entity:
                result.add(e)
        return result


    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keysPressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        print("[0]=", keycode[0])
        print("[0]=", keycode[1])
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)


class Entity(object):
    def __init__(self):
        self._pos = (0,0)
        self._size = (50,50)
        self._source = "car.png"
        self._instruction = Rectangle(pos=self._pos,size=self._size,source=self._source)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source


class Poop(Entity):
    def __init__(self,pos,speed=300):
        super().__init__()
        sound = SoundLoader.load("Pew_Pew.wav")
        sound.play()
        self.pos = pos
        self._speed = speed
        self.source = "poop.png"
        self.size = (25,25)
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        #check for collision/out of bounds
        if self.pos[1] < 0:
            game.unbind(on_frame=self.move_step)
            game.remove_entity(self)
            return
        for e in game.colliding_entities(self):
            if isinstance(e, Enemy):
                game.add_entity(Explosion(self.pos))
                self.stop_callbacks()
                game.remove_entity(self)
                e.stop_callbacks()
                game.remove_entity(e)
                return

        #move
        step_size = self._speed * dt
        new_y = self.pos[1] - (step_size * 2)
        new_x = self.pos[0]
        self.pos = (new_x, new_y)


class Enemy(Entity):
    def __init__(self, pos, size, speed=100):
        super().__init__()
        self._pos = pos
        self._speed = speed
        self.size = size
        game.bind(on_frame=self.move_step)
        self.track_dir = set()

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        # check for collision/out of bounds
        # if self.pos[1] < 0:
        #     game.unbind(on_frame=self.move_step)
        #     game.remove_entity(self)
        #     return
        for e in game.colliding_entities(self):
            if e == game.player:
                #Explosion
                game.add_entity(Explosion(self.pos))
                self.stop_callbacks()
                game.remove_entity(self)
                return

        # move
        print("here")
        step_size = self._speed * dt

        currentx = self.pos[0]
        direction = -1
        d = 0
        if currentx <= 0 and not self.track_dir.__contains__(direction):
            direction *= -1
            self.track_dir.add(direction)
        if currentx >= Window.width and not self.track_dir.__contains__(direction):
            direction *= -1
            self.track_dir.add(direction)

        if currentx > (Window.width / 2) - 20 and currentx < (Window.width / 2) + 20:
            #self.track_dir.remove(direction)
            pass


        # print("stepsize=", step_size)
        # print("currentx=",currentx)
        # print("direction", direction)
        new_y = self.pos[1]
        new_x = currentx + (step_size * direction)

        # print("newx=", new_x)
        self.pos = (new_x, new_y)


class Explosion(Entity):
    def __init__(self, pos):
        super().__init__()

        sound = SoundLoader.load("Explosion.wav")
        sound.play()
        self.pos = (pos[0],pos[1]-50)
        self.source = "boom.png"
        self.size = (100, 50)
        Clock.schedule_once(self._remove_me, 2)

    def _remove_me(self,dt):
        game.remove_entity(self)


class Player(Entity):
    def __init__(self):
        super().__init__()
        self.source = "bird.png"
        self.size = (75,50)
        game.bind(on_frame=self.on_frame)
        self.pos = (Window.width / 2, Window.height - 150)

    def stop_callbacks(self):
        game.unbind(on_frame=self.on_frame)

    def on_frame(self, sender, dt):
        #move
        currentx = self.pos[0]
        currenty = self.pos[1]
        step_size = 200 * dt

        if "w" in game.keysPressed:
            currenty += step_size
        if "s" in game.keysPressed:
            currenty -= step_size
        if "a" in game.keysPressed:
            currentx -= step_size
        if "d" in game.keysPressed:
            currentx += step_size

        newx = currentx
        newy = currenty
        self.pos = (newx, newy)

        #shoot poop
        if "spacebar" in game.keysPressed:
            x = self.pos[0]
            y = self.pos[1] - 20
            game.add_entity(Poop((x,y)))


game = GameWidget()
game.player = Player()
game.add_entity(game.player)



class MyApp(App):
    def build(self):
        return game

if __name__ == "__main__":
    app = MyApp()
    app.run()
