#VALUE OBJECTS



class IdefierInterface:
    def create_new_id(self) -> str:
        pass

class Idd:
    def __init__(self, idefier: IdefierInterface):
        self._id = idefier.create_new_id()

    @property
    def id(self):
        return self._id     

    def __eq__(self, other):
        return self._id == other.id

    def __repr__(self):
        return f"{self.id}"

    def __str__(self):
        return f"{self.id}"



class CambioHumor:
    HUMOR_MEJORA = 1
    HUMOR_EMPEORA = -1
    def __init__(self, cambio: int):
        self._cambio = cambio

    @property
    def cambio(self):
        return self._cambio


class CodigoResultado:
    MAL_RESULTADO = 0
    BUEN_RESULTADO = 1
    def __init__(self, codigo):
        self._codigo = codigo

    @property
    def codigo(self):
        return self._codigo

    def __eq__(self, other):
        return self.codigo == other.codigo

    def __str__(self):
        return "bueno" if self.codigo == self.BUEN_RESULTADO else "MALO"


class ResultadoAccion:
    def __init__(self, codigo: CodigoResultado, msg: str):
        print(type(codigo))
        self._codigo = codigo
        self._msg = msg

    @property
    def codigo(self):
        return self._codigo

    @property
    def msg(self):
        return self._msg

    def is_good(self):
        return self._codigo == CodigoResultado(CodigoResultado.BUEN_RESULTADO)

    def __repr__(self):
        return "{self}"

    def __str__(self):
        return f"Resultado[codigo: : {self._codigo}; msg: {self._msg}"

class TipoAccion:

    def __init__(self, nombre: str):
        self._nombre = nombre

    @property
    def nombre(self):
        return self._nombre


    def __eq__(self, other):
        return self.nombre == other.nombre


    def __repr__(self):
        return f"{self.nombre}"


    def __str__(self):
        return f"{self.nombre}"


class Prioridad:
    def __init__(self, value: int):
        if not value in (0, 1):
            raise AttributeError("La prioridad solo puede ser 1 o 0")
        self._value = value

    @property
    def value(self):
        return self._value


    def __eq__(self, other):
        return self.value == other.value
    

    def __lt__(self, other):
        return self.value < other.value


    def __gt__(self, other):
        return self.value > other.value


    def __repr__(self):
        return "prioridad: {}".format("alta" if self.value == 1 else "baja")


    def __str__(self):
        return "prioridad: {}".format("alta" if self.value == 1 else "baja")
