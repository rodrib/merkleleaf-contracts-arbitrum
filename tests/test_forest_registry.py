import boa
import pytest
from src import ForestRegistry


NDVI_PLACEHOLDER = 0
SPECTRAL_SOURCE_PLACEHOLDER = "Pendiente de carga (Sentinel-2 L2A)"


@pytest.fixture(scope="function")
def forest_registry():
    return ForestRegistry.deploy()


def test_owner_is_deployer(forest_registry):
    # boa.env.eoa es la cuenta que hizo el deploy en el entorno local de test
    assert forest_registry.owner() == boa.env.eoa


def test_starts_with_zero_samples(forest_registry):
    assert forest_registry.total_samples() == 0


def test_log_single_sample(forest_registry):
    sample_id = forest_registry.log_sample(
        "QUEBRA 1",
        -25917750,
        -58376806,
        305,   # dap_mm
        830,   # hf_cm
        1600,  # ht_cm
        NDVI_PLACEHOLDER,
        SPECTRAL_SOURCE_PLACEHOLDER,
        b"\x00" * 32,
    )

    assert sample_id == 0
    assert forest_registry.total_samples() == 1

    sample = forest_registry.get_sample(0)
    assert sample.name == "QUEBRA 1"
    assert sample.dap_mm == 305
    assert sample.ht_cm == 1600


def test_unauthorized_address_cannot_log(forest_registry):
    random_address = boa.env.generate_address()
    with boa.env.prank(random_address):
        with boa.reverts():
            forest_registry.log_sample(
                "QUEBRA X",
                0, 0, 0, 0, 0,
                NDVI_PLACEHOLDER,
                SPECTRAL_SOURCE_PLACEHOLDER,
                b"\x00" * 32,
            )


def test_owner_can_authorize_new_logger(forest_registry):
    field_operator = boa.env.generate_address()
    forest_registry.set_authorized_logger(field_operator, True)

    with boa.env.prank(field_operator):
        sample_id = forest_registry.log_sample(
            "QUEBRA 2",
            -25917778,
            -58376833,
            350, 800, 1600,
            NDVI_PLACEHOLDER,
            SPECTRAL_SOURCE_PLACEHOLDER,
            b"\x00" * 32,
        )

    assert sample_id == 0


def test_ndvi_out_of_range_reverts(forest_registry):
    with boa.reverts():
        forest_registry.log_sample(
            "QUEBRA X",
            0, 0, 0, 0, 0,
            15_000,  # fuera del rango permitido (-10000 a 10000)
            SPECTRAL_SOURCE_PLACEHOLDER,
            b"\x00" * 32,
        )


def test_latitude_out_of_range_reverts(forest_registry):
    with boa.reverts():
        forest_registry.log_sample(
            "QUEBRA X",
            95_000_000,  # > 90 grados, invalido
            0,
            305, 830, 1600,
            NDVI_PLACEHOLDER,
            SPECTRAL_SOURCE_PLACEHOLDER,
            b"\x00" * 32,
        )


def test_longitude_out_of_range_reverts(forest_registry):
    with boa.reverts():
        forest_registry.log_sample(
            "QUEBRA X",
            0,
            185_000_000,  # > 180 grados, invalido
            305, 830, 1600,
            NDVI_PLACEHOLDER,
            SPECTRAL_SOURCE_PLACEHOLDER,
            b"\x00" * 32,
        )


def test_zero_dap_reverts(forest_registry):
    with boa.reverts():
        forest_registry.log_sample(
            "QUEBRA X",
            0, 0,
            0,  # dap_mm invalido
            830, 1600,
            NDVI_PLACEHOLDER,
            SPECTRAL_SOURCE_PLACEHOLDER,
            b"\x00" * 32,
        )


def test_height_total_less_than_fuste_reverts(forest_registry):
    with boa.reverts():
        forest_registry.log_sample(
            "QUEBRA X",
            0, 0,
            305,
            1600,  # hf_cm mayor que ht_cm, invalido
            800,
            NDVI_PLACEHOLDER,
            SPECTRAL_SOURCE_PLACEHOLDER,
            b"\x00" * 32,
        )


def test_get_sample_invalid_id_reverts(forest_registry):
    with boa.reverts():
        forest_registry.get_sample(0)


def test_non_owner_cannot_set_authorized_logger(forest_registry):
    random_address = boa.env.generate_address()
    with boa.env.prank(random_address):
        with boa.reverts():
            forest_registry.set_authorized_logger(random_address, True)


def test_set_authorized_logger_zero_address_reverts(forest_registry):
    with boa.reverts():
        forest_registry.set_authorized_logger(
            "0x0000000000000000000000000000000000000000", True
        )


def test_revoked_logger_cannot_log(forest_registry):
    field_operator = boa.env.generate_address()
    forest_registry.set_authorized_logger(field_operator, True)
    forest_registry.set_authorized_logger(field_operator, False)

    with boa.env.prank(field_operator):
        with boa.reverts():
            forest_registry.log_sample(
                "QUEBRA X",
                0, 0, 305, 830, 1600,
                NDVI_PLACEHOLDER,
                SPECTRAL_SOURCE_PLACEHOLDER,
                b"\x00" * 32,
            )


def test_owner_can_transfer_ownership(forest_registry):
    new_owner = boa.env.generate_address()
    forest_registry.transfer_ownership(new_owner)

    assert forest_registry.owner() == new_owner

    # el owner anterior ya no puede autorizar loggers
    with boa.reverts():
        forest_registry.set_authorized_logger(new_owner, True)

    # el nuevo owner si puede
    with boa.env.prank(new_owner):
        forest_registry.set_authorized_logger(new_owner, True)
    assert forest_registry.authorized_loggers(new_owner) is True


def test_non_owner_cannot_transfer_ownership(forest_registry):
    random_address = boa.env.generate_address()
    with boa.env.prank(random_address):
        with boa.reverts():
            forest_registry.transfer_ownership(random_address)


def test_transfer_ownership_zero_address_reverts(forest_registry):
    with boa.reverts():
        forest_registry.transfer_ownership(
            "0x0000000000000000000000000000000000000000"
        )