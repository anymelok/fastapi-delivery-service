import pytest

# Базовые данные для тестов
VALID_PARCEL = {'name': 'Iphone 15', 'weight': 0.5, 'type_id': 2, 'price_usd': 1000.0}


@pytest.mark.asyncio
async def test_get_types(ac):
    """Тест получения типов посылок"""
    resp = await ac.get('/parcels/types')
    assert resp.status_code == 200
    assert len(resp.json()) == 3
    assert resp.json()[0]['name'] == 'одежда'


@pytest.mark.asyncio
async def test_register_parcel_success(ac):
    """Успешная регистрация и получение куки сессии"""
    resp = await ac.post('/parcels/', json=VALID_PARCEL)
    assert resp.status_code == 201
    assert 'id' in resp.json()
    assert 'session_id' in resp.cookies


@pytest.mark.asyncio
async def test_register_parcel_validation_error(ac):
    """Ошибка валидации: отрицательный вес"""
    invalid_data = VALID_PARCEL.copy()
    invalid_data['weight'] = -1.0
    resp = await ac.post('/parcels/', json=invalid_data)
    assert resp.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_list_my_parcels(ac):
    """Проверка списка (должна примениться кука из сессии клиента)"""
    # Регистрируем
    await ac.post('/parcels/', json=VALID_PARCEL)
    # Получаем список
    resp = await ac.get('/parcels/')
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]['delivery_cost'] == 'Не рассчитано'
    assert data[0]['type_name'] == 'электроника'


@pytest.mark.asyncio
async def test_get_parcel_by_id_success(ac):
    """Получение своей посылки по ID"""
    reg_resp = await ac.post('/parcels/', json=VALID_PARCEL)
    parcel_id = reg_resp.json()['id']

    resp = await ac.get(f'/parcels/{parcel_id}')
    assert resp.status_code == 200
    assert resp.json()['id'] == parcel_id


@pytest.mark.asyncio
async def test_get_parcel_by_id_forbidden(ac):
    """Попытка получить чужую посылку (без нужной куки)"""
    reg_resp = await ac.post('/parcels/', json=VALID_PARCEL)
    parcel_id = reg_resp.json()['id']

    # Очищаем куки у клиента (эмулируем другого юзера)
    ac.cookies.clear()

    resp = await ac.get(f'/parcels/{parcel_id}')
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_parcel_not_found(ac):
    """Получение несуществующей посылки"""
    resp = await ac.get('/parcels/fake-uuid-1234')
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_run_calculation_changes_status(ac):
    """Тест фоновой задачи расчета стоимости"""
    # 1. Создаем посылку
    await ac.post('/parcels/', json=VALID_PARCEL)

    # 2. Запускаем пересчет
    calc_resp = await ac.post('/parcels/tasks/run-calculation')
    assert calc_resp.status_code == 200

    # 3. Проверяем, что статус "Не рассчитано" изменился на число
    list_resp = await ac.get('/parcels/')
    data = list_resp.json()

    # Последняя добавленная посылка
    parcel = data[-1]
    assert parcel['delivery_cost'] != 'Не рассчитано'
    assert isinstance(parcel['delivery_cost'], float)
