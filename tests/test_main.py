import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from api.main import app, get_session
from api.models import Measurement, Observer


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="observer_1")
def observer_fixture(session: Session):
    observer = Observer(phone="+1555-555-5555", email="555-5555@bsd.pw")
    session.add(observer)
    session.commit()
    yield observer
    session.delete(observer)


def test_create_observer(client: TestClient):
    response = client.post(
        "/observers/", json={"phone": "+1555-555-5555", "email": "555-5555@bsd.pw"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["phone"] == "+1555-555-5555"
    assert data["email"] == "555-5555@bsd.pw"
    assert data["id"] is not None


def test_create_observer_incomplete(client: TestClient):
    # No hande
    response = client.post("/observers/", json={"phone": "+1555-555-5555"})
    assert response.status_code == 422


def test_create_observer_invalid(client: TestClient):
    # email has an invalid type
    response = client.post(
        "/observers/", json={"phone": "+1555-555-5555", "email": {"key": "value"}}
    )
    assert response.status_code == 422


def test_delete_observer(session: Session, client: TestClient, observer_1: Observer):
    response = client.delete(f"/observers/{observer_1.id}")
    observer_in_db = session.get(Observer, observer_1.id)

    assert response.status_code == 200
    assert observer_in_db is None


def test_create_measurement_wrong_observer(client: TestClient, observer_1: Observer):
    response = client.post(
        "/measurements/",
        json={
            "temperaturescale": "C",
            "temperature": 4,
            "organizationid": 876543,
            "siteid": 65432,
            "observer_id": 8,
        },
    )

    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Not a valid observer id"
