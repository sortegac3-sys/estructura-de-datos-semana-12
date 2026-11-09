from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido
from shared.estructuras import Pila, Cola

# TUPLAS: campos fijos por los que se puede buscar (no deben cambiar nunca)
CAMPOS_BUSCABLES_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")
CAMPOS_BUSCABLES_MATERIA = ("nombre", "codigo")


#Clase base
class CrudBase(ABC):

    @abstractmethod
    def leer(self): pass

    @abstractmethod
    def obtener(self, id_registro): pass

    @abstractmethod
    def buscar(self, texto): pass

    @abstractmethod
    def siguiente(self): pass

    @abstractmethod
    def crear(self, datos): pass

    @abstractmethod
    def actualizar(self, id_registro, datos): pass

    @abstractmethod
    def eliminar(self, id_registro): pass


#Controlador de estudiantes
class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO: emails de los OTROS estudiantes (pertenencia instantánea)
            emails_usados = {e.email for e in self.lista if e.id != id_actual}
            if email in emails_usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            # CONJUNTO: carnets de los OTROS estudiantes
            carnets_usados = {e.carnet for e in self.lista if e.id != id_actual}
            if carnet in carnets_usados:
                return "Ese carnet ya está registrado"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados
        for estudiante in self.lista:
            for campo in CAMPOS_BUSCABLES_ESTUDIANTE:
                if texto in str(getattr(estudiante, campo)).lower():
                    encontrados.append(estudiante)
                    break
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(self.siguiente(),
                                str(datos["nombre"]).strip().title(),
                                str(datos["apellido"]).strip().title(),
                                str(datos["email"]).strip().lower(),
                                str(datos["carnet"]).strip().upper(),
                                str(datos.get("carrera", "")).strip().title())
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un estudiante
        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)   # ANTES de tocar el objeto
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras(self):
        """CONJUNTO de carreras: sin repetidas. sorted() lo devuelve como lista."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})

#Controlador de materias
class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo", "creditos", "cupos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            # CONJUNTO de códigos de las OTRAS materias
            codigos_usados = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos_usados:
                return f"El código {codigo} ya existe"

        if "creditos" in datos:
            creditos = str(datos["creditos"]).strip()
            if not creditos.isdigit() or not 1 <= int(creditos) <= 10:
                return "Los créditos deben ser un entero entre 1 y 10"

        if "cupos" in datos:
            cupos = str(datos["cupos"]).strip()
            if not cupos.isdigit() or int(cupos) > Materia.CUPOS_MAXIMOS:
                return f"Los cupos deben ser un entero entre 0 y {Materia.CUPOS_MAXIMOS}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas
        for materia in self.lista:
            for campo in CAMPOS_BUSCABLES_MATERIA:
                if texto in str(getattr(materia, campo)).lower():
                    encontradas.append(materia)
                    break
        return encontradas

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = Materia(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["codigo"]).strip().upper(),
                          int(datos["creditos"]),
                          int(datos["cupos"]))
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        sin_cupo = []
        for materia in self.lista:
            if not materia.hay_cupo():
                sin_cupo.append(materia)
        return sin_cupo


#Controlador de matrículas
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias,
                 archivo="data/matriculas.json", archivo_espera="data/espera.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.gestor_espera = GestorJSON(archivo_espera)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

        self.espera = {}
        for pedido in self.gestor_espera.leer():
            self.espera.setdefault(pedido["materia_id"], Cola()).encolar(pedido)

        self.historial = Pila()

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def guardar_espera(self):
        datos = []
        for cola in self.espera.values():
            datos.extend(cola.a_lista())          # cada cola conserva su orden
        self.gestor_espera.guardar(datos)

    def _ya_matriculado(self, estudiante_id, materia_id, periodo):
        # Se comparan LOS TRES juntos, no cada uno por separado
        for m in self.lista:
            if (m.estudiante_id == estudiante_id and m.materia_id == materia_id
                    and m.periodo == periodo):
                return True
        return False

    def _ya_en_espera(self, estudiante_id, materia_id, periodo):
        cola = self.espera.get(materia_id)
        if cola is None:
            return False
        for pedido in cola.a_lista():
            if pedido["estudiante_id"] == estudiante_id and pedido["periodo"] == periodo:
                return True
        return False

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        periodo = str(datos.get("periodo", "")).strip()
        if periodo == "":
            return "El periodo es obligatorio (ej. 2026-1)"
        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"
        if self.materias.obtener(materia_id) is None:
            return f"No existe una materia con id {materia_id}"
        if self._ya_matriculado(estudiante_id, materia_id, periodo):
            return "Ese estudiante ya está matriculado en esa materia y periodo"
        if self._ya_en_espera(estudiante_id, materia_id, periodo):
            return "Ese estudiante ya está en la lista de espera de esa materia"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        # Las matrículas se buscan por periodo, ej: "2026-1"
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas
        for matricula in self.lista:
            if texto in matricula.periodo:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        """Matricula si hay cupo; si no hay, el pedido entra a la COLA de espera."""
        error = self.validar(datos)
        if error:
            return False, error

        estudiante_id = int(datos["estudiante_id"])
        materia_id = int(datos["materia_id"])
        periodo = str(datos["periodo"]).strip()
        materia = self.materias.obtener(materia_id)

        # ---- Sin cupo: ENCOLAR (entra por el final de la fila) ----
        if not materia.hay_cupo():
            pedido = {"estudiante_id": estudiante_id,
                      "materia_id": materia_id,
                      "periodo": periodo}
            self.espera.setdefault(materia_id, Cola()).encolar(pedido)
            self.guardar_espera()
            posicion = len(self.espera[materia_id])
            return True, (f"{materia.nombre} no tiene cupo. El estudiante quedó en "
                          f"lista de espera (posición {posicion})")

        # ---- Con cupo: matricular normalmente ----
        matricula = Matricula(self.siguiente(), estudiante_id, materia_id, periodo)
        materia.ocupar_cupo()
        self.lista.append(matricula)
        self.materias.guardar()
        self.guardar()

        # PILA: anotamos la acción para poder deshacerla
        self.historial.apilar(("matricular", matricula.id))
        return True, f"Matrícula {matricula.id} registrada"

    def actualizar(self, id_matricula, datos):
        # Lo único que se puede cambiar de una matrícula es la nota
        if set(datos) != {"nota"}:
            return False, "Solo se puede registrar la nota de una matrícula"
        return self.registrar_nota(id_matricula, datos["nota"])

    def registrar_nota(self, id_matricula, nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        if not Materia.es_nota_valida(nota):          # método ESTÁTICO
            return False, "La nota debe ser un número entre 0 y 20"
        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota registrada: {matricula.nota:.1f} ({matricula.estado()})"

    def eliminar(self, id_matricula):
        """Retirar una matrícula: libera el cupo y atiende al primero de la cola."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        # PILA: guardamos una copia de lo que se borra, para poder restaurarla
        self.historial.apilar(("retirar", matricula.a_diccionario()))

        promovidos = self._quitar(matricula)
        mensaje = f"Matrícula {id_matricula} retirada y cupo liberado"
        for promovido in promovidos:
            mensaje += (f"\n  → De la lista de espera se matriculó el estudiante "
                        f"{promovido.estudiante_id} (matrícula {promovido.id})")
        return True, mensaje

    def _quitar(self, matricula):
        """Borra la matrícula, libera el cupo y llama a la cola. Devuelve los promovidos."""
        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
        self.lista.remove(matricula)
        promovidos = self._promover(matricula.materia_id)
        self.materias.guardar()
        self.guardar()
        self.guardar_espera()
        return promovidos

    def _promover(self, materia_id):
        """COLA: mientras haya cupo, DESENCOLAR al primero de la fila y matricularlo."""
        promovidos = []
        materia = self.materias.obtener(materia_id)
        cola = self.espera.get(materia_id)
        if materia is None or cola is None:
            return promovidos

        while materia.hay_cupo() and not cola.esta_vacia():
            pedido = cola.desencolar()                       # sale el que llegó primero
            if self.estudiantes.obtener(pedido["estudiante_id"]) is None:
                continue                                     # ya no existe: se salta
            nueva = Matricula(self.siguiente(), pedido["estudiante_id"],
                              materia_id, pedido["periodo"])
            materia.ocupar_cupo()
            self.lista.append(nueva)
            promovidos.append(nueva)
        return promovidos

    def ver_espera(self, id_materia):
        """Devuelve los pedidos en orden de atención (el primero de la lista es el siguiente)."""
        cola = self.espera.get(id_materia)
        if cola is None:
            return []
        return cola.a_lista()

    def deshacer(self):
        """PILA: saca la ÚLTIMA acción registrada y la revierte."""
        ultima = self.historial.cima()                 # miramos sin sacar todavía
        if ultima is None:
            return False, "No hay acciones para deshacer"

        accion, dato = ultima

        if accion == "matricular":
            matricula = self.obtener(dato)
            if matricula is None:
                self.historial.desapilar()
                return False, "Esa matrícula ya no existe; se descartó del historial"
            self._quitar(matricula)
            self.historial.desapilar()
            return True, f"Deshecho: se anuló la matrícula {dato}"

        if accion == "retirar":
            materia = self.materias.obtener(dato["materia_id"])
            if materia is None or not materia.hay_cupo():
                # Ese cupo ya lo tomó alguien de la cola: se descarta para no trabar la pila
                self.historial.desapilar()
                return False, ("No se puede restaurar: el cupo ya fue ocupado por otro "
                               "estudiante. La acción se descartó del historial")
            if self._ya_matriculado(dato["estudiante_id"], dato["materia_id"], dato["periodo"]):
                self.historial.desapilar()
                return False, "El estudiante ya fue matriculado de nuevo; se descartó"
            datos = dict(dato)
            datos["id"] = self.siguiente()
            restaurada = Matricula.desde_diccionario(datos)
            materia.ocupar_cupo()
            self.lista.append(restaurada)
            self.materias.guardar()
            self.guardar()
            self.historial.desapilar()
            return True, f"Deshecho: se restauró la matrícula (ahora con id {restaurada.id})"

        return False, "Acción desconocida en el historial"

    def ver_historial(self):
        """Acciones pendientes de deshacer, de la más reciente a la más antigua."""
        textos = []
        for accion, dato in self.historial.a_lista():
            if accion == "matricular":
                textos.append(f"Matricular (matrícula {dato})")
            else:
                textos.append(f"Retirar (estudiante {dato['estudiante_id']}, "
                              f"materia {dato['materia_id']})")
        return textos

    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        # DICCIONARIOS ÍNDICE {id: objeto}: acceso directo sin recorrer listas
        estudiantes = {e.id: e for e in self.estudiantes.leer()}
        materias = {m.id: m for m in self.materias.leer()}
        estudiante = estudiantes.get(matricula.estudiante_id)
        materia = materias.get(matricula.materia_id)

        nota = "-" if matricula.nota is None else f"{matricula.nota:.1f}"
        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        if estudiante:
            texto += f"Estudiante: {estudiante.nombre_completo()}   ({estudiante.carnet})\n"
        else:
            texto += "Estudiante: eliminado\n"
        if materia:
            texto += f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
        else:
            texto += "Materia   : eliminada\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {nota}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO de LISTAS: {estudiante_id: [matrículas de ese estudiante]}."""
        agrupadas = {}
        for matricula in self.lista:
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        notas = []
        for matricula in self.lista:
            if matricula.estudiante_id == id_estudiante and matricula.nota is not None:
                notas.append(matricula.nota)
        if not notas:
            return None
        return round(sum(notas) / len(notas), 2)

    def total_aprobadas(self):
        total = 0
        for matricula in self.lista:
            if matricula.esta_aprobada():
                total += 1
        return total
