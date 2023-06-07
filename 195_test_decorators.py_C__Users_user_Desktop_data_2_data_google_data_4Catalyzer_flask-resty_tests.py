from flask_resty import Api, get_item_or_404, ModelView
import pytest
from sqlalchemy import Column, Integer

# -----------------------------------------------------------------------------


@pytest.yield_fixture
def models(db):
    class Widget(db.Model):
        __tablename__ = 'widgets'

        id = Column(Integer, primary_key=True)

    db.create_all()

    yield {
        'widget': Widget,
    }

    db.drop_all()


@pytest.fixture(autouse=True)
def routes(app, models):
    class WidgetView(ModelView):
        model = models['widget']

        @get_item_or_404
        def get(self, item):
            return str(item.id)

        @get_item_or_404(create_missing=True)
        def put(self, item):
            return str(item.id)

    api = Api(app)
    api.add_resource('/widgets/<int:id>', WidgetView)


@pytest.fixture(autouse=True)
def data(db, models):
    db.session.add(models['widget']())
    db.session.commit()


# -----------------------------------------------------------------------------


def test_get_item(client):
    response = client.get('/widgets/1')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == '1'


def test_get_item_create_missing(client):
    response = client.put('/widgets/2')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == '2'


# -----------------------------------------------------------------------------


def test_error_not_found(client):
    response = client.get('/widgets/2')
    assert response.status_code == 404
