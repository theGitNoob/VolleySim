import numpy as np
import random
import tensorflow as tf
from tensorflow.keras import layers
import matplotlib.pyplot as plt


class PlayerAI:
    def __init__(self, altura, resistencia, salto_maximo, velocidad):
        self.altura = altura
        self.resistencia = resistencia
        self.salto_maximo = salto_maximo
        self.velocidad = velocidad
        self.current_resistencia = resistencia
        self.model = self._build_model()
        self.memory = []
        self.gamma = 0.95  # Discount rate
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999  # Ajuste para disminuir más lentamente

    def _build_model(self):
        inputs = tf.keras.Input(shape=(4,))  # Ajusta según la dimensión de entrada adecuada
        x = layers.Dense(24, activation='relu')(inputs)
        x = layers.Dense(24, activation='relu')(x)
        outputs = layers.Dense(3, activation='linear')(x)  # 3 acciones posibles: pasar, bloquear, disparar

        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=0.001))
        return model

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            action = random.randrange(3)
        else:
            act_values = self.model.predict(state)
            print("Valores predichos por la red:", act_values)
            action = np.argmax(act_values[0])

        action_name = ['Pase', 'Bloqueo', 'Tiro'][action]
        print(f'Acción ejecutada: {action_name}')
        return action

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return  # No se puede hacer replay si no hay suficientes experiencias almacenadas

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            history = self.model.fit(state, target_f, epochs=1, verbose=0)
            print(f"Entrenando modelo: Pérdida = {history.history['loss'][0]}")
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        print(f"Epsilon actual: {self.epsilon}")


class Game:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.score = [0, 0]
        self.state = self.get_initial_state()

    @staticmethod
    def get_initial_state():
        # Example state could include player positions, scores, and possession
        return np.zeros((1, 4))  # Simplified for illustration

    def play(self, episodes=2):  # Aumenta el número de episodios para entrenar más tiempo
        rewards = []
        for episode in range(episodes):
            if episode == 10: break
            print(f'\n--- Episodio {episode + 1} ---')
            total_reward = 0
            done = False
            for step in range(10):  # Run for 10 steps
                print(f'\n--- Step {step + 1} ---')
                action = self.team1.act(self.state)
                next_state, reward, done = self.step(action)

                # Verificación antes de la normalización
                if np.max(next_state) != 0:
                    next_state = next_state / np.max(next_state)
                else:
                    print("Skipping normalization due to max value being 0")

                self.team1.remember(self.state, action, reward, next_state, done)
                self.state = next_state
                self.team1.replay()
                total_reward += reward
                print(f'Score: Equipo 1: {self.score[0]}, Equipo 2: {self.score[1]}')
                if done:
                    break
            rewards.append(total_reward)
            print(f"Recompensa total para el episodio {episode + 1}: {total_reward}")
            if done:
                print(f"Juego terminado en el episodio {episode + 1}")
                break

        self.plot_rewards(rewards)

    def step(self, action):
        # Implementación de la lógica de paso del juego
        if action == 0:  # Pase
            print("El jugador realiza un pase.")
            reward = 1.0  # Recompensa ajustada
        elif action == 1:  # Bloqueo
            print("El jugador intenta bloquear.")
            reward = 2.0  # Recompensa ajustada
        else:  # Tiro
            print("El jugador realiza un tiro.")
            reward = 3.0  # Recompensa ajustada

        # Actualización de puntuación ficticia para mostrar el progreso del juego
        if random.random() > 0.5:  # Simplificado: posibilidad de marcar punto
            self.score[0] += 1
            print("Equipo 1 marca un punto!")
        else:
            self.score[1] += 1
            print("Equipo 2 marca un punto!")

        next_state = np.zeros((1, 4))
        done = False
        return next_state, reward, done

    def plot_rewards(self, rewards):
        plt.plot(rewards)
        plt.xlabel('Episodios')
        plt.ylabel('Recompensa acumulada')
        plt.title('Desempeño de la red neuronal')
        plt.show()


# Inicialización de jugadores con IA
team1_player = PlayerAI(altura=1.9, resistencia=100, salto_maximo=0.6, velocidad=5.5)
team2_player = PlayerAI(altura=1.85, resistencia=95, salto_maximo=0.58, velocidad=5.8)

# Creación de un juego
game = Game(team1_player, team2_player)
game.play(episodes=100)  # Aumenta el número de episodios para observar el aprendizaje
