import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRATOS_DIR = ROOT / "src" / "gestion_atencion" / "modulos" / "atencion" / "infraestructura" / "contratos" / "avro"


def _cargar_schema(version: str):
    path = CONTRATOS_DIR / version / f"SolicitudPartnerRegistrada.{version}.avsc"
    assert path.exists(), f"No existe el schema Avro para {version}: {path}"

    with path.open("r", encoding="utf-8") as archivo:
        schema = json.load(archivo)

    assert schema["type"] == "record"
    assert schema["name"] == "SolicitudPartnerRegistrada"
    assert "fields" in schema and schema["fields"]
    return schema


def _campos_del_record(record_schema):
    return {campo["name"]: campo for campo in record_schema["fields"]}


def test_schema_v1_existe_y_es_valido():
    schema = _cargar_schema("v1")
    metadata = schema["fields"][0]["type"]
    data = schema["fields"][1]["type"]

    metadata_campos = _campos_del_record(metadata)
    data_campos = _campos_del_record(data)

    assert set(metadata_campos) == {"event_id", "event_time", "event_type", "event_version"}
    assert metadata_campos["event_time"]["type"] == "long"
    assert data_campos.keys() == {
        "solicitud_id",
        "partner_id",
        "referencia_externa",
        "tipo_servicio",
    }


def test_schema_v2_existe_y_es_compatible_con_v1_y_agrega_estado():
    schema_v1 = _cargar_schema("v1")
    schema_v2 = _cargar_schema("v2")

    metadata_v1 = _campos_del_record(schema_v1["fields"][0]["type"])
    metadata_v2 = _campos_del_record(schema_v2["fields"][0]["type"])
    data_v1 = _campos_del_record(schema_v1["fields"][1]["type"])
    data_v2 = _campos_del_record(schema_v2["fields"][1]["type"])

    assert set(metadata_v1) == set(metadata_v2)
    assert metadata_v1["event_type"]["type"] == metadata_v2["event_type"]["type"] == "string"
    assert metadata_v1["event_type"]["default"] == metadata_v2["event_type"]["default"] == "SolicitudPartnerRegistrada"
    assert metadata_v1["event_version"]["type"] == metadata_v2["event_version"]["type"] == "string"
    assert metadata_v1["event_version"]["default"] == "v1"
    assert metadata_v2["event_version"]["default"] == "v2"

    for nombre in metadata_v1:
        if nombre != "event_version":
            assert metadata_v1[nombre]["type"] == metadata_v2[nombre]["type"]

    for nombre in data_v1:
        assert nombre in data_v2
        assert data_v1[nombre]["type"] == data_v2[nombre]["type"]

    assert set(data_v2) - set(data_v1) == {"estado"}
    assert data_v2["estado"]["type"] == ["null", "string"]
    assert data_v2["estado"]["default"] is None
