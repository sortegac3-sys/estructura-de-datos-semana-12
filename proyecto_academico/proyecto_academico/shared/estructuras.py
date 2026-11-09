"""
PILA y COLA construidas SOBRE UNA LISTA de Python.

Las dos usan una list por dentro (self.items). Lo único que cambia
es POR DÓNDE entran y POR DÓNDE salen los elementos:

    PILA (LIFO)  Last In, First Out    -> entra y sale por el MISMO extremo (el final)
    COLA (FIFO)  First In, First Out   -> entra por el final, sale por el INICIO
"""


class Pila:
    """Como una pila de platos: el último que pones es el primero que sacas."""

    def __init__(self):
        self.items = []

    def apilar(self, elemento):          # push
        self.items.append(elemento)      # agrega al FINAL

    def desapilar(self):                 # pop
        if self.esta_vacia():
            return None
        return self.items.pop()          # saca del FINAL

    def cima(self):                      # peek: mira el tope sin sacarlo
        if self.esta_vacia():
            return None
        return self.items[-1]

    def esta_vacia(self):
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)

    def a_lista(self):
        # de la cima hacia el fondo (lo más reciente primero)
        return list(reversed(self.items))


class Cola:
    """Como la fila del banco: el primero que llega es el primero que se atiende."""

    def __init__(self):
        self.items = []

    def encolar(self, elemento):         # enqueue
        self.items.append(elemento)      # entra por el FINAL

    def desencolar(self):                # dequeue
        if self.esta_vacia():
            return None
        return self.items.pop(0)         # sale por el INICIO

    def frente(self):                    # peek: quién sigue, sin sacarlo
        if self.esta_vacia():
            return None
        return self.items[0]

    def esta_vacia(self):
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)

    def a_lista(self):
        # del frente hacia el final (en el orden en que serán atendidos)
        return list(self.items)
