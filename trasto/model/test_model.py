import pytest

from trasto.infrastructure.memory.repositories import Idefier
from trasto.model.entities import Tarea, EstadoHumor
from trasto.model.value_entities import Idd, Prioridad, CodigoResultado


def test_valida_nombre_tarea():
    
    with pytest.raises(AttributeError): 
        Tarea(
            idd=Idd(Idefier()),
            nombre="",
            accionid=Idd(idefier=Idefier()),
            prioridad=Prioridad(1)
        )

    with pytest.raises(AttributeError): 
        Tarea(
            idd=Idd(Idefier()),
            nombre="hola",
            accionid=Idd(idefier=Idefier()),
            prioridad=Prioridad(1)
        )

    with pytest.raises(AttributeError): 
        Tarea(
            idd=Idd(Idefier()),
            nombre="ho",
            accionid=Idd(idefier=Idefier()),
            prioridad=Prioridad(1)
        )


def test_valida_prioridad_tarea():
    with pytest.raises(AttributeError): 
        Prioridad(value=4)

    with pytest.raises(AttributeError): 
        Prioridad(value=-1)

    assert Prioridad(value=0) != Prioridad(value=1)
    assert Prioridad(value=1) == Prioridad(value=1)
    assert Prioridad(value=0) == Prioridad(value=0)

    
def test_estado_humor():

   e = EstadoHumor(Idd(idefier=Idefier()))
   assert e.estado == 0
   assert e.como_estas() == "Normal"
   e.mejora() #1
   assert int(e.estado) == 1
   assert e.como_estas() == "Bien"
   e.mejora() #2
   e.mejora() #3
   assert e.como_estas() == "Muy bien"
   e.empeora() #2
   e.empeora() #1
   e.empeora() #0
   e.empeora() #-1
   assert e.estado == -1
   assert e.como_estas() == "Mal"
   e.empeora() #-2
   e.empeora() #-3
   assert e.como_estas() == "Muy mal"


def test_idd():
    idd1 = Idd(Idefier())
    idd2 = Idd(Idefier())
    assert isinstance(idd1.id, str)
    assert idd1 == idd1
    assert idd2 != idd1
    assert idd1 != idd2

    idd3 = Idd(Idefier(), idd_str=idd1.id)
    assert idd1 == idd3
    assert idd3 == idd1


def test_codigo_resultado():
    cr_bien = CodigoResultado(codigo=CodigoResultado.BUEN_RESULTADO)
    cr_mal = CodigoResultado(codigo=CodigoResultado.MAL_RESULTADO)
    cr_bien1 = CodigoResultado(codigo=CodigoResultado.BUEN_RESULTADO)

    assert cr_bien != cr_mal
    assert cr_bien == cr_bien

    assert cr_bien == cr_bien1

    assert cr_mal == cr_mal